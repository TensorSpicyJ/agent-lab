param(
    [string]$Model = "kimi-code/kimi-for-coding",
    [string]$Agent = "kimi_code_kimi26_file_isolated_network_not_enforced"
)

$ErrorActionPreference = "Stop"

$BenchmarkRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskId = "quantum-hard-result-only-suite"
$TaskRoot = Join-Path $BenchmarkRoot "tasks\$TaskId"
$PromptPath = Join-Path $TaskRoot "prompt.md"
$VerifierPath = Join-Path $TaskRoot "verify.py"

if (-not (Test-Path $PromptPath)) {
    throw "Prompt not found: $PromptPath"
}

$Kimi = Get-Command kimi -ErrorAction Stop
$KimiVersion = (& kimi --version).Trim()
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunId = "${Timestamp}__${Agent}__${TaskId}"
$RunRoot = Join-Path $BenchmarkRoot "runs\$RunId"
$OutputDir = Join-Path $RunRoot "outputs"
$ScoresDir = Join-Path $RunRoot "scores"
$LogsDir = Join-Path $RunRoot "logs"
New-Item -ItemType Directory -Force -Path $OutputDir, $ScoresDir, $LogsDir | Out-Null

$TempRoot = Join-Path $env:TEMP "agent-lab-kimi-hard-$Timestamp"
New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null
Copy-Item -Path $PromptPath -Destination (Join-Path $TempRoot "prompt.md") -Force

$PromptHash = (Get-FileHash -Algorithm SHA256 -Path $PromptPath).Hash
$StdoutPath = Join-Path $LogsDir "$TaskId.stdout.txt"
$StderrPath = Join-Path $LogsDir "$TaskId.stderr.txt"
$OutputPath = Join-Path $OutputDir "$TaskId.md"
$ScorePath = Join-Path $ScoresDir "$TaskId.score.json"
$ScoreStderrPath = Join-Path $LogsDir "$TaskId.scorer.stderr.txt"

$PromptText = @"
Read prompt.md in the current directory and complete the benchmark exactly as written.

Important:
- Do not browse the web or use search.
- Do not ask a follow-up question.
- Output exactly one JSON object and no explanation.
"@

$Started = Get-Date
$PreviousErrorActionPreference = $ErrorActionPreference
Push-Location $TempRoot
try {
    $ErrorActionPreference = "Continue"
    if (Test-Path "variable:PSNativeCommandUseErrorActionPreference") {
        $PreviousNativeErrorPreference = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
    }
    & $Kimi.Source -m $Model -p $PromptText --output-format text 1> $StdoutPath 2> $StderrPath
    $KimiExitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $PreviousErrorActionPreference
    if (Test-Path "variable:PreviousNativeErrorPreference") {
        $PSNativeCommandUseErrorActionPreference = $PreviousNativeErrorPreference
    }
    Pop-Location
}
$Finished = Get-Date

Copy-Item -Path $StdoutPath -Destination $OutputPath -Force
$OutputHash = (Get-FileHash -Algorithm SHA256 -Path $OutputPath).Hash
"$KimiExitCode" | Set-Content -Path (Join-Path $RunRoot "exit-code.txt") -Encoding utf8

$PreviousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
if (Test-Path "variable:PSNativeCommandUseErrorActionPreference") {
    $PreviousNativeErrorPreferenceForScorer = $PSNativeCommandUseErrorActionPreference
    $PSNativeCommandUseErrorActionPreference = $false
}
& python $VerifierPath $OutputPath 1> $ScorePath 2> $ScoreStderrPath
$ScoreExitCode = $LASTEXITCODE
$ErrorActionPreference = $PreviousErrorActionPreference
if (Test-Path "variable:PreviousNativeErrorPreferenceForScorer") {
    $PSNativeCommandUseErrorActionPreference = $PreviousNativeErrorPreferenceForScorer
}

$CwdListing = Get-ChildItem -Recurse -File $TempRoot | ForEach-Object {
    $_.FullName.Substring($TempRoot.Length + 1).Replace('\', '/')
}

$Metadata = [ordered]@{
    benchmark_id = "web-physics-hard-result-only-v0.1"
    task_id = $TaskId
    run_id = $RunId
    agent = $Agent
    model_alias = $Model
    model_display_name_note = "Local config displays kimi-code/kimi-for-coding as Kimi-k2.6."
    command = "kimi -m $Model -p <read prompt.md and output JSON> --output-format text"
    started_at = $Started.ToString("o")
    finished_at = $Finished.ToString("o")
    runtime_seconds = [Math]::Round(($Finished - $Started).TotalSeconds, 3)
    kimi_exit_code = $KimiExitCode
    scorer_exit_code = $ScoreExitCode
    kimi_executable = $Kimi.Source
    kimi_version = $KimiVersion
    temp_cwd = $TempRoot
    cwd_listing = @($CwdListing)
    prompt = $PromptPath
    prompt_sha256 = $PromptHash
    output = $OutputPath
    output_sha256 = $OutputHash
    score = $ScorePath
    network_allowed = $false
    network_enforced = $false
    local_leakage_boundary = "Initial temp cwd contains only prompt.md. Agent-created scratch files may appear during the run; gold, verifier, run history, and source metadata are not mounted in cwd."
}

$Metadata | ConvertTo-Json -Depth 8 | Set-Content -Path (Join-Path $RunRoot "run-metadata.json") -Encoding utf8

Write-Host "Run directory: $RunRoot"
Write-Host "Kimi exit code: $KimiExitCode"
Write-Host "Scorer exit code: $ScoreExitCode"
Write-Host "Output: $OutputPath"
Write-Host "Score: $ScorePath"
