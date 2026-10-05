-- ============================================================================
-- L3 Migration: Kundenstamm Table
-- Source: L3 ERP Kunden-Maske
-- Generated: 2025-10-26
-- ============================================================================

-- Kunden-Haupttabelle
CREATE TABLE IF NOT EXISTS kunden (
    -- Primary Key
    kunden_nr VARCHAR(20) PRIMARY KEY,
    
    -- Allgemein
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geloescht BOOLEAN DEFAULT FALSE,
    
    -- Kunden-Anschrift
    name1 VARCHAR(100) NOT NULL,
    name2 VARCHAR(100),
    strasse VARCHAR(100),
    plz VARCHAR(10),
    ort VARCHAR(100),
    tel VARCHAR(50),
    email VARCHAR(100),
    
    -- Rechnung/Kontoauszug
    kontonutzung_rechnung BOOLEAN DEFAULT FALSE,
    kontoauszug_gewuenscht BOOLEAN DEFAULT FALSE,
    saldo_druck_rechnung BOOLEAN DEFAULT FALSE,
    druck_verbot_rechnung BOOLEAN DEFAULT FALSE,
    versandpauschalen_berechnen BOOLEAN DEFAULT FALSE,
    einzel_abrechnung VARCHAR(20) CHECK (einzel_abrechnung IN ('Einzel', 'Sammel')),
    sammel_abrechnungskennzeichen VARCHAR(50),
    bonus_rechnungsempfaenger_id VARCHAR(20) REFERENCES kunden(kunden_nr),
    selbstabrechnung_durch_kunden BOOLEAN DEFAULT FALSE,
    kunden_zusatz TEXT,
    
    -- Kundenrabatte
    rabatt_liste_id INTEGER REFERENCES rabatt_listen(id),
    rabatt_liste_speichern BOOLEAN DEFAULT FALSE,
    
    -- Preise / Rabatte
    direktes_konto BOOLEAN DEFAULT FALSE,
    rabatt_verrechnung VARCHAR(20) CHECK (rabatt_verrechnung IN ('Sofort', 'Nachträglich')),
    selbstabholer_rabatt DECIMAL(5,2) DEFAULT 0 CHECK (selbstabholer_rabatt >= 0 AND selbstabholer_rabatt <= 100),
    preisermittlung_sorten BOOLEAN DEFAULT FALSE,
    direktabzug BOOLEAN DEFAULT FALSE,
    wochenpreis_ec_basis BOOLEAN DEFAULT FALSE,
    gueltig_ab DATE,
    gueltig_bis DATE,
    
    -- Bank / Zahlungsverkehr
    zahlungsbedingungen_tage INTEGER CHECK (zahlungsbedingungen_tage >= 0 AND zahlungsbedingungen_tage <= 365),
    skonto DECIMAL(5,2) DEFAULT 0 CHECK (skonto >= 0 AND skonto <= 100),
    netto_kasse BOOLEAN DEFAULT FALSE,
    mahnwesen BOOLEAN DEFAULT FALSE,
    lastschriftverfahren VARCHAR(20) CHECK (lastschriftverfahren IN ('SEPA', 'Mandat', 'Keines')),
    iban VARCHAR(34),
    bic VARCHAR(11),
    umrechnung_euro BOOLEAN DEFAULT FALSE,
    waehrung VARCHAR(3) DEFAULT 'EUR' CHECK (waehrung IN ('EUR', 'USD', 'GBP', 'CHF')),
    zinstabelle_id INTEGER REFERENCES zinstabellen(id),
    letzter_zinstermin DATE,
    saldo_letzte_zinsabrechnung DECIMAL(12,2) DEFAULT 0,
    verrechnung_automatisch BOOLEAN DEFAULT FALSE,
    
    -- Wegbeschreibung
    lade_information TEXT,
    allgemeine_angaben TEXT,
    
    -- Sonstiges
    nachkalkulation BOOLEAN DEFAULT FALSE,
    formular_id INTEGER REFERENCES formulare(id),
    offene_posten_nicht_aufrufen BOOLEAN DEFAULT FALSE,
    versicherung BOOLEAN DEFAULT FALSE,
    sprachschluessel VARCHAR(2) DEFAULT 'DE' CHECK (sprachschluessel IN ('DE', 'EN', 'FR', 'NL')),
    statistik_kennzeichen VARCHAR(50),
    landwirtschaftsamt_betriebsnummer VARCHAR(50),
    marktpreis_auswertung BOOLEAN DEFAULT FALSE,
    schwellenwert DECIMAL(12,2) DEFAULT 0 CHECK (schwellenwert >= 0),
    webshop_kunde BOOLEAN DEFAULT FALSE,
    
    -- Selektionen
    selektion_schluessel VARCHAR(50),
    selektion_berechnung TEXT,
    
    -- Schnittstelle
    tankkarte_ean_code VARCHAR(50),
    kundenkarten_kennzeichen VARCHAR(50),
    edifact_invoic BOOLEAN DEFAULT FALSE,
    edifact_orders BOOLEAN DEFAULT FALSE,
    edifact_desadv BOOLEAN DEFAULT FALSE,
    rechnungs_sammeldruck BOOLEAN DEFAULT FALSE,
    webshop_kunden_nr VARCHAR(50),
    webshop_bezeichnung VARCHAR(200)
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_kunden_name1 ON kunden(name1);
CREATE INDEX IF NOT EXISTS idx_kunden_email ON kunden(email);
CREATE INDEX IF NOT EXISTS idx_kunden_plz ON kunden(plz);
CREATE INDEX IF NOT EXISTS idx_kunden_webshop_kunde ON kunden(webshop_kunde);
CREATE INDEX IF NOT EXISTS idx_kunden_geloescht ON kunden(geloescht);

-- Full-Text-Search Index für Suche
CREATE INDEX IF NOT EXISTS idx_kunden_search ON kunden USING gin(to_tsvector('german', 
    COALESCE(name1, '') || ' ' || 
    COALESCE(name2, '') || ' ' || 
    COALESCE(kunden_nr, '') || ' ' || 
    COALESCE(email, '')
));

-- Kommentare für Dokumentation
COMMENT ON TABLE kunden IS 'Kundenstamm-Datenbanktabelle basierend auf L3 ERP Kunden-Maske';
COMMENT ON COLUMN kunden.kunden_nr IS 'Eindeutige Kundennummer (Primary Key)';
COMMENT ON COLUMN kunden.name1 IS 'Hauptname des Kunden';
COMMENT ON COLUMN kunden.email IS 'E-Mail-Adresse für Kommunikation';
COMMENT ON COLUMN kunden.iban IS 'Internationale Bankkontonummer (SEPA)';
COMMENT ON COLUMN kunden.bic IS 'Bank Identifier Code';
COMMENT ON COLUMN kunden.selbstabholer_rabatt IS 'Rabatt in Prozent für Selbstabholer (0-100)';
COMMENT ON COLUMN kunden.skonto IS 'Skonto-Rabatt in Prozent (0-100)';
COMMENT ON COLUMN kunden.schwellenwert IS 'Mindestumsatz-Schwellenwert für Marktpreis-Auswertung';

-- ============================================================================
-- Zusätzliche Hilfstabellen für Relations
-- ============================================================================

-- Rabatt-Listen (für Lookup)
CREATE TABLE IF NOT EXISTS rabatt_listen (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    aktiv BOOLEAN DEFAULT TRUE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Zinstabellen (für Lookup)
CREATE TABLE IF NOT EXISTS zinstabellen (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    soll_zins DECIMAL(5,2) DEFAULT 0,
    haben_zins DECIMAL(5,2) DEFAULT 0,
    aktiv BOOLEAN DEFAULT TRUE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Formulare (für Lookup)
CREATE TABLE IF NOT EXISTS formulare (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    datei_path VARCHAR(500),
    aktiv BOOLEAN DEFAULT TRUE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Seed-Daten für Testzwecke
-- ============================================================================

INSERT INTO rabatt_listen (name, beschreibung) VALUES
    ('Standard-Rabatt', 'Standard-Rabatt für alle Kunden'),
    ('VIP-Rabatt', 'Erhöhter Rabatt für VIP-Kunden'),
    ('Selbstabholer-Rabatt', 'Rabatt für Selbstabholer')
ON CONFLICT DO NOTHING;

INSERT INTO zinstabellen (name, soll_zins, haben_zins) VALUES
    ('Standard Soll/Zins', 8.0, 2.0),
    ('Landwirtschaft Soll/Zins', 6.0, 1.5)
ON CONFLICT DO NOTHING;

INSERT INTO formulare (name, beschreibung) VALUES
    ('Rechnung Standard', 'Standard-Rechnungsformular'),
    ('Lieferschein A4', 'Lieferschein im A4-Format')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Stored Procedures / Functions (Optional)
-- ============================================================================

-- Funktion: Aktualisiere geaendert_am automatisch
CREATE OR REPLACE FUNCTION update_kunden_geaendert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geaendert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger für automatische Update-Zeitstempel
CREATE TRIGGER trigger_kunden_geaendert_am
    BEFORE UPDATE ON kunden
    FOR EACH ROW
    EXECUTE FUNCTION update_kunden_geaendert_am();

-- ============================================================================
-- Migration Notes
-- ============================================================================
-- 1. Die Tabelle wurde aus L3 ERP Kunden-Maske extrahiert
-- 2. Alle Felder wurden 1:1 aus L3 übernommen
-- 3. Foreign Keys zu: kunden (bonus_rechnungsempfaenger), rabatt_listen, zinstabellen, formulare
-- 4. Indizes für häufig abgefragte Felder hinzugefügt
-- 5. Full-Text-Search für schnelle Kunden-Suche implementiert
-- 6. Constraints für Datenintegrität (CHECK, REFERENCES)

