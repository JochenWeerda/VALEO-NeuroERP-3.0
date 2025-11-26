#!/usr/bin/env python3
"""
Generiert vollständige SQL-CREATE-Statements für alle 14 Kundenstamm-Tabellen
"""

SQL_HEADER = """-- ============================================================================
-- L3 Migration: Kundenstamm - COMPLETE TABLES
-- Source: L3 ERP Kunden-Maske (ChatGPT-Analyse + Bestehendes Schema)
-- Generated: 2025-10-26
-- Total Tables: 14
-- Total Fields: ~200
-- ============================================================================

"""

SQL_TABLES = {
    "kunden": """
-- ============================================================================
-- Tabellen-ID: 1/14
-- Kunden Haupttabelle (60 Felder)
-- ============================================================================

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
    name3 VARCHAR(100),
    strasse VARCHAR(100),
    plz VARCHAR(10),
    ort VARCHAR(100),
    land VARCHAR(100),
    postfach VARCHAR(10),
    postfach_plz VARCHAR(10),
    postfach_ort VARCHAR(100),
    tel VARCHAR(50),
    fax VARCHAR(50),
    email VARCHAR(100),
    homepage VARCHAR(200),
    
    -- Rechnung/Kontoauszug
    kontonutzung_rechnung BOOLEAN DEFAULT FALSE,
    kontoauszug_gewuenscht BOOLEAN DEFAULT FALSE,
    saldo_druck_rechnung BOOLEAN DEFAULT FALSE,
    druck_verbot_rechnung BOOLEAN DEFAULT FALSE,
    druck_werbetext BOOLEAN DEFAULT FALSE,
    versandpauschalen_berechnen BOOLEAN DEFAULT FALSE,
    einzel_abrechnung VARCHAR(20) CHECK (einzel_abrechnung IN ('Einzel', 'Sammel')),
    sammel_abrechnung BOOLEAN DEFAULT FALSE,
    sammel_abrechnung_ohne_einzel BOOLEAN DEFAULT FALSE,
    sammel_abrechnungskennzeichen VARCHAR(50),
    bonus_berechtigung BOOLEAN DEFAULT FALSE,
    bonus_rechnungsempfaenger_id VARCHAR(20) REFERENCES kunden(kunden_nr),
    bemerkenswerte_forderung BOOLEAN DEFAULT FALSE,
    selbstabrechnung_durch_kunden BOOLEAN DEFAULT FALSE,
    selbstabrechner_verkauf_zukauf VARCHAR(50),
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
    sepa_verfahren BOOLEAN DEFAULT FALSE,
    mandat BOOLEAN DEFAULT FALSE,
    bank VARCHAR(200),
    iban VARCHAR(34),
    bic VARCHAR(11),
    umrechnung_euro BOOLEAN DEFAULT FALSE,
    umrechnungskurs DECIMAL(10,4),
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

-- Indizes
CREATE INDEX IF NOT EXISTS idx_kunden_name1 ON kunden(name1);
CREATE INDEX IF NOT EXISTS idx_kunden_email ON kunden(email);
CREATE INDEX IF NOT EXISTS idx_kunden_plz ON kunden(plz);
CREATE INDEX IF NOT EXISTS idx_kunden_webshop_kunde ON kunden(webshop_kunde);
CREATE INDEX IF NOT EXISTS idx_kunden_geloescht ON kunden(geloescht);

-- Full-Text-Search
CREATE INDEX IF NOT EXISTS idx_kunden_search ON kunden USING gin(to_tsvector('german', 
    COALESCE(name1, '') || ' ' || 
    COALESCE(name2, '') || ' ' || 
    COALESCE(kunden_nr, '') || ' ' || 
    COALESCE(email, '')
));

-- Trigger für automatische Update-Zeitstempel
CREATE OR REPLACE FUNCTION update_kunden_geaendert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geaendert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_kunden_geaendert_am
    BEFORE UPDATE ON kunden
    FOR EACH ROW
    EXECUTE FUNCTION update_kunden_geaendert_am();

""",

    "kunden_profil": """
-- ============================================================================
-- Tabellen-ID: 2/14
-- Kundenprofil (13 Felder)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_profil (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    firmenname VARCHAR(200),
    gruendung DATE,
    jahresumsatz DECIMAL(15,2),
    berufsgenossenschaft VARCHAR(100),
    berufsgen_nr VARCHAR(50),
    branche VARCHAR(100),
    mitbewerber VARCHAR(200),
    engpaesse TEXT,
    organisationsstruktur TEXT,
    mitarbeiteranzahl INTEGER CHECK (mitarbeiteranzahl >= 0),
    wettbewerbsdifferenzierung TEXT,
    betriebsrat BOOLEAN DEFAULT FALSE,
    unternehmensphilosophie TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_profil_branche ON kunden_profil(branche);
CREATE INDEX IF NOT EXISTS idx_kunden_profil_gruendung ON kunden_profil(gruendung);

""",

    "kunden_ansprechpartner": """
-- ============================================================================
-- Tabellen-ID: 3/14
-- Kunden-Ansprechpartner (21 Felder) - MEHRFACH!
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_ansprechpartner (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    prioritaet INTEGER DEFAULT 0,
    vorname VARCHAR(100),
    nachname VARCHAR(100),
    position VARCHAR(100),
    abteilung VARCHAR(100),
    telefon1 VARCHAR(50),
    telefon2 VARCHAR(50),
    mobil VARCHAR(50),
    email VARCHAR(100),
    strasse VARCHAR(100),
    plz VARCHAR(10),
    ort VARCHAR(100),
    anrede VARCHAR(20),
    briefanrede VARCHAR(50),
    geburtsdatum DATE,
    hobbys TEXT,
    info1 TEXT,
    info2 TEXT,
    empfanger_rechnung_email BOOLEAN DEFAULT FALSE,
    empfanger_mahnung_email BOOLEAN DEFAULT FALSE,
    kontaktart VARCHAR(50),
    erstanlage DATE,
    cad_system VARCHAR(100),
    softwaresysteme VARCHAR(200),
    datenschutzbeauftragter BOOLEAN DEFAULT FALSE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_ansprechpartner_kunden_nr ON kunden_ansprechpartner(kunden_nr);
CREATE INDEX IF NOT EXISTS idx_kunden_ansprechpartner_email ON kunden_ansprechpartner(email);
CREATE INDEX IF NOT EXISTS idx_kunden_ansprechpartner_prioritaet ON kunden_ansprechpartner(prioritaet);

""",

    "kunden_versand": """
-- ============================================================================
-- Tabellen-ID: 4/14
-- Versandinformationen (6 Felder)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_versand (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    versandart_rechnung VARCHAR(50),
    versandart_mahnung VARCHAR(50),
    versandart_kontakt VARCHAR(50),
    dispo_nummer VARCHAR(50),
    initialisierungsweisung TEXT,
    versandmedium VARCHAR(50) CHECK (versandmedium IN ('Brief', 'E-Mail', 'ZUGFeRD', 'Kombiniert')),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

""",

    "kunden_lieferung_zahlung": """
-- ============================================================================
-- Tabellen-ID: 5/14
-- Lieferung/Zahlung (6 Felder)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_lieferung_zahlung (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    lieferbedingung VARCHAR(100),
    zahlungsbedingung VARCHAR(100),
    faelligkeit_ab VARCHAR(50) CHECK (faelligkeit_ab IN ('Rechnungsdatum', 'Termin', 'Valuta')),
    pro_forma_rechnung BOOLEAN DEFAULT FALSE,
    pro_forma_rabatt1 DECIMAL(5,2) CHECK (pro_forma_rabatt1 >= 0 AND pro_forma_rabatt1 <= 100),
    pro_forma_rabatt2 DECIMAL(5,2) CHECK (pro_forma_rabatt2 >= 0 AND pro_forma_rabatt2 <= 100),
    einzel_sammelversand_avis VARCHAR(50),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

""",

    "kunden_datenschutz": """
-- ============================================================================
-- Tabellen-ID: 6/14
-- Datenschutz (4 Felder)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_datenschutz (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    einwilligung BOOLEAN DEFAULT FALSE,
    anlagedatum DATE,
    anlagebearbeiter VARCHAR(100),
    zusatzbemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_datenschutz_einwilligung ON kunden_datenschutz(einwilligung);

""",

    "kunden_genossenschaft": """
-- ============================================================================
-- Tabellen-ID: 7/14
-- Genossenschaftsanteile (8 Felder)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_genossenschaft (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    geschaeftsguthaben_konto VARCHAR(50),
    mitgliedschaft_gekuendigt BOOLEAN DEFAULT FALSE,
    kuendigungsgrund TEXT,
    datum_kuendigung DATE,
    datum_austritt DATE,
    mitgliedsnummer VARCHAR(50),
    pflichtanteile INTEGER DEFAULT 0 CHECK (pflichtanteile >= 0),
    eintrittsdatum DATE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_genossenschaft_mitgliedsnummer ON kunden_genossenschaft(mitgliedsnummer);

""",

    "kunden_email_verteiler": """
-- ============================================================================
-- Tabellen-ID: 8/14
-- E-Mail-Verteiler (3 Felder) - MEHRFACH!
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_email_verteiler (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    verteilername VARCHAR(100),
    bezeichnung VARCHAR(200),
    email VARCHAR(100),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_email_verteiler_kunden_nr ON kunden_email_verteiler(kunden_nr);
CREATE INDEX IF NOT EXISTS idx_kunden_email_verteiler_email ON kunden_email_verteiler(email);

""",

    "kunden_betriebsgemeinschaften": """
-- ============================================================================
-- Tabellen-ID: 9/14
-- Betriebsgemeinschaften (4 Felder) - MEHRFACH!
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_betriebsgemeinschaften (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    verbundnummer VARCHAR(50),
    mitglieder_kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    anteil_prozent DECIMAL(5,2) CHECK (anteil_prozent >= 0 AND anteil_prozent <= 100),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_betriebsgemeinschaften_kunden_nr ON kunden_betriebsgemeinschaften(kunden_nr);
CREATE INDEX IF NOT EXISTS idx_kunden_betriebsgemeinschaften_verbundnummer ON kunden_betriebsgemeinschaften(verbundnummer);

""",

    "kunden_freitext": """
-- ============================================================================
-- Tabellen-ID: 10/14
-- Freitext / Chef-Anweisung (3 Felder)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_freitext (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    chef_anweisung TEXT,
    langtext TEXT,
    bemerkungen TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

""",

    "kunden_allgemein_erweitert": """
-- ============================================================================
-- Tabellen-ID: 11/14
-- Allgemein Erweitert (15 Felder)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_allgemein_erweitert (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    staat VARCHAR(100),
    bundesland VARCHAR(100),
    kunde_seit DATE,
    debitoren_konto VARCHAR(50),
    deb_kto_hauptkonto VARCHAR(50),
    disponent VARCHAR(100),
    vertriebsbeauftragter VARCHAR(100),
    abc_umsatzstatus VARCHAR(50),
    betriebsnummer VARCHAR(50),
    ust_id_nr VARCHAR(50),
    steuernummer VARCHAR(50),
    sperrgrund TEXT,
    kundengruppe VARCHAR(100),
    fax_sperre BOOLEAN DEFAULT FALSE,
    infofeld4 TEXT,
    infofeld5 TEXT,
    infofeld6 TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_allgemein_erweitert_debitoren_konto ON kunden_allgemein_erweitert(debitoren_konto);
CREATE INDEX IF NOT EXISTS idx_kunden_allgemein_erweitert_kundengruppe ON kunden_allgemein_erweitert(kundengruppe);

""",

    "kunden_cpd_konto": """
-- ============================================================================
-- Tabellen-ID: 12/14
-- CPD-Konto (12 Felder) - MEHRFACH!
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_cpd_konto (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    debitoren_konto VARCHAR(50),
    suchbegriff VARCHAR(100),
    rechnungsadresse TEXT,
    geschaeftsstelle VARCHAR(100),
    kostenstelle VARCHAR(100),
    rechnungsart VARCHAR(50),
    sammelrechnung BOOLEAN DEFAULT FALSE,
    rechnungsformular VARCHAR(100),
    vb VARCHAR(100),
    gebiet VARCHAR(100),
    zahlungsbedingungen TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_cpd_konto_kunden_nr ON kunden_cpd_konto(kunden_nr);
CREATE INDEX IF NOT EXISTS idx_kunden_cpd_konto_debitoren_konto ON kunden_cpd_konto(debitoren_konto);

""",

    "kunden_rabatte_detail": """
-- ============================================================================
-- Tabellen-ID: 13/14
-- Kundenrabatte Detail (6 Felder) - MEHRFACH!
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_rabatte_detail (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    artikel_nr VARCHAR(50),
    bezeichnung VARCHAR(200),
    rabatt DECIMAL(5,2) CHECK (rabatt >= 0 AND rabatt <= 100),
    rabatt_gueltig_bis DATE,
    rabatt_liste_id INTEGER REFERENCES rabatt_listen(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_rabatte_detail_kunden_nr ON kunden_rabatte_detail(kunden_nr);
CREATE INDEX IF NOT EXISTS idx_kunden_rabatte_detail_artikel_nr ON kunden_rabatte_detail(artikel_nr);

""",

    "kunden_preise_detail": """
-- ============================================================================
-- Tabellen-ID: 14/14
-- Vereinbarte Kundenpreise Detail (10 Felder) - MEHRFACH!
-- ============================================================================

CREATE TABLE IF NOT EXISTS kunden_preise_detail (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr) ON DELETE CASCADE,
    artikel_nr VARCHAR(50),
    bezeichnung VARCHAR(200),
    preis_netto DECIMAL(10,2),
    preis_inkl_fracht DECIMAL(10,2),
    preis_einheit VARCHAR(20),
    rabatt_erlaubt BOOLEAN DEFAULT TRUE,
    sonderfracht DECIMAL(10,2),
    zahlungsbedingung VARCHAR(100),
    gueltig_bis DATE,
    bediener VARCHAR(100),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kunden_preise_detail_kunden_nr ON kunden_preise_detail(kunden_nr);
CREATE INDEX IF NOT EXISTS idx_kunden_preise_detail_artikel_nr ON kunden_preise_detail(artikel_nr);

"""
}

