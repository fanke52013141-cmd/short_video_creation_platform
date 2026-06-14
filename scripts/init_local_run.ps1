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

$dirs = @(
  "inputs",
  "outputs\01_story",
  "outputs\02_art_direction",
  "outputs\03_storyboard",
  "outputs\04_assets\characters",
  "outputs\04_assets\scenes",
  "outputs\04_assets\props",
  "outputs\05_video_prompts",
  "outputs\06_external_results",
  "outputs\07_final_delivery",
  "references",
  "external_results",
  "logs"
)

foreach ($dir in $dirs) {
  New-Item -ItemType Directory -Force -Path (Join-Path $runRoot $dir) | Out-Null
}

Copy-Item -LiteralPath (Join-Path $repoRoot "inputs\idea_brief.template.md") -Destination (Join-Path $runRoot "inputs\idea_brief.md") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "checkpoint.template.json") -Destination (Join-Path $runRoot "checkpoint.json") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "docs\local_run_template.md") -Destination (Join-Path $runRoot "notes.md") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "templates\production_status.template.csv") -Destination (Join-Path $runRoot "production_status.csv") -Force

Write-Output "Created local run: $runRoot"
