# Smoke: Process Kernel Action Execute + CreatePurchaseOrder (nach alembic upgrade head)
# Voraussetzung: Backend laeuft, API_DEV_TOKEN oder gueltiger Bearer, X-Tenant-ID

param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$Token = $env:API_DEV_TOKEN,
    [string]$TenantId = "dev-tenant"
)

$ErrorActionPreference = "Stop"
if (-not $Token) {
    Write-Error "API_DEV_TOKEN nicht gesetzt"
}

$headers = @{
    "Authorization" = "Bearer $Token"
    "Content-Type"  = "application/json"
    "X-Tenant-ID"   = $TenantId
}

$body = @{
    command_name      = "CreatePurchaseOrder"
    aggregate_type    = "purchase_order"
    aggregate_id      = "smoke-po-1"
    payload           = @{
        approval_status = "approved"
        lieferant_id    = 1
    }
    tenant_id         = $TenantId
    issuer_type       = "human"
    issuer_role       = "procurement_agent"
    idempotency_key   = "smoke-$(Get-Date -Format 'yyyyMMddHHmmss')"
} | ConvertTo-Json -Depth 6

$uri = "$BaseUrl/api/v1/process/actions/execute"
Write-Host "POST $uri"
Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
