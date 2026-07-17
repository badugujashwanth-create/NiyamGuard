[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host 'Starting NiyamGuard AI in local demo mode.'
Write-Host 'Review environment placeholders and use synthetic data before continuing.'
.\scripts\start-demo.ps1

