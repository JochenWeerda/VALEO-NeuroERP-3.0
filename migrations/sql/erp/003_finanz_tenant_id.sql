-- Finanz-Stammdaten: Mandanten-Isolation (x-tenant-id / resolveTenantId).
-- Bestehende Zeilen erhalten tenant_id='_legacy'.

BEGIN;

ALTER TABLE finanz.konten ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255) NOT NULL DEFAULT '_legacy';
ALTER TABLE finanz.bankkonten ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255) NOT NULL DEFAULT '_legacy';
ALTER TABLE finanz.debitoren ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255) NOT NULL DEFAULT '_legacy';
ALTER TABLE finanz.kreditoren ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255) NOT NULL DEFAULT '_legacy';
ALTER TABLE finanz.buchungen ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255) NOT NULL DEFAULT '_legacy';

DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN
    SELECT n.nspname AS sch, t.relname AS tbl, c.conname
    FROM pg_constraint c
    INNER JOIN pg_class t ON c.conrelid = t.oid
    INNER JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname = 'finanz'
      AND t.relname IN ('konten', 'debitoren', 'kreditoren', 'buchungen')
      AND c.contype = 'u'
      AND array_length(c.conkey, 1) = 1
      AND EXISTS (
        SELECT 1
        FROM unnest(c.conkey) AS u(attnum)
        INNER JOIN pg_attribute a
          ON a.attrelid = c.conrelid AND a.attnum = u.attnum
        WHERE a.attname IN ('kontonummer', 'debitor_nr', 'kreditor_nr', 'buchungsnummer')
      )
  LOOP
    EXECUTE format('ALTER TABLE %I.%I DROP CONSTRAINT %I', r.sch, r.tbl, r.conname);
  END LOOP;
END;
$$;

CREATE UNIQUE INDEX IF NOT EXISTS finanz_konten_tenant_kontonummer_uq ON finanz.konten (tenant_id, kontonummer);
CREATE UNIQUE INDEX IF NOT EXISTS finanz_debitoren_tenant_debitor_nr_uq ON finanz.debitoren (tenant_id, debitor_nr);
CREATE UNIQUE INDEX IF NOT EXISTS finanz_kreditoren_tenant_kreditor_nr_uq ON finanz.kreditoren (tenant_id, kreditor_nr);
CREATE UNIQUE INDEX IF NOT EXISTS finanz_buchungen_tenant_buchungsnummer_uq ON finanz.buchungen (tenant_id, buchungsnummer);

CREATE INDEX IF NOT EXISTS finanz_bankkonten_tenant_idx ON finanz.bankkonten (tenant_id);
CREATE INDEX IF NOT EXISTS finanz_konten_tenant_idx ON finanz.konten (tenant_id);
CREATE INDEX IF NOT EXISTS finanz_buchungen_tenant_idx ON finanz.buchungen (tenant_id);

COMMIT;
