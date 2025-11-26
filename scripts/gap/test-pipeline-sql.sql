-- Test-Script für GAP-Pipeline (vereinfacht, direkt über SQL)
-- Führt die Pipeline-Schritte manuell aus, um die Logik zu testen

-- Schritt 1: Test-Import (manuell ein paar Zeilen)
-- In Produktion würde das über das TypeScript-Script laufen
INSERT INTO gap_payments (
  ref_year,
  data_source,
  member_state,
  region_code,
  region_name,
  beneficiary_name_raw,
  beneficiary_name_norm,
  postal_code,
  city,
  measure_code,
  amount_egfl,
  amount_total,
  load_batch_id
) VALUES
  (2024, 'test', 'DE', NULL, NULL, 'Test Betrieb 1', 'test betrieb 1', '12345', 'Teststadt', 'I.1', 1000.00, 1000.00, gen_random_uuid()),
  (2024, 'test', 'DE', NULL, NULL, 'Test Betrieb 2', 'test betrieb 2', '54321', 'Musterstadt', 'I.2', 2000.00, 2000.00, gen_random_uuid())
ON CONFLICT DO NOTHING;

-- Schritt 2: Prüfe ob View existiert (wird von aggregate.ts verwendet)
-- Wenn nicht, erstelle eine einfache View
CREATE OR REPLACE VIEW gap_payments_direct_agg AS
SELECT
  ref_year,
  beneficiary_name_norm,
  postal_code,
  city,
  SUM(COALESCE(amount_egfl, 0)) as direct_total_eur
FROM gap_payments
WHERE measure_code IN ('I.1', 'I.2', 'I.3')  -- Direktzahlungen
GROUP BY ref_year, beneficiary_name_norm, postal_code, city;

-- Schritt 3: Test-Aggregation
SELECT
  COUNT(*)::text AS cnt,
  COALESCE(SUM(direct_total_eur), 0)::text AS sum
FROM gap_payments_direct_agg
WHERE ref_year = 2024;

-- Schritt 4: Test-Matching (wenn customers vorhanden)
-- Erstelle Test-Kunden falls nicht vorhanden
INSERT INTO customers (name, postal_code, city, status)
SELECT 'Test Betrieb 1', '12345', 'Teststadt', 'active'
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = 'Test Betrieb 1' AND postal_code = '12345')
ON CONFLICT DO NOTHING;

-- Schritt 5: Test-Snapshot (vereinfacht)
-- In Produktion würde das über snapshot.ts laufen
DELETE FROM customer_potential_snapshot WHERE ref_year = 2024;

INSERT INTO customer_potential_snapshot (
  ref_year,
  customer_id,
  gap_direct_total_eur,
  gap_estimated_area_ha,
  potential_seed_eur,
  potential_fertilizer_eur,
  potential_psm_eur,
  potential_total_eur,
  segment
)
SELECT
  2024,
  c.id,
  COALESCE(agg.direct_total_eur, 0),
  CASE WHEN COALESCE(agg.direct_total_eur, 0) > 0 THEN COALESCE(agg.direct_total_eur, 0) / 270 ELSE 0 END,
  CASE WHEN COALESCE(agg.direct_total_eur, 0) > 0 THEN (COALESCE(agg.direct_total_eur, 0) / 270) * 50 ELSE 0 END,
  CASE WHEN COALESCE(agg.direct_total_eur, 0) > 0 THEN (COALESCE(agg.direct_total_eur, 0) / 270) * 150 ELSE 0 END,
  CASE WHEN COALESCE(agg.direct_total_eur, 0) > 0 THEN (COALESCE(agg.direct_total_eur, 0) / 270) * 80 ELSE 0 END,
  CASE WHEN COALESCE(agg.direct_total_eur, 0) > 0 THEN (COALESCE(agg.direct_total_eur, 0) / 270) * 280 ELSE 0 END,
  'A'
FROM customers c
LEFT JOIN gap_payments_direct_agg agg ON 
  LOWER(TRIM(c.name)) = LOWER(TRIM(agg.beneficiary_name_norm))
  AND c.postal_code = agg.postal_code
  AND c.city = agg.city
WHERE agg.ref_year = 2024
  AND c.status = 'active'
LIMIT 10;

-- Schritt 6: Status prüfen
SELECT
  'gap_payments' as table_name,
  COUNT(*) as count
FROM gap_payments
WHERE ref_year = 2024
UNION ALL
SELECT
  'customer_potential_snapshot' as table_name,
  COUNT(*) as count
FROM customer_potential_snapshot
WHERE ref_year = 2024;

