param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$TenantId = "00000000-0000-0000-0000-000000000001",
  [string]$BearerToken = $(if ($env:API_BEARER_TOKEN) { $env:API_BEARER_TOKEN } else { "dev-token" }),
  [string]$CustomerId = "67d2990e-32c4-42ac-8493-9a2753fa4683",
  [string]$PostgresContainer = "valeo-neuro-erp-postgres",
  [string]$PostgresUser = "valeo_dev",
  [string]$PostgresDb = "valeo_neuro_erp"
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
    [Parameter(Mandatory = $false)]$Body
  )
  $headers = @{
    "Content-Type" = "application/json"
    "X-Tenant-ID" = $TenantId
    "Authorization" = "Bearer $BearerToken"
  }
  if ($null -ne $Body) {
    return Invoke-RestMethod -Method $Method -Uri $Url -Headers $headers -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 20)
  }
  return Invoke-RestMethod -Method $Method -Uri $Url -Headers $headers
}

function New-PosCompliance {
  param(
    [string]$terminalId,
    [string]$transactionType = "sale",
    [string]$originalHeaderId = ""
  )
  $now = (Get-Date).ToUniversalTime()
  return @{
    terminal_id = $terminalId
    cash_register_id = "KASSE-1"
    transaction_type = $transactionType
    payment_breakdown = @{
      card = 19.99
      cash = 0
    }
    tse_transaction_id = "$terminalId-" + (Get-Date -Format "yyyyMMddHHmmssfff")
    tse_signature = "SIG-" + [guid]::NewGuid().ToString()
    tse_signature_counter = [int64](Get-Random -Minimum 1000 -Maximum 900000)
    transaction_started_at = $now.AddSeconds(-10).ToString("o")
    transaction_ended_at = $now.ToString("o")
    receipt_issued_at = $now.ToString("o")
    dsfinvk_export_batch_id = "BATCH-" + (Get-Date -Format "yyyyMM")
    correction_type = $(if ($transactionType -eq "sale") { $null } elseif ($transactionType -eq "storno") { "storno" } else { "retoure" })
    original_header_id = $(if ($originalHeaderId) { $originalHeaderId } else { $null })
  }
}

Write-Host "== POS/TSE B2B Flow (Stammkunde + ODP) =="
$stamp = Get-Date -Format "yyyyMMddHHmmss"

# Fall 1: Stammkunde verlangt Sofort-Rechnung
$receipt1 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/" -Body @{
  doc_type = "pos_receipt"
  doc_number = "POS-SK-$stamp"
  status = "open"
  source_system = "pos_b2c"
  source_ref = "KASSE1-$stamp"
  customer_id = $CustomerId
  items = @(@{
    article_number = "ART-1"
    description = "Hofmarkt Artikel"
    quantity = 1
    unit = "st"
    unit_price = 19.99
    tax_rate = 7
  })
  pos_compliance = (New-PosCompliance -terminalId "TSE-KASSE-1")
}
Assert-True -Condition ($receipt1.doc_type -eq "pos_receipt") -Message "receipt1 not created"
Assert-True -Condition ($null -ne $receipt1.pos_compliance) -Message "receipt1 missing pos compliance"

$postReceipt1 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$($receipt1.id)/post" -Body @{
  idempotency_key = "post-$($receipt1.id)"
  posted_by = "kasse.user"
}
Assert-True -Condition ($postReceipt1.status -eq "ok") -Message "receipt1 post failed"

$invoice1 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$($receipt1.id)/convert" -Body @{
  target_doc_type = "sales_invoice"
  idempotency_key = "inv-$($receipt1.id)"
}
Assert-True -Condition ($invoice1.status -eq "ok") -Message "receipt1 -> invoice conversion failed"

# Fall 2: ODP (Einmalkunde ohne Kundenkonto) verlangt Sofort-Rechnung
$receipt2 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/" -Body @{
  doc_type = "pos_receipt"
  doc_number = "POS-ODP-$stamp"
  status = "open"
  source_system = "pos_b2c"
  source_ref = "ODP-$stamp"
  customer_id = $null
  items = @(@{
    article_number = "ART-2"
    description = "Einmalkauf"
    quantity = 2
    unit = "st"
    unit_price = 8.50
    tax_rate = 19
  })
  pos_compliance = (New-PosCompliance -terminalId "TSE-KASSE-2")
}
Assert-True -Condition ($receipt2.doc_type -eq "pos_receipt") -Message "receipt2 not created"

$postReceipt2 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$($receipt2.id)/post" -Body @{
  idempotency_key = "post-$($receipt2.id)"
  posted_by = "kasse.user"
}
Assert-True -Condition ($postReceipt2.status -eq "ok") -Message "receipt2 post failed"

$invoice2 = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$($receipt2.id)/convert" -Body @{
  target_doc_type = "sales_invoice"
  idempotency_key = "inv-$($receipt2.id)"
}
Assert-True -Condition ($invoice2.status -eq "ok") -Message "receipt2 -> invoice conversion failed"

$invoice2Doc = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/docflow/$($invoice2.target_doc_id)"
Assert-True -Condition ($null -eq $invoice2Doc.customer_id -or $invoice2Doc.customer_id -eq "") -Message "ODP invoice must not force customer_id"

# Storno als eigener Vorgang mit Referenz auf Originalbon
$storno = Invoke-Json -Method Post -Url "$BaseUrl/api/v1/docflow/$($receipt1.id)/convert" -Body @{
  target_doc_type = "pos_storno"
  idempotency_key = "storno-$($receipt1.id)"
}
Assert-True -Condition ($storno.status -eq "ok") -Message "storno conversion failed"
$stornoCompliance = Invoke-Json -Method Get -Url "$BaseUrl/api/v1/docflow/$($storno.target_doc_id)/pos-compliance"
Assert-True -Condition ($stornoCompliance.correction_type -eq "storno") -Message "storno correction_type missing"
Assert-True -Condition ($stornoCompliance.original_header_id -eq $receipt1.id) -Message "storno original reference missing"

$sql = "select count(*) from domain_docflow.pos_receipt_compliance where header_id in ('$($receipt1.id)','$($receipt2.id)','$($storno.target_doc_id)');"
$posRows = docker exec $PostgresContainer psql -U $PostgresUser -d $PostgresDb -t -A -c $sql
$posRows = [int]("$posRows".Trim())
Assert-True -Condition ($posRows -ge 3) -Message "pos compliance rows missing"

$result = [ordered]@{
  timestamp = (Get-Date).ToString("o")
  stammkunde = @{
    receipt_id = "$($receipt1.id)"
    invoice_id = "$($invoice1.target_doc_id)"
  }
  odp = @{
    receipt_id = "$($receipt2.id)"
    invoice_id = "$($invoice2.target_doc_id)"
  }
  storno = @{
    document_id = "$($storno.target_doc_id)"
    original_receipt_id = "$($receipt1.id)"
  }
  db = @{
    pos_compliance_rows = $posRows
  }
}

Write-Host "POS/TSE B2B Flow erfolgreich:"
$result | ConvertTo-Json -Depth 8
