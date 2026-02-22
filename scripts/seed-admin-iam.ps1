Param(
  [string]$DbContainer = "valeo-neuro-erp-postgres",
  [string]$DbUser = "valeo_dev",
  [string]$DbName = "valeo_neuro_erp",
  [string]$TenantId = "00000000-0000-0000-0000-000000000001"
)

$tenant = $TenantId.Replace("'","''")

$sql = @"
INSERT INTO domain_shared.tenants (id, name, domain, settings, is_active, created_at)
VALUES ('$tenant'::uuid, 'Default Tenant', 'default.local', '{}'::jsonb, true, NOW())
ON CONFLICT (id) DO NOTHING;

UPDATE domain_shared.tenants
SET settings = (
  COALESCE(settings, '{}'::jsonb) || jsonb_build_object(
    'admin_roles',
    (
      COALESCE(settings -> 'admin_roles', '{}'::jsonb)
      - '90000000-0000-0000-0000-000000000003'
      - '90000000-0000-0000-0000-000000000002'
    ) || jsonb_build_object(
      'dispo_lead', jsonb_build_object(
        'name', 'dispo_lead',
        'beschreibung', 'Disposition Teamlead mit Monitoring-Fokus',
        'rechte_liste', jsonb_build_array('logistics:read','inventory:read','admin:monitoring:read'),
        'is_system', false
      ),
      'audit_reader', jsonb_build_object(
        'name', 'audit_reader',
        'beschreibung', 'Nur Leserechte auf Audit und Compliance',
        'rechte_liste', jsonb_build_array('audit:read','compliance:read'),
        'is_system', false
      )
    )
  )
),
updated_at = NOW()
WHERE id = '$tenant'::uuid;

INSERT INTO domain_shared.users
  (id, keycloak_id, username, email, first_name, last_name, is_active, roles, tenant_id, preferences, created_at, updated_at)
VALUES
  ('90000000-0000-0000-0000-000000000001'::uuid, 'local-90000000-0000-0000-0000-000000000001', 'admin.master', 'admin.master@valeo.local', 'Admin', 'Master', true, ARRAY['admin']::varchar[], '$tenant'::uuid, '{}'::jsonb, NOW(), NOW()),
  ('90000000-0000-0000-0000-000000000002'::uuid, 'local-90000000-0000-0000-0000-000000000002', 'dispo.lead',  'dispo.lead@valeo.local',  'Dispo', 'Lead',   true, ARRAY['dispo_lead']::varchar[], '$tenant'::uuid, '{}'::jsonb, NOW(), NOW()),
  ('90000000-0000-0000-0000-000000000003'::uuid, 'local-90000000-0000-0000-0000-000000000003', 'audit.reader','audit.reader@valeo.local','Audit', 'Reader', true, ARRAY['audit_reader']::varchar[], '$tenant'::uuid, '{}'::jsonb, NOW(), NOW())
ON CONFLICT (username) DO UPDATE SET
  email = EXCLUDED.email,
  first_name = EXCLUDED.first_name,
  last_name = EXCLUDED.last_name,
  roles = EXCLUDED.roles,
  is_active = EXCLUDED.is_active,
  updated_at = NOW();

INSERT INTO infrastructure.audit_log
  (id, user_id, action, resource_type, resource_id, old_values, new_values, ip_address, user_agent, timestamp)
VALUES
  ('a9000000-0000-0000-0000-000000000001'::uuid, '90000000-0000-0000-0000-000000000001'::uuid, 'admin.user.created', 'user', '90000000-0000-0000-0000-000000000002'::uuid, '{}'::jsonb, '{}'::jsonb, '127.0.0.1', 'seed-script', NOW() - INTERVAL '2 day'),
  ('a9000000-0000-0000-0000-000000000002'::uuid, '90000000-0000-0000-0000-000000000001'::uuid, 'admin.role.updated', 'role', '91000000-0000-0000-0000-000000000001'::uuid, '{}'::jsonb, '{}'::jsonb, '127.0.0.1', 'seed-script', NOW() - INTERVAL '1 day'),
  ('a9000000-0000-0000-0000-000000000003'::uuid, '90000000-0000-0000-0000-000000000003'::uuid, 'admin.auth.failed', 'session', '90000000-0000-0000-0000-000000000003'::uuid, '{}'::jsonb, '{}'::jsonb, '127.0.0.1', 'seed-script', NOW() - INTERVAL '6 hour')
ON CONFLICT (id) DO NOTHING;
"@

docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1 -c $sql
