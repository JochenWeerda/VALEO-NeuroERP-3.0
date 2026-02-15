param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$TenantId = "default",
  [string]$User = "system",
  [string]$BearerToken = $(if ($env:API_BEARER_TOKEN) { $env:API_BEARER_TOKEN } else { "dev-token" })
)

$ErrorActionPreference = "Stop"

function Invoke-JsonPost {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)]$Body
  )
  $headers = @{
    "Content-Type" = "application/json"
    "X-Tenant-ID" = $TenantId
  }
  if ($BearerToken) { $headers["Authorization"] = "Bearer $BearerToken" }
  return Invoke-RestMethod -Method Post -Uri $Url -Headers $headers -Body ($Body | ConvertTo-Json -Depth 20)
}

function Invoke-JsonPatch {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)]$Body
  )
  $headers = @{
    "Content-Type" = "application/json"
    "X-Tenant-ID" = $TenantId
  }
  if ($BearerToken) { $headers["Authorization"] = "Bearer $BearerToken" }
  return Invoke-RestMethod -Method Patch -Uri $Url -Headers $headers -Body ($Body | ConvertTo-Json -Depth 20)
}

Write-Host "== Einkauf E2E (/api/v1 + /api/einkauf) =="

$getHeaders = @{ "X-Tenant-ID" = $TenantId }
if ($BearerToken) { $getHeaders["Authorization"] = "Bearer $BearerToken" }

$supplierRes = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/crm/suppliers?limit=1&is_active=true" -Headers $getHeaders
if (-not $supplierRes.items -or $supplierRes.items.Count -eq 0) {
  throw "Kein aktiver Lieferant gefunden. Bitte Seed-Daten laden."
}
$supplier = $supplierRes.items[0]

$poNumber = "PO-E2E-" + (Get-Date -Format "yyyyMMddHHmmss")
$today = Get-Date -Format "yyyy-MM-dd"
$deliveryDate = (Get-Date).AddDays(3).ToString("yyyy-MM-dd")

$poPayload = @{
  purchaseOrderNumber = $poNumber
  orderDate = $today
  supplierId = "$($supplier.id)"
  subject = "E2E Lieferant $($supplier.name)"
  description = "Automatischer E2E-Test"
  status = "ENTWURF"
  deliveryDate = $deliveryDate
  paymentTerms = "net30"
  taxRate = 19
  items = @(
    @{
      id = "POITEM-1"
      itemType = "PRODUCT"
      articleId = "ART-E2E-001"
      description = "E2E Testartikel"
      quantity = 10
      unit = "kg"
      unitPrice = 12.5
      discountPercent = 0
    }
  )
}

$po = Invoke-JsonPost -Url "$BaseUrl/api/v1/purchase-orders" -Body $poPayload
$poId = "$($po.id)"
if (-not $poId) { throw "PO konnte nicht erstellt werden." }

$approvedPo = Invoke-JsonPost -Url "$BaseUrl/api/v1/purchase-orders/$poId/approve" -Body @{}

$grPayload = @{
  purchaseOrderId = $poId
  deliveryNoteNumber = "LS-E2E-" + (Get-Date -Format "HHmmss")
  receivedDate = $today
  receivedBy = $User
  receivedLocation = "Lager A"
  qualityInspectionStatus = "PASSED"
  inspectionNotes = "E2E automatisch"
  items = @(
    @{
      purchaseOrderItemId = "POITEM-1"
      articleId = "ART-E2E-001"
      articleName = "E2E Testartikel"
      orderedQuantity = 10
      receivedQuantity = 10
      acceptedQuantity = 10
      rejectedQuantity = 0
      condition = "PERFECT"
    }
  )
}

$gr = Invoke-JsonPost -Url "$BaseUrl/api/v1/einkauf/goods-receipts" -Body $grPayload
$grId = "$($gr.id)"
if (-not $grId) { throw "Wareneingang konnte nicht erstellt werden." }

$invNumber = "RE-E2E-" + (Get-Date -Format "yyyyMMddHHmmss")
$invoicePayload = @{
  rechnungsNummer = $invNumber
  lieferantId = "$($supplier.id)"
  lieferantName = "$($supplier.name)"
  bestellungId = $poId
  wareneingangId = $grId
  rechnungsDatum = $today
  faelligkeitsDatum = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")
  nettoBetrag = 125
  mwstBetrag = 23.75
  bruttoBetrag = 148.75
  waehrung = "EUR"
  status = "OFFEN"
  zahlungsreferenz = "E2E-TEST"
  notizen = "E2E automatisch"
  positionen = @(
    @{
      artikelId = "ART-E2E-001"
      artikelName = "E2E Testartikel"
      menge = 10
      einzelpreis = 12.5
      gesamtpreis = 125
      mwstSatz = 19
    }
  )
}

$invoice = Invoke-JsonPost -Url "$BaseUrl/api/einkauf/rechnungseingaenge" -Body $invoicePayload
$invoiceId = "$($invoice.id)"
if (-not $invoiceId) { throw "Rechnungseingang konnte nicht erstellt werden." }

$reList = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/einkauf/rechnungseingaenge" -Headers $getHeaders
$createdInvoice = $reList | Where-Object { $_.id -eq $invoiceId -or $_.rechnungsNummer -eq $invNumber } | Select-Object -First 1
if (-not $createdInvoice) {
  throw "Rechnungseingang wurde nicht in /api/v1/einkauf/rechnungseingaenge gefunden."
}

$result = [ordered]@{
  purchaseOrder = @{
    id = $poId
    number = $poNumber
    status = "$($approvedPo.status)"
  }
  goodsReceipt = @{
    id = $grId
    status = "$($gr.status)"
  }
  invoice = @{
    id = $invoiceId
    number = $invNumber
    status = "$($createdInvoice.status)"
  }
}

Write-Host "E2E erfolgreich:"
$result | ConvertTo-Json -Depth 10
