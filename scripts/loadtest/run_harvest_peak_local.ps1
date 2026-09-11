<#
.SYNOPSIS
  Lokaler Erntepeak-Lasttest (SPEC-P1-10) gegen docker-compose / localhost.

.DESCRIPTION
  Wartet auf Backend-Health und startet k6 mit PROFILE=local (oder smoke).
  Voraussetzung: Backend laeuft (z. B. docker compose -f docker-compose.dev.yml up -d
  oder uvicorn auf Port 8000), k6 ist installiert.

.EXAMPLE
  pwsh scripts/loadtest/run_harvest_peak_local.ps1
  pwsh scripts/loadtest/run_harvest_peak_local.ps1 -Profile smoke
#>
param(
  [ValidateSet('local', 'smoke')]
  [string]$Profile = 'local',
  [string]$BaseUrl = $(if ($env:BASE_URL) { $env:BASE_URL } else { 'http://127.0.0.1:8000' }),
  [string]$ApiToken = $(if ($env:API_DEV_TOKEN) { $env:API_DEV_TOKEN } else { 'dev-token' }),
  [string]$TenantId = $(if ($env:TENANT_ID) { $env:TENANT_ID } else { '00000000-0000-0000-0000-000000000001' }),
  [int]$ReadyTimeoutSec = 90
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

if (-not (Get-Command k6 -ErrorAction SilentlyContinue)) {
  Write-Error "k6 fehlt. Installation: https://k6.io/docs/get-started/installation/"
}

$healthUrls = @(
  "$BaseUrl/healthz",
  "$BaseUrl/health/live",
  "$BaseUrl/api/v1/status"
)

Write-Host "Warte auf Backend unter $BaseUrl (Timeout ${ReadyTimeoutSec}s)..."
$deadline = (Get-Date).AddSeconds($ReadyTimeoutSec)
$ready = $false
while ((Get-Date) -lt $deadline) {
  foreach ($url in $healthUrls) {
    try {
      $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
      if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
        $ready = $true
        Write-Host "OK: $url -> $($resp.StatusCode)"
        break
      }
    } catch {
      # retry
    }
  }
  if ($ready) { break }
  Start-Sleep -Seconds 2
}

if (-not $ready) {
  Write-Error "Backend nicht erreichbar unter $BaseUrl. Bitte zuerst starten (docker compose / uvicorn)."
}

New-Item -ItemType Directory -Path 'reports/performance' -Force | Out-Null
$summary = "reports/performance/harvest-peak-$Profile-summary.json"

Write-Host "Starte k6 PROFILE=$Profile gegen $BaseUrl"
k6 run `
  --env "PROFILE=$Profile" `
  --env "BASE_URL=$BaseUrl" `
  --env "API_DEV_TOKEN=$ApiToken" `
  --env "TENANT_ID=$TenantId" `
  --summary-export $summary `
  tests/load/harvest-peak.js

Write-Host "Fertig. Summary: $summary"
