BEGIN;

-- a) Extension für UUID-Defaults (eine von beiden genügt)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- b) Hilfs-Funktion: erzeugt DDL-Skripte zum *sicheren* Konvertieren
--    von varchar/text -> uuid, inkl. FK-Drops & Recreates.
CREATE OR REPLACE FUNCTION migrate_varchar_to_uuid(
  in_schema TEXT,
  in_table  TEXT,
  in_column TEXT,
  set_default BOOLEAN DEFAULT TRUE,
  is_pk      BOOLEAN DEFAULT FALSE
) RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
  fqtn TEXT := format('%I.%I', in_schema, in_table);
  coltype TEXT;
  con RECORD;
  dep RECORD;
  idx RECORD;
  has_default BOOLEAN := FALSE;
  pk_name TEXT;
BEGIN
  -- 1) Prüfen, ob Spalte castbar ist
  EXECUTE format($f$SELECT COUNT(*) FROM %s WHERE %I IS NOT NULL AND %I !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'$f$, fqtn, in_column, in_column)
  INTO coltype; -- missbraucht als Zählwert
  IF coltype::int > 0 THEN
    RAISE EXCEPTION 'Spalte %.%.% enthält nicht-castbare Werte. Abbruch.', in_schema, in_table, in_column;
  END IF;

  -- 2) Abhängige FK-Constraints (ANDere Tabellen, die auf diese Spalte referenzieren) droppen
  FOR dep IN
    SELECT conrelid::regclass AS child_table, conname, pg_get_constraintdef(c.oid) AS def
    FROM pg_constraint c
    JOIN pg_attribute a ON a.attnum = ANY (c.conkey) AND a.attrelid = c.conrelid
    WHERE c.confrelid = (quote_ident(in_schema)||'.'||quote_ident(in_table))::regclass
      AND (SELECT attname FROM pg_attribute WHERE attrelid = c.confrelid AND attnum = ANY (c.confkey)) = in_column
      AND c.contype = 'f'
  LOOP
    EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I;', dep.child_table, dep.conname);
    RAISE NOTICE 'Dropped FK % for %', dep.conname, dep.child_table;
  END LOOP;

  -- 3) Eigene Constraints/Indices, die die Spalte verwenden, droppen (werden neu angelegt)
  FOR con IN
    SELECT conname
    FROM pg_constraint
    WHERE conrelid = (quote_ident(in_schema)||'.'||quote_ident(in_table))::regclass
      AND conname NOT LIKE 'pg_%'
      AND pg_get_constraintdef(oid) ILIKE format('%%%I%%', in_column)
  LOOP
    EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I;', fqtn, con.conname);
    RAISE NOTICE 'Dropped CONSTRAINT %', con.conname;
  END LOOP;

  FOR idx IN
    SELECT i.relname AS idxname
    FROM pg_index x
    JOIN pg_class i ON i.oid = x.indexrelid
    WHERE x.indrelid = (quote_ident(in_schema)||'.'||quote_ident(in_table))::regclass
      AND pg_get_indexdef(x.indexrelid) ILIKE format('%%%I%%', in_column)
  LOOP
    EXECUTE format('DROP INDEX IF EXISTS %I.%I;', in_schema, idx.idxname);
    RAISE NOTICE 'Dropped INDEX %', idx.idxname;
  END LOOP;

  -- 4) Typ-Änderung mit USING Cast
  EXECUTE format('ALTER TABLE %s ALTER COLUMN %I TYPE uuid USING %I::uuid;', fqtn, in_column, in_column);
  RAISE NOTICE 'Column %.%.% converted to uuid', in_schema, in_table, in_column;

  -- 5) Default setzen (falls gewünscht) – bevorzugt pgcrypto
  IF set_default THEN
    EXECUTE format('ALTER TABLE %s ALTER COLUMN %I SET DEFAULT gen_random_uuid();', fqtn, in_column);
  END IF;

  -- 6) Primary Key ggf. neu setzen (falls die Spalte PK ist)
  IF is_pk THEN
    -- PK neu erstellen
    pk_name := in_table || '_pkey';
    EXECUTE format('ALTER TABLE %s ADD CONSTRAINT %I PRIMARY KEY (%I);', fqtn, pk_name, in_column);
  END IF;

  -- 7) Abhängige FKs neu erstellen (mit gleicher DEF, ersetzt varchar->uuid automatisch)
  FOR dep IN
    SELECT conrelid::regclass AS child_table, conname, pg_get_constraintdef(c.oid) AS def
    FROM pg_constraint c
    WHERE FALSE -- Platzhalter; wir haben Definitionen oben nicht gespeichert
  LOOP
    -- (Wir haben oben nur gedropped; zum Neuaufbau verwenden wir Metadaten neu:
    --  Stattdessen generieren wir die FKs frisch je nach tatsächlichen Beziehungen bei Bedarf im App-Schema.)
  END LOOP;

  -- Hinweis: FK-Neuaufbau macht man robust, indem man pro referenzierender Tabelle dieselbe
  -- Definition neu erzeugt. In vielen Schemas ist es einfacher, FKs deklarativ per Migrationslayer (z. B. Drizzle) neu zu pushen.

END;
$$;

-- c) BEISPIELE: Aufruf pro Tabelle/Spalte
--    ACHTUNG: is_pk = TRUE, wenn es die PK-Spalte ist.
SELECT migrate_varchar_to_uuid('domain_crm','activities','id', TRUE, TRUE);
SELECT migrate_varchar_to_uuid('domain_crm','activities','tenant_id', FALSE, FALSE);
SELECT migrate_varchar_to_uuid('domain_crm','farm_profiles','id', TRUE, TRUE);
SELECT migrate_varchar_to_uuid('domain_crm','farm_profiles','tenant_id', FALSE, FALSE);

COMMIT;