-- =====================================================
-- VALEO NeuroERP - Finanzbuchhaltung Schema
-- Enterprise ERP System - Finanzmodul
-- =====================================================

-- Schema fÃ¼r Finanzbuchhaltung
CREATE SCHEMA IF NOT EXISTS finanz;

-- =====================================================
-- KONTENPLAN UND BUCHHALTUNG
-- =====================================================

-- Kontenplan
CREATE TABLE IF NOT EXISTS finanz.konten (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kontonummer VARCHAR(20) UNIQUE NOT NULL,
    kontobezeichnung VARCHAR(255) NOT NULL,
    kontotyp VARCHAR(50) NOT NULL CHECK (kontotyp IN ('Aktiv', 'Passiv', 'Ertrag', 'Aufwand')),
    kontenklasse VARCHAR(10),
    kontengruppe VARCHAR(50),
    ist_aktiv BOOLEAN DEFAULT true,
    ist_steuerpflichtig BOOLEAN DEFAULT false,
    steuersatz DECIMAL(5,2),
    beschreibung TEXT,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BuchungssÃ¤tze
CREATE TABLE IF NOT EXISTS finanz.buchungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buchungsnummer VARCHAR(50) UNIQUE NOT NULL,
    buchungsdatum DATE NOT NULL,
    belegdatum DATE NOT NULL,
    belegnummer VARCHAR(50),
    buchungstext TEXT NOT NULL,
    sollkonto UUID REFERENCES finanz.konten(id),
    habenkonto UUID REFERENCES finanz.konten(id),
    betrag DECIMAL(15,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    steuerbetrag DECIMAL(15,2) DEFAULT 0,
    steuersatz DECIMAL(5,2) DEFAULT 0,
    buchungsart VARCHAR(50),
    referenz_typ VARCHAR(50),
    referenz_id UUID,
    ist_storniert BOOLEAN DEFAULT false,
    storno_buchung_id UUID REFERENCES finanz.buchungen(id),
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jahresabschluss
CREATE TABLE IF NOT EXISTS finanz.jahresabschluss (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jahr INTEGER NOT NULL,
    abschluss_typ VARCHAR(50) NOT NULL CHECK (abschluss_typ IN ('Monat', 'Quartal', 'Jahr')),
    periode_start DATE NOT NULL,
    periode_ende DATE NOT NULL,
    erloese DECIMAL(15,2) DEFAULT 0,
    aufwendungen DECIMAL(15,2) DEFAULT 0,
    gewinn_verlust DECIMAL(15,2) DEFAULT 0,
    aktiva DECIMAL(15,2) DEFAULT 0,
    passiva DECIMAL(15,2) DEFAULT 0,
    eigenkapital DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Entwurf' CHECK (status IN ('Entwurf', 'Freigegeben', 'Geschlossen')),
    freigegeben_von UUID REFERENCES users(id),
    freigegeben_am TIMESTAMP,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jahr, abschluss_typ, periode_start)
);

-- =====================================================
-- DEBITORENBUCHHALTUNG
-- =====================================================

-- Debitoren (Kunden)
CREATE TABLE IF NOT EXISTS finanz.debitoren (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunden_id UUID REFERENCES customers(id),
    debitor_nr VARCHAR(20) UNIQUE NOT NULL,
    kreditlimit DECIMAL(15,2) DEFAULT 0,
    zahlungsziel INTEGER DEFAULT 30,
    zahlungsart VARCHAR(50),
    bankverbindung TEXT,
    steuernummer VARCHAR(50),
    ust_id VARCHAR(50),
    ist_aktiv BOOLEAN DEFAULT true,
    notizen TEXT,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Debitoren-Rechnungen
CREATE TABLE IF NOT EXISTS finanz.debitoren_rechnungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rechnungsnummer VARCHAR(50) UNIQUE NOT NULL,
    debitor_id UUID REFERENCES finanz.debitoren(id),
    rechnungsdatum DATE NOT NULL,
    faelligkeitsdatum DATE NOT NULL,
    netto_betrag DECIMAL(15,2) NOT NULL,
    steuerbetrag DECIMAL(15,2) DEFAULT 0,
    brutto_betrag DECIMAL(15,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(50) DEFAULT 'Offen' CHECK (status IN ('Offen', 'Teilzahlung', 'Bezahlt', 'Mahnung', 'Storniert')),
    bezahlt_am DATE,
    bezahlter_betrag DECIMAL(15,2) DEFAULT 0,
    restbetrag DECIMAL(15,2) DEFAULT 0,
    mahnstufe INTEGER DEFAULT 0,
    letzte_mahnung DATE,
    referenz_typ VARCHAR(50),
    referenz_id UUID,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Debitoren-Zahlungen
CREATE TABLE IF NOT EXISTS finanz.debitoren_zahlungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zahlungsnummer VARCHAR(50) UNIQUE NOT NULL,
    rechnung_id UUID REFERENCES finanz.debitoren_rechnungen(id),
    zahlungsdatum DATE NOT NULL,
    zahlungsart VARCHAR(50) NOT NULL,
    zahlungsbetrag DECIMAL(15,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    zahlungsreferenz VARCHAR(100),
    zahlungsinfo TEXT,
    status VARCHAR(50) DEFAULT 'Eingegangen' CHECK (status IN ('Eingegangen', 'Verarbeitet', 'Storniert')),
    verarbeitet_am TIMESTAMP,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KREDITORENBUCHHALTUNG
-- =====================================================

-- Kreditoren (Lieferanten)
CREATE TABLE IF NOT EXISTS finanz.kreditoren (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferanten_id UUID REFERENCES suppliers(id),
    kreditor_nr VARCHAR(20) UNIQUE NOT NULL,
    zahlungsziel INTEGER DEFAULT 30,
    zahlungsart VARCHAR(50),
    bankverbindung TEXT,
    steuernummer VARCHAR(50),
    ust_id VARCHAR(50),
    ist_aktiv BOOLEAN DEFAULT true,
    notizen TEXT,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kreditoren-Rechnungen
CREATE TABLE IF NOT EXISTS finanz.kreditoren_rechnungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rechnungsnummer VARCHAR(50) UNIQUE NOT NULL,
    kreditor_id UUID REFERENCES finanz.kreditoren(id),
    lieferanten_rechnungsnr VARCHAR(50),
    rechnungsdatum DATE NOT NULL,
    faelligkeitsdatum DATE NOT NULL,
    netto_betrag DECIMAL(15,2) NOT NULL,
    steuerbetrag DECIMAL(15,2) DEFAULT 0,
    brutto_betrag DECIMAL(15,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(50) DEFAULT 'Offen' CHECK (status IN ('Offen', 'Teilzahlung', 'Bezahlt', 'Storniert')),
    bezahlt_am DATE,
    bezahlter_betrag DECIMAL(15,2) DEFAULT 0,
    restbetrag DECIMAL(15,2) DEFAULT 0,
    referenz_typ VARCHAR(50),
    referenz_id UUID,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kreditoren-Zahlungen
CREATE TABLE IF NOT EXISTS finanz.kreditoren_zahlungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zahlungsnummer VARCHAR(50) UNIQUE NOT NULL,
    rechnung_id UUID REFERENCES finanz.kreditoren_rechnungen(id),
    zahlungsdatum DATE NOT NULL,
    zahlungsart VARCHAR(50) NOT NULL,
    zahlungsbetrag DECIMAL(15,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    zahlungsreferenz VARCHAR(100),
    zahlungsinfo TEXT,
    status VARCHAR(50) DEFAULT 'Geplant' CHECK (status IN ('Geplant', 'AusgefÃ¼hrt', 'Storniert')),
    ausgefuehrt_am TIMESTAMP,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KASSEN- UND BANKENVERWALTUNG
-- =====================================================

-- Bankkonten
CREATE TABLE IF NOT EXISTS finanz.bankkonten (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kontoname VARCHAR(100) NOT NULL,
    bankname VARCHAR(100) NOT NULL,
    iban VARCHAR(34),
    bic VARCHAR(11),
    kontonummer VARCHAR(50),
    blz VARCHAR(10),
    waehrung VARCHAR(3) DEFAULT 'EUR',
    kontostand DECIMAL(15,2) DEFAULT 0,
    letzter_abgleich DATE,
    ist_aktiv BOOLEAN DEFAULT true,
    notizen TEXT,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kassen
CREATE TABLE IF NOT EXISTS finanz.kassen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kassenname VARCHAR(100) NOT NULL,
    kassentyp VARCHAR(50) NOT NULL CHECK (kassentyp IN ('Hauptkasse', 'Nebenkasse', 'Reisekasse')),
    waehrung VARCHAR(3) DEFAULT 'EUR',
    kassenstand DECIMAL(15,2) DEFAULT 0,
    letzter_abgleich DATE,
    verantwortlicher UUID REFERENCES users(id),
    ist_aktiv BOOLEAN DEFAULT true,
    notizen TEXT,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kassenbewegungen
CREATE TABLE IF NOT EXISTS finanz.kassenbewegungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kasse_id UUID REFERENCES finanz.kassen(id),
    bewegungstyp VARCHAR(50) NOT NULL CHECK (bewegungstyp IN ('Einzahlung', 'Auszahlung')),
    betrag DECIMAL(15,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    bewegungsdatum DATE NOT NULL,
    bewegungszeit TIME NOT NULL,
    zahlungsart VARCHAR(50),
    buchung_id UUID REFERENCES finanz.buchungen(id),
    beschreibung TEXT,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bankbewegungen
CREATE TABLE IF NOT EXISTS finanz.bankbewegungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bankkonto_id UUID REFERENCES finanz.bankkonten(id),
    bewegungstyp VARCHAR(50) NOT NULL CHECK (bewegungstyp IN ('Einzahlung', 'Auszahlung')),
    betrag DECIMAL(15,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    bewegungsdatum DATE NOT NULL,
    wertstellung DATE,
    verwendungszweck TEXT,
    buchung_id UUID REFERENCES finanz.buchungen(id),
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- STEUERN UND ABGABEN
-- =====================================================

-- SteuersÃ¤tze
CREATE TABLE IF NOT EXISTS finanz.steuersaetze (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    steuername VARCHAR(100) NOT NULL,
    steuersatz DECIMAL(5,2) NOT NULL,
    steuerart VARCHAR(50) NOT NULL CHECK (steuerart IN ('Umsatzsteuer', 'Vorsteuer', 'Lohnsteuer', 'Gewerbesteuer')),
    ist_aktiv BOOLEAN DEFAULT true,
    gueltig_ab DATE NOT NULL,
    gueltig_bis DATE,
    beschreibung TEXT,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SteuererklÃ¤rungen
CREATE TABLE IF NOT EXISTS finanz.steuererklaerungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    steuerart VARCHAR(50) NOT NULL,
    jahr INTEGER NOT NULL,
    periode VARCHAR(20),
    meldedatum DATE NOT NULL,
    faelligkeitsdatum DATE NOT NULL,
    meldebetrag DECIMAL(15,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Offen' CHECK (status IN ('Offen', 'Gemeldet', 'Bezahlt')),
    bezahlt_am DATE,
    bezahlter_betrag DECIMAL(15,2) DEFAULT 0,
    notizen TEXT,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KOSTENSTELLEN UND KOSTENTRÃ„GER
-- =====================================================

-- Kostenstellen
CREATE TABLE IF NOT EXISTS finanz.kostenstellen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kostenstellen_nr VARCHAR(20) UNIQUE NOT NULL,
    bezeichnung VARCHAR(255) NOT NULL,
    beschreibung TEXT,
    kostenstellen_typ VARCHAR(50),
    verantwortlicher UUID REFERENCES users(id),
    ist_aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KostentrÃ¤ger
CREATE TABLE IF NOT EXISTS finanz.kostentraeger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kostentraeger_nr VARCHAR(20) UNIQUE NOT NULL,
    bezeichnung VARCHAR(255) NOT NULL,
    beschreibung TEXT,
    kostentraeger_typ VARCHAR(50),
    verantwortlicher UUID REFERENCES users(id),
    ist_aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID REFERENCES users(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXE
-- =====================================================

-- Konten-Indexe
CREATE INDEX IF NOT EXISTS idx_konten_kontonummer ON finanz.konten(kontonummer);
CREATE INDEX IF NOT EXISTS idx_konten_kontotyp ON finanz.konten(kontotyp);
CREATE INDEX IF NOT EXISTS idx_konten_aktiv ON finanz.konten(ist_aktiv);

-- Buchungen-Indexe
CREATE INDEX IF NOT EXISTS idx_buchungen_datum ON finanz.buchungen(buchungsdatum);
CREATE INDEX IF NOT EXISTS idx_buchungen_belegnummer ON finanz.buchungen(belegnummer);
CREATE INDEX IF NOT EXISTS idx_buchungen_sollkonto ON finanz.buchungen(sollkonto);
CREATE INDEX IF NOT EXISTS idx_buchungen_habenkonto ON finanz.buchungen(habenkonto);
CREATE INDEX IF NOT EXISTS idx_buchungen_referenz ON finanz.buchungen(referenz_typ, referenz_id);

-- Debitoren-Indexe
CREATE INDEX IF NOT EXISTS idx_debitoren_nr ON finanz.debitoren(debitoren_nr);
CREATE INDEX IF NOT EXISTS idx_debitoren_kunden ON finanz.debitoren(kunden_id);
CREATE INDEX IF NOT EXISTS idx_debitoren_rechnungen_datum ON finanz.debitoren_rechnungen(rechnungsdatum);
CREATE INDEX IF NOT EXISTS idx_debitoren_rechnungen_status ON finanz.debitoren_rechnungen(status);
CREATE INDEX IF NOT EXISTS idx_debitoren_rechnungen_faellig ON finanz.debitoren_rechnungen(faelligkeitsdatum);

-- Kreditoren-Indexe
CREATE INDEX IF NOT EXISTS idx_kreditoren_nr ON finanz.kreditoren(kreditor_nr);
CREATE INDEX IF NOT EXISTS idx_kreditoren_lieferanten ON finanz.kreditoren(lieferanten_id);
CREATE INDEX IF NOT EXISTS idx_kreditoren_rechnungen_datum ON finanz.kreditoren_rechnungen(rechnungsdatum);
CREATE INDEX IF NOT EXISTS idx_kreditoren_rechnungen_status ON finanz.kreditoren_rechnungen(status);

-- Bank- und Kassen-Indexe
CREATE INDEX IF NOT EXISTS idx_bankkonten_name ON finanz.bankkonten(kontoname);
CREATE INDEX IF NOT EXISTS idx_kassen_name ON finanz.kassen(kassenname);
CREATE INDEX IF NOT EXISTS idx_kassenbewegungen_datum ON finanz.kassenbewegungen(bewegungsdatum);
CREATE INDEX IF NOT EXISTS idx_bankbewegungen_datum ON finanz.bankbewegungen(bewegungsdatum);

-- =====================================================
-- TRIGGER
-- =====================================================

-- Update-Timestamp-Trigger
CREATE OR REPLACE FUNCTION update_finanz_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.aktualisiert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_konten_updated_at BEFORE UPDATE ON finanz.konten
    FOR EACH ROW EXECUTE FUNCTION update_finanz_updated_at();

CREATE TRIGGER update_buchungen_updated_at BEFORE UPDATE ON finanz.buchungen
    FOR EACH ROW EXECUTE FUNCTION update_finanz_updated_at();

CREATE TRIGGER update_debitoren_updated_at BEFORE UPDATE ON finanz.debitoren
    FOR EACH ROW EXECUTE FUNCTION update_finanz_updated_at();

CREATE TRIGGER update_kreditoren_updated_at BEFORE UPDATE ON finanz.kreditoren
    FOR EACH ROW EXECUTE FUNCTION update_finanz_updated_at();

-- =====================================================
-- VIEWS
-- =====================================================

-- Kontenplan-Ãœbersicht
CREATE OR REPLACE VIEW finanz.kontenplan_uebersicht AS
SELECT 
    k.kontonummer,
    k.kontobezeichnung,
    k.kontotyp,
    k.kontenklasse,
    k.kontengruppe,
    k.ist_aktiv,
    COALESCE(soll.betrag, 0) as soll_betrag,
    COALESCE(haben.betrag, 0) as haben_betrag,
    COALESCE(soll.betrag, 0) - COALESCE(haben.betrag, 0) as saldo
FROM finanz.konten k
LEFT JOIN (
    SELECT sollkonto, SUM(betrag) as betrag 
    FROM finanz.buchungen 
    WHERE ist_storniert = false 
    GROUP BY sollkonto
) soll ON k.id = soll.sollkonto
LEFT JOIN (
    SELECT habenkonto, SUM(betrag) as betrag 
    FROM finanz.buchungen 
    WHERE ist_storniert = false 
    GROUP BY habenkonto
) haben ON k.id = haben.habenkonto
WHERE k.ist_aktiv = true
ORDER BY k.kontonummer;

-- Debitoren-Ãœbersicht
CREATE OR REPLACE VIEW finanz.debitoren_uebersicht AS
SELECT 
    d.debitoren_nr,
    c.name as kundenname,
    d.kreditlimit,
    d.zahlungsziel,
    COALESCE(offen.betrag, 0) as offene_betraege,
    COALESCE(ueberfaellig.betrag, 0) as ueberfaellige_betraege,
    d.kreditlimit - COALESCE(offen.betrag, 0) as verfuegbares_kreditlimit
FROM finanz.debitoren d
JOIN customers c ON d.kunden_id = c.id
LEFT JOIN (
    SELECT debitor_id, SUM(restbetrag) as betrag
    FROM finanz.debitoren_rechnungen
    WHERE status IN ('Offen', 'Teilzahlung')
    GROUP BY debitor_id
) offen ON d.id = offen.debitor_id
LEFT JOIN (
    SELECT debitor_id, SUM(restbetrag) as betrag
    FROM finanz.debitoren_rechnungen
    WHERE status IN ('Offen', 'Teilzahlung') AND faelligkeitsdatum < CURRENT_DATE
    GROUP BY debitor_id
) ueberfaellig ON d.id = ueberfaellig.debitor_id
WHERE d.ist_aktiv = true;

-- Kreditoren-Ãœbersicht
CREATE OR REPLACE VIEW finanz.kreditoren_uebersicht AS
SELECT 
    k.kreditor_nr,
    s.name as lieferantenname,
    k.zahlungsziel,
    COALESCE(offen.betrag, 0) as offene_betraege,
    COALESCE(ueberfaellig.betrag, 0) as ueberfaellige_betraege
FROM finanz.kreditoren k
JOIN suppliers s ON k.lieferanten_id = s.id
LEFT JOIN (
    SELECT kreditor_id, SUM(restbetrag) as betrag
    FROM finanz.kreditoren_rechnungen
    WHERE status IN ('Offen', 'Teilzahlung')
    GROUP BY kreditor_id
) offen ON k.id = offen.kreditor_id
LEFT JOIN (
    SELECT kreditor_id, SUM(restbetrag) as betrag
    FROM finanz.kreditoren_rechnungen
    WHERE status IN ('Offen', 'Teilzahlung') AND faelligkeitsdatum < CURRENT_DATE
    GROUP BY kreditor_id
) ueberfaellig ON k.id = ueberfaellig.kreditor_id
WHERE k.ist_aktiv = true;

-- =====================================================
-- FUNKTIONEN
-- =====================================================

-- Automatische Buchungsnummer generieren
CREATE OR REPLACE FUNCTION finanz.generate_buchungsnummer()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_num INTEGER;
    buchungsnummer VARCHAR(50);
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(buchungsnummer FROM 4) AS INTEGER)), 0) + 1
    INTO next_num
    FROM finanz.buchungen
    WHERE buchungsnummer LIKE 'BCH%';
    
    buchungsnummer := 'BCH' || LPAD(next_num::TEXT, 8, '0');
    RETURN buchungsnummer;
END;
$$ LANGUAGE plpgsql;

-- Automatische Rechnungsnummer generieren
CREATE OR REPLACE FUNCTION finanz.generate_rechnungsnummer(rechnungs_typ VARCHAR(10))
RETURNS VARCHAR(50) AS $$
DECLARE
    next_num INTEGER;
    rechnungsnummer VARCHAR(50);
    year_prefix VARCHAR(4);
BEGIN
    year_prefix := EXTRACT(YEAR FROM CURRENT_DATE)::TEXT;
    
    IF rechnungs_typ = 'DEBITOR' THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(rechnungsnummer FROM 9) AS INTEGER)), 0) + 1
        INTO next_num
        FROM finanz.debitoren_rechnungen
        WHERE rechnungsnummer LIKE 'RECH-DEB-' || year_prefix || '%';
        
        rechnungsnummer := 'RECH-DEB-' || year_prefix || '-' || LPAD(next_num::TEXT, 6, '0');
    ELSE
        SELECT COALESCE(MAX(CAST(SUBSTRING(rechnungsnummer FROM 9) AS INTEGER)), 0) + 1
        INTO next_num
        FROM finanz.kreditoren_rechnungen
        WHERE rechnungsnummer LIKE 'RECH-KRED-' || year_prefix || '%';
        
        rechnungsnummer := 'RECH-KRED-' || year_prefix || '-' || LPAD(next_num::TEXT, 6, '0');
    END IF;
    
    RETURN rechnungsnummer;
END;
$$ LANGUAGE plpgsql;

-- Saldo fÃ¼r ein Konto berechnen
CREATE OR REPLACE FUNCTION finanz.get_kontosaldo(konto_id UUID, bis_datum DATE DEFAULT CURRENT_DATE)
RETURNS DECIMAL(15,2) AS $$
DECLARE
    soll_betrag DECIMAL(15,2);
    haben_betrag DECIMAL(15,2);
    saldo DECIMAL(15,2);
BEGIN
    SELECT COALESCE(SUM(betrag), 0)
    INTO soll_betrag
    FROM finanz.buchungen
    WHERE sollkonto = konto_id 
    AND buchungsdatum <= bis_datum 
    AND ist_storniert = false;
    
    SELECT COALESCE(SUM(betrag), 0)
    INTO haben_betrag
    FROM finanz.buchungen
    WHERE habenkonto = konto_id 
    AND buchungsdatum <= bis_datum 
    AND ist_storniert = false;
    
    saldo := soll_betrag - haben_betrag;
    RETURN saldo;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TESTDATEN
-- =====================================================

-- Standard-Kontenplan einfÃ¼gen
INSERT INTO finanz.konten (kontonummer, kontobezeichnung, kontotyp, kontenklasse, kontengruppe) VALUES
('1000', 'Kasse', 'Aktiv', '1', 'UmlaufvermÃ¶gen'),
('1200', 'Bankkonto', 'Aktiv', '1', 'UmlaufvermÃ¶gen'),
('1400', 'Forderungen aus Lieferungen und Leistungen', 'Aktiv', '1', 'UmlaufvermÃ¶gen'),
('1600', 'Vorsteuer', 'Aktiv', '1', 'UmlaufvermÃ¶gen'),
('2000', 'Verbindlichkeiten aus Lieferungen und Leistungen', 'Passiv', '2', 'Kurzfristige Verbindlichkeiten'),
('2200', 'Verbindlichkeiten gegenÃ¼ber FinanzÃ¤mtern', 'Passiv', '2', 'Kurzfristige Verbindlichkeiten'),
('2400', 'Verbindlichkeiten gegenÃ¼ber Sozialversicherung', 'Passiv', '2', 'Kurzfristige Verbindlichkeiten'),
('3000', 'Eigenkapital', 'Passiv', '3', 'Eigenkapital'),
('4000', 'UmsatzerlÃ¶se', 'Ertrag', '4', 'ErtrÃ¤ge'),
('5000', 'Wareneingang', 'Aufwand', '5', 'Aufwendungen'),
('6000', 'Personalaufwand', 'Aufwand', '6', 'Aufwendungen'),
('7000', 'Raumkosten', 'Aufwand', '7', 'Aufwendungen'),
('8000', 'Abschreibungen', 'Aufwand', '8', 'Aufwendungen');

-- Standard-SteuersÃ¤tze
INSERT INTO finanz.steuersaetze (steuername, steuersatz, steuerart, gueltig_ab) VALUES
('Umsatzsteuer 19%', 19.00, 'Umsatzsteuer', '2024-01-01'),
('Umsatzsteuer 7%', 7.00, 'Umsatzsteuer', '2024-01-01'),
('Vorsteuer 19%', 19.00, 'Vorsteuer', '2024-01-01'),
('Vorsteuer 7%', 7.00, 'Vorsteuer', '2024-01-01');

COMMIT; 
