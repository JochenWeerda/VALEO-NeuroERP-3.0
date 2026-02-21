-- Seed: Drying rule sets (sample defaults) for Landhandel drying loss & optional fees
-- Hinweis: Das ist bewusst ein STARTER-SET (konfigurierbar/erweiterbar).
-- Tenant: default

-- ── RuleSet: MAIS (Körnermais) - LOOKUP_TABLE, base 15.0 ─────────
INSERT INTO domain_inventory.drying_rule_sets (
  id, tenant_id, crop_code, site_id, valid_from, valid_to, version, is_active,
  method, base_moisture_pct, rounding_mode, clamp_mode, min_moisture_pct, max_moisture_pct,
  start_threshold_moisture_pct, fee_basis, created_at
) VALUES (
  'rs-maize-default', 'default', 'MAIZE', NULL, NULL, NULL, 1, TRUE,
  'LOOKUP_TABLE', 15.0, 'ROUND_NEAREST', 'HARD_ERROR', 0.0, 60.0,
  NULL, 'INVOICE_WEIGHT', NOW()
)
ON CONFLICT DO NOTHING;

-- Minimal-Beispielzeile aus Vorgabe:
-- moisture=20.0 -> entzug=5.0; loss_pct=6.75; invoice_weight(1000kg)=932.5kg
INSERT INTO domain_inventory.drying_rule_lookup_rows (
  id, rule_set_id, moisture_pct, entzug_pct_points, loss_pct, fee_value, fee_unit, created_at
) VALUES (
  'row-maize-20-0', 'rs-maize-default', 20.0, 5.0, 6.75, NULL, NULL, NOW()
)
ON CONFLICT DO NOTHING;

-- ── RuleSet: WEIZEN/GETREIDE - FACTOR_FROM_BASE (stufig), base 14.5 ─
INSERT INTO domain_inventory.drying_rule_sets (
  id, tenant_id, crop_code, site_id, valid_from, valid_to, version, is_active,
  method, base_moisture_pct, rounding_mode, clamp_mode, min_moisture_pct, max_moisture_pct,
  start_threshold_moisture_pct, fee_basis, created_at
) VALUES (
  'rs-wheat-default', 'default', 'WHEAT', NULL, NULL, NULL, 1, TRUE,
  'FACTOR_FROM_BASE', 14.5, 'ROUND_NEAREST', 'HARD_ERROR', 0.0, 60.0,
  15.1, 'INVOICE_WEIGHT', NOW()
)
ON CONFLICT DO NOTHING;

INSERT INTO domain_inventory.drying_rule_factor_ranges (
  id, rule_set_id, from_moisture_incl, to_moisture_incl, factor, created_at
) VALUES
  ('rng-wheat-15-1-19-4', 'rs-wheat-default', 15.1, 19.4, 1.3, NOW()),
  ('rng-wheat-19-5-29-9', 'rs-wheat-default', 19.5, 29.9, 1.4, NOW()),
  ('rng-wheat-30-0-99-9', 'rs-wheat-default', 30.0, 99.9, 1.5, NOW())
ON CONFLICT DO NOTHING;

-- GERSTE nutzt initial gleiche Defaults (separates crop_code, später unabhängig konfigurierbar)
INSERT INTO domain_inventory.drying_rule_sets (
  id, tenant_id, crop_code, site_id, valid_from, valid_to, version, is_active,
  method, base_moisture_pct, rounding_mode, clamp_mode, min_moisture_pct, max_moisture_pct,
  start_threshold_moisture_pct, fee_basis, created_at
) VALUES (
  'rs-barley-default', 'default', 'BARLEY', NULL, NULL, NULL, 1, TRUE,
  'FACTOR_FROM_BASE', 14.5, 'ROUND_NEAREST', 'HARD_ERROR', 0.0, 60.0,
  15.1, 'INVOICE_WEIGHT', NOW()
)
ON CONFLICT DO NOTHING;

INSERT INTO domain_inventory.drying_rule_factor_ranges (
  id, rule_set_id, from_moisture_incl, to_moisture_incl, factor, created_at
) VALUES
  ('rng-barley-15-1-19-4', 'rs-barley-default', 15.1, 19.4, 1.3, NOW()),
  ('rng-barley-19-5-29-9', 'rs-barley-default', 19.5, 29.9, 1.4, NOW()),
  ('rng-barley-30-0-99-9', 'rs-barley-default', 30.0, 99.9, 1.5, NOW())
ON CONFLICT DO NOTHING;

