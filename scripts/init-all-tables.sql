-- ============================================================================
-- VALEO-NeuroERP - MASTER DATABASE INITIALIZATION SCRIPT
-- Erstellt ALLE Tabellen für Production-Ready System
-- Version: 1.0
-- Date: 2025-10-16
-- ============================================================================

-- Basis-Extensions aktivieren
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. CRM MODUL (Customer Relationship Management)
-- ============================================================================

-- Kontakte
CREATE TABLE IF NOT EXISTS crm_contacts (
    id SERIAL PRIMARY KEY,
    salutation VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    company VARCHAR(255),
    position VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    street VARCHAR(255),
    postal_code VARCHAR(20),
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Deutschland',
    contact_type VARCHAR(50) DEFAULT 'customer',
    tags TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crm_contacts_email ON crm_contacts(email);
CREATE INDEX idx_crm_contacts_company ON crm_contacts(company);
CREATE INDEX idx_crm_contacts_type ON crm_contacts(contact_type);
CREATE INDEX idx_crm_contacts_name ON crm_contacts(last_name, first_name);

-- Leads
CREATE TABLE IF NOT EXISTS crm_leads (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES crm_contacts(id) ON DELETE CASCADE,
    lead_source VARCHAR(100),
    status VARCHAR(50) DEFAULT 'new',
    priority VARCHAR(20) DEFAULT 'medium',
    estimated_value DECIMAL(12,2),
    probability INTEGER,
    expected_close_date DATE,
    assigned_to VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crm_leads_contact ON crm_leads(contact_id);
CREATE INDEX idx_crm_leads_status ON crm_leads(status);
CREATE INDEX idx_crm_leads_assigned ON crm_leads(assigned_to);

-- Aktivitäten
CREATE TABLE IF NOT EXISTS crm_activities (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES crm_contacts(id) ON DELETE CASCADE,
    lead_id INTEGER REFERENCES crm_leads(id) ON DELETE CASCADE,
    activity_type VARCHAR(50),
    subject VARCHAR(255),
    description TEXT,
    activity_date TIMESTAMP,
    duration_minutes INTEGER,
    outcome VARCHAR(100),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crm_activities_contact ON crm_activities(contact_id);
CREATE INDEX idx_crm_activities_lead ON crm_activities(lead_id);
CREATE INDEX idx_crm_activities_date ON crm_activities(activity_date);

-- Betriebsprofile (Landwirtschaft)
CREATE TABLE IF NOT EXISTS crm_betriebsprofile (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES crm_contacts(id) ON DELETE CASCADE,
    betriebsnummer VARCHAR(100) UNIQUE,
    betriebsart VARCHAR(100),
    flaeche_gesamt_ha DECIMAL(10,2),
    flaeche_acker_ha DECIMAL(10,2),
    flaeche_gruenland_ha DECIMAL(10,2),
    tierbestand_rinder INTEGER,
    tierbestand_schweine INTEGER,
    bio_zertifiziert BOOLEAN DEFAULT FALSE,
    hauptkulturen TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crm_betrieb_contact ON crm_betriebsprofile(contact_id);
CREATE INDEX idx_crm_betrieb_nummer ON crm_betriebsprofile(betriebsnummer);

-- ============================================================================
-- 2. AGRAR MODUL (Landhandel)
-- ============================================================================

-- PSM (Pflanzenschutzmittel) Produkte
CREATE TABLE IF NOT EXISTS agrar_psm_products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    active_ingredient VARCHAR(255),
    product_type VARCHAR(100),
    registration_number VARCHAR(100) UNIQUE,
    manufacturer VARCHAR(255),
    approval_status VARCHAR(50) DEFAULT 'active',
    application_areas TEXT,
    dosage_instructions TEXT,
    safety_interval_days INTEGER,
    water_protection_class VARCHAR(10),
    bee_hazard VARCHAR(50),
    price_per_liter DECIMAL(10,2),
    price_per_kg DECIMAL(10,2),
    stock_quantity DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_psm_products_name ON agrar_psm_products(product_name);
CREATE INDEX idx_psm_products_regno ON agrar_psm_products(registration_number);
CREATE INDEX idx_psm_products_type ON agrar_psm_products(product_type);

-- PSM Abgabedokumentation
CREATE TABLE IF NOT EXISTS agrar_psm_documentation (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES agrar_psm_products(id) ON DELETE CASCADE,
    customer_id INTEGER,
    customer_name VARCHAR(255) NOT NULL,
    customer_address TEXT,
    quantity_liters DECIMAL(10,2),
    quantity_kg DECIMAL(10,2),
    sale_date DATE NOT NULL,
    application_purpose TEXT,
    application_area_hectares DECIMAL(10,2),
    sachkundenachweis_number VARCHAR(100),
    beratung_documented BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_psm_doc_product ON agrar_psm_documentation(product_id);
CREATE INDEX idx_psm_doc_customer ON agrar_psm_documentation(customer_id);
CREATE INDEX idx_psm_doc_date ON agrar_psm_documentation(sale_date);

-- Saatgut
CREATE TABLE IF NOT EXISTS agrar_saatgut (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    crop_type VARCHAR(100),
    variety VARCHAR(100),
    certification VARCHAR(50),
    tkm DECIMAL(8,2),
    germination_rate DECIMAL(5,2),
    producer VARCHAR(255),
    batch_number VARCHAR(100),
    packaging_unit VARCHAR(50),
    price_per_unit DECIMAL(10,2),
    stock_quantity DECIMAL(10,2),
    harvest_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_saatgut_name ON agrar_saatgut(product_name);
CREATE INDEX idx_saatgut_crop ON agrar_saatgut(crop_type);
CREATE INDEX idx_saatgut_batch ON agrar_saatgut(batch_number);

-- Düngemittel
CREATE TABLE IF NOT EXISTS agrar_duengemittel (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    composition VARCHAR(255),
    n_content DECIMAL(5,2),
    p_content DECIMAL(5,2),
    k_content DECIMAL(5,2),
    mg_content DECIMAL(5,2),
    s_content DECIMAL(5,2),
    organic_matter DECIMAL(5,2),
    manufacturer VARCHAR(255),
    packaging_unit VARCHAR(50),
    price_per_unit DECIMAL(10,2),
    stock_quantity DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_duengemittel_name ON agrar_duengemittel(product_name);
CREATE INDEX idx_duengemittel_type ON agrar_duengemittel(type);

-- ============================================================================
-- 3. SALES MODUL (Verkauf)
-- ============================================================================

-- Angebote
CREATE TABLE IF NOT EXISTS sales_angebote (
    id SERIAL PRIMARY KEY,
    angebotsnummer VARCHAR(50) UNIQUE NOT NULL,
    kunde_id INTEGER,
    kunde_name VARCHAR(255) NOT NULL,
    angebotsdatum DATE NOT NULL,
    gueltig_bis DATE,
    status VARCHAR(50) DEFAULT 'entwurf',
    netto_summe DECIMAL(12,2),
    mwst_betrag DECIMAL(12,2),
    brutto_summe DECIMAL(12,2),
    zahlungsbedingungen TEXT,
    lieferbedingungen TEXT,
    notizen TEXT,
    erstellt_von VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sales_angebote_nummer ON sales_angebote(angebotsnummer);
CREATE INDEX idx_sales_angebote_kunde ON sales_angebote(kunde_id);
CREATE INDEX idx_sales_angebote_status ON sales_angebote(status);
CREATE INDEX idx_sales_angebote_datum ON sales_angebote(angebotsdatum);

-- Angebot Positionen
CREATE TABLE IF NOT EXISTS sales_angebot_positionen (
    id SERIAL PRIMARY KEY,
    angebot_id INTEGER REFERENCES sales_angebote(id) ON DELETE CASCADE,
    position_nr INTEGER,
    artikel_nr VARCHAR(100),
    beschreibung TEXT,
    menge DECIMAL(10,2),
    einheit VARCHAR(20),
    einzelpreis DECIMAL(10,2),
    rabatt_prozent DECIMAL(5,2) DEFAULT 0,
    netto_betrag DECIMAL(12,2),
    mwst_satz DECIMAL(5,2) DEFAULT 19.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_angebot_pos_angebot ON sales_angebot_positionen(angebot_id);

-- Aufträge
CREATE TABLE IF NOT EXISTS sales_auftraege (
    id SERIAL PRIMARY KEY,
    auftragsnummer VARCHAR(50) UNIQUE NOT NULL,
    angebot_id INTEGER REFERENCES sales_angebote(id),
    kunde_id INTEGER,
    kunde_name VARCHAR(255) NOT NULL,
    auftragsdatum DATE NOT NULL,
    lieferdatum DATE,
    status VARCHAR(50) DEFAULT 'offen',
    netto_summe DECIMAL(12,2),
    mwst_betrag DECIMAL(12,2),
    brutto_summe DECIMAL(12,2),
    zahlungsstatus VARCHAR(50) DEFAULT 'unbezahlt',
    lieferstatus VARCHAR(50) DEFAULT 'nicht_geliefert',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sales_auftraege_nummer ON sales_auftraege(auftragsnummer);
CREATE INDEX idx_sales_auftraege_kunde ON sales_auftraege(kunde_id);
CREATE INDEX idx_sales_auftraege_status ON sales_auftraege(status);

-- ============================================================================
-- 4. FINANCE MODUL (Finanzbuchhaltung)
-- ============================================================================

-- Buchungsjournal
CREATE TABLE IF NOT EXISTS finance_buchungsjournal (
    id SERIAL PRIMARY KEY,
    belegnummer VARCHAR(50),
    buchungsdatum DATE NOT NULL,
    valutadatum DATE,
    soll_konto VARCHAR(20) NOT NULL,
    haben_konto VARCHAR(20) NOT NULL,
    betrag DECIMAL(12,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    buchungstext TEXT,
    kostenstelle VARCHAR(50),
    kostentraeger VARCHAR(50),
    steuerschluessel VARCHAR(10),
    gegenkonto VARCHAR(20),
    erstellt_von VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_buchungsjournal_datum ON finance_buchungsjournal(buchungsdatum);
CREATE INDEX idx_buchungsjournal_soll ON finance_buchungsjournal(soll_konto);
CREATE INDEX idx_buchungsjournal_haben ON finance_buchungsjournal(haben_konto);
CREATE INDEX idx_buchungsjournal_beleg ON finance_buchungsjournal(belegnummer);

-- Debitoren (Kundenforderungen)
CREATE TABLE IF NOT EXISTS finance_debitoren (
    id SERIAL PRIMARY KEY,
    debitorennummer VARCHAR(50) UNIQUE NOT NULL,
    kunde_id INTEGER,
    kunde_name VARCHAR(255) NOT NULL,
    rechnungsnummer VARCHAR(50),
    rechnungsdatum DATE NOT NULL,
    faelligkeitsdatum DATE,
    betrag_brutto DECIMAL(12,2) NOT NULL,
    betrag_offen DECIMAL(12,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'offen',
    zahlungsziel_tage INTEGER DEFAULT 30,
    mahnstufe INTEGER DEFAULT 0,
    letzte_mahnung DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_debitoren_nummer ON finance_debitoren(debitorennummer);
CREATE INDEX idx_debitoren_kunde ON finance_debitoren(kunde_id);
CREATE INDEX idx_debitoren_status ON finance_debitoren(status);
CREATE INDEX idx_debitoren_faelligkeit ON finance_debitoren(faelligkeitsdatum);

-- Kreditoren (Lieferantenverbindlichkeiten)
CREATE TABLE IF NOT EXISTS finance_kreditoren (
    id SERIAL PRIMARY KEY,
    kreditorennummer VARCHAR(50) UNIQUE NOT NULL,
    lieferant_id INTEGER,
    lieferant_name VARCHAR(255) NOT NULL,
    rechnungsnummer VARCHAR(50),
    rechnungsdatum DATE NOT NULL,
    faelligkeitsdatum DATE,
    betrag_brutto DECIMAL(12,2) NOT NULL,
    betrag_offen DECIMAL(12,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'offen',
    skonto_prozent DECIMAL(5,2),
    skonto_bis DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kreditoren_nummer ON finance_kreditoren(kreditorennummer);
CREATE INDEX idx_kreditoren_lieferant ON finance_kreditoren(lieferant_id);
CREATE INDEX idx_kreditoren_status ON finance_kreditoren(status);
CREATE INDEX idx_kreditoren_faelligkeit ON finance_kreditoren(faelligkeitsdatum);

-- ============================================================================
-- 5. INVENTORY MODUL (Lagerverwaltung)
-- ============================================================================

-- Artikel
CREATE TABLE IF NOT EXISTS inventory_artikel (
    id SERIAL PRIMARY KEY,
    artikelnummer VARCHAR(50) UNIQUE NOT NULL,
    artikelname VARCHAR(255) NOT NULL,
    beschreibung TEXT,
    kategorie VARCHAR(100),
    einheit VARCHAR(20),
    einkaufspreis DECIMAL(10,2),
    verkaufspreis DECIMAL(10,2),
    mwst_satz DECIMAL(5,2) DEFAULT 19.00,
    mindestbestand DECIMAL(10,2),
    lagerort VARCHAR(100),
    lieferant_id INTEGER,
    barcode VARCHAR(100),
    aktiv BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_artikel_nummer ON inventory_artikel(artikelnummer);
CREATE INDEX idx_artikel_name ON inventory_artikel(artikelname);
CREATE INDEX idx_artikel_kategorie ON inventory_artikel(kategorie);
CREATE INDEX idx_artikel_barcode ON inventory_artikel(barcode);

-- Lagerbestand
CREATE TABLE IF NOT EXISTS inventory_lagerbestand (
    id SERIAL PRIMARY KEY,
    artikel_id INTEGER REFERENCES inventory_artikel(id) ON DELETE CASCADE,
    lagerort VARCHAR(100) NOT NULL,
    menge DECIMAL(10,2) NOT NULL DEFAULT 0,
    reserviert DECIMAL(10,2) DEFAULT 0,
    verfuegbar DECIMAL(10,2) GENERATED ALWAYS AS (menge - reserviert) STORED,
    letzter_zugang DATE,
    letzter_abgang DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lagerbestand_artikel ON inventory_lagerbestand(artikel_id);
CREATE INDEX idx_lagerbestand_ort ON inventory_lagerbestand(lagerort);

-- Lagerbewegungen
CREATE TABLE IF NOT EXISTS inventory_bewegungen (
    id SERIAL PRIMARY KEY,
    artikel_id INTEGER REFERENCES inventory_artikel(id) ON DELETE CASCADE,
    bewegungsart VARCHAR(50) NOT NULL,
    menge DECIMAL(10,2) NOT NULL,
    lagerort VARCHAR(100),
    referenz_typ VARCHAR(50),
    referenz_id INTEGER,
    bemerkung TEXT,
    buchungsdatum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von VARCHAR(100)
);

CREATE INDEX idx_bewegungen_artikel ON inventory_bewegungen(artikel_id);
CREATE INDEX idx_bewegungen_datum ON inventory_bewegungen(buchungsdatum);
CREATE INDEX idx_bewegungen_art ON inventory_bewegungen(bewegungsart);

-- ============================================================================
-- 6. EINKAUF MODUL
-- ============================================================================

-- Lieferanten
CREATE TABLE IF NOT EXISTS einkauf_lieferanten (
    id SERIAL PRIMARY KEY,
    lieferantennummer VARCHAR(50) UNIQUE NOT NULL,
    firmenname VARCHAR(255) NOT NULL,
    ansprechpartner VARCHAR(255),
    email VARCHAR(255),
    telefon VARCHAR(50),
    strasse VARCHAR(255),
    plz VARCHAR(20),
    ort VARCHAR(100),
    land VARCHAR(100) DEFAULT 'Deutschland',
    zahlungsbedingungen TEXT,
    lieferzeit_tage INTEGER,
    bewertung INTEGER,
    aktiv BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lieferanten_nummer ON einkauf_lieferanten(lieferantennummer);
CREATE INDEX idx_lieferanten_name ON einkauf_lieferanten(firmenname);

-- Bestellungen
CREATE TABLE IF NOT EXISTS einkauf_bestellungen (
    id SERIAL PRIMARY KEY,
    bestellnummer VARCHAR(50) UNIQUE NOT NULL,
    lieferant_id INTEGER REFERENCES einkauf_lieferanten(id),
    bestelldatum DATE NOT NULL,
    gewuenschtes_lieferdatum DATE,
    status VARCHAR(50) DEFAULT 'entwurf',
    netto_summe DECIMAL(12,2),
    mwst_betrag DECIMAL(12,2),
    brutto_summe DECIMAL(12,2),
    erstellt_von VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bestellungen_nummer ON einkauf_bestellungen(bestellnummer);
CREATE INDEX idx_bestellungen_lieferant ON einkauf_bestellungen(lieferant_id);
CREATE INDEX idx_bestellungen_status ON einkauf_bestellungen(status);

-- ============================================================================
-- TRIGGER FÜR AUTOMATISCHE TIMESTAMPS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger für alle Tabellen mit updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename LIKE '%crm_%' 
        OR tablename LIKE '%agrar_%' 
        OR tablename LIKE '%sales_%'
        OR tablename LIKE '%finance_%'
        OR tablename LIKE '%inventory_%'
        OR tablename LIKE '%einkauf_%'
    LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = t AND column_name = 'updated_at'
        ) THEN
            EXECUTE format('
                DROP TRIGGER IF EXISTS trg_update_%I ON %I;
                CREATE TRIGGER trg_update_%I 
                BEFORE UPDATE ON %I 
                FOR EACH ROW EXECUTE FUNCTION update_timestamp();
            ', t, t, t, t);
        END IF;
    END LOOP;
END $$;

-- ============================================================================
-- ABSCHLUSS
-- ============================================================================

SELECT 
    '✅ VALEO-NeuroERP Database erfolgreich initialisiert!' AS status,
    COUNT(DISTINCT table_name) AS anzahl_tabellen
FROM information_schema.tables
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';

