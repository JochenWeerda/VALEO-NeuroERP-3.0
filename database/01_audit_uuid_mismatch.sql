-- 1) Übersicht: Spalten, die vermutlich UUID sein sollten, aber varchar/text sind
--    Heuristik: Name endet auf id / enthält _id, Typ = varchar/text, Länge <= 36
WITH candidates AS (
  SELECT
    n.nspname  AS schema_name,
    c.relname  AS table_name,
    a.attname  AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type
  FROM pg_attribute a
  JOIN pg_class     c ON c.oid = a.attrelid
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE a.attnum > 0 AND NOT a.attisdropped
    AND c.relkind IN ('r','p')
    AND pg_catalog.format_type(a.atttypid, a.atttypmod) IN ('character varying', 'text')
    AND (a.attname ~* '(^id$|_id$)')
)
SELECT
  schema_name, table_name, column_name, data_type,
  -- Anzahl Zeilen, die wie UUID aussehen (Regex)
  SUM( CASE WHEN (t."val" ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$') THEN 1 ELSE 0 END ) AS uuid_like_rows,
  COUNT(*) AS total_rows,
  COUNT(*) - SUM( CASE WHEN (t."val" ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$') THEN 1 ELSE 0 END ) AS invalid_rows
FROM candidates cand
JOIN LATERAL (
  EXECUTE FORMAT('SELECT %I::text AS val FROM %I.%I', cand.column_name, cand.schema_name, cand.table_name)
) t ON TRUE
GROUP BY schema_name, table_name, column_name, data_type
ORDER BY invalid_rows DESC, schema_name, table_name;