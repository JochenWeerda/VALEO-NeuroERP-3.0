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

Write-Host "Seeding admin mobile/routing/connectors for tenant $TenantId ..."

$sql = @"
INSERT INTO domain_shared.admin_stations
  (id, tenant_id, station_code, name, station_type, location_name, is_active, settings, created_at, updated_at)
VALUES
  ('30000000-0000-0000-0000-000000000101', '$TenantId', 'KASSE-01', 'Kasse 1', 'pos', 'Hofmarkt', TRUE, '{"fallback_station":"PACK-01"}'::jsonb, NOW(), NOW()),
  ('30000000-0000-0000-0000-000000000102', '$TenantId', 'PACK-01', 'Packplatz 1', 'packstation', 'Lager', TRUE, '{}'::jsonb, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.admin_scan_profiles
  (id, tenant_id, profile_code, name, source_type, target_action, is_active, barcode_formats, parse_rules, validation_rules, error_mode, created_at, updated_at)
VALUES
  ('30000000-0000-0000-0000-000000000111', '$TenantId', 'INV_SCAN_STD', 'Inventur Standard', 'camera', 'inventory_count', TRUE, '["EAN13","Code128","QR"]'::jsonb, '{"trim":true}'::jsonb, '{"charge_required":false}'::jsonb, 'dialog', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.admin_mobile_devices
  (id, tenant_id, device_code, name, device_type, ownership_type, platform, os_version, app_version, station_id, scan_profile_id, status, last_sync_at, capabilities, settings, is_active, created_at, updated_at)
VALUES
  ('30000000-0000-0000-0000-000000000121', '$TenantId', 'MOB-INV-01', 'Inventur Handy 1', 'smartphone', 'company', 'android', '14', '1.0.0', '30000000-0000-0000-0000-000000000102', '30000000-0000-0000-0000-000000000111', 'active', NOW(), '{"camera_scan":true}'::jsonb, '{}'::jsonb, TRUE, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.admin_connector_configs
  (id, tenant_id, config_code, name, connector_type, status, auth_type, credentials, scopes, mapping, retry_policy, rate_limit_per_minute, last_health_at, last_error, created_at, updated_at)
VALUES
  ('30000000-0000-0000-0000-000000000131', '$TenantId', 'SLACK_ALERTS', 'Slack Alerts', 'slack', 'active', 'token', '{"token":"***"}'::jsonb, '["alerts:write"]'::jsonb, '{"channel":"#erp-alerts"}'::jsonb, '{"max_retries":5,"backoff_sec":30}'::jsonb, 120, NOW(), NULL, NOW(), NOW()),
  ('30000000-0000-0000-0000-000000000132', '$TenantId', 'N8N_AUTOMATION', 'n8n Automation', 'n8n', 'active', 'api_key', '{"api_key":"***"}'::jsonb, '["workflow:trigger"]'::jsonb, '{"endpoint":"/webhook/erp"}'::jsonb, '{"max_retries":3,"backoff_sec":20}'::jsonb, 300, NOW(), NULL, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.admin_connector_events
  (id, tenant_id, connector_id, event_type, status, message, payload, retry_count, next_retry_at, created_at)
VALUES
  ('30000000-0000-0000-0000-000000000141', '$TenantId', '30000000-0000-0000-0000-000000000131', 'health_check', 'ok', 'connector healthy', '{"latency_ms":120}'::jsonb, 0, NULL, NOW()),
  ('30000000-0000-0000-0000-000000000142', '$TenantId', '30000000-0000-0000-0000-000000000132', 'delivery', 'warning', 'retry scheduled', '{"job_id":"abc-123"}'::jsonb, 1, NOW() + interval '2 minutes', NOW())
ON CONFLICT (id) DO NOTHING;
"@

Invoke-Db -Sql $sql | Out-Null
Write-Host "Seed complete."
