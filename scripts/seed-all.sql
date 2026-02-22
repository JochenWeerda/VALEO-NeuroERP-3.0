-- =================================================================
-- VALEO NeuroERP 3.0 - Consolidated Seed Script
-- Compatible with SQLAlchemy model schema (post UUID v7 migration)
-- =================================================================
-- Run: docker exec -i valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp < scripts/seed-all.sql

SET client_min_messages TO WARNING;

-- ============================================
-- 0. SCHEMAS
-- ============================================
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_erp;
CREATE SCHEMA IF NOT EXISTS domain_finance;
CREATE SCHEMA IF NOT EXISTS domain_ops;
CREATE SCHEMA IF NOT EXISTS domain_portal;
CREATE SCHEMA IF NOT EXISTS domain_log;
CREATE SCHEMA IF NOT EXISTS domain_agrar;

-- ============================================
-- 1. TENANT
-- ============================================
INSERT INTO domain_shared.tenants (id, name, domain, is_active)
VALUES ('00000000-0000-0000-0000-000000000001', 'Default Tenant', 'default.local', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 2. BRANCHES
-- ============================================
INSERT INTO domain_shared.branches (id, tenant_id, branch_number, name, address, is_active)
VALUES
    ('019c0000-0000-7000-8000-000000000001', '00000000-0000-0000-0000-000000000001', 1, 'Hauptwerk Oldenburg', '{"street":"Industriestr. 10","zip":"26121","city":"Oldenburg"}', true),
    ('019c0000-0000-7000-8000-000000000002', '00000000-0000-0000-0000-000000000001', 2, 'Zweigstelle Cloppenburg', '{"street":"Am Markt 3","zip":"49661","city":"Cloppenburg"}', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 3. BUSINESS PARTNERS (4)
-- ============================================
INSERT INTO domain_crm.business_partners (
    partner_id, tenant_id, partner_number, name_1, city, country, status,
    is_customer, is_supplier, is_carrier, is_employee, is_service_provider,
    blocked_for_delivery, blocked_for_invoice, bio_certified,
    email_opt_in, sms_opt_in, whatsapp_opt_in, newsletter_opt_in, flyer_subscription,
    privacy_policy_accepted, data_processing_agreement_signed,
    bank_connection_active, wants_account_statement, print_balance_on_invoice,
    invoice_print_blocked, delivery_note_print_blocked, calculate_shipping_flat,
    self_billing_customer, auto_offset_enabled, post_open_items_blocked,
    market_price_evaluation, webshop_customer, fax_blocked, proforma_invoice,
    membership_terminated, customer_card_flag,
    edifact_invoic, edifact_orders, edifact_desadv
) VALUES
('BP-001','00000000-0000-0000-0000-000000000001','BP-10001','Landwirt Heinrich Müller','Oldenburg','DE','active',
 true,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false),
('BP-002','00000000-0000-0000-0000-000000000001','BP-10002','Hof Janssen GbR','Cloppenburg','DE','active',
 true,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false),
('BP-003','00000000-0000-0000-0000-000000000001','BP-10003','Agrargenossenschaft Wesermarsch','Brake','DE','active',
 true,true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false),
('BP-004','00000000-0000-0000-0000-000000000001','BP-10004','Oelmuehle Nordwest GmbH','Bremen','DE','active',
 true,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false)
ON CONFLICT (partner_id) DO NOTHING;

-- ============================================
-- 4. CUSTOMERS (3)
-- ============================================
INSERT INTO domain_crm.customers (id, customer_number, company_name, tenant_id, is_active)
VALUES
    ('019c0008-0000-7000-8000-000000000001', 'KD-10001', 'Landwirt Heinrich Mueller', '00000000-0000-0000-0000-000000000001', true),
    ('019c0008-0000-7000-8000-000000000002', 'KD-10002', 'Hof Janssen GbR', '00000000-0000-0000-0000-000000000001', true),
    ('019c0008-0000-7000-8000-000000000003', 'KD-10003', 'Agrargenossenschaft Wesermarsch', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 5. ARTICLES (12 base)
-- ============================================
INSERT INTO domain_inventory.articles (
    id, article_number, name, description, suchbegriff, hersteller, warengruppe,
    lagerartikel, mehrwertsteuer_prozent, ean_code, unit, category, sales_price,
    tenant_id, is_active, mhd_erforderlich, lagerorte, chargenpflicht,
    qs_pruefung_erforderlich, bio_kennzeichnung, gmp_plus_relevanz
) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567890','ART-001','Weizen Tierfutter Weizenschrot Klasse A','Hochwertiges Tierfutter','Weizen','BayWa AG','Futtermittel',true,19.0,'4006381333931','T','Futtermittel',245.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('b2c3d4e5-f6a7-8901-bcde-f12345678901','ART-002','Rapssaatgut Defender','Winterraps-Saatgut 50kg','Raps','Bayer CropScience','Saatgut',true,19.0,'4012345678901','SAC','Saatgut',189.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('c3d4e5f6-a7b8-9012-cdef-123456789012','ART-003','NPK-Duenger 20-10-10','Universeller NPK-Duenger 25kg','Duenger','Compo Expert','Duenger',true,19.0,'4021234567890','SAC','Duenger',45.50,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('d4e5f6a7-b8c9-0123-def0-234567890123','ART-004','Glyphosat RoundUp Ultra','Totalherbizid 5L','Glyphosat','Monsanto','Pflanzenschutz',true,19.0,'4031234567890','KAN','Pflanzenschutz',89.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('e5f6a7b8-c9d0-1234-ef01-345678901234','ART-005','Stallmist Kompost','Organischer Stallmist-Kompost 1000kg','Kompost','Regional','Organisch',true,19.0,'4041234567890','BBL','Organisch',120.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('f6a7b8c9-d0e1-2345-f012-456789012345','ART-006','Kalkstickstoff 46','Kalkstickstoff 25kg','Kalk','AlzChem','Duenger',true,19.0,'4051234567890','SAC','Duenger',38.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('a7b8c9d0-e1f2-3456-0123-567890123456','ART-007','Mais Saatgut Maximus','Silomais 50000 Koerner','Mais','KWS','Saatgut',true,19.0,'4061234567890','KRT','Saatgut',285.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('b8c9d0e1-f2a3-4567-1234-678901234567','ART-008','Methylobacterium','Biostimulanz 1L','Bio','Syngenta','Biostimulanzien',true,19.0,'4071234567890','FLA','Biostimulanzien',156.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('c9d0e1f2-a3b4-5678-2345-789012345678','ART-009','Gerste Braugerste','Braugerste Qualitaetsklasse I','Gerste','Volverde','Getreide',true,19.0,'4081234567890','T','Getreide',195.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('d0e1f2a3-b4c5-6789-3456-890123456789','ART-010','Ackerbohnen Saatgut','Ackerbohnen 50kg','Bohnen','Pioneer','Saatgut',true,19.0,'4091234567890','SAC','Saatgut',165.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('e1f2a3b4-c5d6-7890-4567-901234567890','ART-011','Kartoffel-Duenger NPK 15-15-15','Spezialduenger 25kg','Kartoffel','K+S','Duenger',true,19.0,'4101234567890','SAC','Duenger',52.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false),
('f2a3b4c5-d6e7-8901-5678-012345678901','ART-012','Winterweizen Saatgut Ponticus','Winterweizen 500kg','Weizen','RAGT','Saatgut',true,19.0,'4111234567890','SAC','Saatgut',320.00,'00000000-0000-0000-0000-000000000001',true,false,'[]',false,false,false,false)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 6. WAREHOUSES (2)
-- ============================================
INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, address, city, postal_code, tenant_id, is_active)
VALUES
    ('019c0010-0000-7000-8000-000000000001', 'WH-MAIN', 'Hauptlager Oldenburg', 'Industriestr. 10', 'Oldenburg', '26121', '00000000-0000-0000-0000-000000000001', true),
    ('019c0010-0000-7000-8000-000000000002', 'WH-CLP', 'Aussenlager Cloppenburg', 'Am Markt 3', 'Cloppenburg', '49661', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 7. SILOS (4)
-- ============================================
INSERT INTO domain_inventory.silos (id, silo_number, name, article_id, capacity_tons, tenant_id, is_active)
VALUES
    ('019c0006-0000-7000-8000-000000000001', 'S001', 'Silo Weizen Nord', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 500.000, '00000000-0000-0000-0000-000000000001', true),
    ('019c0006-0000-7000-8000-000000000002', 'S002', 'Silo Weizen Sued', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 500.000, '00000000-0000-0000-0000-000000000001', true),
    ('019c0006-0000-7000-8000-000000000003', 'S003', 'Silo Raps', 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 300.000, '00000000-0000-0000-0000-000000000001', true),
    ('019c0006-0000-7000-8000-000000000004', 'S004', 'Silo Gerste', 'c9d0e1f2-a3b4-5678-2345-789012345678', 400.000, '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 8. AGRAR CONTRACTS (3)
-- ============================================
INSERT INTO domain_inventory.agrar_contracts (id, contract_number, contract_type, harvest_year, partner_id, article_id, pricing_model, fixed_price, currency, total_quantity_kg, remaining_quantity_kg, status, valid_from, valid_until, tenant_id)
VALUES
    ('019c0004-0000-7000-8000-000000000001', 'KT-2026-001', 'buy', 2026, 'BP-001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'fixed', 245.00, 'EUR', 100000.000, 75000.000, 'partially_allocated', '2026-01-01', '2026-12-31', '00000000-0000-0000-0000-000000000001'),
    ('019c0004-0000-7000-8000-000000000002', 'KT-2026-002', 'buy', 2026, 'BP-002', 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 'follow', NULL, 'EUR', 50000.000, 50000.000, 'open', '2026-01-01', '2026-12-31', '00000000-0000-0000-0000-000000000001'),
    ('019c0004-0000-7000-8000-000000000003', 'KT-2026-003', 'buy', 2026, 'BP-003', 'c9d0e1f2-a3b4-5678-2345-789012345678', 'pool', NULL, 'EUR', 80000.000, 80000.000, 'open', '2026-03-01', '2026-11-30', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 9. WEIGHING TICKETS (5)
-- ============================================
INSERT INTO domain_inventory.weighing_tickets (id, ticket_number, scale_id, vehicle_plate, gross_weight, tare_weight, net_weight, first_weighing_at, second_weighing_at, moisture_pct, protein_pct, impurities_pct, hl_weight, billing_weight, weighing_date, status, direction, tenant_id)
VALUES
    ('019c0005-0000-7000-8000-000000000001', 'WG-2026-00001', 'WAAGE-01', 'OL-AB 1234', 42500.000, 17200.000, 25300.000, '2026-01-15 08:12:00', '2026-01-15 08:45:00', 14.2, 12.8, 1.1, 78.5, 25000.000, '2026-01-15 08:12:00', 'closed', 'in', '00000000-0000-0000-0000-000000000001'),
    ('019c0005-0000-7000-8000-000000000002', 'WG-2026-00002', 'WAAGE-01', 'CLP-CD 5678', 38700.000, 16800.000, 21900.000, '2026-01-18 10:30:00', '2026-01-18 11:05:00', 13.8, 11.5, 0.8, 79.1, 21900.000, '2026-01-18 10:30:00', 'closed', 'out', '00000000-0000-0000-0000-000000000001'),
    ('019c0005-0000-7000-8000-000000000003', 'WG-2026-00003', 'WAAGE-02', 'VEC-EF 9012', 35200.000, 15600.000, 19600.000, '2026-02-10 07:45:00', '2026-02-10 08:20:00', 15.1, 10.2, 1.5, 66.8, 19200.000, '2026-02-10 07:45:00', 'closed', 'in', '00000000-0000-0000-0000-000000000001'),
    ('019c0005-0000-7000-8000-000000000004', 'WG-2026-00004', 'WAAGE-01', 'OL-GH 3456', 44100.000, 17500.000, 26600.000, '2026-02-15 09:00:00', '2026-02-15 09:35:00', 13.5, 13.1, 0.6, 80.2, 26600.000, '2026-02-15 09:00:00', 'open', 'in', '00000000-0000-0000-0000-000000000001'),
    ('019c0005-0000-7000-8000-000000000005', 'WG-2026-00005', 'WAAGE-02', 'CLP-IJ 7890', 31500.000, 14200.000, 17300.000, '2026-02-18 14:20:00', NULL, NULL, NULL, NULL, NULL, NULL, '2026-02-18 14:20:00', 'open', 'in', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 10. SILO LOTS (3)
-- ============================================
INSERT INTO domain_inventory.silo_lots (id, silo_id, virtual_lot_number, source_ticket_id, source_partner_id, article_id, quantity_tons, moisture_pct, protein_pct, impurities_pct, hl_weight, status, tenant_id)
VALUES
    ('019c0007-0000-7000-8000-000000000001', '019c0006-0000-7000-8000-000000000001', 'LOT-2026-S001-001', '019c0005-0000-7000-8000-000000000001', 'BP-001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 25.000, 14.2, 12.8, 1.1, 78.5, 'active', '00000000-0000-0000-0000-000000000001'),
    ('019c0007-0000-7000-8000-000000000002', '019c0006-0000-7000-8000-000000000001', 'LOT-2026-S001-002', '019c0005-0000-7000-8000-000000000004', 'BP-002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 26.600, 13.5, 13.1, 0.6, 80.2, 'active', '00000000-0000-0000-0000-000000000001'),
    ('019c0007-0000-7000-8000-000000000003', '019c0006-0000-7000-8000-000000000004', 'LOT-2026-S004-001', '019c0005-0000-7000-8000-000000000003', 'BP-003', 'c9d0e1f2-a3b4-5678-2345-789012345678', 19.200, 15.1, 10.2, 1.5, 66.8, 'active', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 11. FINANCE: Kontenrahmen (12 Konten)
-- ============================================
INSERT INTO domain_erp.finance_accounts (id, account_number, account_name, account_type, category, subcategory, description, tenant_id, is_active, balance)
VALUES
    ('019c0001-0000-7000-8000-000000000001', '1000', 'Kasse', 'asset', 'current_assets', 'Liquide Mittel', 'Barkasse Hauptwerk', '00000000-0000-0000-0000-000000000001', true, 5230.00),
    ('019c0001-0000-7000-8000-000000000002', '1200', 'Bank Volksbank', 'asset', 'current_assets', 'Liquide Mittel', 'Girokonto Volksbank', '00000000-0000-0000-0000-000000000001', true, 182450.00),
    ('019c0001-0000-7000-8000-000000000003', '1400', 'Forderungen aus L+L', 'asset', 'current_assets', 'Forderungen', 'Forderungen aus Lieferungen und Leistungen', '00000000-0000-0000-0000-000000000001', true, 45600.00),
    ('019c0001-0000-7000-8000-000000000004', '1600', 'Vorsteuer', 'asset', 'current_assets', 'Steuerforderungen', 'Vorsteuer 19%', '00000000-0000-0000-0000-000000000001', true, 8640.00),
    ('019c0001-0000-7000-8000-000000000005', '3300', 'Verbindlichkeiten aus L+L', 'liability', 'current_liabilities', 'Lieferanten', 'Verbindlichkeiten ggue. Lieferanten', '00000000-0000-0000-0000-000000000001', true, 67200.00),
    ('019c0001-0000-7000-8000-000000000006', '3800', 'Umsatzsteuer', 'liability', 'current_liabilities', 'Steuerverbindlichkeiten', 'USt 19%', '00000000-0000-0000-0000-000000000001', true, 12340.00),
    ('019c0001-0000-7000-8000-000000000007', '4400', 'Erloese 19% USt', 'revenue', 'revenue', 'Warenverkauf', 'Erloese aus Warenverkauf 19%', '00000000-0000-0000-0000-000000000001', true, 256800.00),
    ('019c0001-0000-7000-8000-000000000008', '4300', 'Erloese 7% USt', 'revenue', 'revenue', 'Warenverkauf', 'Erloese aus Warenverkauf 7%', '00000000-0000-0000-0000-000000000001', true, 89400.00),
    ('019c0001-0000-7000-8000-000000000009', '5200', 'Wareneingang', 'expense', 'cost_of_goods_sold', 'Wareneinkauf', 'Wareneinkauf / Wareneingang', '00000000-0000-0000-0000-000000000001', true, 189500.00),
    ('019c0001-0000-7000-8000-000000000010', '5400', 'Betriebsstoffe', 'expense', 'cost_of_goods_sold', 'Hilfs-/Betriebsstoffe', 'Betriebsstoffe und Verpackung', '00000000-0000-0000-0000-000000000001', true, 12300.00),
    ('019c0001-0000-7000-8000-000000000011', '6300', 'Personalkosten', 'expense', 'operating_expenses', 'Loehne', 'Personalkosten Loehne und Gehaelter', '00000000-0000-0000-0000-000000000001', true, 78900.00),
    ('019c0001-0000-7000-8000-000000000012', '6800', 'Abschreibungen', 'expense', 'operating_expenses', 'AfA', 'Planmaessige Abschreibungen', '00000000-0000-0000-0000-000000000001', true, 24500.00)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 12. FINANCE: Journal Entries (5)
-- ============================================
INSERT INTO domain_erp.finance_journal_entries (id, entry_number, entry_date, posting_date, description, reference, source, status, total_debit, total_credit, tenant_id)
VALUES
    ('019c0002-0000-7000-8000-000000000001', 'BU-2026-0001', '2026-01-15', '2026-01-15', 'Wareneingang Weizen 25t', 'WG-2026-00001', 'procurement', 'posted', 6125.00, 6125.00, '00000000-0000-0000-0000-000000000001'),
    ('019c0002-0000-7000-8000-000000000002', 'BU-2026-0002', '2026-01-18', '2026-01-18', 'Verkauf Raps 10t', 'LS-2026-00001', 'sales', 'posted', 4200.00, 4200.00, '00000000-0000-0000-0000-000000000001'),
    ('019c0002-0000-7000-8000-000000000003', 'BU-2026-0003', '2026-01-22', '2026-01-22', 'Zahlung Lieferant Mueller', 'ZA-2026-00001', 'payment', 'posted', 3500.00, 3500.00, '00000000-0000-0000-0000-000000000001'),
    ('019c0002-0000-7000-8000-000000000004', 'BU-2026-0004', '2026-02-01', '2026-02-01', 'Duengemittel-Einkauf NPK', 'BE-2026-00001', 'procurement', 'posted', 8950.00, 8950.00, '00000000-0000-0000-0000-000000000001'),
    ('019c0002-0000-7000-8000-000000000005', 'BU-2026-0005', '2026-02-10', '2026-02-10', 'Wareneingang Gerste 15t', 'WG-2026-00003', 'procurement', 'draft', 3675.00, 3675.00, '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- Journal Entry Lines
INSERT INTO domain_erp.finance_journal_entry_lines (id, journal_entry_id, account_id, debit, credit, description)
VALUES
    ('019c0003-0000-7000-8000-000000000001', '019c0002-0000-7000-8000-000000000001', '019c0001-0000-7000-8000-000000000009', 6125.00, 0, 'Wareneingang Weizen 25t'),
    ('019c0003-0000-7000-8000-000000000002', '019c0002-0000-7000-8000-000000000001', '019c0001-0000-7000-8000-000000000005', 0, 6125.00, 'Verbindlichkeit Lieferant'),
    ('019c0003-0000-7000-8000-000000000003', '019c0002-0000-7000-8000-000000000002', '019c0001-0000-7000-8000-000000000003', 4200.00, 0, 'Forderung Oelmuehle'),
    ('019c0003-0000-7000-8000-000000000004', '019c0002-0000-7000-8000-000000000002', '019c0001-0000-7000-8000-000000000007', 0, 4200.00, 'Erloese Raps 10t'),
    ('019c0003-0000-7000-8000-000000000005', '019c0002-0000-7000-8000-000000000003', '019c0001-0000-7000-8000-000000000005', 3500.00, 0, 'Verbindlichkeit Mueller ausgeglichen'),
    ('019c0003-0000-7000-8000-000000000006', '019c0002-0000-7000-8000-000000000003', '019c0001-0000-7000-8000-000000000002', 0, 3500.00, 'Bankabbuchung'),
    ('019c0003-0000-7000-8000-000000000007', '019c0002-0000-7000-8000-000000000004', '019c0001-0000-7000-8000-000000000009', 7521.01, 0, 'Wareneingang NPK'),
    ('019c0003-0000-7000-8000-000000000008', '019c0002-0000-7000-8000-000000000004', '019c0001-0000-7000-8000-000000000004', 1428.99, 0, 'Vorsteuer 19%'),
    ('019c0003-0000-7000-8000-000000000009', '019c0002-0000-7000-8000-000000000004', '019c0001-0000-7000-8000-000000000005', 0, 8950.00, 'Verbindlichkeit Compo Expert'),
    ('019c0003-0000-7000-8000-000000000010', '019c0002-0000-7000-8000-000000000005', '019c0001-0000-7000-8000-000000000009', 3675.00, 0, 'Wareneingang Gerste 15t'),
    ('019c0003-0000-7000-8000-000000000011', '019c0002-0000-7000-8000-000000000005', '019c0001-0000-7000-8000-000000000005', 0, 3675.00, 'Verbindlichkeit Lieferant')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 13. HARVEST ACCEPTANCES (3)
-- ============================================
INSERT INTO domain_inventory.harvest_acceptances (id, acceptance_number, tenant_id, branch_id, delivery_date, delivery_time, operator_id, weighing_ticket_id, customer_id, contract_id, article_id, variety_id, vehicle_plate, origin_nuts2_code, origin_country_code, is_sustainable_biomass, release_status, pricing_mode, print_remarks_on_acceptance_note, print_remarks_on_settlement, total_net_amount_eur, total_vat_amount_eur, total_gross_amount_eur, vat_rate_percent, acceptance_mode, ownership_type)
VALUES
    ('019c0009-0000-7000-8000-000000000001', 'EA-2026-0001', '00000000-0000-0000-0000-000000000001', '019c0000-0000-7000-8000-000000000001', '2026-01-15', '08:45', 'operator-001', '019c0005-0000-7000-8000-000000000001', '019c0008-0000-7000-8000-000000000001', '019c0004-0000-7000-8000-000000000001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Ponticus', 'OL-AB 1234', 'DE93', 'DE', false, 'released', 'contract', false, false, 6125.00, 1163.75, 7288.75, 19.00, 'PURCHASE_AT_DELIVERY_PTBF', 'OWN_STOCK'),
    ('019c0009-0000-7000-8000-000000000002', 'EA-2026-0002', '00000000-0000-0000-0000-000000000001', '019c0000-0000-7000-8000-000000000001', '2026-02-10', '08:20', 'operator-001', '019c0005-0000-7000-8000-000000000003', '019c0008-0000-7000-8000-000000000002', NULL, 'c9d0e1f2-a3b4-5678-2345-789012345678', 'Meridian', 'VEC-EF 9012', 'DE94', 'DE', false, 'released', 'spot_daily', false, false, 3675.00, 698.25, 4373.25, 19.00, 'PURCHASE_AT_DELIVERY_PTBF', 'OWN_STOCK'),
    ('019c0009-0000-7000-8000-000000000003', 'EA-2026-0003', '00000000-0000-0000-0000-000000000001', '019c0000-0000-7000-8000-000000000002', '2026-02-15', '09:35', 'operator-002', '019c0005-0000-7000-8000-000000000004', '019c0008-0000-7000-8000-000000000003', '019c0004-0000-7000-8000-000000000001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Benchmark', 'OL-GH 3456', 'DE93', 'DE', false, 'draft', 'contract', false, false, NULL, NULL, NULL, 19.00, 'PURCHASE_AT_DELIVERY_PTBF', 'OWN_STOCK')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
DECLARE cnt INTEGER;
BEGIN
    RAISE NOTICE '=== SEED VERIFICATION ===';
    SELECT COUNT(*) INTO cnt FROM domain_shared.tenants; RAISE NOTICE 'Tenants: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_shared.branches; RAISE NOTICE 'Branches: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_crm.business_partners; RAISE NOTICE 'Business Partners: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_crm.customers; RAISE NOTICE 'Customers: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.articles; RAISE NOTICE 'Articles: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.warehouses; RAISE NOTICE 'Warehouses: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.silos; RAISE NOTICE 'Silos: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.agrar_contracts; RAISE NOTICE 'Agrar Contracts: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.weighing_tickets; RAISE NOTICE 'Weighing Tickets: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.silo_lots; RAISE NOTICE 'Silo Lots: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_erp.finance_accounts; RAISE NOTICE 'Finance Accounts: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_erp.finance_journal_entries; RAISE NOTICE 'Journal Entries: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_erp.finance_journal_entry_lines; RAISE NOTICE 'Journal Lines: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.harvest_acceptances; RAISE NOTICE 'Harvest Acceptances: %', cnt;
    RAISE NOTICE '=== SEED COMPLETE ===';
END $$;
