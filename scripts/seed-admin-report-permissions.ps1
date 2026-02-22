Param(
  [string]$DbContainer = "valeo-neuro-erp-postgres",
  [string]$DbUser = "valeo_dev",
  [string]$DbName = "valeo_neuro_erp",
  [string]$TenantId = "00000000-0000-0000-0000-000000000001"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$sql = @'
INSERT INTO domain_shared.admin_report_permissions
  (id, tenant_id, role_id, report_key, can_view, can_export, allowed_scopes, filters, active, created_at, updated_at)
VALUES
  (gen_random_uuid(), '__TENANT__', 'controller', 'finance.bwa', true, true, jsonb_build_array('tenant'), '{}'::jsonb, true, now(), now()),
  (gen_random_uuid(), '__TENANT__', 'manager', 'finance.profit-loss', true, false, jsonb_build_array('tenant'), '{}'::jsonb, true, now(), now())
ON CONFLICT (tenant_id, role_id, report_key) DO UPDATE
SET can_view = EXCLUDED.can_view,
    can_export = EXCLUDED.can_export,
    allowed_scopes = EXCLUDED.allowed_scopes,
    filters = EXCLUDED.filters,
    active = EXCLUDED.active,
    updated_at = now();
'@
$sql = $sql.Replace("__TENANT__", $TenantId)

docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1 -c $sql
if ($LASTEXITCODE -ne 0) {
  throw "Seeding admin_report_permissions failed."
}
Write-Host "admin_report_permissions seeded for tenant $TenantId ($DbContainer/$DbName as $DbUser)"
