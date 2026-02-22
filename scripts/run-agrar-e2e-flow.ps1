param(
  [string]$BaseUrl = 'http://localhost:8000',
  [string]$TenantId = '00000000-0000-0000-0000-000000000001',
  [string]$ApiToken = 'dev-token'
)

$ErrorActionPreference = 'Stop'

$headers = @{
  Authorization = "Bearer $ApiToken"
  'X-Tenant-ID' = $TenantId
}

$ts = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

$ticketPayload = @{ 
  ticket_number = "E2E-WT-$ts"
  scale_id = 'W-001'
  vehicle_plate = 'E2E-PLATE'
  gross_weight = 28000
  tare_weight = 9000
  moisture_pct = 15.5
  impurities_pct = 1.3
  direction = 'in'
  reference_doc = 'e2e-flow'
} | ConvertTo-Json

$ticket = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/weighing-tickets/" -Headers $headers -ContentType 'application/json' -Body $ticketPayload
if (-not $ticket.id) { throw "Ticket creation failed" }

$settlementPayload = @{
  settlement_number = "E2E-SET-$ts"
  ticket_id = $ticket.id
  supplier_id = 'SUP-E2E-001'
  gross_quantity_kg = 19000
  billing_quantity_kg = 18500
  unit_price_eur_per_ton = 220
  deductions = @(@{ deduction_type='drying'; mode='per_ton'; rate_per_ton_eur=3.5 })
  note = 'e2e flow test'
} | ConvertTo-Json -Depth 5

$settlement = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/agrar/settlements/" -Headers $headers -ContentType 'application/json' -Body $settlementPayload
if (-not $settlement.id) { throw "Settlement creation failed" }

$postPayload = @{ 
  debit_account = '5000'
  credit_account_supplier = '3300'
  credit_account_deductions = '5490'
} | ConvertTo-Json

$postResult = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/agrar/settlements/$($settlement.id)/post-fibu" -Headers $headers -ContentType 'application/json' -Body $postPayload
if (-not $postResult.ok) { throw "Posting failed" }

[pscustomobject]@{
  run_at_utc = (Get-Date).ToUniversalTime().ToString('o')
  tenant_id = $TenantId
  ticket_id = $ticket.id
  ticket_number = $ticket.ticket_number
  settlement_id = $settlement.id
  settlement_number = $settlement.settlement_number
  journal_ref = $postResult.journal_ref
  flow_ok = $true
} | ConvertTo-Json