SQL_HELPER_TABLES = """
-- ============================================================================
-- HILFSTABELLEN (Für Lookups)
-- ============================================================================

-- Rabatt-Listen
CREATE TABLE IF NOT EXISTS rabatt_listen (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    aktiv BOOLEAN DEFAULT TRUE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Zinstabellen
CREATE TABLE IF NOT EXISTS zinstabellen (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    soll_zins DECIMAL(5,2) DEFAULT 0,
    haben_zins DECIMAL(5,2) DEFAULT 0,
    aktiv BOOLEAN DEFAULT TRUE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Formulare
CREATE TABLE IF NOT EXISTS formulare (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    datei_path VARCHAR(500),
    aktiv BOOLEAN DEFAULT TRUE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SEED-DATEN
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

"""

SQL_FOOTER = """
-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================
-- 
-- Tabellen: 14 Haupttabellen + 3 Hilfstabellen = 17 Tabellen gesamt
-- Felder: ~200 Felder gesamt
-- 
-- Foreign Keys:
-- - Alle Untertabellen → kunden(kunden_nr) ON DELETE CASCADE
-- - Bonus-Rechnungsempfänger → kunden(kunden_nr) [self-reference]
-- - Betriebsgemeinschaften Mitglieder → kunden(kunden_nr)
-- 
-- Indizes: Für Performance auf häufig abgefragten Feldern
-- Constraints: CHECK für Datenintegrität
-- Triggers: Automatische Update-Zeitstempel
-- 
-- Migration Strategy:
-- 1. Import bestehender L3-Daten in kunden-Haupttabelle
-- 2. Daten auf Untertabellen verteilen (wenn verfügbar)
-- 3. Relations validieren
-- 4. Indizes optimieren
-- 
-- ============================================================================
"""

