param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$TenantId = "00000000-0000-0000-0000-000000000001",
  [string]$BearerToken = $(if ($env:API_BEARER_TOKEN) { $env:API_BEARER_TOKEN } else { "dev-token" })
)

$ErrorActionPreference = "Stop"

function Invoke-Json {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $false)]$Body
  )
  $headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $BearerToken"
    "X-Tenant-ID" = $TenantId
  }
  if ($null -ne $Body) {
    return Invoke-RestMethod -Method $Method -Uri $Url -Headers $headers -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 20)
  }
  return Invoke-RestMethod -Method $Method -Uri $Url -Headers $headers
}

Write-Host "== Admin POS/TSE + DSFinV-K Smoke =="
$ts = Get-Date -Format "yyyyMMddHHmmss"

$terminal = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/admin/pos/terminals" -Body @{
  terminal_code = "KASSE-$ts"
  name = "Kasse $ts"
  location_name = "Hofmarkt"
  branch_code = "HOF"
  is_active = $true
  metadata = @{ printer = "Kyocera"; scanner = "Honeywell" }
}

$device = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/admin/pos/tse-devices" -Body @{
  terminal_id = $terminal.id
  serial_number = "TSE-$ts"
  provider = "Swissbit"
  status = "active"
  settings = @{ transport = "usb" }
}

$notice = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/admin/pos/notices" -Body @{
  terminal_id = $terminal.id
  tse_device_id = $device.id
  notice_type = "install"
  notice_status = "submitted"
  effective_date = (Get-Date).ToString("yyyy-MM-dd")
  submitted_at = (Get-Date).ToUniversalTime().ToString("o")
  reference_number = "BZST-$ts"
  payload = @{ comment = "Initialmeldung" }
}

$periodFrom = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
$periodTo = (Get-Date).ToString("yyyy-MM-dd")
$export = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/admin/pos/dsfinvk-exports" -Body @{
  period_from = $periodFrom
  period_to = $periodTo
  generated_by = "admin.smoke"
}

$list = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/admin/pos/dsfinvk-exports"
$tmpFile = Join-Path $env:TEMP ("dsfinvk-" + $export.id + ".csv")
$downloadGet = Invoke-WebRequest -Method Get -Uri "$BaseUrl/api/v1/admin/pos/dsfinvk-exports/$($export.id)/download" -Headers @{
  "Authorization" = "Bearer $BearerToken"
  "X-Tenant-ID" = $TenantId
} -OutFile $tmpFile

$result = [ordered]@{
  terminal_id = "$($terminal.id)"
  tse_device_id = "$($device.id)"
  notice_id = "$($notice.id)"
  export_id = "$($export.id)"
  export_status = "$($export.status)"
  export_rows = $export.row_count
  export_checksum = "$($export.checksum_sha256)"
  total_exports = @($list).Count
  download_http_status = $downloadGet.StatusCode
  download_file = $tmpFile
}

Write-Host "Admin POS/TSE Smoke erfolgreich:"
$result | ConvertTo-Json -Depth 8
