param(
  [Parameter(Mandatory=$true)][string]$BaseUrl,
  [string]$ApiToken = "dev-token"
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

Write-Host "Checking $BaseUrl ..."

function Test-Endpoint {
  param(
    [Parameter(Mandatory=$true)][string]$Url,
    [hashtable]$Headers = @{}
  )

  try {
    $args = @('-sS', '-L', '-m', '15')
    foreach ($entry in $Headers.GetEnumerator()) {
      $args += @('-H', "$($entry.Key): $($entry.Value)")
    }
    $args += @('-o', 'NUL', '-w', '%{http_code}', $Url)

    $response = & curl.exe @args
    if ($LASTEXITCODE -ne 0) {
      throw "curl failed with exit code $LASTEXITCODE"
    }
    if (-not ($response -match '^\d{3}$')) {
      throw "Invalid HTTP status response: '$response'"
    }

    $code = [int]$response
    if ($code -lt 200 -or $code -ge 300) {
      throw "Unexpected status $code for $Url"
    }

    Write-Host "OK $Url ($code)"
  } catch {
    Write-Error "FAILED $Url : $($_.Exception.Message)"
    exit 1
  }
}

Test-Endpoint -Url "$BaseUrl/healthz"
Test-Endpoint -Url "$BaseUrl/readyz"
Test-Endpoint -Url "$BaseUrl/api/v1/openapi.json" -Headers @{ Authorization = "Bearer $ApiToken" }

Write-Host "Staging smoke checks passed."
