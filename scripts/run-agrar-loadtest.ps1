param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$ApiToken = "dev-token",
  [string]$TenantId = "00000000-0000-0000-0000-000000000001"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command k6 -ErrorAction SilentlyContinue)) {
  Write-Error "k6 ist nicht installiert. Bitte zuerst k6 installieren: https://k6.io/docs/get-started/installation/"
}

New-Item -ItemType Directory -Path "reports/performance" -Force | Out-Null

$env:BASE_URL = $BaseUrl
$env:API_TOKEN = $ApiToken
$env:TENANT_ID = $TenantId

Write-Host "Starte AGRAR-PERF-01 Lasttest gegen $BaseUrl (Tenant=$TenantId)"
k6 run tests/performance/agrar-core-loadtest.js

Write-Host "Fertig. Ergebnisdatei: reports/performance/agrar-perf-summary.json"