def generate_sql():
    """Generiert vollständiges SQL-CREATE-Statement"""
    
    sql_content = SQL_HEADER
    
    # ERST: Hilfstabellen (müssen vor Haupttabellen existieren wegen Foreign Keys)
    sql_content += SQL_HELPER_TABLES
    sql_content += "\n"
    
    # DANN: Haupttabellen
    for table_name, table_sql in SQL_TABLES.items():
        sql_content += table_sql
        sql_content += "\n"
    
    # Footer
    sql_content += SQL_FOOTER
    
    return sql_content

if __name__ == "__main__":
    # Generiere SQL
    sql_output = generate_sql()
    
    # Speichere in Datei
    output_file = "schemas/sql/kundenstamm_complete.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_output)
    
    print("=" * 80)
    print("✅ SQL-GENERATOR ABGESCHLOSSEN")
    print("=" * 80)
    print(f"\n📄 Datei erstellt: {output_file}")
    print(f"📊 Tabellen: 14 Haupttabellen + 3 Hilfstabellen = 17 gesamt")
    print(f"📋 Felder: ~200 Felder")
    print(f"\n🎯 Nächste Schritte:")
    print(f"   1. SQL-Review durchführen")
    print(f"   2. In PostgreSQL importieren:")
    print(f"      psql -U valeo -d valeo_neuro_erp -f {output_file}")
    print(f"   3. Mask Builder JSON erstellen (nächster Schritt)")

