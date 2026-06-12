param(
    [string]$TaskId = "cmt-hard-research-8",
    [int[]]$ProblemNumbers = @(1, 7),
    [string]$ProblemList = "",
    [string]$Model = "deepseek/deepseek-v4-pro",
    [int]$IdleTimeoutMinutes = 20,
    [int]$MaxRuntimeMinutes = 10,
    [int]$PollSeconds = 20,
    [string]$HakimiPath = "D:\DevCache\TaiS\pnpm\hakimi.CMD",
    [string]$RunLabel = "experimental_ab"
)

$ErrorActionPreference = "Stop"
if (Test-Path "variable:PSNativeCommandUseErrorActionPreference") {
    $PSNativeCommandUseErrorActionPreference = $false
}

$BenchmarkRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskRoot = Join-Path $BenchmarkRoot "tasks\$TaskId"
$FullPromptPath = Join-Path $TaskRoot "prompt.md"
$VerifierPath = Join-Path $TaskRoot "verify.py"
$GoldPath = Join-Path $TaskRoot "private\gold.json"
$SourceConfigPath = Join-Path $env:USERPROFILE ".hakimi\config.toml"

if (-not (Test-Path $FullPromptPath)) { throw "Prompt not found: $FullPromptPath" }
if (-not (Test-Path $VerifierPath)) { throw "Verifier not found: $VerifierPath" }
if (-not (Test-Path $GoldPath)) { throw "Gold not found: $GoldPath" }
if (-not (Test-Path $HakimiPath)) { throw "Hakimi command not found: $HakimiPath" }
if (-not (Test-Path $SourceConfigPath)) { throw "Hakimi config not found: $SourceConfigPath" }

if ($ProblemList.Trim()) {
    $ProblemNumbers = @($ProblemList -split '[,\s]+' | Where-Object { $_ } | ForEach-Object { [int]$_ })
}

$PythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($PythonCommand) {
    $PythonExe = $PythonCommand.Source
} else {
    $BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (-not (Test-Path $BundledPython)) { throw "Python not found: $BundledPython" }
    $PythonExe = $BundledPython
}

$Gold = Get-Content $GoldPath -Raw | ConvertFrom-Json
$Fields = @($Gold.checks | ForEach-Object { $_.field })
$FullPrompt = Get-Content $FullPromptPath -Raw

$DefaultOnFlags = @(
    "KIMI_CODE_EXPERIMENTAL_PHYSICS_MEMORY",
    "KIMI_CODE_EXPERIMENTAL_RESEARCH_LEDGER",
    "KIMI_CODE_EXPERIMENTAL_RESEARCH_ACTION",
    "KIMI_CODE_EXPERIMENTAL_DOMAIN_PROFILE",
    "KIMI_CODE_EXPERIMENTAL_WORKFLOW_RECIPE",
    "KIMI_CODE_EXPERIMENTAL_RESEARCH_HARNESS",
    "KIMI_CODE_EXPERIMENTAL_GOAL_COMMAND"
)

$AllFlagEnvNames = $DefaultOnFlags + @(
    "KIMI_CODE_EXPERIMENTAL_MICRO_COMPACTION",
    "KIMI_CODE_EXPERIMENTAL_BACKGROUND_ASK",
    "KIMI_CODE_EXPERIMENTAL_FLAG"
)

function Read-TextFileBestEffort {
    param([string]$Path)
    for ($try = 0; $try -lt 10; $try++) {
        try {
            if (-not (Test-Path $Path)) { return "" }
            $bytes = [System.IO.File]::ReadAllBytes($Path)
            if ($bytes.Length -eq 0) { return "" }
            if ($bytes.Length -ge 2 -and $bytes[0] -eq 0xff -and $bytes[1] -eq 0xfe) {
                return [System.Text.Encoding]::Unicode.GetString($bytes)
            }
            if ($bytes.Length -ge 2 -and $bytes[0] -eq 0xfe -and $bytes[1] -eq 0xff) {
                return [System.Text.Encoding]::BigEndianUnicode.GetString($bytes)
            }
            if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xef -and $bytes[1] -eq 0xbb -and $bytes[2] -eq 0xbf) {
                return [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
            }
            return [System.Text.Encoding]::UTF8.GetString($bytes)
        } catch {
            Start-Sleep -Milliseconds 300
        }
    }
    return ""
}