-- ── RuleSet: HAFER - FACTOR_FROM_BASE (stufig), base 14.0 ──────────
INSERT INTO domain_inventory.drying_rule_sets (
  id, tenant_id, crop_code, site_id, valid_from, valid_to, version, is_active,
  method, base_moisture_pct, rounding_mode, clamp_mode, min_moisture_pct, max_moisture_pct,
  start_threshold_moisture_pct, fee_basis, created_at
) VALUES (
  'rs-oats-default', 'default', 'OATS', NULL, NULL, NULL, 1, TRUE,
  'FACTOR_FROM_BASE', 14.0, 'ROUND_NEAREST', 'HARD_ERROR', 0.0, 60.0,
  14.1, 'INVOICE_WEIGHT', NOW()
)
ON CONFLICT DO NOTHING;

INSERT INTO domain_inventory.drying_rule_factor_ranges (
  id, rule_set_id, from_moisture_incl, to_moisture_incl, factor, created_at
) VALUES
  ('rng-oats-14-1-16-5', 'rs-oats-default', 14.1, 16.5, 1.3, NOW()),
  ('rng-oats-16-6-20-0', 'rs-oats-default', 16.6, 20.0, 1.4, NOW()),
  ('rng-oats-20-1-99-9', 'rs-oats-default', 20.1, 99.9, 1.5, NOW())
ON CONFLICT DO NOTHING;

-- ── RuleSet: RAPS - DRY_MATTER_NORMALIZATION, base 9.0 ─────────────
INSERT INTO domain_inventory.drying_rule_sets (
  id, tenant_id, crop_code, site_id, valid_from, valid_to, version, is_active,
  method, base_moisture_pct, rounding_mode, clamp_mode, min_moisture_pct, max_moisture_pct,
  start_threshold_moisture_pct, fee_basis, created_at
) VALUES (
  'rs-rapeseed-default', 'default', 'RAPESEED', NULL, NULL, NULL, 1, TRUE,
  'DRY_MATTER_NORMALIZATION', 9.0, 'ROUND_NEAREST', 'HARD_ERROR', 0.0, 60.0,
  NULL, 'INVOICE_WEIGHT', NOW()
)
ON CONFLICT DO NOTHING;

-- ── RuleSets: LEGUMINOSEN (Platzhalter: FACTOR_FROM_BASE, base 14.0) ─
INSERT INTO domain_inventory.drying_rule_sets (
  id, tenant_id, crop_code, site_id, valid_from, valid_to, version, is_active,
  method, base_moisture_pct, rounding_mode, clamp_mode, min_moisture_pct, max_moisture_pct,
  start_threshold_moisture_pct, fee_basis, created_at
) VALUES
  ('rs-field-beans-default', 'default', 'FIELD_BEANS', NULL, NULL, NULL, 1, TRUE, 'FACTOR_FROM_BASE', 14.0, 'ROUND_NEAREST', 'HARD_ERROR', 0.0, 60.0, 14.1, 'INVOICE_WEIGHT', NOW()),
  ('rs-peas-default',        'default', 'PEAS',       NULL, NULL, NULL, 1, TRUE, 'FACTOR_FROM_BASE', 14.0, 'ROUND_NEAREST', 'HARD_ERROR', 0.0, 60.0, 14.1, 'INVOICE_WEIGHT', NOW()),
  ('rs-lupins-default',      'default', 'LUPINS',     NULL, NULL, NULL, 1, TRUE, 'FACTOR_FROM_BASE', 14.0, 'ROUND_NEAREST', 'HARD_ERROR', 0.0, 60.0, 14.1, 'INVOICE_WEIGHT', NOW())
ON CONFLICT DO NOTHING;

INSERT INTO domain_inventory.drying_rule_factor_ranges (
  id, rule_set_id, from_moisture_incl, to_moisture_incl, factor, created_at
) VALUES
  ('rng-fb-14-1-19-9', 'rs-field-beans-default', 14.1, 19.9, 1.3, NOW()),
  ('rng-fb-20-0-99-9', 'rs-field-beans-default', 20.0, 99.9, 1.4, NOW()),
  ('rng-peas-14-1-19-9', 'rs-peas-default', 14.1, 19.9, 1.3, NOW()),
  ('rng-peas-20-0-99-9', 'rs-peas-default', 20.0, 99.9, 1.4, NOW()),
  ('rng-lupins-14-1-19-9', 'rs-lupins-default', 14.1, 19.9, 1.3, NOW()),
  ('rng-lupins-20-0-99-9', 'rs-lupins-default', 20.0, 99.9, 1.4, NOW())
ON CONFLICT DO NOTHING;



