param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$BearerToken = $(if ($env:API_BEARER_TOKEN) { $env:API_BEARER_TOKEN } else { "dev-token" }),
  [string]$PostgresContainer = "valeo-neuro-erp-postgres",
  [string]$PostgresUser = "valeo_dev",
  [string]$PostgresDb = "valeo_neuro_erp",
  [string]$TenantId = "00000000-0000-0000-0000-000000000010"
)

$ErrorActionPreference = "Stop"

function Assert-True {
  param([bool]$Condition, [string]$Message)
  if (-not $Condition) { throw "ASSERTION FAILED: $Message" }
}

function Invoke-Json {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $false)]$Body,
    [string]$Tenant = $TenantId
  )
  $headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $BearerToken"
    "X-Tenant-ID" = $Tenant
  }
  $uri = if ($Url -match "\?") { "$($Url)&tenant_id=$Tenant" } else { "$($Url)?tenant_id=$Tenant" }
  if ($null -ne $Body) {
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 20)
  }
  return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
}

function Invoke-ExpectedFail {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $false)]$Body,
    [string]$Tenant = $TenantId
  )
  try {
    Invoke-Json -Method $Method -Url $Url -Body $Body -Tenant $Tenant | Out-Null
    return @{ ok = $false; detail = "unexpected success" }
  } catch {
    $detail = $_.ErrorDetails.Message
    if ([string]::IsNullOrWhiteSpace($detail) -and $null -ne $_.Exception.Response) {
      try {
        $stream = $_.Exception.Response.GetResponseStream()
        if ($null -ne $stream) {
          $reader = New-Object System.IO.StreamReader($stream)
          $detail = $reader.ReadToEnd()
        }
      } catch {
        # keep fallback detail
      }
    }
    if ([string]::IsNullOrWhiteSpace($detail)) {
      $detail = "$_"
    }
    return @{ ok = $true; detail = $detail }
  }
}

function Invoke-Db {
  param([Parameter(Mandatory = $true)][string]$Sql)
  return ($Sql | docker exec -i $PostgresContainer psql -v ON_ERROR_STOP=1 -U $PostgresUser -d $PostgresDb -t -A)
}

Write-Host "== Inventory Charge Lineage + Agrar Gating =="
$ArticleId = "00000000-0000-0000-0000-000000000011"
$WarehouseId = "00000000-0000-0000-0000-000000000012"

for ($i = 0; $i -lt 30; $i++) {
  try {
    Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/status" -Headers @{ "Authorization" = "Bearer $BearerToken" } -TimeoutSec 2 | Out-Null
    break
  } catch {
    Start-Sleep -Seconds 1
  }
  if ($i -eq 29) {
    throw "API not ready at $BaseUrl/api/v1/status"
  }
}

# Ensure tenant exists with agrar disabled
$tenantSql = @"
INSERT INTO domain_shared.tenants (id, name, domain, settings, is_active, created_at, updated_at)
VALUES ('$TenantId', 'Agrar-Gating Tenant', 'agrar-gating.local', jsonb_build_object('enabled_modules', ARRAY['core']), TRUE, NOW(), NOW())
ON CONFLICT (id)
DO UPDATE SET settings = EXCLUDED.settings, is_active = TRUE, updated_at = NOW();
"@
Invoke-Db -Sql $tenantSql | Out-Null