function Get-FileLengthSafe {
    param([string]$Path)
    try {
        if (Test-Path $Path) { return (Get-Item $Path).Length }
    } catch {
    }
    return 0
}

function Get-ProblemBlock {
    param([string]$Text, [int]$ProblemNumber)
    $next = $ProblemNumber + 1
    $pattern = "(?s)(### $ProblemNumber\..*?)(?=### $next\.|$)"
    $match = [regex]::Match($Text, $pattern)
    if (-not $match.Success) { throw "Problem block not found: $ProblemNumber" }
    return $match.Groups[1].Value.Trim()
}

function Write-JsonFile {
    param([object]$Value, [string]$Path, [int]$Depth = 12)
    ConvertTo-Json -InputObject $Value -Depth $Depth | Set-Content -Path $Path -Encoding utf8
}

function Write-StageFile {
    param([string]$Path, [string]$Stage, [object]$Extra = $null)
    $payload = [ordered]@{
        stage = $Stage
        updated_at = (Get-Date).ToString("o")
    }
    if ($Extra -ne $null) {
        $payload.extra = $Extra
    }
    Write-JsonFile -Value $payload -Path $Path -Depth 14
}

function Extract-FirstJsonObject {
    param([string]$Text)
    $fenceMatches = [regex]::Matches($Text, '(?is)```(?:json)?\s*(\{.*?\})\s*```')
    foreach ($match in $fenceMatches) {
        $candidate = $match.Groups[1].Value
        try {
            $null = $candidate | ConvertFrom-Json
            return $candidate
        } catch {
        }
    }

    $startIndexes = @()
    for ($i = 0; $i -lt $Text.Length; $i++) {
        if ($Text[$i] -eq [char]123) { $startIndexes += $i }
    }
    foreach ($start in $startIndexes) {
        $depth = 0
        $inString = $false
        $escaped = $false
        for ($i = $start; $i -lt $Text.Length; $i++) {
            $ch = $Text[$i]
            if ($inString) {
                if ($escaped) {
                    $escaped = $false
                } elseif ($ch -eq [char]92) {
                    $escaped = $true
                } elseif ($ch -eq [char]34) {
                    $inString = $false
                }
                continue
            }
            if ($ch -eq [char]34) {
                $inString = $true
            } elseif ($ch -eq [char]123) {
                $depth += 1
            } elseif ($ch -eq [char]125) {
                $depth -= 1
                if ($depth -eq 0) {
                    $candidate = $Text.Substring($start, $i - $start + 1)
                    try {
                        $null = $candidate | ConvertFrom-Json
                        return $candidate
                    } catch {
                        break
                    }
                }
            }
        }
    }
    return $null
}

