[CmdletBinding()]
param(
  [int]$BackendPort = 8010,
  [int]$FrontendPort = 5180
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backend = Join-Path $repo "backend"
$frontend = Join-Path $repo "frontend"
$python = (Resolve-Path (Join-Path $backend ".venv\Scripts\python.exe")).Path
$runId = [guid]::NewGuid().ToString("N")
$backendOut = Join-Path $env:TEMP "niyamguard-backend-$runId.out.log"
$backendErr = Join-Path $env:TEMP "niyamguard-backend-$runId.err.log"
$frontendOut = Join-Path $env:TEMP "niyamguard-frontend-$runId.out.log"
$frontendErr = Join-Path $env:TEMP "niyamguard-frontend-$runId.err.log"

$env:APP_ENV = "development"
$env:DEBUG = "false"
$env:DEMO_MODE = "true"
$env:DATABASE_URL = "sqlite:///./niyamguard.db"
$env:SECRET_KEY = "local-demo-secret-key-not-for-production"
$env:RATE_LIMIT_ENABLED = "false"
$env:SEED_DEMO_ON_STARTUP = "false"

Push-Location $backend
try {
  & $python -m app.seed_demo
  if ($LASTEXITCODE -ne 0) { throw "Demo seed failed." }
}
finally { Pop-Location }

$backendProcess = Start-Process -FilePath $python `
  -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", [string]$BackendPort) `
  -WorkingDirectory $backend -WindowStyle Hidden -PassThru `
  -RedirectStandardOutput $backendOut -RedirectStandardError $backendErr

$env:VITE_API_BASE_URL = "http://127.0.0.1:$BackendPort"
$frontendProcess = Start-Process -FilePath "npm.cmd" `
  -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", [string]$FrontendPort) `
  -WorkingDirectory $frontend -WindowStyle Hidden -PassThru `
  -RedirectStandardOutput $frontendOut -RedirectStandardError $frontendErr

$deadline = (Get-Date).AddSeconds(40)
$backendHealthy = $false
$frontendHealthy = $false
do {
  Start-Sleep -Seconds 1
  try {
    $backendHealthy = (Invoke-WebRequest "http://127.0.0.1:$BackendPort/api/integration/health" -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200
  }
  catch { $backendHealthy = $false }
  try {
    $frontendHealthy = (Invoke-WebRequest "http://127.0.0.1:$FrontendPort" -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200
  }
  catch { $frontendHealthy = $false }
} while ((-not $backendHealthy -or -not $frontendHealthy) -and (Get-Date) -lt $deadline)

$result = [ordered]@{
  backend_pid = $backendProcess.Id
  frontend_pid = $frontendProcess.Id
  backend_healthy = $backendHealthy
  frontend_healthy = $frontendHealthy
  backend_output = $backendOut
  backend_error = $backendErr
  frontend_output = $frontendOut
  frontend_error = $frontendErr
}
$result | ConvertTo-Json
if (-not $backendHealthy -or -not $frontendHealthy) { throw "Recording services did not become healthy." }