$cloneArticleSql = @"
INSERT INTO domain_inventory.articles
(id, tenant_id, article_number, name, description, unit, category, sales_price, is_active, current_stock, reserved_stock, available_stock, created_at, updated_at)
VALUES ('$ArticleId', '$TenantId', 'A010-ART-1', 'Agrar Testartikel', 'Agrar Gating Test', 'kg', 'test', 10, TRUE, 100, 0, 100, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;
"@
Invoke-Db -Sql $cloneArticleSql | Out-Null

$cloneWarehouseSql = @"
INSERT INTO domain_inventory.warehouses
(id, tenant_id, warehouse_code, name, address, is_active, created_at, updated_at)
VALUES ('$WarehouseId', '$TenantId', 'A010WH', 'Agrar Testlager', '{"street":"Testweg 1","city":"Emden","postal_code":"26721","country":"DE"}', TRUE, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;
"@
Invoke-Db -Sql $cloneWarehouseSql | Out-Null

# 1) agrar disabled -> should block agrar fields on stock movement
$blockedMovement = Invoke-ExpectedFail -Method Post -Url "$BaseUrl/api/v1/inventory/stock-movements/" -Body @{
  article_id = $ArticleId
  warehouse_id = $WarehouseId
  movement_type = "in"
  quantity = 5
  unit = "kg"
  charge = "CH-A010-NEW"
  process_type = "mix"
  agrar_contract_id = "AGRAR-C-1"
  lineage_sources = @(
    @{ from_charge = "CH-A010-SRC"; quantity_share = 5; share_percent = 100 }
  )
}
Assert-True -Condition ($blockedMovement.ok -eq $true) -Message "Agrar-disabled movement unexpectedly succeeded"
Assert-True -Condition ($blockedMovement.detail -match "Agrar module disabled|agrar fields/lineage") -Message "Missing gating error message for stock movement"

# 2) agrar disabled -> should block direct lineage endpoint
$blockedLineage = Invoke-ExpectedFail -Method Post -Url "$BaseUrl/api/v1/inventory/charge-lineage/" -Body @{
  article_id = $ArticleId
  from_charge = "CH-A010-SRC"
  to_charge = "CH-A010-NEW"
  process_type = "mix"
  quantity_share = 5
}
Assert-True -Condition ($blockedLineage.ok -eq $true) -Message "Agrar-disabled lineage unexpectedly succeeded"
Assert-True -Condition ($blockedLineage.detail -match "Agrar module disabled") -Message "Missing gating error message for lineage"

# enable agrar module for test tenant
$enableAgrarSql = @"
UPDATE domain_shared.tenants
SET settings = jsonb_build_object('enabled_modules', ARRAY['core','agrar']), updated_at = NOW()
WHERE id = '$TenantId';
"@
Invoke-Db -Sql $enableAgrarSql | Out-Null

# 3) agrar enabled -> movement with lineage should succeed and persist lineage
$movementOk = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/inventory/stock-movements/" -Body @{
  article_id = $ArticleId
  warehouse_id = $WarehouseId
  movement_type = "in"
  quantity = 5
  unit = "kg"
  charge = "CH-A010-NEW"
  process_type = "mix"
  agrar_contract_id = "AGRAR-C-1"
  lineage_sources = @(
    @{ from_charge = "CH-A010-SRC1"; quantity_share = 2; share_percent = 40 },
    @{ from_charge = "CH-A010-SRC2"; quantity_share = 3; share_percent = 60 }
  )
}
Assert-True -Condition ($null -ne $movementOk.id) -Message "Movement not created after enabling agrar"

$lineageList = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/inventory/charge-lineage/?charge=CH-A010-NEW&limit=10"
Assert-True -Condition (@($lineageList).Count -ge 2) -Message "Lineage links not persisted"

$dbLineageCount = Invoke-Db -Sql "select count(*) from domain_inventory.charge_lineage_links where tenant_id = '$TenantId' and to_charge = 'CH-A010-NEW';"
$dbLineageCount = [int]("$dbLineageCount".Trim())
Assert-True -Condition ($dbLineageCount -ge 2) -Message "DB lineage count too low"

$result = [ordered]@{
  tenant_id = $TenantId
  blocked_when_disabled = @{
    stock_movement = $true
    charge_lineage = $true
  }
  enabled_flow = @{
    movement_id = "$($movementOk.id)"
    lineage_rows_api = @($lineageList).Count
    lineage_rows_db = $dbLineageCount
  }
}

Write-Host "Inventory Charge Lineage + Agrar Gating erfolgreich:"
$result | ConvertTo-Json -Depth 8
