-- Seed business partners using correct column names
INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name, customer_number, is_active, partner_type)
VALUES 
  ('11111111-1111-1111-1111-111111111111', '00000000-0000-0000-0000-000000000001', 'K-001', 'Müller Landwirtschaft GmbH', '10001', true, 'CUSTOMER'),
  ('22222222-2222-2222-2222-222222222222', '00000000-0000-0000-0000-000000000001', 'K-002', 'Schmidt Agrar OHG', '10002', true, 'CUSTOMER'),
  ('33333333-3333-3333-3333-333333333333', '00000000-0000-0000-0000-000000000001', 'L-001', 'BayWa Agrar GmbH', '20001', true, 'SUPPLIER'),
  ('44444444-4444-4444-4444-444444444444', '00000000-0000-0000-0000-000000000001', 'L-002', 'Raiffeisen Waren GmbH', '20002', true, 'SUPPLIER');

-- Seed warehouses
INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name, address, is_active)
VALUES 
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '00000000-0000-0000-0000-000000000001', 'MAIN', 'Hauptlager', '{"street": "Industriestraße 1", "postal_code": "12345", "city": "Berlin", "country": "DE"}', true),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '00000000-0000-0000-0000-000000000001', 'SILO1', 'Siloanlage Nord', '{"street": "Hafenstraße 10", "postal_code": "26789", "city": "Emden", "country": "DE"}', true);

-- Seed articles with correct schema
INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, category, unit, sales_price, current_stock, is_active)
VALUES 
  ('aaaa0000-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '00000000-0000-0000-0000-000000000001', 'A-001', 'Winterweizen (Saatgut)', 'SAATGUT', 'DT', 45.50, 150, true),
  ('aaaa0001-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '00000000-0000-0000-0000-000000000001', 'A-002', 'Raps (Saatgut)', 'SAATGUT', 'DT', 85.00, 80, true),
  ('aaaa0002-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '00000000-0000-0000-0000-000000000001', 'A-003', 'Stickstoffdünger 46%', 'DUENGER', 'DT', 32.00, 200, true),
  ('aaaa0003-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '00000000-0000-0000-0000-000000000001', 'A-004', 'Phosphordünger', 'DUENGER', 'DT', 48.00, 120, true),
  ('aaaa0004-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '00000000-0000-0000-0000-000000000001', 'A-005', 'PSM Fungizid', 'PFLANZENSCHUTZ', 'L', 125.00, 50, true);
