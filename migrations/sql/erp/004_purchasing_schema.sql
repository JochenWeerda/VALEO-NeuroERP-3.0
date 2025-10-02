-- =====================================================
-- EINKAUFSMANAGEMENT SCHEMA
-- =====================================================

-- Schema erstellen
CREATE SCHEMA IF NOT EXISTS einkauf;

-- 1. GRUNDLEGENDE EINKAUFSSTRUKTUREN
-- Lieferanten
CREATE TABLE einkauf.lieferanten (
    lieferant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferant_nr VARCHAR(50) UNIQUE NOT NULL,
    firmenname VARCHAR(200) NOT NULL,
    ansprechpartner VARCHAR(100),
    telefon VARCHAR(50),
    email VARCHAR(100),
    webseite VARCHAR(200),
    steuernummer VARCHAR(50),
    ust_id VARCHAR(50),
    zahlungsziel INTEGER DEFAULT 30,
    skonto_prozent DECIMAL(5,2) DEFAULT 0,
    skonto_tage INTEGER DEFAULT 0,
    kategorie VARCHAR(50) CHECK (kategorie IN ('A', 'B', 'C', 'DÃœNGER', 'FUTTERMITTEL', 'PSM', 'MASCHINEN', 'DIENSTLEISTUNG')),
    status VARCHAR(20) DEFAULT 'AKTIV' CHECK (status IN ('AKTIV', 'INAKTIV', 'GESPERRT')),
    bewertung INTEGER CHECK (bewertung >= 1 AND bewertung <= 5),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Lieferanten-Adressen
CREATE TABLE einkauf.lieferanten_adressen (
    adresse_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferant_id UUID NOT NULL REFERENCES einkauf.lieferanten(lieferant_id) ON DELETE CASCADE,
    adress_typ VARCHAR(20) NOT NULL CHECK (adress_typ IN ('RECHNUNG', 'LIEFERUNG', 'HAUPTADRESSE')),
    strasse VARCHAR(200) NOT NULL,
    hausnummer VARCHAR(20),
    plz VARCHAR(10) NOT NULL,
    ort VARCHAR(100) NOT NULL,
    land VARCHAR(50) DEFAULT 'Deutschland',
    ist_standard BOOLEAN DEFAULT FALSE,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lieferanten-Bankverbindungen
CREATE TABLE einkauf.lieferanten_bankverbindungen (
    bankverbindung_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferant_id UUID NOT NULL REFERENCES einkauf.lieferanten(lieferant_id) ON DELETE CASCADE,
    kontoinhaber VARCHAR(200) NOT NULL,
    iban VARCHAR(34) NOT NULL,
    bic VARCHAR(11),
    bank_name VARCHAR(200),
    verwendungszweck VARCHAR(200),
    ist_standard BOOLEAN DEFAULT FALSE,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. ARTIKEL- UND PREISVERWALTUNG
-- Lieferanten-Artikel
CREATE TABLE einkauf.lieferanten_artikel (
    lieferanten_artikel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferant_id UUID NOT NULL REFERENCES einkauf.lieferanten(lieferant_id) ON DELETE CASCADE,
    artikel_id UUID REFERENCES produktion.artikel(artikel_id),
    lieferanten_artikel_nr VARCHAR(100),
    bezeichnung VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    einheit VARCHAR(20) NOT NULL,
    mindestbestellmenge DECIMAL(10,4) DEFAULT 0,
    lieferzeit_tage INTEGER DEFAULT 1,
    verpackungseinheit DECIMAL(10,4) DEFAULT 1,
    verpackungsart VARCHAR(50),
    status VARCHAR(20) DEFAULT 'AKTIV' CHECK (status IN ('AKTIV', 'INAKTIV', 'GESPERRT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lieferanten-Preise
CREATE TABLE einkauf.lieferanten_preise (
    preis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferanten_artikel_id UUID NOT NULL REFERENCES einkauf.lieferanten_artikel(lieferanten_artikel_id) ON DELETE CASCADE,
    preistyp VARCHAR(20) NOT NULL CHECK (preistyp IN ('LISTENPREIS', 'RABATT', 'SONDERPREIS')),
    menge_von DECIMAL(10,4) NOT NULL,
    menge_bis DECIMAL(10,4),
    preis DECIMAL(10,4) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    gueltig_von DATE NOT NULL,
    gueltig_bis DATE,
    rabatt_prozent DECIMAL(5,2) DEFAULT 0,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. BESTELLWESEN
-- Bestellungen
CREATE TABLE einkauf.bestellungen (
    bestellung_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bestellung_nr VARCHAR(50) UNIQUE NOT NULL,
    lieferant_id UUID NOT NULL REFERENCES einkauf.lieferanten(lieferant_id),
    bestell_datum DATE NOT NULL,
    liefer_datum DATE,
    bestell_typ VARCHAR(20) DEFAULT 'NORMAL' CHECK (bestell_typ IN ('NORMAL', 'DRINGEND', 'RAHMENBESTELLUNG', 'VORBESTELLUNG')),
    status VARCHAR(20) DEFAULT 'ERSTELLT' CHECK (status IN ('ERSTELLT', 'BESTÃ„TIGT', 'TEILLIEFERUNG', 'VOLLSTÃ„NDIG', 'STORNIERT')),
    gesamtbetrag DECIMAL(12,2) DEFAULT 0,
    mwst_betrag DECIMAL(12,2) DEFAULT 0,
    skonto_betrag DECIMAL(12,2) DEFAULT 0,
    zahlungsziel DATE,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Bestellpositionen
CREATE TABLE einkauf.bestellpositionen (
    position_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bestellung_id UUID NOT NULL REFERENCES einkauf.bestellungen(bestellung_id) ON DELETE CASCADE,
    lieferanten_artikel_id UUID NOT NULL REFERENCES einkauf.lieferanten_artikel(lieferanten_artikel_id),
    position_nr INTEGER NOT NULL,
    bestellmenge DECIMAL(10,4) NOT NULL,
    gelieferte_menge DECIMAL(10,4) DEFAULT 0,
    einheitspreis DECIMAL(10,4) NOT NULL,
    rabatt_prozent DECIMAL(5,2) DEFAULT 0,
    mwst_prozent DECIMAL(5,2) DEFAULT 19,
    gesamtpreis DECIMAL(12,2) GENERATED ALWAYS AS (
        bestellmenge * einheitspreis * (1 - rabatt_prozent / 100)
    ) STORED,
    liefer_datum DATE,
    status VARCHAR(20) DEFAULT 'OFFEN' CHECK (status IN ('OFFEN', 'TEILLIEFERUNG', 'VOLLSTÃ„NDIG', 'STORNIERT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. LIEFERUNGEN UND WARENEINGANG
-- Lieferungen
CREATE TABLE einkauf.lieferungen (
    lieferung_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferung_nr VARCHAR(50) UNIQUE NOT NULL,
    bestellung_id UUID REFERENCES einkauf.bestellungen(bestellung_id),
    lieferant_id UUID NOT NULL REFERENCES einkauf.lieferanten(lieferant_id),
    liefer_datum DATE NOT NULL,
    liefer_zeit TIME,
    lkw_kennzeichen VARCHAR(20),
    fahrer_name VARCHAR(100),
    lieferung_typ VARCHAR(20) DEFAULT 'NORMAL' CHECK (lieferung_typ IN ('NORMAL', 'DRINGEND', 'NACHTLIEFERUNG')),
    status VARCHAR(20) DEFAULT 'ANGEKÃœNDIGT' CHECK (status IN ('ANGEKÃœNDIGT', 'UNTERWEGS', 'ANGEKOMMEN', 'ENTLADEN', 'ABGESCHLOSSEN')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Lieferpositionen
CREATE TABLE einkauf.lieferpositionen (
    lieferposition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferung_id UUID NOT NULL REFERENCES einkauf.lieferungen(lieferung_id) ON DELETE CASCADE,
    bestellposition_id UUID REFERENCES einkauf.bestellpositionen(position_id),
    lieferanten_artikel_id UUID NOT NULL REFERENCES einkauf.lieferanten_artikel(lieferanten_artikel_id),
    position_nr INTEGER NOT NULL,
    gelieferte_menge DECIMAL(10,4) NOT NULL,
    einheitspreis DECIMAL(10,4),
    chargen_nr VARCHAR(100),
    mindesthaltbarkeit DATE,
    qualitaetspruefung_erforderlich BOOLEAN DEFAULT FALSE,
    qualitaetspruefung_durchgefuehrt BOOLEAN DEFAULT FALSE,
    qualitaetspruefung_ergebnis VARCHAR(20) CHECK (qualitaetspruefung_ergebnis IN ('POSITIV', 'NEGATIV', 'BEDINGT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. RECHNUNGSWESEN
-- Rechnungen
CREATE TABLE einkauf.rechnungen (
    rechnung_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rechnung_nr VARCHAR(50) UNIQUE NOT NULL,
    lieferant_id UUID NOT NULL REFERENCES einkauf.lieferanten(lieferant_id),
    bestellung_id UUID REFERENCES einkauf.bestellungen(bestellung_id),
    rechnungs_datum DATE NOT NULL,
    faelligkeits_datum DATE NOT NULL,
    rechnungs_betrag DECIMAL(12,2) NOT NULL,
    mwst_betrag DECIMAL(12,2) DEFAULT 0,
    skonto_betrag DECIMAL(12,2) DEFAULT 0,
    zahlungs_betrag DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'OFFEN' CHECK (status IN ('OFFEN', 'TEILZAHLUNG', 'VOLLSTÃ„NDIG', 'ÃœBERFÃ„LLIG', 'STORNIERT')),
    zahlungs_datum DATE,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Rechnungspositionen
CREATE TABLE einkauf.rechnungspositionen (
    rechnungsposition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rechnung_id UUID NOT NULL REFERENCES einkauf.rechnungen(rechnung_id) ON DELETE CASCADE,
    lieferanten_artikel_id UUID NOT NULL REFERENCES einkauf.lieferanten_artikel(lieferanten_artikel_id),
    position_nr INTEGER NOT NULL,
    menge DECIMAL(10,4) NOT NULL,
    einheitspreis DECIMAL(10,4) NOT NULL,
    rabatt_prozent DECIMAL(5,2) DEFAULT 0,
    mwst_prozent DECIMAL(5,2) DEFAULT 19,
    gesamtpreis DECIMAL(12,2) GENERATED ALWAYS AS (
        menge * einheitspreis * (1 - rabatt_prozent / 100)
    ) STORED,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. QUALITÃ„TSMANAGEMENT
-- QualitÃ¤tsprÃ¼fungen
CREATE TABLE einkauf.qualitaetspruefungen (
    pruefung_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pruefung_nr VARCHAR(50) UNIQUE NOT NULL,
    lieferung_id UUID REFERENCES einkauf.lieferungen(lieferung_id),
    lieferposition_id UUID REFERENCES einkauf.lieferpositionen(lieferposition_id),
    pruef_datum DATE NOT NULL,
    pruefer_id UUID,
    pruefung_typ VARCHAR(50) NOT NULL CHECK (pruefung_typ IN ('VISUELL', 'LABOR', 'GEWICHT', 'FEUCHTE', 'KEIMZAHL', 'TOXINE')),
    ergebnis VARCHAR(20) NOT NULL CHECK (ergebnis IN ('POSITIV', 'NEGATIV', 'BEDINGT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- 7. INDEXE
CREATE INDEX idx_lieferanten_status ON einkauf.lieferanten(status);
CREATE INDEX idx_lieferanten_kategorie ON einkauf.lieferanten(kategorie);
CREATE INDEX idx_bestellungen_status ON einkauf.bestellungen(status);
CREATE INDEX idx_bestellungen_datum ON einkauf.bestellungen(bestell_datum);
CREATE INDEX idx_lieferungen_status ON einkauf.lieferungen(status);
CREATE INDEX idx_lieferungen_datum ON einkauf.lieferungen(liefer_datum);
CREATE INDEX idx_rechnungen_status ON einkauf.rechnungen(status);
CREATE INDEX idx_rechnungen_faelligkeit ON einkauf.rechnungen(faelligkeits_datum);

-- 8. TRIGGER FÃœR AUTOMATISCHE TIMESTAMP-UPDATES
CREATE OR REPLACE FUNCTION einkauf.update_geaendert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geaendert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_lieferanten_update
    BEFORE UPDATE ON einkauf.lieferanten
    FOR EACH ROW EXECUTE FUNCTION einkauf.update_geaendert_am();

CREATE TRIGGER trigger_lieferanten_artikel_update
    BEFORE UPDATE ON einkauf.lieferanten_artikel
    FOR EACH ROW EXECUTE FUNCTION einkauf.update_geaendert_am();

CREATE TRIGGER trigger_bestellungen_update
    BEFORE UPDATE ON einkauf.bestellungen
    FOR EACH ROW EXECUTE FUNCTION einkauf.update_geaendert_am();

CREATE TRIGGER trigger_bestellpositionen_update
    BEFORE UPDATE ON einkauf.bestellpositionen
    FOR EACH ROW EXECUTE FUNCTION einkauf.update_geaendert_am();

CREATE TRIGGER trigger_lieferungen_update
    BEFORE UPDATE ON einkauf.lieferungen
    FOR EACH ROW EXECUTE FUNCTION einkauf.update_geaendert_am();

CREATE TRIGGER trigger_lieferpositionen_update
    BEFORE UPDATE ON einkauf.lieferpositionen
    FOR EACH ROW EXECUTE FUNCTION einkauf.update_geaendert_am();

CREATE TRIGGER trigger_rechnungen_update
    BEFORE UPDATE ON einkauf.rechnungen
    FOR EACH ROW EXECUTE FUNCTION einkauf.update_geaendert_am();

CREATE TRIGGER trigger_rechnungspositionen_update
    BEFORE UPDATE ON einkauf.rechnungspositionen
    FOR EACH ROW EXECUTE FUNCTION einkauf.update_geaendert_am();

-- 9. FUNKTIONEN FÃœR AUTOMATISCHE NUMMERIERUNG
CREATE OR REPLACE FUNCTION einkauf.generate_bestellnummer()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_num INTEGER;
    result VARCHAR(50);
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(bestellung_nr FROM 4) AS INTEGER)), 0) + 1
    INTO next_num
    FROM einkauf.bestellungen
    WHERE bestellung_nr LIKE 'BES%';
    
    result := 'BES' || LPAD(next_num::TEXT, 6, '0');
    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION einkauf.generate_liefernummer()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_num INTEGER;
    result VARCHAR(50);
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(lieferung_nr FROM 4) AS INTEGER)), 0) + 1
    INTO next_num
    FROM einkauf.lieferungen
    WHERE lieferung_nr LIKE 'LIE%';
    
    result := 'LIE' || LPAD(next_num::TEXT, 6, '0');
    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION einkauf.generate_rechnungsnummer()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_num INTEGER;
    result VARCHAR(50);
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(rechnung_nr FROM 4) AS INTEGER)), 0) + 1
    INTO next_num
    FROM einkauf.rechnungen
    WHERE rechnung_nr LIKE 'REK%';
    
    result := 'REK' || LPAD(next_num::TEXT, 6, '0');
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 10. FUNKTIONEN FÃœR BERECHNUNGEN
CREATE OR REPLACE FUNCTION einkauf.get_bestellwert(lieferant_uuid UUID)
RETURNS DECIMAL(12,2) AS $$
BEGIN
    RETURN COALESCE((
        SELECT SUM(b.gesamtbetrag)
        FROM einkauf.bestellungen b
        WHERE b.lieferant_id = lieferant_uuid
        AND b.status IN ('ERSTELLT', 'BESTÃ„TIGT', 'TEILLIEFERUNG')
    ), 0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION einkauf.get_offene_rechnungen(lieferant_uuid UUID)
RETURNS DECIMAL(12,2) AS $$
BEGIN
    RETURN COALESCE((
        SELECT SUM(r.rechnungs_betrag - r.zahlungs_betrag)
        FROM einkauf.rechnungen r
        WHERE r.lieferant_id = lieferant_uuid
        AND r.status IN ('OFFEN', 'TEILZAHLUNG', 'ÃœBERFÃ„LLIG')
    ), 0);
END;
$$ LANGUAGE plpgsql;

-- 11. VIEWS FÃœR REPORTING
-- EinkaufsÃ¼bersicht
CREATE VIEW einkauf.einkaufs_uebersicht AS
SELECT 
    l.lieferant_id,
    l.lieferant_nr,
    l.firmenname,
    l.kategorie,
    l.status,
    l.bewertung,
    COUNT(DISTINCT b.bestellung_id) as anzahl_bestellungen,
    COUNT(DISTINCT r.rechnung_id) as anzahl_rechnungen,
    einkauf.get_bestellwert(l.lieferant_id) as offene_bestellungen,
    einkauf.get_offene_rechnungen(l.lieferant_id) as offene_rechnungen,
    l.erstellt_am
FROM einkauf.lieferanten l
LEFT JOIN einkauf.bestellungen b ON l.lieferant_id = b.lieferant_id
LEFT JOIN einkauf.rechnungen r ON l.lieferant_id = r.lieferant_id
GROUP BY l.lieferant_id, l.lieferant_nr, l.firmenname, l.kategorie, l.status, l.bewertung, l.erstellt_am;

-- BestellÃ¼bersicht
CREATE VIEW einkauf.bestell_uebersicht AS
SELECT 
    b.bestellung_id,
    b.bestellung_nr,
    b.bestell_datum,
    b.liefer_datum,
    b.status,
    b.gesamtbetrag,
    l.firmenname as lieferant,
    l.kategorie as lieferant_kategorie,
    COUNT(bp.position_id) as anzahl_positionen,
    SUM(bp.bestellmenge) as gesamtmenge,
    SUM(bp.gelieferte_menge) as gelieferte_menge,
    CASE 
        WHEN SUM(bp.bestellmenge) > 0 THEN 
            ROUND((SUM(bp.gelieferte_menge) / SUM(bp.bestellmenge)) * 100, 2)
        ELSE 0 
    END as lieferfortschritt_prozent
FROM einkauf.bestellungen b
JOIN einkauf.lieferanten l ON b.lieferant_id = l.lieferant_id
LEFT JOIN einkauf.bestellpositionen bp ON b.bestellung_id = bp.bestellung_id
GROUP BY b.bestellung_id, b.bestellung_nr, b.bestell_datum, b.liefer_datum, b.status, b.gesamtbetrag, l.firmenname, l.kategorie;

-- RechnungsÃ¼bersicht
CREATE VIEW einkauf.rechnungs_uebersicht AS
SELECT 
    r.rechnung_id,
    r.rechnung_nr,
    r.rechnungs_datum,
    r.faelligkeits_datum,
    r.rechnungs_betrag,
    r.zahlungs_betrag,
    (r.rechnungs_betrag - r.zahlungs_betrag) as offener_betrag,
    r.status,
    l.firmenname as lieferant,
    l.kategorie as lieferant_kategorie,
    CASE 
        WHEN r.faelligkeits_datum < CURRENT_DATE AND r.status IN ('OFFEN', 'TEILZAHLUNG') 
        THEN CURRENT_DATE - r.faelligkeits_datum 
        ELSE 0 
    END as ueberfaellig_tage
FROM einkauf.rechnungen r
JOIN einkauf.lieferanten l ON r.lieferant_id = l.lieferant_id;

-- 12. BEISPIELDATEN
-- Lieferanten
INSERT INTO einkauf.lieferanten (lieferant_nr, firmenname, ansprechpartner, telefon, email, kategorie, bewertung) VALUES
('LIE001', 'Agrarhandel MÃ¼ller GmbH', 'Hans MÃ¼ller', '+49 123 456789', 'h.mueller@agrar-mueller.de', 'DÃœNGER', 5),
('LIE002', 'Futtermittel Schmidt KG', 'Maria Schmidt', '+49 234 567890', 'info@futter-schmidt.de', 'FUTTERMITTEL', 4),
('LIE003', 'PSM-Handel Weber', 'Peter Weber', '+49 345 678901', 'p.weber@psm-weber.de', 'PSM', 4),
('LIE004', 'Landmaschinen Bauer', 'Klaus Bauer', '+49 456 789012', 'k.bauer@landmaschinen-bauer.de', 'MASCHINEN', 5),
('LIE005', 'Transportdienst Meyer', 'Anna Meyer', '+49 567 890123', 'a.meyer@transport-meyer.de', 'DIENSTLEISTUNG', 3);

-- Lieferanten-Adressen
INSERT INTO einkauf.lieferanten_adressen (lieferant_id, adress_typ, strasse, hausnummer, plz, ort, ist_standard) VALUES
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE001'), 'HAUPTADRESSE', 'HauptstraÃŸe', '123', '12345', 'Musterstadt', TRUE),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE002'), 'HAUPTADRESSE', 'Industrieweg', '45', '23456', 'Beispielort', TRUE),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE003'), 'HAUPTADRESSE', 'Gewerbepark', '67', '34567', 'Testdorf', TRUE),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE004'), 'HAUPTADRESSE', 'MaschinenstraÃŸe', '89', '45678', 'Landstadt', TRUE),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE005'), 'HAUPTADRESSE', 'Transportweg', '12', '56789', 'Frachtort', TRUE);

-- Lieferanten-Artikel
INSERT INTO einkauf.lieferanten_artikel (lieferant_id, lieferanten_artikel_nr, bezeichnung, einheit, mindestbestellmenge, lieferzeit_tage) VALUES
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE001'), 'DNG001', 'NPK 15-15-15', 'kg', 1000, 3),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE001'), 'DNG002', 'Kalkammonsalpeter', 'kg', 500, 2),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE002'), 'FUT001', 'Schweinefutter', 'kg', 500, 5),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE002'), 'FUT002', 'Rinderfutter', 'kg', 1000, 5),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE003'), 'PSM001', 'Roundup', 'l', 100, 7),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE003'), 'PSM002', 'Fungizid X', 'l', 50, 7),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE004'), 'MAS001', 'Traktor Ersatzteile', 'StÃ¼ck', 1, 14),
((SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE005'), 'DIENST001', 'Transportdienst', 'Fahrt', 1, 1);

-- Lieferanten-Preise
INSERT INTO einkauf.lieferanten_preise (lieferanten_artikel_id, preistyp, menge_von, menge_bis, preis, gueltig_von) VALUES
((SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'DNG001'), 'LISTENPREIS', 1, 999, 0.85, CURRENT_DATE),
((SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'DNG001'), 'LISTENPREIS', 1000, 4999, 0.80, CURRENT_DATE),
((SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'DNG001'), 'LISTENPREIS', 5000, NULL, 0.75, CURRENT_DATE),
((SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'FUT001'), 'LISTENPREIS', 1, 999, 0.45, CURRENT_DATE),
((SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'FUT001'), 'LISTENPREIS', 1000, NULL, 0.42, CURRENT_DATE),
((SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'PSM001'), 'LISTENPREIS', 1, 99, 15.50, CURRENT_DATE),
((SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'PSM001'), 'LISTENPREIS', 100, NULL, 14.80, CURRENT_DATE),
((SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'DIENST001'), 'LISTENPREIS', 1, NULL, 150.00, CURRENT_DATE);

-- Bestellungen
INSERT INTO einkauf.bestellungen (bestellung_nr, lieferant_id, bestell_datum, liefer_datum, status, gesamtbetrag) VALUES
('BES000001', (SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE001'), CURRENT_DATE, CURRENT_DATE + INTERVAL '7 days', 'ERSTELLT', 8500.00),
('BES000002', (SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE002'), CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE + INTERVAL '2 days', 'BESTÃ„TIGT', 4500.00),
('BES000003', (SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE003'), CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '3 days', 'VOLLSTÃ„NDIG', 1550.00);

-- Bestellpositionen
INSERT INTO einkauf.bestellpositionen (bestellung_id, lieferanten_artikel_id, position_nr, bestellmenge, einheitspreis) VALUES
((SELECT bestellung_id FROM einkauf.bestellungen WHERE bestellung_nr = 'BES000001'), 
 (SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'DNG001'), 1, 10000, 0.80),
((SELECT bestellung_id FROM einkauf.bestellungen WHERE bestellung_nr = 'BES000002'), 
 (SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'FUT001'), 1, 10000, 0.42),
((SELECT bestellung_id FROM einkauf.bestellungen WHERE bestellung_nr = 'BES000003'), 
 (SELECT lieferanten_artikel_id FROM einkauf.lieferanten_artikel WHERE lieferanten_artikel_nr = 'PSM001'), 1, 100, 14.80);

-- Rechnungen
INSERT INTO einkauf.rechnungen (rechnung_nr, lieferant_id, rechnungs_datum, faelligkeits_datum, rechnungs_betrag, status) VALUES
('REK000001', (SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE001'), CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '10 days', 8500.00, 'VOLLSTÃ„NDIG'),
('REK000002', (SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE002'), CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE + INTERVAL '15 days', 4500.00, 'OFFEN'),
('REK000003', (SELECT lieferant_id FROM einkauf.lieferanten WHERE lieferant_nr = 'LIE003'), CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE + INTERVAL '25 days', 1550.00, 'OFFEN'); 
