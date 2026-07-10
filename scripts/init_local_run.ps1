param(
  [Parameter(Mandatory=$true)]
  [string]$ProjectSlug,

  [string]$Date = (Get-Date -Format "yyyy-MM-dd")
)

$ErrorActionPreference = "Stop"

if ($ProjectSlug -notmatch '^[a-z0-9]+(-[a-z0-9]+)*$') {
  throw "ProjectSlug must use lowercase letters, numbers, and hyphens only. Example: lonely-robot-rainy-city"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$runRoot = Join-Path $repoRoot "local_runs\$Date\$ProjectSlug"
$createdAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$resolvedRunRoot = [System.IO.Path]::GetFullPath($runRoot)

$dirs = @(
  "inputs",
  "outputs",
  "outputs\drafts",
  "outputs\drafts\storyboard_prompts",
  "outputs\drafts\video_generation",
  "outputs\approved",
  "outputs\approved\assets",
  "outputs\approved\storyboards",
  "outputs\approved\video_generation",
  "outputs\assets",
  "outputs\assets\characters",
  "outputs\assets\characters\prompts",
  "outputs\assets\characters\images",
  "outputs\assets\scenes",
  "outputs\assets\scenes\prompts",
  "outputs\assets\scenes\images",
  "outputs\assets\props",
  "outputs\assets\props\prompts",
  "outputs\assets\props\images",
  "outputs\storyboard_prompts",
  "outputs\storyboards",
  "outputs\reviews",
  "outputs\video_generation",
  "outputs\imports",
  "references",
  "logs"
)

foreach ($dir in $dirs) {
  New-Item -ItemType Directory -Force -Path (Join-Path $runRoot $dir) | Out-Null
}

Copy-Item -LiteralPath (Join-Path $repoRoot "inputs\idea_brief.template.md") -Destination (Join-Path $runRoot "inputs\idea_brief.md") -Force

$checkpointTemplate = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $repoRoot "checkpoint.template.json")
$checkpoint = $checkpointTemplate.Replace("__PROJECT_SLUG__", $ProjectSlug)
$checkpoint = $checkpoint.Replace("__CREATED_AT__", $createdAt)
$checkpoint = $checkpoint.Replace("__RUN_DIR__", ($resolvedRunRoot -replace '\\', '/'))
Set-Content -LiteralPath (Join-Path $runRoot "checkpoint.json") -Value $checkpoint -Encoding UTF8

Copy-Item -LiteralPath (Join-Path $repoRoot "docs\local_run_template.md") -Destination (Join-Path $runRoot "notes.md") -Force

$requiredFiles = @(
  "inputs\idea_brief.md",
  "checkpoint.json",
  "notes.md"
)

foreach ($file in $requiredFiles) {
  $path = Join-Path $runRoot $file
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Initialization failed. Required file missing: $path"
  }
}

Write-Output "Created local run: $runRoot"
