BEGIN;

-- Extension für UUID-Defaults
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Migrate domain_crm.activities
ALTER TABLE domain_crm.activities 
  DROP CONSTRAINT IF EXISTS activities_pkey CASCADE;

ALTER TABLE domain_crm.activities 
  DROP CONSTRAINT IF EXISTS activities_tenant_id_fkey CASCADE;

-- Default droppen vor Type-Change
ALTER TABLE domain_crm.activities 
  ALTER COLUMN id DROP DEFAULT;

-- Konvertiere id zu UUID
ALTER TABLE domain_crm.activities 
  ALTER COLUMN id TYPE uuid USING COALESCE(id::uuid, gen_random_uuid());

-- Default neu setzen
ALTER TABLE domain_crm.activities 
  ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- Konvertiere tenant_id zu UUID (nullable)
ALTER TABLE domain_crm.activities 
  ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid;

-- Primary Key wiederherstellen
ALTER TABLE domain_crm.activities 
  ADD CONSTRAINT activities_pkey PRIMARY KEY (id);

-- Migrate domain_crm.farm_profiles
ALTER TABLE domain_crm.farm_profiles 
  DROP CONSTRAINT IF EXISTS farm_profiles_pkey CASCADE;

ALTER TABLE domain_crm.farm_profiles 
  DROP CONSTRAINT IF EXISTS farm_profiles_tenant_id_fkey CASCADE;

-- Konvertiere id zu UUID
ALTER TABLE domain_crm.farm_profiles 
  ALTER COLUMN id TYPE uuid USING COALESCE(id::uuid, gen_random_uuid());

ALTER TABLE domain_crm.farm_profiles 
  ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- Konvertiere tenant_id zu UUID (nullable)
ALTER TABLE domain_crm.farm_profiles 
  ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid;

-- Primary Key wiederherstellen
ALTER TABLE domain_crm.farm_profiles 
  ADD CONSTRAINT farm_profiles_pkey PRIMARY KEY (id);

-- Foreign Keys wiederherstellen (wenn domain_shared.tenants existiert)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'domain_shared' AND table_name = 'tenants') THEN
    ALTER TABLE domain_crm.activities 
      ADD CONSTRAINT activities_tenant_id_fkey 
      FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id);
    
    ALTER TABLE domain_crm.farm_profiles 
      ADD CONSTRAINT farm_profiles_tenant_id_fkey 
      FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id);
  END IF;
END $$;

COMMIT;

-- Verification
SELECT 'UUID Migration completed successfully!' AS status;
SELECT schema_name, table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'domain_crm' 
  AND table_name IN ('activities', 'farm_profiles')
  AND column_name IN ('id', 'tenant_id')
ORDER BY table_name, column_name;

