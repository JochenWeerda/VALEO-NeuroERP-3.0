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

Write-Host "Seeding admin devices/output settings for tenant $TenantId ..."

$sql = @"
INSERT INTO domain_shared.admin_devices
  (id, tenant_id, device_type, name, vendor, model, station_code, connection_uri, capabilities, is_active, created_at, updated_at)
VALUES
  ('20000000-0000-0000-0000-000000000101', '$TenantId', 'printer', 'Packplatz Drucker 1', 'Kyocera', 'M3540dn', 'PACK-01', 'ipp://printserver/pack-01', '{"paper":"A4","duplex":true}'::jsonb, TRUE, NOW(), NOW()),
  ('20000000-0000-0000-0000-000000000102', '$TenantId', 'scanner', 'Wareneingang Scanner 1', 'Zebra', 'DS2278', 'WE-01', 'usb://scanner/we-01', '{"barcode":["EAN13","GS1-128"]}'::jsonb, TRUE, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.admin_device_mappings
  (id, tenant_id, device_id, document_type, process_code, output_format, copies, is_default, settings, created_at, updated_at)
VALUES
  ('20000000-0000-0000-0000-000000000111', '$TenantId', '20000000-0000-0000-0000-000000000101', 'delivery_note', 'shipping', 'pdf', 1, TRUE, '{"tray":"A4"}'::jsonb, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.admin_output_templates
  (id, tenant_id, template_code, name, document_type, output_format, language, is_active, current_version, created_at, updated_at)
VALUES
  ('20000000-0000-0000-0000-000000000121', '$TenantId', 'LS_STD_DE', 'Lieferschein Standard DE', 'delivery_note', 'pdf', 'de', TRUE, 1, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.admin_output_template_versions
  (id, tenant_id, template_id, version_no, content, metadata, change_note, created_at)
VALUES
  ('20000000-0000-0000-0000-000000000131', '$TenantId', '20000000-0000-0000-0000-000000000121', 1, '<template code=""LS_STD_DE"">...</template>', '{"engine":"jinja2"}'::jsonb, 'Initialversion', NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.admin_output_profiles
  (id, tenant_id, profile_code, name, document_type, process_code, template_id, device_id, output_channel, archive_mode, archive_retention_days, is_active, settings, created_at, updated_at)
VALUES
  ('20000000-0000-0000-0000-000000000141', '$TenantId', 'LS_SHIP_STD', 'Lieferschein Versand Standard', 'delivery_note', 'shipping', '20000000-0000-0000-0000-000000000121', '20000000-0000-0000-0000-000000000101', 'print', 'dms', 3650, TRUE, '{"auto_archive":true}'::jsonb, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;
"@

Invoke-Db -Sql $sql | Out-Null
Write-Host "Seed complete."
