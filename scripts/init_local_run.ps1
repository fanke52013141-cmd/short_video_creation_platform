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
  "outputs\01_story",
  "outputs\02_art_direction",
  "outputs\03_storyboard",
  "outputs\03_storyboard\keyframes",
  "outputs\04_assets\characters",
  "outputs\04_assets\scenes",
  "outputs\04_assets\props",
  "outputs\04_assets\audio",
  "outputs\04_assets\final_images\characters",
  "outputs\04_assets\final_images\scenes",
  "outputs\04_assets\final_images\props",
  "outputs\05_video_prompts",
  "outputs\05_video_prompts\shots",
  "outputs\06_external_results",
  "outputs\07_final_delivery",
  "references",
  "references\audio",
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
Copy-Item -LiteralPath (Join-Path $repoRoot "templates\production_status.template.csv") -Destination (Join-Path $runRoot "production_status.csv") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "templates\voice_reference_manifest.template.json") -Destination (Join-Path $runRoot "outputs\04_assets\audio\voice_reference_manifest.json") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "templates\image_generation_queue.template.json") -Destination (Join-Path $runRoot "outputs\04_assets\image_generation_queue.json") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "templates\image_result_manifest.template.json") -Destination (Join-Path $runRoot "outputs\06_external_results\image_result_manifest.json") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "templates\shot_result_manifest.template.json") -Destination (Join-Path $runRoot "outputs\06_external_results\shot_result_manifest.template.json") -Force

$requiredFiles = @(
  "inputs\idea_brief.md",
  "checkpoint.json",
  "notes.md",
  "production_status.csv",
  "outputs\04_assets\audio\voice_reference_manifest.json",
  "outputs\04_assets\image_generation_queue.json",
  "outputs\06_external_results\image_result_manifest.json",
  "outputs\06_external_results\shot_result_manifest.template.json"
)

foreach ($file in $requiredFiles) {
  $path = Join-Path $runRoot $file
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Initialization failed. Required file missing: $path"
  }
}

Write-Output "Created local run: $runRoot"
