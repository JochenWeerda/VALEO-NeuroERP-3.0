param(
    [string]$DbContainer = "valeo-neuro-erp-postgres",
    [string]$DbUser = "valeo_dev",
    [string]$DbName = "valeo_neuro_erp"
)

$ErrorActionPreference = "Stop"

$sql = @"
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_inventory;

CREATE TABLE IF NOT EXISTS domain_crm.business_partners (
    partner_id VARCHAR(36) PRIMARY KEY,
    partner_number VARCHAR(64) UNIQUE NOT NULL,
    matchcode VARCHAR(120),
    name_1 VARCHAR(255) NOT NULL,
    name_2 VARCHAR(255),
    legal_form VARCHAR(80),
    street VARCHAR(120),
    house_number VARCHAR(40),
    postal_code VARCHAR(20),
    city VARCHAR(120),
    country VARCHAR(2),
    state VARCHAR(80),
    language VARCHAR(10),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    is_customer BOOLEAN NOT NULL DEFAULT FALSE,
    is_supplier BOOLEAN NOT NULL DEFAULT FALSE,
    is_carrier BOOLEAN NOT NULL DEFAULT FALSE,
    is_employee BOOLEAN NOT NULL DEFAULT FALSE,
    is_service_provider BOOLEAN NOT NULL DEFAULT FALSE,
    phone VARCHAR(60),
    mobile VARCHAR(60),
    email VARCHAR(255),
    website VARCHAR(255),
    fax VARCHAR(60),
    iban VARCHAR(34),
    bic VARCHAR(20),
    bank_name VARCHAR(120),
    sepa_mandate_reference VARCHAR(120),
    sepa_mandate_signed_at TIMESTAMPTZ,
    debtor_account VARCHAR(40),
    creditor_account VARCHAR(40),
    tax_number VARCHAR(60),
    vat_id VARCHAR(60),
    tax_type VARCHAR(40),
    payment_terms_id VARCHAR(36),
    credit_limit DECIMAL(14,2),
    dunning_level INTEGER DEFAULT 0,
    blocked_for_delivery BOOLEAN NOT NULL DEFAULT FALSE,
    blocked_for_invoice BOOLEAN NOT NULL DEFAULT FALSE,
    farm_number VARCHAR(80),
    eu_farm_id VARCHAR(80),
    harvest_year_default INTEGER,
    qs_certificate_number VARCHAR(80),
    qs_valid_until TIMESTAMPTZ,
    bio_certified BOOLEAN NOT NULL DEFAULT FALSE,
    bio_certificate_valid_until TIMESTAMPTZ,
    contract_group VARCHAR(80),
    default_silo_location VARCHAR(120),
    default_route_id VARCHAR(36),
    preferred_carrier_id VARCHAR(36),
    loading_requirements TEXT,
    email_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
    email_opt_in_timestamp TIMESTAMPTZ,
    sms_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
    sms_opt_in_timestamp TIMESTAMPTZ,
    whatsapp_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
    whatsapp_opt_in_timestamp TIMESTAMPTZ,
    newsletter_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
    newsletter_language VARCHAR(10),
    flyer_subscription BOOLEAN NOT NULL DEFAULT FALSE,
    flyer_delivery_type VARCHAR(20),
    marketing_segment VARCHAR(80),
    privacy_policy_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    privacy_policy_version VARCHAR(40),
    privacy_policy_accepted_at TIMESTAMPTZ,
    data_processing_agreement_signed BOOLEAN NOT NULL DEFAULT FALSE,
    data_retention_until TIMESTAMPTZ,
    contact_block_reason VARCHAR(255),
    anonymized_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by VARCHAR(36),
    updated_at TIMESTAMPTZ,
    updated_by VARCHAR(36)
);

