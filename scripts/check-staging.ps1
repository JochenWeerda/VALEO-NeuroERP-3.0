param(
  [Parameter(Mandatory=$true)][string]$BaseUrl
)

$ErrorActionPreference = 'Stop'

Write-Host "Checking $BaseUrl ..."

$endpoints = @('/healthz', '/readyz', '/api/v1/openapi.json')
foreach ($ep in $endpoints) {
  $url = "$BaseUrl$ep"
  try {
    $resp = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 15
    if ($resp.StatusCode -lt 200 -or $resp.StatusCode -ge 300) {
      throw "Unexpected status $($resp.StatusCode) for $url"
    }
    Write-Host "OK $url"
  } catch {
    Write-Error "FAILED $url : $($_.Exception.Message)"
    exit 1
  }
}

Write-Host "Staging smoke checks passed."
