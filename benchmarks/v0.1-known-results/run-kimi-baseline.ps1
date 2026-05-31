param(
    [ValidateSet("kimi_project_default", "kimi_vanilla")]
    [string]$Agent = "kimi_project_default",

    [string]$TaskId = "toric-code-gsd-basic",

    [string]$Model = "",

    [switch]$NetworkAllowed
)

$ErrorActionPreference = "Stop"

$BenchmarkRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BenchmarkRoot "..\..")
$PromptPath = Join-Path $BenchmarkRoot "tasks\$TaskId\prompt.md"

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

$PromptHash = (Get-FileHash -Algorithm SHA256 -Path $PromptPath).Hash

$ArgsList = @()

if ($Agent -eq "kimi_vanilla") {
    $EmptySkills = Join-Path $RunRoot "empty-skills"
    New-Item -ItemType Directory -Force -Path $EmptySkills | Out-Null
    $ArgsList += @("--skills-dir", $EmptySkills)
    $SkillsDirValue = $EmptySkills -replace '\\','/'
    $DiscoveryNote = "explicit empty --skills-dir requested"
} else {
    $SkillsDirValue = ""
    $DiscoveryNote = "normal Kimi discovery in repository"
}

if ($Model.Trim().Length -gt 0) {
    $ArgsList += @("--model", $Model)
}

$PromptFileForKimi = "benchmarks/v0.1-known-results/tasks/$TaskId/prompt.md"
$PromptText = @"
Read the benchmark prompt file at `$PromptFileForKimi`, then complete the task exactly as written.

Important:
- Do not ask a follow-up question.
- Output the answer directly.
- Include the machine-gradable JSON block required by the prompt.
"@

$ArgsList += @("-p", $PromptText, "--output-format", "text")

$StdoutPath = Join-Path $LogsDir "$TaskId.stdout.txt"
$StderrPath = Join-Path $LogsDir "$TaskId.stderr.txt"
$OutputPath = Join-Path $OutputDir "$TaskId.md"

$Started = Get-Date
$PreviousErrorActionPreference = $ErrorActionPreference
Push-Location $RepoRoot
try {
    $ErrorActionPreference = "Continue"
    if (Test-Path "variable:PSNativeCommandUseErrorActionPreference") {
        $PreviousNativeErrorPreference = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
    }
    & $Kimi.Source @ArgsList 1> $StdoutPath 2> $StderrPath
    $ExitCode = $LASTEXITCODE
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

$CommandText = if ($Agent -eq "kimi_vanilla") {
    "kimi --skills-dir <run>/empty-skills -p <read-and-complete-prompt-file:$TaskId> --output-format text"
} else {
    "kimi -p <read-and-complete-prompt-file:$TaskId> --output-format text"
}

if ($Model.Trim().Length -gt 0) {
    $CommandText = $CommandText -replace "kimi ", "kimi --model $Model "
}

$NetworkAllowedValue = $NetworkAllowed.IsPresent.ToString().ToLowerInvariant()

$Metadata = @"
run_id: "$RunId"
date: "$($Started.ToString("o"))"
agent: "$Agent"

environment:
  cwd: "$($RepoRoot.Path -replace '\\','/')"
  kimi_version: "$KimiVersion"
  kimi_executable: "$($Kimi.Source -replace '\\','/')"
  command: "$($CommandText -replace '"','''')"
  model_alias: "$Model"
  skills_dir: "$SkillsDirValue"
  discovered_skills_note: "$DiscoveryNote"
  network_allowed: $NetworkAllowedValue
  web_access_used: null

benchmark:
  benchmark_id: known-result-physics-v0.1
  manifest_revision: draft
  rubric_revision: known-result-physics-rubric-v0.1
  task_ids:
    - "$TaskId"
  rollouts_per_task: 1

artifacts:
  outputs_dir: "outputs/"
  scores_dir: "scores/"
  logs_dir: "logs/"
  prompt_file: "$($PromptPath -replace '\\','/')"
  prompt_checksums:
    ${TaskId}: "$PromptHash"
  output_checksums:
    ${TaskId}: "$OutputHash"

execution:
  exit_code: $ExitCode
  started_at: "$($Started.ToString("o"))"
  finished_at: "$($Finished.ToString("o"))"
  runtime_seconds: $([Math]::Round(($Finished - $Started).TotalSeconds, 3))

notes:
  manual_interventions: []
  known_deviations: []
  scorer_notes:
    - "Raw Kimi stdout copied to outputs/$TaskId.md"
"@

$Metadata | Set-Content -Path (Join-Path $RunRoot "run-metadata.yaml") -Encoding utf8

Write-Host "Run directory: $RunRoot"
Write-Host "Exit code: $ExitCode"
Write-Host "Output: $OutputPath"
