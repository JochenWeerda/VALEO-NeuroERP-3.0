$ErrorActionPreference = 'Stop'

$baseUrl = if ($env:SUPERGLUE_CI_BASE_URL) { $env:SUPERGLUE_CI_BASE_URL } elseif ($env:SUPERGLUE_BASE_URL) { $env:SUPERGLUE_BASE_URL } else { 'http://localhost:3011' }
$tenantId = if ($env:SUPERGLUE_CI_TENANT_ID) { $env:SUPERGLUE_CI_TENANT_ID } else { 'ci-tenant' }

Write-Host "Superglue CI smoke against $baseUrl for tenant $tenantId"
Invoke-RestMethod -Uri ($baseUrl.TrimEnd('/') + '/v1/health') -Method Get | Out-Null
Invoke-RestMethod -Uri ($baseUrl.TrimEnd('/') + '/v1/tools?page=1&limit=100') -Method Get | Out-Null
Write-Host 'Superglue CI smoke passed'