function Stop-ProcessTreeBestEffort {
    param([int]$RootProcessId)
    $descendants = New-Object System.Collections.Generic.List[int]
    $queue = New-Object System.Collections.Generic.Queue[int]
    $queue.Enqueue($RootProcessId)
    while ($queue.Count -gt 0) {
        $currentPid = $queue.Dequeue()
        $children = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$currentPid" -ErrorAction SilentlyContinue)
        foreach ($child in $children) {
            $childPid = [int]$child.ProcessId
            $descendants.Add($childPid)
            $queue.Enqueue($childPid)
        }
    }
    [array]::Reverse($descendants)
    foreach ($childPid in $descendants) {
        Stop-Process -Id $childPid -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $RootProcessId -Force -ErrorAction SilentlyContinue
}

function Invoke-CommandWithModeEnv {
    param(
        [hashtable]$Mode,
        [string]$WorkingDirectory,
        [string]$ArgumentLine,
        [string]$StdoutPath,
        [string]$StderrPath,
        [int]$IdleTimeoutSeconds,
        [int]$MaxRuntimeSeconds,
        [int]$PollSeconds
    )

    $saved = @{}
    foreach ($name in @("HAKIMI_HOME", "KIMI_CODE_HOME") + $AllFlagEnvNames) {
        $saved[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
    }

    try {
        [Environment]::SetEnvironmentVariable("HAKIMI_HOME", $Mode.home, "Process")
        [Environment]::SetEnvironmentVariable("KIMI_CODE_HOME", $null, "Process")
        foreach ($name in $AllFlagEnvNames) {
            [Environment]::SetEnvironmentVariable($name, $null, "Process")
        }
        if ($Mode.flagsOff -eq $true) {
            foreach ($name in $DefaultOnFlags) {
                [Environment]::SetEnvironmentVariable($name, "0", "Process")
            }
            [Environment]::SetEnvironmentVariable("KIMI_CODE_EXPERIMENTAL_MICRO_COMPACTION", "0", "Process")
            [Environment]::SetEnvironmentVariable("KIMI_CODE_EXPERIMENTAL_BACKGROUND_ASK", "0", "Process")
            [Environment]::SetEnvironmentVariable("KIMI_CODE_EXPERIMENTAL_FLAG", "0", "Process")
        }

        $proc = Start-Process -FilePath $HakimiPath -ArgumentList $ArgumentLine -WorkingDirectory $WorkingDirectory -NoNewWindow -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath -PassThru
        $started = Get-Date
        $lastGrowthAt = $started
        $lastBytes = 0
        $status = "running"
        $exitCode = $null

        while ($true) {
            Start-Sleep -Seconds $PollSeconds
            $proc.Refresh()
            $now = Get-Date
            $stdoutBytes = Get-FileLengthSafe -Path $StdoutPath
            $stderrBytes = Get-FileLengthSafe -Path $StderrPath
            $totalBytes = $stdoutBytes + $stderrBytes
            if ($totalBytes -gt $lastBytes) {
                $lastBytes = $totalBytes
                $lastGrowthAt = $now
            }
            if ($proc.HasExited) {
                $proc.Refresh()
                $exitCode = $proc.ExitCode
                $status = "completed"
                break
            }
            if ($MaxRuntimeSeconds -gt 0 -and ($now - $started).TotalSeconds -ge $MaxRuntimeSeconds) {
                Stop-ProcessTreeBestEffort -RootProcessId $proc.Id
                Start-Sleep -Milliseconds 800
                $exitCode = -2
                $status = "max_runtime_timeout"
                break
            }
            if (($now - $lastGrowthAt).TotalSeconds -ge $IdleTimeoutSeconds) {
                Stop-ProcessTreeBestEffort -RootProcessId $proc.Id
                Start-Sleep -Milliseconds 800
                $exitCode = -1
                $status = "idle_timeout"
                break
            }
        }

        $finished = Get-Date
        return [ordered]@{
            status = $status
            exit_code = $exitCode
            runtime_seconds = [Math]::Round(($finished - $started).TotalSeconds, 3)
            stdout_bytes = Get-FileLengthSafe -Path $StdoutPath
            stderr_bytes = Get-FileLengthSafe -Path $StderrPath
        }
    } finally {
        foreach ($entry in $saved.GetEnumerator()) {
            [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, "Process")
        }
    }
}

function New-IsolatedHome {
    param([string]$Root, [string]$ModeName)
    $homeDir = Join-Path $Root "hakimi-home-$ModeName"
    New-Item -ItemType Directory -Force -Path $homeDir | Out-Null
    Copy-Item -Path $SourceConfigPath -Destination (Join-Path $homeDir "config.toml") -Force
    return $homeDir
}

function Read-FlagLogLines {
    param([string]$HomeDir)
    $logPath = Join-Path $HomeDir "logs\kimi-code.log"
    if (-not (Test-Path $logPath)) { return @() }
    return [string[]]@(Get-Content $logPath | Where-Object { $_ -match "experimental flags enabled" })
}

function Convert-ProviderSmoke {
    param([object]$Value)
    return [ordered]@{
        status = [string]$Value.status
        exit_code = $Value.exit_code
        runtime_seconds = [double]$Value.runtime_seconds
        stdout_bytes = [int]$Value.stdout_bytes
        stderr_bytes = [int]$Value.stderr_bytes
    }
}

function Convert-ItemRun {
    param([object]$Value)
    return [ordered]@{
        mode = [string]$Value.mode
        field = [string]$Value.field
        problem_number = [int]$Value.problem_number
        status = [string]$Value.status
        exit_code = $Value.exit_code
        runtime_seconds = [double]$Value.runtime_seconds
        stdout_bytes = [int]$Value.stdout_bytes
        stderr_bytes = [int]$Value.stderr_bytes
        captured_json = [bool]$Value.captured_json
        prompt = [string]$Value.prompt
        stdout = [string]$Value.stdout
        stderr = [string]$Value.stderr
    }
}

function Convert-CheckRecord {
    param([object]$Value)
    return [ordered]@{
        field = [string]$Value.field
        type = [string]$Value.type
        source = [string]$Value.source
        source_index = $Value.source_index
        domain = [string]$Value.domain
        difficulty = [string]$Value.difficulty
        passed = [bool]$Value.passed
        expected = @($Value.expected)
        actual_raw = $Value.actual_raw
        actual_parsed = @($Value.actual_parsed)
        actual_normalized = $Value.actual_normalized
        expected_normalized = @($Value.expected_normalized)
        abs_errors = @($Value.abs_errors)
        abs_tol = $Value.abs_tol
        error = $Value.error
    }
}

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$SafeTaskId = $TaskId -replace '[^A-Za-z0-9_]+', '_'
$SafeRunLabel = $RunLabel -replace '[^A-Za-z0-9_]+', '_'
$RunId = "${Timestamp}__hakimi013_deepseek_flags_ab__${SafeTaskId}__${SafeRunLabel}"
$RunRoot = Join-Path $BenchmarkRoot "runs\$RunId"
$OutputDir = Join-Path $RunRoot "outputs"
$ScoresDir = Join-Path $RunRoot "scores"
$LogsDir = Join-Path $RunRoot "logs"
$PartialMetadataPath = Join-Path $RunRoot "run-metadata.partial.json"
$StagePath = Join-Path $RunRoot "live-stage.json"
$TempRoot = Join-Path $env:TEMP "agent-lab-$RunId"
New-Item -ItemType Directory -Force -Path $RunRoot, $OutputDir, $ScoresDir, $LogsDir, $TempRoot | Out-Null

$Modes = @(
    @{ name = "default_on"; flagsOff = $false; home = (New-IsolatedHome -Root $TempRoot -ModeName "default-on") },
    @{ name = "all_default_on_flags_off"; flagsOff = $true; home = (New-IsolatedHome -Root $TempRoot -ModeName "flags-off") }
)

$Started = Get-Date
$ModeResults = @()
Write-StageFile -Path $StagePath -Stage "initialized" -Extra ([ordered]@{
    run_id = $RunId
    problem_numbers = @($ProblemNumbers)
})

foreach ($mode in $Modes) {
    $modeName = $mode.name
    Write-StageFile -Path $StagePath -Stage "mode-started" -Extra ([ordered]@{
        mode = $modeName
    })
    $modeOutput = Join-Path $OutputDir "$TaskId.$modeName.json"
    $modeSummary = Join-Path $ScoresDir "$TaskId.$modeName.summary.json"
    $modeScore = Join-Path $ScoresDir "$TaskId.$modeName.full-score.json"
    $flagSmokeOut = Join-Path $LogsDir "$modeName.provider.stdout.txt"
    $flagSmokeErr = Join-Path $LogsDir "$modeName.provider.stderr.txt"

    $providerResult = Invoke-CommandWithModeEnv -Mode $mode -WorkingDirectory $BenchmarkRoot -ArgumentLine "provider list" -StdoutPath $flagSmokeOut -StderrPath $flagSmokeErr -IdleTimeoutSeconds 120 -MaxRuntimeSeconds 120 -PollSeconds 2
    $versionOut = Join-Path $LogsDir "$modeName.version.stdout.txt"
    $versionErr = Join-Path $LogsDir "$modeName.version.stderr.txt"
    $versionResult = Invoke-CommandWithModeEnv -Mode $mode -WorkingDirectory $BenchmarkRoot -ArgumentLine "--version" -StdoutPath $versionOut -StderrPath $versionErr -IdleTimeoutSeconds 120 -MaxRuntimeSeconds 120 -PollSeconds 2
    Write-StageFile -Path $StagePath -Stage "mode-smoke-completed" -Extra ([ordered]@{
        mode = $modeName
        provider_status = $providerResult.status
        version_status = $versionResult.status
    })

    $Merged = [ordered]@{}
    $ItemRuns = @()
    foreach ($problemNumber in $ProblemNumbers) {
        if ($problemNumber -lt 1 -or $problemNumber -gt $Fields.Count) {
            throw "Problem number out of range: $problemNumber"
        }
        $field = $Fields[$problemNumber - 1]
        $itemPromptPath = Join-Path $LogsDir ("{0}.item-{1:00}-{2}.prompt.md" -f $modeName, $problemNumber, $field)
        $stdoutPath = Join-Path $LogsDir ("{0}.item-{1:00}-{2}.stdout.txt" -f $modeName, $problemNumber, $field)
        $stderrPath = Join-Path $LogsDir ("{0}.item-{1:00}-{2}.stderr.txt" -f $modeName, $problemNumber, $field)
        $problemBlock = Get-ProblemBlock -Text $FullPrompt -ProblemNumber $problemNumber
        $itemPrompt = @"
# $TaskId Item $problemNumber

Return exactly one JSON object and no explanation.

Use exactly this key:

- ``$field``

For multiple-answer questions, return a semicolon-separated lowercase choice set such as `"a;b;d"`.
For symbolic answers, use compact LaTeX-like strings.
For numeric vectors, return a JSON array of numbers.

$problemBlock
"@
        $itemPrompt | Set-Content -Path $itemPromptPath -Encoding utf8

        $tempCwd = Join-Path $TempRoot "$modeName-item-$problemNumber"
        New-Item -ItemType Directory -Force -Path $tempCwd | Out-Null
        Copy-Item -Path $itemPromptPath -Destination (Join-Path $tempCwd "prompt.md") -Force

        $promptText = @"
Read prompt.md in the current directory and complete the benchmark item exactly as written.

Important:
- Do not browse the web or use search.
- Do not ask a follow-up question.
- Output exactly one JSON object and no explanation.
"@
        $escapedPrompt = $promptText.Replace('"', '\"')
        $argumentLine = "-m `"$Model`" -p `"$escapedPrompt`" --output-format text"
        $invokeResult = Invoke-CommandWithModeEnv -Mode $mode -WorkingDirectory $tempCwd -ArgumentLine $argumentLine -StdoutPath $stdoutPath -StderrPath $stderrPath -IdleTimeoutSeconds ($IdleTimeoutMinutes * 60) -MaxRuntimeSeconds ($MaxRuntimeMinutes * 60) -PollSeconds $PollSeconds
        $stdoutText = Read-TextFileBestEffort -Path $stdoutPath
        $jsonText = Extract-FirstJsonObject -Text $stdoutText
        $capturedJson = $false
        if ($jsonText -ne $null) {
            try {
                $obj = $jsonText | ConvertFrom-Json
                if ($obj.PSObject.Properties.Name -contains $field) {
                    $Merged[$field] = $obj.$field
                    $capturedJson = $true
                }
            } catch {
            }
        }

        $ItemRuns += [ordered]@{
            mode = $modeName
            field = $field
            problem_number = $problemNumber
            status = $invokeResult.status
            exit_code = $invokeResult.exit_code
            runtime_seconds = $invokeResult.runtime_seconds
            stdout_bytes = $invokeResult.stdout_bytes
            stderr_bytes = $invokeResult.stderr_bytes
            captured_json = $capturedJson
            prompt = $itemPromptPath
            stdout = $stdoutPath
            stderr = $stderrPath
        }
        Write-JsonFile -Value ([ordered]@{
            benchmark_id = "existing-cmt-hard-stress-v0.1"
            task_id = $TaskId
            run_id = $RunId
            current_mode = $modeName
            model_alias = $Model
            problem_numbers = @($ProblemNumbers)
            temp_home_root = $TempRoot
            item_runs = @($ItemRuns | ForEach-Object { Convert-ItemRun $_ })
            updated_at = (Get-Date).ToString("o")
        }) -Path $PartialMetadataPath -Depth 14
        Write-StageFile -Path $StagePath -Stage "item-completed" -Extra ([ordered]@{
            mode = $modeName
            problem_number = $problemNumber
            field = $field
            status = $invokeResult.status
            captured_json = $capturedJson
        })
    }

    $Merged | ConvertTo-Json -Depth 8 | Set-Content -Path $modeOutput -Encoding utf8
    Write-StageFile -Path $StagePath -Stage "scoring-started" -Extra ([ordered]@{
        mode = $modeName
        output = $modeOutput
    })
    $scoreText = & $PythonExe $VerifierPath $modeOutput 2>&1
    $scoreExitCode = $LASTEXITCODE
    $scoreText | Set-Content -Path $modeScore -Encoding utf8
    $score = $scoreText | ConvertFrom-Json
    $sliceFields = @($ProblemNumbers | ForEach-Object { $Fields[$_ - 1] })
    $sliceChecks = @($score.checks | Where-Object { $sliceFields -contains $_.field })
    $slicePassed = @($sliceChecks | Where-Object { $_.passed }).Count
    $sliceTotal = $sliceChecks.Count
    $summary = [ordered]@{
        benchmark_id = "existing-cmt-hard-stress-v0.1"
        task_id = $TaskId
        run_id = $RunId
        mode = $modeName
        model_alias = $Model
        problem_numbers = @($ProblemNumbers)
        passed = $slicePassed
        total = $sliceTotal
        hard_score = if ($sliceTotal) { $slicePassed / $sliceTotal } else { $null }
        provider_status = [string]$providerResult.status
        provider_exit_code = $providerResult.exit_code
        provider_runtime_seconds = [double]$providerResult.runtime_seconds
        version_status = [string]$versionResult.status
        version_exit_code = $versionResult.exit_code
        version_runtime_seconds = [double]$versionResult.runtime_seconds
        version_stdout = (Read-TextFileBestEffort -Path $versionOut).Trim()
        provider_stdout = (Read-TextFileBestEffort -Path $flagSmokeOut).Trim()
        experimental_flag_log_lines = @(Read-FlagLogLines -HomeDir $mode.home)
        output = $modeOutput
        full_score = $modeScore
        item_runs = @($ItemRuns | ForEach-Object { Convert-ItemRun $_ })
        slice_check_fields = @($sliceChecks | ForEach-Object { [string]$_.field })
    }
    Write-StageFile -Path $StagePath -Stage "summary-writing" -Extra ([ordered]@{
        mode = $modeName
        passed = $slicePassed
        total = $sliceTotal
    })
    Write-JsonFile -Value $summary -Path $modeSummary -Depth 14
    $ModeResults += [ordered]@{
        mode = $modeName
        passed = $slicePassed
        total = $sliceTotal
        hard_score = if ($sliceTotal) { $slicePassed / $sliceTotal } else { $null }
        output = $modeOutput
        full_score = $modeScore
        summary = $modeSummary
        item_run_count = @($ItemRuns).Count
        experimental_flag_log_lines = @(Read-FlagLogLines -HomeDir $mode.home)
    }
    Write-JsonFile -Value ([ordered]@{
        benchmark_id = "existing-cmt-hard-stress-v0.1"
        task_id = $TaskId
        run_id = $RunId
        completed_modes = @($ModeResults | ForEach-Object { [string]$_.mode })
        model_alias = $Model
        problem_numbers = @($ProblemNumbers)
        temp_home_root = $TempRoot
        modes = @($ModeResults)
        updated_at = (Get-Date).ToString("o")
    }) -Path $PartialMetadataPath -Depth 16
    Write-StageFile -Path $StagePath -Stage "mode-completed" -Extra ([ordered]@{
        mode = $modeName
    })
}

$Finished = Get-Date
$Metadata = [ordered]@{
    benchmark_id = "existing-cmt-hard-stress-v0.1"
    task_id = $TaskId
    run_id = $RunId
    agent = "hakimi013_deepseek_flags_ab"
    model_alias = $Model
    hakimi_command = $HakimiPath
    command = "hakimi -m $Model -p <single problem prompt> --output-format text"
    started_at = $Started.ToString("o")
    finished_at = $Finished.ToString("o")
    runtime_seconds = [Math]::Round(($Finished - $Started).TotalSeconds, 3)
    idle_timeout_minutes = $IdleTimeoutMinutes
    max_runtime_minutes = $MaxRuntimeMinutes
    poll_seconds = $PollSeconds
    problem_numbers = @($ProblemNumbers)
    source_config = "~/.hakimi/config.toml copied into isolated temp homes; API keys are not stored in this run directory."
    temp_home_root = $TempRoot
    local_leakage_boundary = "Each item temp cwd contains only prompt.md. Gold, verifier, source rows, and prior run outputs are not mounted in cwd."
    modes = @($ModeResults)
}
Write-JsonFile -Value $Metadata -Path (Join-Path $RunRoot "run-metadata.json") -Depth 16

Write-Host "Run directory: $RunRoot"
Write-Host "Metadata: $(Join-Path $RunRoot 'run-metadata.json')"
