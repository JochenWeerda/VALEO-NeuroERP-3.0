param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$TenantId = "00000000-0000-0000-0000-000000000001",
  [string]$BearerToken = $(if ($env:API_BEARER_TOKEN) { $env:API_BEARER_TOKEN } else { "dev-token" }),
  [string]$WarehouseId = "",
  [string]$OwnerPartnerId = "OWNER-E2E-001",
  [string]$ArticleId = ""
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
    "X-Tenant-ID" = $TenantId
  }
  if ($BearerToken) { $headers["Authorization"] = "Bearer $BearerToken" }

  if ($null -ne $Body) {
    return Invoke-RestMethod -Method $Method -Uri $Url -Headers $headers -Body ($Body | ConvertTo-Json -Depth 20)
  }
  return Invoke-RestMethod -Method $Method -Uri $Url -Headers $headers
}

Write-Host "== E2E Fremdbestand + Lagergeld =="

if (-not $WarehouseId) {
  $movementList = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/inventory/stock-movements/?limit=1"
  if ($movementList.items -and $movementList.items.Count -gt 0) {
    $WarehouseId = "$($movementList.items[0].warehouse_id)"
  }
}
if (-not $WarehouseId) {
  $warehouses = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/inventory/warehouses/?limit=1"
  if (-not $warehouses.items -or $warehouses.items.Count -eq 0) {
    throw "Kein Warehouse gefunden. Bitte Seed laden."
  }
  $WarehouseId = "$($warehouses.items[0].id)"
}

if (-not $ArticleId) {
  $articles = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/inventory/articles/?limit=1"
  if (-not $articles.items -or $articles.items.Count -eq 0) {
    throw "Kein Artikel gefunden. Bitte Seed laden."
  }
  $ArticleId = "$($articles.items[0].id)"
}

$today = Get-Date
$todayStr = $today.ToString("yyyy-MM-dd")
$period = $today.ToString("yyyy-MM")

# 1) Einlagerung Fremdbestand (consigned IN)
$inMovement = @{
  article_id = $ArticleId
  warehouse_id = $WarehouseId
  movement_type = "in"
  quantity = 120.000
  unit = "kg"
  movement_date = $todayStr
  reference_number = "E2E-CONSIGN-IN-" + (Get-Date -Format "yyyyMMddHHmmss")
  notes = "E2E Fremdbestand Einlagerung"
  charge = "CH-E2E-001"
  ownership_type = "consigned"
  owner_partner_id = $OwnerPartnerId
  agrar_contract_id = "AGRAR-CONTRACT-E2E"
  weighing_ticket_id = "WT-E2E-001"
  storage_fee_relevant = $true
  storage_fee_start_date = $todayStr
  storage_fee_monthly_rate = 0.0150
}
$inRes = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/inventory/stock-movements/" -Body $inMovement

# 2) Teilentnahme/Abruf (consigned OUT)
$outMovement = @{
  article_id = $ArticleId
  warehouse_id = $WarehouseId
  movement_type = "out"
  quantity = -20.000
  unit = "kg"
  movement_date = $todayStr
  reference_number = "E2E-CONSIGN-OUT-" + (Get-Date -Format "yyyyMMddHHmmss")
  notes = "E2E Fremdbestand Abruf"
  charge = "CH-E2E-001"
  ownership_type = "consigned"
  owner_partner_id = $OwnerPartnerId
  storage_fee_relevant = $true
  storage_fee_start_date = $todayStr
  storage_fee_monthly_rate = 0.0150
}
$outRes = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/inventory/stock-movements/" -Body $outMovement

# 3) Dry-run Lagergeld
$dryRun = @{
  period = $period
  dry_run = $true
  post_to_ledger = $false
  created_by = "e2e.script"
  note = "dry run"
}
$dryRes = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/inventory/storage-fees/run" -Body $dryRun

# 4) Echter Lauf mit Buchung
$postRun = @{
  period = $period
  dry_run = $false
  post_to_ledger = $true
  created_by = "e2e.script"
  note = "post run"
}
$postRes = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/inventory/storage-fees/run" -Body $postRun

# 5) Idempotenz pruefen (zweiter Lauf muss existing-run liefern)
$idemRes = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/inventory/storage-fees/run" -Body $postRun

# 6) Run-Details laden
$selectedRunId = "$($postRes.run_id)"
if (-not $selectedRunId) { $selectedRunId = "$($idemRes.run_id)" }
Write-Host "Storage-Fee Run-ID: $selectedRunId"
$runDetails = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/inventory/storage-fees/runs/$selectedRunId"

$result = [ordered]@{
  movements = @{
    in_id = "$($inRes.id)"
    out_id = "$($outRes.id)"
  }
  dry_run = @{
    total_items = $dryRes.total_items
    total_amount = $dryRes.total_amount
  }
  posted_run = @{
    run_id = $postRes.run_id
    total_items = $postRes.total_items
    total_amount = $postRes.total_amount
    journal_entry_id = $postRes.journal_entry_id
  }
  idempotency = @{
    idempotent_hit = $idemRes.idempotent_hit
    run_id = $idemRes.run_id
  }
  run_details = @{
    status = $runDetails.run.status
    charge_count = @($runDetails.charges).Count
  }
}

Write-Host "E2E erfolgreich:"
$result | ConvertTo-Json -Depth 10
