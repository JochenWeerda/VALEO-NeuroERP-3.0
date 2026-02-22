param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$TenantId = "00000000-0000-0000-0000-000000000001",
  [string]$BearerToken = $(if ($env:API_BEARER_TOKEN) { $env:API_BEARER_TOKEN } else { "dev-token" }),
  [string]$CustomerId = "67d2990e-32c4-42ac-8493-9a2753fa4683",
  [string]$PostgresContainer = "valeo-neuro-erp-postgres",
  [string]$PostgresUser = "valeo_dev",
  [string]$PostgresDb = "valeo_neuro_erp",
  [switch]$SkipDbChecks
)

$ErrorActionPreference = "Stop"

function Assert-True {
  param(
    [bool]$Condition,
    [string]$Message
  )
  if (-not $Condition) {
    throw "ASSERTION FAILED: $Message"
  }
}

function Invoke-Json {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $false)]$Body
  )

  $headers = @{
    "Content-Type" = "application/json"
    "X-Tenant-ID" = $TenantId
    "Authorization" = "Bearer $BearerToken"
  }

  if ($null -ne $Body) {
    $jsonBody = $Body | ConvertTo-Json -Depth 20
    return Invoke-RestMethod -Method $Method -Uri $Url -Headers $headers -ContentType "application/json" -Body $jsonBody
  }
  return Invoke-RestMethod -Method $Method -Uri $Url -Headers $headers
}

function Invoke-ExpectedFail {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $false)]$Body
  )
  try {
    if ($null -ne $Body) {
      Invoke-Json -Method $Method -Url $Url -Body $Body | Out-Null
    } else {
      Invoke-Json -Method $Method -Url $Url | Out-Null
    }
    return @{ ok = $false; detail = "request unexpectedly succeeded" }
  } catch {
    $raw = $_.ErrorDetails.Message
    return @{ ok = $true; detail = $raw }
  }
}

function Get-DbScalar {
  param(
    [Parameter(Mandatory = $true)][string]$Sql
  )
  $value = docker exec $PostgresContainer psql -U $PostgresUser -d $PostgresDb -t -A -c $Sql
  return "$value".Trim()
}

Write-Host "== DOCFLOW Multi-Channel E2E =="

$nowStamp = Get-Date -Format "yyyyMMddHHmmss"
$channels = @(
  @{ name = "erp_sales"; source = "erp_sales"; sourceRef = "ERP-$nowStamp"; fromType = "sales_order"; toType = "sales_delivery" },
  @{ name = "pos_b2c"; source = "pos_b2c"; sourceRef = "POS-$nowStamp"; fromType = "sales_delivery"; toType = "sales_invoice" },
  @{ name = "portal_b2b"; source = "portal_b2b"; sourceRef = "PORTAL-$nowStamp"; fromType = "sales_order"; toType = "sales_invoice" }
)

$channelResults = @()
$sourceDocIds = @()
$targetDocIds = @()
$idemKeys = @()

foreach ($ch in $channels) {
  $docNumber = "$($ch.name.ToUpper())-$nowStamp"
  $createBody = @{
    doc_type = $ch.fromType
    doc_number = $docNumber
    status = "open"
    source_system = $ch.source
    source_ref = $ch.sourceRef
    customer_id = $CustomerId
    document_date = (Get-Date).ToUniversalTime().ToString("o")
    items = @(
      @{
        article_number = "ART-1"
        description = "E2E $($ch.name)"
        quantity = 3
        unit = "kg"
        unit_price = 10
        discount_percent = 0
        tax_rate = 19
      }
    )
  }

  $created = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/" -Body $createBody
  Assert-True -Condition ([string]::IsNullOrWhiteSpace($created.id) -eq $false) -Message "$($ch.name): create id missing"
  Assert-True -Condition ($created.source_system -eq $ch.source) -Message "$($ch.name): source_system mismatch"

  $sourceDocIds += "$($created.id)"
  $dryIdemKey = "dry-$($created.id)"
  $convIdemKey = "conv-$($created.id)"
  $postIdemKey = "post-$($created.id)"
  $idemKeys += $convIdemKey
  $idemKeys += $postIdemKey

  $dryRun = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$($created.id)/convert" -Body @{
    target_doc_type = $ch.toType
    idempotency_key = $dryIdemKey
    dry_run = $true
  }
  Assert-True -Condition ($dryRun.status -eq "dry_run") -Message "$($ch.name): dry-run failed"

  $convert1 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$($created.id)/convert" -Body @{
    target_doc_type = $ch.toType
    idempotency_key = $convIdemKey
  }
  $convert2 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$($created.id)/convert" -Body @{
    target_doc_type = $ch.toType
    idempotency_key = $convIdemKey
  }
  Assert-True -Condition ($convert1.status -eq "ok") -Message "$($ch.name): convert failed"
  Assert-True -Condition ($convert2.idempotent_hit -eq $true) -Message "$($ch.name): convert idempotency not hit"
  Assert-True -Condition ($convert1.target_doc_id -eq $convert2.target_doc_id) -Message "$($ch.name): idempotent target mismatch"

  $targetDocId = "$($convert1.target_doc_id)"
  $targetDocIds += $targetDocId

  $post1 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$targetDocId/post" -Body @{
    idempotency_key = $postIdemKey
    posted_by = "e2e.script"
  }
  $post2 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$targetDocId/post" -Body @{
    idempotency_key = $postIdemKey
    posted_by = "e2e.script"
  }
  Assert-True -Condition ($post1.status -eq "ok") -Message "$($ch.name): post failed"
  Assert-True -Condition ($post2.idempotent_hit -eq $true) -Message "$($ch.name): post idempotency not hit"

  $targetDoc = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/docflow/$targetDocId"
  Assert-True -Condition ($targetDoc.status -eq "posted") -Message "$($ch.name): target status not posted"

  $channelResults += [ordered]@{
    channel = $ch.name
    source_doc_id = "$($created.id)"
    source_doc_number = "$($created.doc_number)"
    target_doc_id = $targetDocId
    target_doc_number = "$($convert1.payload.target_doc_number)"
    convert_idempotent = $convert2.idempotent_hit
    post_idempotent = $post2.idempotent_hit
  }
}

