-- =================================================================
-- VALEO NeuroERP 3.0 - Full Testdata Seed
-- Finance, Agrar-Kontrakte, Wiegungen, Silo-Lots, Ernte-Annahme
-- =================================================================
-- Run: docker exec -i valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp < scripts/seed-full-testdata.sql

SET client_min_messages TO WARNING;

-- Ensure schemas exist
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_erp;
CREATE SCHEMA IF NOT EXISTS domain_finance;

-- ============================================
-- 0. PREREQUISITES: Tenant + Branches
-- ============================================
INSERT INTO domain_shared.tenants (id, name, domain, is_active)
VALUES ('00000000-0000-0000-0000-000000000001', 'Default Tenant', 'default.local', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_shared.branches (id, tenant_id, branch_number, name, address, is_active)
VALUES
    ('019c0000-0000-7000-8000-000000000001', '00000000-0000-0000-0000-000000000001', 1, 'Hauptwerk Oldenburg', '{"street":"Industriestr. 10","zip":"26121","city":"Oldenburg"}', true),
    ('019c0000-0000-7000-8000-000000000002', '00000000-0000-0000-0000-000000000001', 2, 'Zweigstelle Cloppenburg', '{"street":"Am Markt 3","zip":"49661","city":"Cloppenburg"}', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 1. FINANCE: Kontenrahmen (Chart of Accounts)
-- ============================================
INSERT INTO domain_erp.finance_accounts (id, account_number, account_name, account_type, category, subcategory, description, tenant_id, is_active, balance)
VALUES
    -- Aktiva
    ('019c0001-0000-7000-8000-000000000001', '1000', 'Kasse', 'asset', 'Umlaufvermögen', 'Liquide Mittel', 'Barkasse Hauptwerk', '00000000-0000-0000-0000-000000000001', true, 5230.00),
    ('019c0001-0000-7000-8000-000000000002', '1200', 'Bank Volksbank', 'asset', 'Umlaufvermögen', 'Liquide Mittel', 'Girokonto Volksbank', '00000000-0000-0000-0000-000000000001', true, 182450.00),
    ('019c0001-0000-7000-8000-000000000003', '1400', 'Forderungen aus L+L', 'asset', 'Umlaufvermögen', 'Forderungen', 'Forderungen aus Lieferungen und Leistungen', '00000000-0000-0000-0000-000000000001', true, 45600.00),
    ('019c0001-0000-7000-8000-000000000004', '1600', 'Vorsteuer', 'asset', 'Umlaufvermögen', 'Steuerforderungen', 'Vorsteuer 19%', '00000000-0000-0000-0000-000000000001', true, 8640.00),
    -- Passiva
    ('019c0001-0000-7000-8000-000000000005', '3300', 'Verbindlichkeiten aus L+L', 'liability', 'Kurzfristige Verbindlichkeiten', 'Lieferanten', 'Verbindlichkeiten ggü. Lieferanten', '00000000-0000-0000-0000-000000000001', true, 67200.00),
    ('019c0001-0000-7000-8000-000000000006', '3800', 'Umsatzsteuer', 'liability', 'Kurzfristige Verbindlichkeiten', 'Steuerverbindlichkeiten', 'USt 19%', '00000000-0000-0000-0000-000000000001', true, 12340.00),
    -- Erlöse
    ('019c0001-0000-7000-8000-000000000007', '4400', 'Erlöse 19% USt', 'revenue', 'Umsatzerlöse', 'Warenverkauf', 'Erlöse aus Warenverkauf 19%', '00000000-0000-0000-0000-000000000001', true, 256800.00),
    ('019c0001-0000-7000-8000-000000000008', '4300', 'Erlöse 7% USt', 'revenue', 'Umsatzerlöse', 'Warenverkauf', 'Erlöse aus Warenverkauf 7%', '00000000-0000-0000-0000-000000000001', true, 89400.00),
    -- Aufwand
    ('019c0001-0000-7000-8000-000000000009', '5200', 'Wareneingang', 'expense', 'Materialaufwand', 'Wareneinkauf', 'Wareneinkauf / Wareneingang', '00000000-0000-0000-0000-000000000001', true, 189500.00),
    ('019c0001-0000-7000-8000-000000000010', '5400', 'Betriebsstoffe', 'expense', 'Materialaufwand', 'Hilfs-/Betriebsstoffe', 'Betriebsstoffe und Verpackung', '00000000-0000-0000-0000-000000000001', true, 12300.00),
    ('019c0001-0000-7000-8000-000000000011', '6300', 'Personalkosten', 'expense', 'Personalaufwand', 'Löhne', 'Personalkosten Löhne und Gehälter', '00000000-0000-0000-0000-000000000001', true, 78900.00),
    ('019c0001-0000-7000-8000-000000000012', '6800', 'Abschreibungen', 'expense', 'Abschreibungen', 'AfA', 'Planmäßige Abschreibungen', '00000000-0000-0000-0000-000000000001', true, 24500.00)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 2. FINANCE: Buchungsjournale (Journal Entries)
-- ============================================
INSERT INTO domain_erp.finance_journal_entries (id, entry_number, entry_date, posting_date, description, reference, source, status, total_debit, total_credit, tenant_id)
VALUES
    ('019c0002-0000-7000-8000-000000000001', 'BU-2026-0001', '2026-01-15', '2026-01-15', 'Wareneingang Weizen 25t', 'WG-2026-00001', 'procurement', 'posted', 6125.00, 6125.00, '00000000-0000-0000-0000-000000000001'),
    ('019c0002-0000-7000-8000-000000000002', 'BU-2026-0002', '2026-01-18', '2026-01-18', 'Verkauf Raps 10t an Ölmühle', 'LS-2026-00001', 'sales', 'posted', 4200.00, 4200.00, '00000000-0000-0000-0000-000000000001'),
    ('019c0002-0000-7000-8000-000000000003', 'BU-2026-0003', '2026-01-22', '2026-01-22', 'Zahlung Lieferant Müller', 'ZA-2026-00001', 'payment', 'posted', 3500.00, 3500.00, '00000000-0000-0000-0000-000000000001'),
    ('019c0002-0000-7000-8000-000000000004', 'BU-2026-0004', '2026-02-01', '2026-02-01', 'Düngemittel-Einkauf NPK', 'BE-2026-00001', 'procurement', 'posted', 8950.00, 8950.00, '00000000-0000-0000-0000-000000000001'),
    ('019c0002-0000-7000-8000-000000000005', 'BU-2026-0005', '2026-02-10', '2026-02-10', 'Wareneingang Gerste 15t', 'WG-2026-00003', 'procurement', 'draft', 3675.00, 3675.00, '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- Journal Entry Lines
INSERT INTO domain_erp.finance_journal_entry_lines (id, journal_entry_id, account_id, debit, credit, description)
VALUES
    -- BU-0001: Wareneingang Weizen
    ('019c0003-0000-7000-8000-000000000001', '019c0002-0000-7000-8000-000000000001', '019c0001-0000-7000-8000-000000000009', 6125.00, 0, 'Wareneingang Weizen 25t @ 245 EUR/t'),
    ('019c0003-0000-7000-8000-000000000002', '019c0002-0000-7000-8000-000000000001', '019c0001-0000-7000-8000-000000000005', 0, 6125.00, 'Verbindlichkeit Lieferant'),
    -- BU-0002: Verkauf Raps
    ('019c0003-0000-7000-8000-000000000003', '019c0002-0000-7000-8000-000000000002', '019c0001-0000-7000-8000-000000000003', 4200.00, 0, 'Forderung Ölmühle'),
    ('019c0003-0000-7000-8000-000000000004', '019c0002-0000-7000-8000-000000000002', '019c0001-0000-7000-8000-000000000007', 0, 4200.00, 'Erlöse Raps 10t'),
    -- BU-0003: Zahlung
    ('019c0003-0000-7000-8000-000000000005', '019c0002-0000-7000-8000-000000000003', '019c0001-0000-7000-8000-000000000005', 3500.00, 0, 'Verbindlichkeit Müller ausgeglichen'),
    ('019c0003-0000-7000-8000-000000000006', '019c0002-0000-7000-8000-000000000003', '019c0001-0000-7000-8000-000000000002', 0, 3500.00, 'Bankabbuchung'),
    -- BU-0004: Düngemittel
    ('019c0003-0000-7000-8000-000000000007', '019c0002-0000-7000-8000-000000000004', '019c0001-0000-7000-8000-000000000009', 7521.01, 0, 'Wareneingang NPK 20-10-10'),
    ('019c0003-0000-7000-8000-000000000008', '019c0002-0000-7000-8000-000000000004', '019c0001-0000-7000-8000-000000000004', 1428.99, 0, 'Vorsteuer 19%'),
    ('019c0003-0000-7000-8000-000000000009', '019c0002-0000-7000-8000-000000000004', '019c0001-0000-7000-8000-000000000005', 0, 8950.00, 'Verbindlichkeit Compo Expert'),
    -- BU-0005: Gerste (draft)
    ('019c0003-0000-7000-8000-000000000010', '019c0002-0000-7000-8000-000000000005', '019c0001-0000-7000-8000-000000000009', 3675.00, 0, 'Wareneingang Gerste 15t @ 245 EUR/t'),
    ('019c0003-0000-7000-8000-000000000011', '019c0002-0000-7000-8000-000000000005', '019c0001-0000-7000-8000-000000000005', 0, 3675.00, 'Verbindlichkeit Lieferant')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 3. AGRAR-KONTRAKTE
-- ============================================
INSERT INTO domain_inventory.agrar_contracts (id, contract_number, contract_type, harvest_year, partner_id, article_id, pricing_model, fixed_price, currency, total_quantity_kg, remaining_quantity_kg, status, valid_from, valid_until, tenant_id)
VALUES
    ('019c0004-0000-7000-8000-000000000001', 'KT-2026-001', 'buy', 2026, 'BP-001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'fixed', 245.00, 'EUR', 100000.000, 75000.000, 'partially_allocated', '2026-01-01', '2026-12-31', '00000000-0000-0000-0000-000000000001'),
    ('019c0004-0000-7000-8000-000000000002', 'KT-2026-002', 'buy', 2026, 'BP-002', 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 'follow', NULL, 'EUR', 50000.000, 50000.000, 'open', '2026-01-01', '2026-12-31', '00000000-0000-0000-0000-000000000001'),
    ('019c0004-0000-7000-8000-000000000003', 'KT-2026-003', 'buy', 2026, 'BP-003', 'c9d0e1f2-a3b4-5678-2345-789012345678', 'pool', NULL, 'EUR', 80000.000, 80000.000, 'open', '2026-03-01', '2026-11-30', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 4. WIEGUNGEN (Weighing Tickets - realistic)
-- ============================================
INSERT INTO domain_inventory.weighing_tickets (id, ticket_number, scale_id, vehicle_plate, gross_weight, tare_weight, net_weight, first_weighing_at, second_weighing_at, moisture_pct, protein_pct, impurities_pct, hl_weight, billing_weight, weighing_date, status, direction, article_group, article_id, notes, tenant_id)
VALUES
    ('019c0005-0000-7000-8000-000000000001', 'WG-2026-00001', 'WAAGE-01', 'OL-AB 1234', 42500.000, 17200.000, 25300.000, '2026-01-15 08:12:00', '2026-01-15 08:45:00', 14.2, 12.8, 1.1, 78.5, 25000.000, '2026-01-15 08:12:00', 'closed', 'in', 'Getreide', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Weizen Ernte 2025, Landwirt Müller', '00000000-0000-0000-0000-000000000001'),
    ('019c0005-0000-7000-8000-000000000002', 'WG-2026-00002', 'WAAGE-01', 'CLP-CD 5678', 38700.000, 16800.000, 21900.000, '2026-01-18 10:30:00', '2026-01-18 11:05:00', 13.8, 11.5, 0.8, 79.1, 21900.000, '2026-01-18 10:30:00', 'closed', 'out', 'Ölsaaten', 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 'Raps-Lieferung an Ölmühle', '00000000-0000-0000-0000-000000000001'),
    ('019c0005-0000-7000-8000-000000000003', 'WG-2026-00003', 'WAAGE-02', 'VEC-EF 9012', 35200.000, 15600.000, 19600.000, '2026-02-10 07:45:00', '2026-02-10 08:20:00', 15.1, 10.2, 1.5, 66.8, 19200.000, '2026-02-10 07:45:00', 'closed', 'in', 'Getreide', 'c9d0e1f2-a3b4-5678-2345-789012345678', 'Gerste Anlieferung Winter, leicht feucht', '00000000-0000-0000-0000-000000000001'),
    ('019c0005-0000-7000-8000-000000000004', 'WG-2026-00004', 'WAAGE-01', 'OL-GH 3456', 44100.000, 17500.000, 26600.000, '2026-02-15 09:00:00', '2026-02-15 09:35:00', 13.5, 13.1, 0.6, 80.2, 26600.000, '2026-02-15 09:00:00', 'open', 'in', 'Getreide', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Premium-Weizen, sehr gute Qualität', '00000000-0000-0000-0000-000000000001'),
    ('019c0005-0000-7000-8000-000000000005', 'WG-2026-00005', 'WAAGE-02', 'CLP-IJ 7890', 31500.000, 14200.000, 17300.000, '2026-02-18 14:20:00', NULL, NULL, NULL, NULL, NULL, NULL, '2026-02-18 14:20:00', 'open', 'in', 'Getreide', 'c9d0e1f2-a3b4-5678-2345-789012345678', 'Gerste, Zweitwiegung steht aus', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 5. SILO-LOTS (Partien mit Qualitätsdaten)
-- ============================================
-- First ensure silos exist with correct schema
INSERT INTO domain_inventory.silos (id, silo_number, name, article_id, capacity_tons, tenant_id, is_active)
VALUES
    ('019c0006-0000-7000-8000-000000000001', 'S001', 'Silo Weizen Nord', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 500.000, '00000000-0000-0000-0000-000000000001', true),
    ('019c0006-0000-7000-8000-000000000002', 'S002', 'Silo Weizen Süd', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 500.000, '00000000-0000-0000-0000-000000000001', true),
    ('019c0006-0000-7000-8000-000000000003', 'S003', 'Silo Raps', 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 300.000, '00000000-0000-0000-0000-000000000001', true),
    ('019c0006-0000-7000-8000-000000000004', 'S004', 'Silo Gerste', 'c9d0e1f2-a3b4-5678-2345-789012345678', 400.000, '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_inventory.silo_lots (id, silo_id, virtual_lot_number, source_ticket_id, source_partner_id, article_id, quantity_tons, moisture_pct, protein_pct, impurities_pct, hl_weight, status, tenant_id)
VALUES
    ('019c0007-0000-7000-8000-000000000001', '019c0006-0000-7000-8000-000000000001', 'LOT-2026-S001-001', '019c0005-0000-7000-8000-000000000001', 'BP-001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 25.000, 14.2, 12.8, 1.1, 78.5, 'active', '00000000-0000-0000-0000-000000000001'),
    ('019c0007-0000-7000-8000-000000000002', '019c0006-0000-7000-8000-000000000001', 'LOT-2026-S001-002', '019c0005-0000-7000-8000-000000000004', 'BP-002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 26.600, 13.5, 13.1, 0.6, 80.2, 'active', '00000000-0000-0000-0000-000000000001'),
    ('019c0007-0000-7000-8000-000000000003', '019c0006-0000-7000-8000-000000000004', 'LOT-2026-S004-001', '019c0005-0000-7000-8000-000000000003', 'BP-003', 'c9d0e1f2-a3b4-5678-2345-789012345678', 19.200, 15.1, 10.2, 1.5, 66.8, 'active', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 6. ERNTE-ANNAHME (Harvest Acceptance)
-- ============================================
-- Need a customer first
INSERT INTO domain_crm.customers (id, customer_number, company_name, tenant_id, is_active)
VALUES
    ('019c0008-0000-7000-8000-000000000001', 'KD-10001', 'Landwirt Heinrich Müller', '00000000-0000-0000-0000-000000000001', true),
    ('019c0008-0000-7000-8000-000000000002', 'KD-10002', 'Hof Janssen GbR', '00000000-0000-0000-0000-000000000001', true),
    ('019c0008-0000-7000-8000-000000000003', 'KD-10003', 'Agrargenossenschaft Wesermarsch', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_inventory.harvest_acceptances (id, acceptance_number, tenant_id, branch_id, delivery_date, delivery_time, operator_id, weighing_ticket_id, customer_id, contract_id, article_id, variety_id, vehicle_plate, origin_nuts2_code, origin_country_code, release_status, pricing_mode, total_net_amount_eur, total_vat_amount_eur, total_gross_amount_eur, vat_rate_percent, acceptance_mode, ownership_type)
VALUES
    ('019c0009-0000-7000-8000-000000000001', 'EA-2026-0001', '00000000-0000-0000-0000-000000000001', '019c0000-0000-7000-8000-000000000001', '2026-01-15', '08:45', 'operator-001', '019c0005-0000-7000-8000-000000000001', '019c0008-0000-7000-8000-000000000001', '019c0004-0000-7000-8000-000000000001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Ponticus', 'OL-AB 1234', 'DE93', 'DE', 'released', 'contract', 6125.00, 1163.75, 7288.75, 19.00, 'PURCHASE_AT_DELIVERY_PTBF', 'OWN_STOCK'),
    ('019c0009-0000-7000-8000-000000000002', 'EA-2026-0002', '00000000-0000-0000-0000-000000000001', '019c0000-0000-7000-8000-000000000001', '2026-02-10', '08:20', 'operator-001', '019c0005-0000-7000-8000-000000000003', '019c0008-0000-7000-8000-000000000002', NULL, 'c9d0e1f2-a3b4-5678-2345-789012345678', 'Meridian', 'VEC-EF 9012', 'DE94', 'DE', 'released', 'spot_daily', 3675.00, 698.25, 4373.25, 19.00, 'PURCHASE_AT_DELIVERY_PTBF', 'OWN_STOCK'),
    ('019c0009-0000-7000-8000-000000000003', 'EA-2026-0003', '00000000-0000-0000-0000-000000000001', '019c0000-0000-7000-8000-000000000002', '2026-02-15', '09:35', 'operator-002', '019c0005-0000-7000-8000-000000000004', '019c0008-0000-7000-8000-000000000003', '019c0004-0000-7000-8000-000000000001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Benchmark', 'OL-GH 3456', 'DE93', 'DE', 'draft', 'contract', NULL, NULL, NULL, 19.00, 'PURCHASE_AT_DELIVERY_PTBF', 'OWN_STOCK')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 7. VERIFICATION
-- ============================================
DO $$
DECLARE
    cnt INTEGER;
BEGIN
    RAISE NOTICE '=== SEED VERIFICATION ===';
    SELECT COUNT(*) INTO cnt FROM domain_shared.branches; RAISE NOTICE 'Branches: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_erp.finance_accounts; RAISE NOTICE 'Finance Accounts: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_erp.finance_journal_entries; RAISE NOTICE 'Journal Entries: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_erp.finance_journal_entry_lines; RAISE NOTICE 'Journal Entry Lines: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.agrar_contracts; RAISE NOTICE 'Agrar Contracts: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.weighing_tickets; RAISE NOTICE 'Weighing Tickets (new): %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.silos; RAISE NOTICE 'Silos: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.silo_lots; RAISE NOTICE 'Silo Lots: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_crm.customers; RAISE NOTICE 'Customers: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.harvest_acceptances; RAISE NOTICE 'Harvest Acceptances: %', cnt;
    RAISE NOTICE '=== SEED COMPLETE ===';
END $$;
