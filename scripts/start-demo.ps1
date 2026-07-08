param(
  [int]$BackendPort = 8000,
  [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"

Write-Host "Seeding government-core demo data..."
Push-Location $BackendDir
python -m app.seed_demo
Pop-Location

$backendCommand = "cd /d `"$BackendDir`" && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort"
$frontendCommand = "cd /d `"$FrontendDir`" && npm install && npm run dev -- --host 127.0.0.1 --port $FrontendPort"

Write-Host "Starting backend on http://127.0.0.1:$BackendPort"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $backendCommand

Write-Host "Starting frontend on http://127.0.0.1:$FrontendPort"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $frontendCommand

Write-Host ""
Write-Host "Open these URLs after Vite finishes starting:"
Write-Host "  Demo dashboard: http://127.0.0.1:$FrontendPort/demo"
Write-Host "  Admin portal:   http://127.0.0.1:$FrontendPort/admin"
Write-Host "  Citizen portal: http://127.0.0.1:$FrontendPort"
