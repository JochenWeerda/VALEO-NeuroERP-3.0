-- =============================================================================
-- Create articles table in domain_inventory schema
-- Matches SQLAlchemy model: app/infrastructure/models/__init__.py (class Article)
-- =============================================================================

BEGIN;

-- Create schemas if not exist
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_agrar;

-- Ensure tenants table exists (articles FK references it)
CREATE TABLE IF NOT EXISTS domain_shared.tenants (
    id UUID PRIMARY KEY DEFAULT '00000000-0000-0000-0000-000000000001',
    name VARCHAR(255) NOT NULL DEFAULT 'Default Tenant',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
INSERT INTO domain_shared.tenants (id, name)
VALUES ('00000000-0000-0000-0000-000000000001', 'Default Tenant')
ON CONFLICT (id) DO NOTHING;

-- Create articles table
CREATE TABLE IF NOT EXISTS domain_inventory.articles (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- Basic identification
    article_number VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    description2 TEXT,
    short_description VARCHAR(200),
    suchbegriff VARCHAR(100),
    matchcode2 VARCHAR(100),
    hersteller VARCHAR(120),
    herkunftsland VARCHAR(2),
    naehrwertangaben TEXT,

    -- Flags
    mhd_erforderlich BOOLEAN NOT NULL DEFAULT FALSE,
    lagerartikel BOOLEAN NOT NULL DEFAULT TRUE,
    mehrwertsteuer_prozent NUMERIC(5, 2),
    warengruppe VARCHAR(80),

    -- Dangerous goods
    gefahrgutklasse VARCHAR(40),
    gefahrgut_un_nummer VARCHAR(20),
    gefahrgut_verpackungsgruppe VARCHAR(5),
    gefahrgut_anhaenge VARCHAR(200),

    -- Storage
    lagerorte JSONB NOT NULL DEFAULT '[]',
    chargenpflicht BOOLEAN NOT NULL DEFAULT FALSE,
    qs_pruefung_erforderlich BOOLEAN NOT NULL DEFAULT FALSE,
    zolltarifnummer VARCHAR(30),
    bio_kennzeichnung BOOLEAN NOT NULL DEFAULT FALSE,
    gmp_plus_relevanz BOOLEAN NOT NULL DEFAULT FALSE,

    -- Extended labeling
    kennzeichnung_bio VARCHAR(50),
    kennzeichnung_vegan VARCHAR(10),
    kennzeichnung_vegetarisch VARCHAR(10),
    kennzeichnung_allergene TEXT,
    kennzeichnung_herkunft VARCHAR(100),

    -- Extended storage
    lager_min_temperatur NUMERIC(5, 1),
    lager_max_temperatur NUMERIC(5, 1),
    lager_lagerdauer_tage INTEGER,
    lager_zentral BOOLEAN DEFAULT FALSE,
    lager_silo BOOLEAN DEFAULT FALSE,

    -- Extended analysis
    analyse_protein NUMERIC(5, 2),
    analyse_feuchtigkeit NUMERIC(5, 2),
    analyse_schadex NUMERIC(5, 2),
    analyse_fremdstoffe NUMERIC(5, 2),
    analyse_sonstiges TEXT,

    -- Search filter fields
    ean_code VARCHAR(50),
    alt_ean_code VARCHAR(50),
    lieferanten_artikelnummer VARCHAR(50),
    kunden_artikelnummer VARCHAR(50),
    verwendungszweck VARCHAR(255),
    nachhaltige_biomasse BOOLEAN DEFAULT FALSE,
    pool_artikel BOOLEAN DEFAULT FALSE,

    -- Discount/Surcharge fields
    rabatt_auftrag_rechnung NUMERIC(5, 2),
    rabatt_lose NUMERIC(5, 2),
    rabatt_selbstabholer NUMERIC(5, 2),
    zu_abschlag_1_code VARCHAR(50),
    zu_abschlag_1_prozent NUMERIC(5, 2),
    zu_abschlag_2_code VARCHAR(50),
    zu_abschlag_2_prozent NUMERIC(5, 2),
    berechne_zu_abschlag_auf_netto BOOLEAN DEFAULT FALSE,
    einfuegen_summe_nach_zu_abschlag BOOLEAN DEFAULT FALSE,

    -- Discount flags
    skontofaehig BOOLEAN DEFAULT TRUE,
    warenrueckverguetung BOOLEAN DEFAULT FALSE,
    bonus_faehig BOOLEAN DEFAULT FALSE,
    rabattfaehig BOOLEAN DEFAULT TRUE,

    -- Extended Einheiten (alternative units)
    einheit_typ VARCHAR(20),
    einheit_faktor NUMERIC(10, 4),
    einheit_preiseinheit VARCHAR(20),
    gebinde_groesse NUMERIC(10, 2),
    gebinde_einheit VARCHAR(20),

    -- Extended Kennzeichnung (barcode, etikett, web, intrastat)
    etikett_druck BOOLEAN DEFAULT FALSE,
    etikett_preis_je_1kg BOOLEAN DEFAULT FALSE,
    etikett_vorlage VARCHAR(100),
    etikett_abweichende_bezugsgroesse NUMERIC(10, 2),
    web_sichtbar BOOLEAN DEFAULT FALSE,
    web_preis_auf_anfrage BOOLEAN DEFAULT FALSE,
    intrastat_warennr VARCHAR(20),

    -- Process flags
    kontrakt_erlaubt BOOLEAN DEFAULT TRUE,
    chargen_nr_erforderlich BOOLEAN DEFAULT FALSE,
    serien_nr_erforderlich BOOLEAN DEFAULT FALSE,
    bioware BOOLEAN DEFAULT FALSE,
    waage_artikel BOOLEAN DEFAULT FALSE,
    pflanzenschutzmittel BOOLEAN DEFAULT FALSE,
    explosionsstoff BOOLEAN DEFAULT FALSE,
    nur_einzelverkauf BOOLEAN DEFAULT FALSE,
    artikel_umbuchung_bei_ls_freigabe BOOLEAN DEFAULT FALSE,

    -- Additional fields
    haltbarkeit_tage INTEGER,
    regal_flaeche VARCHAR(50),
    min_menge_auftrag NUMERIC(10, 2),
    kostenstelle VARCHAR(50),

    -- Link to nutrient composition (Duengemittel)
    duengemittel_inhalte_id VARCHAR,
    duengemittel_inhalte_bezeichnung VARCHAR(255),

    -- Extended LH/Agrar fields
    kaufabrechnung VARCHAR(50),
    mva_kontrakt BOOLEAN DEFAULT FALSE,
    mahlerzeugnis VARCHAR(50),
    schnittstelle_artikel_nr VARCHAR(50),
    schnittstelle_waage_nr VARCHAR(50),
    schnittstelle_produkt_nr VARCHAR(50),
    waage_etikett_art VARCHAR(10),
    nawaro_endprodukt BOOLEAN DEFAULT FALSE,
    getreidemeldung_formular_spalte VARCHAR(50),
    getreidemeldung_herkunft VARCHAR(50),
    mvo_bereich VARCHAR(50),
    mvo_gruppe VARCHAR(50),
    mvo_erzeugnis VARCHAR(50),
    mvo_bestandsgroesse VARCHAR(50),

    -- Extended analysis
    analyse_text TEXT,
    analyse_bild_datei VARCHAR(255),

    -- Print settings
    druck_anfrage BOOLEAN DEFAULT FALSE,
    druck_angebot BOOLEAN DEFAULT FALSE,
    druck_auftragsbestaetigung BOOLEAN DEFAULT FALSE,
    druck_lieferschein BOOLEAN DEFAULT FALSE,
    druck_rechnung BOOLEAN DEFAULT FALSE,
    druck_kontrakt BOOLEAN DEFAULT FALSE,
    druck_wiegeschein BOOLEAN DEFAULT FALSE,
    druck_statt_artikel_bezeichnung BOOLEAN DEFAULT FALSE,
    druck_zusaetzlich BOOLEAN DEFAULT FALSE,

    -- Base fields
    lieferantennummer VARCHAR(50),
    unit VARCHAR(10) NOT NULL DEFAULT 'ST',
    category VARCHAR(50),
    subcategory VARCHAR(50),
    barcode VARCHAR(50),
    supplier_number VARCHAR(50),
    customer_article_number VARCHAR(50),
    purchase_price NUMERIC(10, 2),
    sales_price NUMERIC(10, 2),
    currency VARCHAR(3) DEFAULT 'EUR',
    min_stock NUMERIC(10, 2),
    max_stock NUMERIC(10, 2),
    weight NUMERIC(8, 2),
    dimensions VARCHAR(50),
    current_stock NUMERIC(10, 2) DEFAULT 0,
    reserved_stock NUMERIC(10, 2) DEFAULT 0,
    available_stock NUMERIC(10, 2) DEFAULT 0,

    -- Tenant and timestamps
    tenant_id VARCHAR(36) NOT NULL DEFAULT '00000000-0000-0000-0000-000000000001',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_articles_article_number ON domain_inventory.articles(article_number);
CREATE INDEX IF NOT EXISTS idx_articles_name ON domain_inventory.articles(name);
CREATE INDEX IF NOT EXISTS idx_articles_warengruppe ON domain_inventory.articles(warengruppe);
CREATE INDEX IF NOT EXISTS idx_articles_category ON domain_inventory.articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_tenant_id ON domain_inventory.articles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_articles_ean_code ON domain_inventory.articles(ean_code);
CREATE INDEX IF NOT EXISTS idx_articles_is_active ON domain_inventory.articles(is_active);

-- Add comments
COMMENT ON TABLE domain_inventory.articles IS 'Article/Product master data table';
COMMENT ON COLUMN domain_inventory.articles.article_number IS 'Unique article number';
COMMENT ON COLUMN domain_inventory.articles.name IS 'Article name';
COMMENT ON COLUMN domain_inventory.articles.warengruppe IS 'Warengruppe/Artikelgruppe';
COMMENT ON COLUMN domain_inventory.articles.tenant_id IS 'Multi-tenant identifier (UUID as text)';

COMMIT;