INSERT INTO domain_crm.business_partners (
    partner_id, partner_number, matchcode, name_1, legal_form, street, house_number, postal_code, city, country, state, language, status,
    is_customer, is_supplier, is_carrier, is_employee, is_service_provider,
    phone, mobile, email, website, iban, bic, bank_name, sepa_mandate_reference, sepa_mandate_signed_at,
    debtor_account, creditor_account, tax_number, vat_id, tax_type, payment_terms_id, credit_limit, dunning_level, blocked_for_delivery, blocked_for_invoice,
    farm_number, eu_farm_id, harvest_year_default, qs_certificate_number, qs_valid_until, bio_certified, bio_certificate_valid_until, contract_group, default_silo_location,
    default_route_id, preferred_carrier_id, loading_requirements,
    email_opt_in, email_opt_in_timestamp, sms_opt_in, whatsapp_opt_in, newsletter_opt_in, newsletter_language, flyer_subscription, flyer_delivery_type, marketing_segment,
    privacy_policy_accepted, privacy_policy_version, privacy_policy_accepted_at, data_processing_agreement_signed, data_retention_until,
    created_by, updated_by
) VALUES
(
    '3e4a4c12-0000-4000-9000-000000000001', 'BP-10001', 'MUSTERHOF', 'Landwirtschaft Musterhof GmbH', 'GmbH', 'Dorfstr.', '12', '29525', 'Uelzen', 'DE', 'Niedersachsen', 'de', 'active',
    TRUE, TRUE, FALSE, FALSE, FALSE,
    '+49 581 12345', '+49 171 1234567', 'info@musterhof.de', 'https://musterhof.de', 'DE12500105170648489890', 'INGDDEFFXXX', 'ING', 'SEPA-MUST-001', now() - interval '200 days',
    '120000', '330000', '47/123/45678', 'DE123456789', 'paragraph24', '00000000-0000-0000-0000-000000000101', 75000, 1, FALSE, FALSE,
    'FARM-UE-1001', 'EU-DE-NI-7788', 2026, 'QS-4711', now() + interval '300 days', TRUE, now() + interval '320 days', 'NORD', 'SILO-DEMO-01',
    '00000000-0000-0000-0000-00000000R001', '00000000-0000-0000-0000-00000000C001', 'Andienung nur mit Terminfenster 06:00-14:00.',
    TRUE, now() - interval '100 days', TRUE, TRUE, TRUE, 'de', TRUE, 'digital', 'A-KUNDE',
    TRUE, '2026.1', now() - interval '100 days', TRUE, now() + interval '3 years',
    '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001'
),
(
    '3e4a4c12-0000-4000-9000-000000000002', 'BP-10002', 'AGRAR-NORD', 'Agrar Nord eG', 'eG', 'Mühlenweg', '5', '29614', 'Soltau', 'DE', 'Niedersachsen', 'de', 'active',
    TRUE, FALSE, TRUE, FALSE, FALSE,
    '+49 5191 5566', '+49 171 5557788', 'zentrale@agrarnord.de', 'https://agrarnord.de', 'DE44500105175407324931', 'DEUTDEFFXXX', 'Deutsche Bank', 'SEPA-AGN-002', now() - interval '120 days',
    '120050', null, '40/987/65432', 'DE987654321', 'standard', '00000000-0000-0000-0000-000000000102', 150000, 0, FALSE, FALSE,
    'FARM-SOL-2102', 'EU-DE-NI-8899', 2026, 'QS-9922', now() + interval '200 days', FALSE, null, 'NORD', 'SILO-DEMO-02',
    '00000000-0000-0000-0000-00000000R002', '00000000-0000-0000-0000-00000000C002', 'Waagepflicht bei jeder Anlieferung.',
    TRUE, now() - interval '70 days', FALSE, FALSE, TRUE, 'de', FALSE, 'postal', 'B-KUNDE',
    TRUE, '2026.1', now() - interval '70 days', TRUE, now() + interval '2 years',
    '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001'
)
ON CONFLICT (partner_id) DO UPDATE SET
    name_1 = EXCLUDED.name_1,
    status = EXCLUDED.status,
    updated_at = now(),
    updated_by = EXCLUDED.updated_by;

