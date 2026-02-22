param(
  [string]$PostgresContainer = "valeo-neuro-erp-postgres",
  [string]$PostgresUser = "valeo_dev",
  [string]$PostgresDb = "valeo_neuro_erp",
  [string]$TenantId = "00000000-0000-0000-0000-000000000001"
)

$ErrorActionPreference = "Stop"

function Invoke-Db {
  param([Parameter(Mandatory = $true)][string]$Sql)
  return ($Sql | docker exec -i $PostgresContainer psql -v ON_ERROR_STOP=1 -U $PostgresUser -d $PostgresDb -t -A)
}

Write-Host "Seeding admin API keys for tenant $TenantId ..."

$sql = @"
INSERT INTO domain_shared.api_keys
  (id, tenant_id, name, key_prefix, key_hash, scopes, ip_allowlist, rate_limit_per_minute, expires_at, status, created_by, created_at, updated_at)
VALUES
  ('10000000-0000-0000-0000-000000000101', '$TenantId', 'seed-active-integration', 'vak_seed_active', md5('seed-active-token'), '["inventory:read","docflow:write"]'::jsonb, '["10.10.0.0/16"]'::jsonb, 600, NOW() + interval '365 days', 'active', NULL, NOW(), NOW()),
  ('10000000-0000-0000-0000-000000000102', '$TenantId', 'seed-revoked-legacy', 'vak_seed_revoked', md5('seed-revoked-token'), '["legacy:read"]'::jsonb, '[]'::jsonb, 120, NULL, 'revoked', NULL, NOW() - interval '90 days', NOW())
ON CONFLICT (id) DO NOTHING;
"@

Invoke-Db -Sql $sql | Out-Null
Write-Host "Seed complete."
