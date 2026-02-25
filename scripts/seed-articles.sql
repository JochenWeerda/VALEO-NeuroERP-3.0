-- Seed data for domain_inventory.articles
-- Agricultural ERP test data

BEGIN;

-- Set default tenant
SET CONSTRAINTS ALL DEFERRED;

-- Insert seed articles
INSERT INTO domain_inventory.articles (
    id, article_number, name, description, category, subcategory, unit, 
    sales_price, purchase_price, hersteller, warengruppe, lagerartikel,
    tenant_id, is_active
) VALUES 
(
    gen_random_uuid()::text,
    'SAAT-001',
    'Winterweizen - Premium',
    'Hochwertiges Winterweichensaatgut, Bayernquality zertifiziert',
    'Saatgut', 'Getreide', 'kg',
    45.00, 38.00, 'Bayern Saat', 'Getreide', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'SAAT-002',
    'Wintergerste - Braugerste',
    'Braugerstensorte für die Mälzerei und Brauindustrie',
    'Saatgut', 'Getreide', 'kg',
    42.00, 35.00, 'Norddeutsche Saat', 'Getreide', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'SAAT-003',
    'Raps - Hybrid',
    'Winterraps Hybridsaatgut mit guter Standfestigkeit',
    'Saatgut', 'Ölsaaten', 'kg',
    85.00, 72.00, 'KWS Saat', 'Raps', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'DUENG-001',
    'Kalkammonsalpeter 27% N',
    'Stickstoffdünger mit Calcium und Magnesium',
    'Dünger', 'Mineraldünger', 'kg',
    32.00, 26.00, 'SKW Piesteritz', 'N-Dünger', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'DUENG-002',
    'Harnstoff 46% N',
    'Granulierter Stickstoffdünger',
    'Dünger', 'Mineraldünger', 'kg',
    38.00, 31.00, 'BASF', 'N-Dünger', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'DUENG-003',
    'NPK 15-15-15',
    'Volldünger für通用施肥',
    'Dünger', 'NPK-Dünger', 'kg',
    42.00, 35.00, 'Compo Expert', 'NPK', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'DUENG-004',
    'Ammonsulfat 21% N',
    'Schwefelhaltiger Stickstoffdünger',
    'Dünger', 'N-Dünger', 'kg',
    28.00, 22.00, 'Lufthansa', 'N-Dünger', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'PSM-001',
    'Fungizid - Azol Pro',
    'Breitwirksames Fungizid gegen Rost und Mehltau',
    'Pflanzenschutz', 'Fungizide', 'l',
    125.00, 98.00, 'Bayer CropScience', 'Fungizide', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'PSM-002',
    'Insektizid - Pyrethroid Extra',
    'Kontaktinsektizid gegen saugende und beißende Insekten',
    'Pflanzenschutz', 'Insektizide', 'l',
    89.00, 72.00, 'Syngenta', 'Insektizide', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'PSM-003',
    'Herbizid - Gräber Total',
    'Totalherbizid zur Unkrautbekämpfung',
    'Pflanzenschutz', 'Herbizide', 'l',
    65.00, 52.00, 'FMC', 'Herbizide', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'PSM-004',
    'Halmstabilisator - Moddus',
    'Halmverkürzer und Standfestigkeit',
    'Pflanzenschutz', 'Wachstumsregler', 'l',
    145.00, 118.00, 'Syngenta', 'Wachstumsregler', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'BIO-001',
    'Biostimulanz - Meeresalgenextrakt',
    'Biostimulans auf Basis von Ascophyllum nodosum',
    'Biostimulanzien', 'Algenpräparate', 'l',
    28.00, 22.00, 'Valagro', 'Biostimulanzien', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'BIO-002',
    'Mykorrhiza-Pilze',
    'Impfstoff für Wurzelbildung',
    'Biostimulanzien', 'Mikroorganismen', 'kg',
    185.00, 150.00, 'K接elpak', 'Mykorrhiza', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'SONST-001',
    'Lackfarbstoff - Blau',
    'Farbstoff zum Beizen von Saatgut',
    'Sonstiges', 'Farbstoffe', 'kg',
    45.00, 36.00, 'BASF', 'Sonstiges', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
),
(
    gen_random_uuid()::text,
    'SONST-002',
    'Saatgut-Fixiermittel',
    'Haftmittel für Saatgutbehandlung',
    'Sonstiges', 'Behandlungsmittel', 'l',
    32.00, 25.00, 'Covestro', 'Sonstiges', TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE
);

-- Verify insertion
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM domain_inventory.articles;
    RAISE NOTICE 'Inserted % articles', v_count;
END $$;

COMMIT;