INSERT INTO domain_inventory.silos (id, silo_number, name, article_id, capacity_tons, tenant_id, is_active)
VALUES
    ('84214088-9c09-4b2c-a79e-9ae7d920760d', 'SILO-DEMO-01', 'Demo Silo Nord', 'ART-WHEAT-A', 1500, '00000000-0000-0000-0000-000000000001', TRUE),
    ('94214088-9c09-4b2c-a79e-9ae7d920760d', 'SILO-DEMO-02', 'Demo Silo Süd', 'ART-BARLEY-A', 1200, '00000000-0000-0000-0000-000000000001', TRUE),
    ('a4214088-9c09-4b2c-a79e-9ae7d920760d', 'SILO-DEMO-03', 'Demo Silo Ost', 'ART-CORN-A', 1800, '00000000-0000-0000-0000-000000000001', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_inventory.silo_lots (
    id, silo_id, virtual_lot_number, source_partner_id, article_id, quantity_tons, moisture_pct, protein_pct, impurities_pct, hl_weight, status, tenant_id
)
VALUES
    ('5bb39451-bca6-43ce-9f0c-5e759a3b79d1', '84214088-9c09-4b2c-a79e-9ae7d920760d', 'LOT-DEMO-01', '3e4a4c12-0000-4000-9000-000000000001', 'ART-WHEAT-A', 320.5, 14.2, 12.8, 1.5, 77.4, 'active', '00000000-0000-0000-0000-000000000001'),
    ('6cc39451-bca6-43ce-9f0c-5e759a3b79d1', '94214088-9c09-4b2c-a79e-9ae7d920760d', 'LOT-DEMO-02', '3e4a4c12-0000-4000-9000-000000000002', 'ART-BARLEY-A', 410.0, 13.7, 11.2, 1.1, 69.5, 'active', '00000000-0000-0000-0000-000000000001'),
    ('7dd39451-bca6-43ce-9f0c-5e759a3b79d1', 'a4214088-9c09-4b2c-a79e-9ae7d920760d', 'LOT-DEMO-03', '3e4a4c12-0000-4000-9000-000000000001', 'ART-CORN-A', 255.8, 15.1, 8.9, 1.9, 71.2, 'active', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_inventory.silo_lot_movements (id, silo_lot_id, movement_type, quantity_tons, note, tenant_id)
VALUES
    ('64e1b47f-4df1-486b-9957-2a9e04c1dc40', '5bb39451-bca6-43ce-9f0c-5e759a3b79d1', 'treatment', 5.0, 'Demo Reinigung', '00000000-0000-0000-0000-000000000001'),
    ('74e1b47f-4df1-486b-9957-2a9e04c1dc40', '6cc39451-bca6-43ce-9f0c-5e759a3b79d1', 'in', 410.0, 'Demo Erstbefuellung', '00000000-0000-0000-0000-000000000001'),
    ('84e1b47f-4df1-486b-9957-2a9e04c1dc40', '7dd39451-bca6-43ce-9f0c-5e759a3b79d1', 'in', 255.8, 'Demo Erstbefuellung', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_inventory.article_batches (id, article_id, batch_number, warehouse_id, quantity, expiry_date, tenant_id)
VALUES
    ('AB-DEMO-20260214-01', 'ART-WHEAT-A', 'BATCH-2026-001', 'WH-DEMO-01', 250.000, now() + interval '180 days', '00000000-0000-0000-0000-000000000001'),
    ('AB-DEMO-20260214-02', 'ART-BARLEY-A', 'BATCH-2026-002', 'WH-DEMO-01', 180.000, now() + interval '210 days', '00000000-0000-0000-0000-000000000001'),
    ('AB-DEMO-20260214-03', 'ART-CORN-A', 'BATCH-2026-003', 'WH-DEMO-02', 320.000, now() + interval '240 days', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;
"@

$sql | docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1

Write-Host "Seed completed: business_partners, silos, lots, movements, article_batches"
