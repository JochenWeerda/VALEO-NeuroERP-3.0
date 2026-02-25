-- Seed Data for VALEO NeuroERP 3.0
-- This script creates and seeds essential data for development
-- Run with: docker exec valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp -f /docker-entrypoint-initdb.d/seed-data.sql

-- ============================================
-- 1. CREATE DOMAIN SCHEMAS
-- ============================================
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_ops;
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS domain_crm;

-- ============================================
-- 2. CREATE TENANTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS domain_shared.tenants (
    id UUID PRIMARY KEY DEFAULT '00000000-0000-0000-0000-000000000001',
    name VARCHAR(255) NOT NULL DEFAULT 'Default Tenant',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO domain_shared.tenants (id, name) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'Default Tenant', true)
ON CONFLICT DO NOTHING;

-- ============================================
-- 3. CREATE ARTICLES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS domain_inventory.articles (
    id VARCHAR(36) PRIMARY KEY,
    article_number VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    tenant_id VARCHAR(36) DEFAULT '00000000-0000-0000-0000-000000000001',
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    description2 TEXT,
    short_description VARCHAR(200),
    suchbegriff VARCHAR(100),
    matchcode2 VARCHAR(100),
    hersteller VARCHAR(120),
    herkunftsland VARCHAR(2),
    naehrwertangaben JSONB,
    mhd_erforderlich BOOLEAN DEFAULT false,
    lagerartikel BOOLEAN DEFAULT true,
    mehrwertsteuer_prozent NUMERIC(5,2),
    warengruppe VARCHAR(80),
    gefahrgutklasse VARCHAR(40),
    gefahrgut_un_nummer VARCHAR(20),
    gefahrgut_verpackungsgruppe VARCHAR(5),
    gefahrgut_anhaenge VARCHAR(200),
    lagerorte JSONB DEFAULT '[]',
    chargenpflicht BOOLEAN DEFAULT false,
    qs_pruefung_erforderlich BOOLEAN DEFAULT false,
    zolltarifnummer VARCHAR(30),
    bio_kennzeichnung BOOLEAN DEFAULT false,
    gmp_plus_relevanz BOOLEAN DEFAULT false,
    kennzeichnung_bio VARCHAR(50),
    kennzeichnung_vegan VARCHAR(10),
    kennzeichnung_vegetarisch VARCHAR(10),
    kennzeichnung_allergene TEXT,
    kennzeichnung_herkunft VARCHAR(100),
    lager_min_temperatur NUMERIC(5,1),
    lager_max_temperatur NUMERIC(5,1),
    lager_lagerdauer_tage INTEGER,
    lager_zentral BOOLEAN DEFAULT false,
    lager_silo BOOLEAN DEFAULT false,
    analyse_protein NUMERIC(5,2),
    analyse_feuchtigkeit NUMERIC(5,2),
    analyse_schadex NUMERIC(5,2),
    analyse_fremdstoffe NUMERIC(5,2),
    analyse_sonstiges TEXT,
    ean_code VARCHAR(50),
    alt_ean_code VARCHAR(50),
    lieferanten_artikelnummer VARCHAR(50),
    kunden_artikelnummer VARCHAR(50),
    verwendungszweck VARCHAR(255),
    nachhaltige_biomasse BOOLEAN DEFAULT false,
    pool_artikel BOOLEAN DEFAULT false,
    rabatt_auftrag_rechnung NUMERIC(5,2),
    rabatt_lose NUMERIC(5,2),
    rabatt_selbstabholer NUMERIC(5,2),
    zu_abschlag_1_code VARCHAR(50),
    zu_abschlag_1_prozent NUMERIC(5,2),
    zu_abschlag_2_code VARCHAR(50),
    zu_abschlag_2_prozent NUMERIC(5,2),
    berechne_zu_abschlag_auf_netto BOOLEAN DEFAULT false,
    einfuegen_summe_nach_zu_abschlag BOOLEAN DEFAULT false,
    skontofaehig BOOLEAN DEFAULT true,
    warenrueckverguetung BOOLEAN DEFAULT false,
    bonus_faehig BOOLEAN DEFAULT false,
    rabattfaehig BOOLEAN DEFAULT true,
    einheit_typ VARCHAR(20),
    einheit_faktor NUMERIC(10,4),
    einheit_preiseinheit VARCHAR(20),
    gebinde_groesse NUMERIC(10,2),
    gebinde_einheit VARCHAR(20),
    etikett_druck BOOLEAN DEFAULT false,
    etikett_preis_je_1kg BOOLEAN DEFAULT false,
    etikett_vorlage VARCHAR(100),
    etikett_abweichende_bezugsgroesse NUMERIC(10,2),
    web_sichtbar BOOLEAN DEFAULT false,
    web_preis_auf_anfrage BOOLEAN DEFAULT false,
    intrastat_warennr VARCHAR(20),
    kontrakt_erlaubt BOOLEAN DEFAULT true,
    chargen_nr_erforderlich BOOLEAN DEFAULT false,
    serien_nr_erforderlich BOOLEAN DEFAULT false,
    bioware BOOLEAN DEFAULT false,
    waage_artikel BOOLEAN DEFAULT false,
    pflanzenschutzmittel BOOLEAN DEFAULT false,
    explosionsstoff BOOLEAN DEFAULT false,
    nur_einzelverkauf BOOLEAN DEFAULT false,
    artikel_umbuchung_bei_ls_freigabe BOOLEAN DEFAULT false,
    haltbarkeit_tage INTEGER,
    regal_flaeche VARCHAR(50),
    min_menge_auftrag NUMERIC(10,2),
    kostenstelle VARCHAR(50),
    duengemittel_inhalte_id VARCHAR,
    duengemittel_inhalte_bezeichnung VARCHAR(255),
    kaufabrechnung VARCHAR(50),
    mva_kontrakt BOOLEAN DEFAULT false,
    mahlerzeugnis VARCHAR(50),
    schnittstelle_artikel_nr VARCHAR(50),
    schnittstelle_waage_nr VARCHAR(50),
    schnittstelle_produkt_nr VARCHAR(50),
    waage_etikett_art VARCHAR(10),
    nawaro_endprodukt BOOLEAN DEFAULT false,
    getreidemeldung_formular_spalte VARCHAR(50),
    getreidemeldung_herkunft VARCHAR(50),
    mvo_bereich VARCHAR(50),
    mvo_gruppe VARCHAR(50),
    mvo_erzeugnis VARCHAR(50),
    mvo_bestandsgroesse VARCHAR(50),
    analyse_text TEXT,
    analyse_bild_datei VARCHAR(255),
    druck_anfrage BOOLEAN DEFAULT false,
    druck_angebot BOOLEAN DEFAULT false,
    druck_auftragsbestaetigung BOOLEAN DEFAULT false,
    druck_lieferschein BOOLEAN DEFAULT false,
    druck_rechnung BOOLEAN DEFAULT false,
    druck_kontrakt BOOLEAN DEFAULT false,
    druck_wiegeschein BOOLEAN DEFAULT false,
    druck_statt_artikel_bezeichnung BOOLEAN DEFAULT false,
    druck_zusaetzlich BOOLEAN DEFAULT false,
    lieferantennummer VARCHAR(50),
    unit VARCHAR(10) DEFAULT 'ST',
    category VARCHAR(50),
    subcategory VARCHAR(50),
    barcode VARCHAR(50),
    supplier_number VARCHAR(50),
    customer_article_number VARCHAR(50),
    purchase_price NUMERIC(10,2),
    sales_price NUMERIC(10,2),
    currency VARCHAR(3) DEFAULT 'EUR',
    min_stock NUMERIC(10,2),
    max_stock NUMERIC(10,2),
    weight NUMERIC(8,2),
    dimensions VARCHAR(50),
    current_stock NUMERIC(10,2) DEFAULT 0,
    reserved_stock NUMERIC(10,2) DEFAULT 0,
    available_stock NUMERIC(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- 4. SEED ARTICLES DATA
-- ============================================
INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, is_active, description, suchbegriff, hersteller, warengruppe, lagerartikel, mehrwertsteuer_prozent, barcode, unit, category, sales_price) VALUES 
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'ART-001', 'Weizen Tierfutter Weizenschrot Klasse A', '00000000-0000-0000-0000-000000000001', true, 'Hochwertiges Tierfutter Weizenschrot für Rinder und Schweine', 'Weizen', 'BayWa AG', 'Futtermittel', true, 19.0, '4006381333931', 'ST', 'Futtermittel', 245.00),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'ART-002', 'Rapssaatgut Defender', '00000000-0000-0000-0000-000000000001', true, 'Winterraps-Saatgut Defender, 50kg Sack', 'Raps', 'Bayer CropScience', 'Saatgut', true, 19.0, '4012345678901', 'SAC', 'Saatgut', 189.00),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'ART-003', 'NPK-Dünger 20-10-10', '00000000-0000-0000-0000-000000000001', true, 'Universeller NPK-Dünger mit Schwefel, 25kg Sack', 'Duenger', 'Compo Expert', 'Duenger', true, 19.0, '4021234567890', 'SAC', 'Duenger', 45.50),
    ('d4e5f6a7-b8c9-0123-def0-234567890123', 'ART-004', 'Glyphosat RoundUp Ultra', '00000000-0000-0000-0000-000000000001', true, 'TotalherbizidGlyphosat 360g/L, 5L Kanister', 'Glyphosat', 'Monsanto', 'Pflanzenschutz', true, 19.0, '4031234567890', 'KAN', 'Pflanzenschutz', 89.00),
    ('e5f6a7b8-c9d0-1234-ef01-345678901234', 'ART-005', 'Stallmist Kompost', '00000000-0000-0000-0000-000000000001', true, 'Organischer Stallmist-Kompost, 1000kg BigBag', 'Kompost', 'Regional', 'Organisch', true, 19.0, '4041234567890', 'BBL', 'Organisch', 120.00),
    ('f6a7b8c9-d0e1-2345-f012-456789012345', 'ART-006', 'Kalkstickstoff 46', '00000000-0000-0000-0000-000000000001', true, 'Kalkstickstoff Düngemittel, 25kg Sack', 'Kalk', 'AlzChem', 'Duenger', true, 19.0, '4051234567890', 'SAC', 'Duenger', 38.00),
    ('a7b8c9d0-e1f2-3456-0123-567890123456', 'ART-007', 'Mais Saatgut Maximus', '00000000-0000-0000-0000-000000000001', true, 'Silomais Saatgut Maximus, 50000 Körner', 'Mais', 'KWS', 'Saatgut', true, 19.0, '4061234567890', 'KRT', 'Saatgut', 285.00),
    ('b8c9d0e1-f2a3-4567-1234-678901234567', 'ART-008', 'Methylobacterium', '00000000-0000-0000-0000-000000000001', true, 'Biostimulanz Methylobacterium, 1L Flasche', 'Bio', 'Syngenta', 'Biostimulanzien', true, 19.0, '4071234567890', 'FLA', 'Biostimulanzien', 156.00),
    ('c9d0e1f2-a3b4-5678-2345-789012345678', 'ART-009', 'Gerste Braugerste', '00000000-0000-0000-0000-000000000001', true, 'Braugerste für Bierproduktion, Qualitätsklasse I', 'Gerste', 'Volverde', 'Getreide', true, 19.0, '4081234567890', 'T', 'Getreide', 195.00),
    ('d0e1f2a3-b4c5-6789-3456-890123456789', 'ART-010', 'Ackerbohnen Saatgut', '00000000-0000-0000-0000-000000000001', true, 'Ackerbohnen Saatgut, 50kg Sack', 'Bohnen', 'Pioneer', 'Saatgut', true, 19.0, '4091234567890', 'SAC', 'Saatgut', 165.00),
    ('e1f2a3b4-c5d6-7890-4567-901234567890', 'ART-011', 'Kartoffel-Dünger NPK 15-15-15', '00000000-0000-0000-0000-000000000001', true, 'Spezialdünger für Kartoffeln, 25kg', 'Kartoffel', 'K+S', 'Duenger', true, 19.0, '4101234567890', 'SAC', 'Duenger', 52.00),
    ('f2a3b4c5-d6e7-8901-5678-012345678901', 'ART-012', 'Winterweizen Saatgut Ponticus', '00000000-0000-0000-0000-000000000001', true, 'WinterweizenSaatgut Ponticus, 500kg', 'Weizen', 'RAGT', 'Saatgut', true, 19.0, '4111234567890', 'SAC', 'Saatgut', 320.00)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 5. CREATE SILOS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS domain_inventory.silos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    silo_number VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    tenant_id VARCHAR(36) DEFAULT '00000000-0000-0000-0000-000000000001',
    capacity_m3 NUMERIC(10,2),
    current_fill_level NUMERIC(5,2) DEFAULT 0,
    product_id VARCHAR(36),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO domain_inventory.silos (silo_number, name, capacity_m3, product_id) VALUES
    ('S001', 'Silo Weizen Nord', 500.0, 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'),
    ('S002', 'Silo Weizen Süd', 500.0, 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'),
    ('S003', 'Silo Raps', 300.0, 'b2c3d4e5-f6a7-8901-bcde-f12345678901'),
    ('S004', 'Silo Dünger', 200.0, 'c3d4e5f6-a7b8-9012-cdef-123456789012')
ON CONFLICT DO NOTHING;

-- ============================================
-- 6. CREATE WEIGHING TICKETS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS domain_inventory.weighing_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_number VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(36) DEFAULT '00000000-0000-0000-0000-000000000001',
    customer_id VARCHAR(36),
    article_id VARCHAR(36),
    weight_kg NUMERIC(10,2),
    weighing_type VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO domain_inventory.weighing_tickets (ticket_number, customer_id, article_id, weight_kg, weighing_type) VALUES
    ('WG-2024-00001', 'c1d2e3f4-a5b6-c7d8-e9f0-123456789012', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 25000.0, 'IN'),
    ('WG-2024-00002', 'c1d2e3f4-a5b6-c7d8-e9f0-123456789012', 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 18000.0, 'OUT')
ON CONFLICT DO NOTHING;

-- ============================================
-- 7. VERIFY DATA
-- ============================================
SELECT 'Tenants:' AS info, COUNT(*) AS count FROM domain_shared.tenants
UNION ALL
SELECT 'Articles:', COUNT(*) FROM domain_inventory.articles
UNION ALL
SELECT 'Silos:', COUNT(*) FROM domain_inventory.silos
UNION ALL
SELECT 'Weighing Tickets:', COUNT(*) FROM domain_inventory.weighing_tickets;
