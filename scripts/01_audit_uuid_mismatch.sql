-- UUID-Mismatch Audit: Finde VARCHAR-Spalten die UUID sein sollten
SELECT
  n.nspname  AS schema_name,
  c.relname  AS table_name,
  a.attname  AS column_name,
  pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
  CASE 
    WHEN a.attnotnull THEN 'NOT NULL'
    ELSE 'NULL'
  END AS nullable,
  CASE
    WHEN pk.contype = 'p' THEN 'PRIMARY KEY'
    WHEN fk.contype = 'f' THEN 'FOREIGN KEY'
    ELSE ''
  END AS constraint_type
FROM pg_attribute a
JOIN pg_class     c ON c.oid = a.attrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_constraint pk ON pk.conrelid = c.oid AND a.attnum = ANY(pk.conkey) AND pk.contype = 'p'
LEFT JOIN pg_constraint fk ON fk.conrelid = c.oid AND a.attnum = ANY(fk.conkey) AND fk.contype = 'f'
WHERE a.attnum > 0 
  AND NOT a.attisdropped
  AND c.relkind IN ('r','p')
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND pg_catalog.format_type(a.atttypid, a.atttypmod) IN ('character varying', 'text')
  AND (a.attname ~* '(^id$|_id$)')
ORDER BY n.nspname, c.relname, a.attname;