# Governance check: submit without role must fail, with role must pass
$wfNumber = "WF-E2E-$nowStamp"
$failSubmit = Invoke-ExpectedFail -Method Post -Url "$BaseUrl/api/workflow/sales/$wfNumber/transition" -Body @{
  action = "submit"
  lines = @(@{ qty = 1; price = 1 })
}
Assert-True -Condition ($failSubmit.ok -eq $true) -Message "workflow submit negative test did not fail"
Assert-True -Condition ($failSubmit.detail -match "Insufficient permissions for submit") -Message "workflow submit failure reason mismatch"

$submitOk = Invoke-Json -Method Post -Url "$BaseUrl/api/workflow/sales/$wfNumber/transition" -Body @{
  action = "submit"
  lines = @(@{ qty = 2; price = 5; cost = 3 })
  user_info = @{ roles = @("admin") }
}
Assert-True -Condition ($submitOk.state -eq "pending") -Message "workflow submit did not reach pending"

$approveOk = Invoke-Json -Method Post -Url "$BaseUrl/api/workflow/sales/$wfNumber/transition" -Body @{
  action = "approve"
  lines = @(@{ qty = 2; price = 5; cost = 3 })
  user_info = @{ roles = @("admin") }
}
Assert-True -Condition ($approveOk.state -eq "approved") -Message "workflow approve did not reach approved"

$postOk = Invoke-Json -Method Post -Url "$BaseUrl/api/workflow/sales/$wfNumber/transition" -Body @{
  action = "post"
  total = 10
  lines = @(@{ qty = 2; price = 5; cost = 3 })
  user_info = @{ roles = @("admin") }
}
Assert-True -Condition ($postOk.state -eq "posted") -Message "workflow post did not reach posted"

$wfAudit = Invoke-Json -Method Get -Url "$BaseUrl/api/workflow/sales/$wfNumber/audit"
Assert-True -Condition (@($wfAudit.items).Count -ge 3) -Message "workflow audit has too few entries"

$dbChecks = $null
if (-not $SkipDbChecks) {
  $srcIn = ($sourceDocIds | ForEach-Object { "'$_'" }) -join ","
  $tgtIn = ($targetDocIds | ForEach-Object { "'$_'" }) -join ","
  $idemIn = ($idemKeys | ForEach-Object { "'$_'" }) -join ","

  $linkCount = 0
  foreach ($srcId in $sourceDocIds) {
    $linkCount += [int](Get-DbScalar -Sql "select count(*) from domain_docflow.document_links where from_header_id = '$srcId';")
  }
  $idemCount = [int](Get-DbScalar -Sql "select count(*) from domain_docflow.command_idempotency_keys where idempotency_key in ($idemIn);")
  $outboxCount = [int](Get-DbScalar -Sql "select count(*) from outbox_events where event_type in ('docflow.document.converted','docflow.document.posted') and aggregate_id in ($tgtIn);")
  $sourceTagCount = [int](Get-DbScalar -Sql "select count(*) from domain_docflow.document_headers where id in ($srcIn) and source_system in ('erp_sales','pos_b2c','portal_b2b');")

  Assert-True -Condition ($linkCount -ge 3) -Message "document_links count too low"
  Assert-True -Condition ($idemCount -ge 6) -Message "idempotency key rows too low"
  Assert-True -Condition ($outboxCount -ge 6) -Message "outbox event rows too low"
  Assert-True -Condition ($sourceTagCount -eq 3) -Message "source_system tagging mismatch"

  $dbChecks = [ordered]@{
    document_links = $linkCount
    idempotency_rows = $idemCount
    outbox_events = $outboxCount
    source_system_rows = $sourceTagCount
  }
}

$result = [ordered]@{
  timestamp = (Get-Date).ToString("o")
  tenant_id = $TenantId
  channels = $channelResults
  workflow_governance = [ordered]@{
    number = $wfNumber
    negative_submit_blocked = $true
    final_state = $postOk.state
    audit_entries = @($wfAudit.items).Count
  }
  db_checks = $dbChecks
}

Write-Host "DOCFLOW Multi-Channel E2E erfolgreich:"
$result | ConvertTo-Json -Depth 12
