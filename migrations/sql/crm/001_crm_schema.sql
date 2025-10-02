-- =====================================================
-- VALEO NeuroERP - CRM (Kundenverwaltung) Schema
-- =====================================================

-- Schema erstellen
CREATE SCHEMA IF NOT EXISTS crm;

-- =====================================================
-- KUNDEN UND KONTAKTE
-- =====================================================

-- Erweiterte Kundenprofile
CREATE TABLE crm.kunden (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunden_nr VARCHAR(20) UNIQUE NOT NULL,
    firmenname VARCHAR(200) NOT NULL,
    kundentyp VARCHAR(50) NOT NULL, -- 'GESCHAEFTSKUNDE', 'PRIVATKUNDE', 'GROSSKUNDE', 'TESTKUNDE'
    branche VARCHAR(100),
    umsatzklasse VARCHAR(50), -- 'KLEIN', 'MITTEL', 'GROSS', 'PREMIUM'
    kundenstatus VARCHAR(50) DEFAULT 'AKTIV', -- 'AKTIV', 'INAKTIV', 'GESPERRT', 'GELOESCHT'
    kundenbewertung INTEGER, -- 1-5 Sterne
    kundenseit VARCHAR(50), -- 'A', 'B', 'C', 'D'
    zahlungsziel INTEGER DEFAULT 30, -- Tage
    skonto_prozent DECIMAL(5,2) DEFAULT 0.00,
    kundenbetreuer_id UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kundenadressen
CREATE TABLE crm.kunden_adressen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    adress_typ VARCHAR(50) NOT NULL, -- 'RECHNUNGSADRESSE', 'LIEFERADRESSE', 'HAUPTADRESSE'
    strasse VARCHAR(200),
    hausnummer VARCHAR(20),
    plz VARCHAR(10),
    ort VARCHAR(100),
    land VARCHAR(100) DEFAULT 'Deutschland',
    telefon VARCHAR(50),
    fax VARCHAR(50),
    email VARCHAR(200),
    website VARCHAR(200),
    ist_hauptadresse BOOLEAN DEFAULT false,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kundenbankverbindungen
CREATE TABLE crm.kunden_bankverbindungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    kontoinhaber VARCHAR(200),
    iban VARCHAR(34),
    bic VARCHAR(11),
    bank_name VARCHAR(200),
    kontonummer VARCHAR(50),
    blz VARCHAR(20),
    ist_hauptkonto BOOLEAN DEFAULT false,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kontakte
CREATE TABLE crm.kontakte (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    kontakt_nr VARCHAR(20) UNIQUE NOT NULL,
    anrede VARCHAR(20), -- 'HERR', 'FRAU', 'DIVERS'
    vorname VARCHAR(100),
    nachname VARCHAR(100),
    position VARCHAR(100),
    abteilung VARCHAR(100),
    telefon VARCHAR(50),
    mobil VARCHAR(50),
    email VARCHAR(200),
    ist_hauptkontakt BOOLEAN DEFAULT false,
    notizen TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- VERKAUFSAKTIVITÃ„TEN
-- =====================================================

-- Leads
CREATE TABLE crm.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_nr VARCHAR(20) UNIQUE NOT NULL,
    firmenname VARCHAR(200) NOT NULL,
    ansprechpartner VARCHAR(200),
    email VARCHAR(200),
    telefon VARCHAR(50),
    quelle VARCHAR(100), -- 'WEBSITE', 'EMPFOHLUNG', 'MESSE', 'WERBUNG', 'SONSTIGES'
    status VARCHAR(50) DEFAULT 'NEU', -- 'NEU', 'KONTAKTIERT', 'INTERESSIERT', 'VERHANDLUNG', 'GEWONNEN', 'VERLOREN'
    prioritaet VARCHAR(20) DEFAULT 'NORMAL', -- 'NIEDRIG', 'NORMAL', 'HOCH', 'KRITISCH'
    wert DECIMAL(12,2),
    beschreibung TEXT,
    verantwortlicher_id UUID,
    naechster_kontakt DATE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VerkaufsaktivitÃ¤ten
CREATE TABLE crm.verkaufsaktivitaeten (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aktivitaet_nr VARCHAR(20) UNIQUE NOT NULL,
    kunde_id UUID REFERENCES crm.kunden(id),
    lead_id UUID REFERENCES crm.leads(id),
    aktivitaet_typ VARCHAR(50) NOT NULL, -- 'TELEFONAT', 'EMAIL', 'BESUCH', 'PRÃ„SENTATION', 'ANGEBOT', 'VERHANDLUNG'
    titel VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    datum DATE NOT NULL,
    uhrzeit TIME,
    dauer INTEGER, -- Minuten
    status VARCHAR(50) DEFAULT 'GEPLANT', -- 'GEPLANT', 'DURCHGEFÃœHRT', 'ABGESAGT', 'VERSCHOBEN'
    ergebnis TEXT,
    naechste_aktion TEXT,
    verantwortlicher_id UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verkaufschancen
CREATE TABLE crm.verkaufschancen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chance_nr VARCHAR(20) UNIQUE NOT NULL,
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    titel VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    phase VARCHAR(50) DEFAULT 'ANALYSE', -- 'ANALYSE', 'ANGEBOT', 'VERHANDLUNG', 'ABSCHLUSS', 'GEWONNEN', 'VERLOREN'
    wahrscheinlichkeit INTEGER, -- 0-100%
    wert DECIMAL(12,2),
    erwarteter_abschluss DATE,
    status VARCHAR(50) DEFAULT 'AKTIV', -- 'AKTIV', 'GEWONNEN', 'VERLOREN', 'PAUSIERT'
    verantwortlicher_id UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KOMMUNIKATION UND NOTIZEN
-- =====================================================

-- Kommunikationshistorie
CREATE TABLE crm.kommunikation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    kontakt_id UUID REFERENCES crm.kontakte(id),
    kommunikation_typ VARCHAR(50) NOT NULL, -- 'TELEFONAT', 'EMAIL', 'BESUCH', 'CHAT', 'BRIEF'
    richtung VARCHAR(20) NOT NULL, -- 'EINGANG', 'AUSGANG'
    betreff VARCHAR(200),
    nachricht TEXT,
    datum DATE NOT NULL,
    uhrzeit TIME,
    dauer INTEGER, -- Minuten
    verantwortlicher_id UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notizen
CREATE TABLE crm.notizen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    kontakt_id UUID REFERENCES crm.kontakte(id),
    notiz_typ VARCHAR(50) DEFAULT 'ALLGEMEIN', -- 'ALLGEMEIN', 'VERKAUF', 'SUPPORT', 'RECHNUNG', 'SONSTIGES'
    titel VARCHAR(200),
    inhalt TEXT NOT NULL,
    ist_oeffentlich BOOLEAN DEFAULT true,
    verantwortlicher_id UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KUNDENBEWERTUNGEN UND FEEDBACK
-- =====================================================

-- Kundenbewertungen
CREATE TABLE crm.kundenbewertungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    bewertung_typ VARCHAR(50) NOT NULL, -- 'PRODUKT', 'SERVICE', 'LIEFERUNG', 'PREIS', 'GESAMT'
    bewertung INTEGER NOT NULL, -- 1-5 Sterne
    kommentar TEXT,
    datum DATE NOT NULL,
    ist_anonym BOOLEAN DEFAULT false,
    verantwortlicher_id UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kundenfeedback
CREATE TABLE crm.kundenfeedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    feedback_typ VARCHAR(50) NOT NULL, -- 'BESCHWERDE', 'ANREGUNG', 'LOBGESANG', 'FRAGE'
    prioritaet VARCHAR(20) DEFAULT 'NORMAL', -- 'NIEDRIG', 'NORMAL', 'HOCH', 'KRITISCH'
    betreff VARCHAR(200),
    beschreibung TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'OFFEN', -- 'OFFEN', 'IN_BEARBEITUNG', 'GELOEST', 'GESCHLOSSEN'
    loesung TEXT,
    verantwortlicher_id UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KUNDENANALYSE UND SEGMENTIERUNG
-- =====================================================

-- Kundensegmente
CREATE TABLE crm.kundensegmente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    segment_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    kriterien TEXT, -- JSON oder Text mit Segmentierungskriterien
    anzahl_kunden INTEGER DEFAULT 0,
    durchschnittlicher_umsatz DECIMAL(12,2),
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kunden-Segment-Zuordnung
CREATE TABLE crm.kunden_segmente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    segment_id UUID NOT NULL REFERENCES crm.kundensegmente(id),
    zuordnungs_datum DATE NOT NULL,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kundenhistorie
CREATE TABLE crm.kundenhistorie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunde_id UUID NOT NULL REFERENCES crm.kunden(id),
    aenderung_typ VARCHAR(50) NOT NULL, -- 'STATUS', 'BEWERTUNG', 'UMSATZKLASSE', 'KUNDENSEIT', 'ADRESSE'
    alter_wert TEXT,
    neuer_wert TEXT,
    aenderungs_datum TIMESTAMP NOT NULL,
    verantwortlicher_id UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Kunden
CREATE INDEX idx_kunden_status ON crm.kunden(kundenstatus);
CREATE INDEX idx_kunden_typ ON crm.kunden(kundentyp);
CREATE INDEX idx_kunden_bewertung ON crm.kunden(kundenbewertung);
CREATE INDEX idx_kunden_seit ON crm.kunden(kundenseit);
CREATE INDEX idx_kunden_betreuer ON crm.kunden(kundenbetreuer_id);

-- Kundenadressen
CREATE INDEX idx_kunden_adressen_kunde ON crm.kunden_adressen(kunde_id);
CREATE INDEX idx_kunden_adressen_typ ON crm.kunden_adressen(adress_typ);

-- Kontakte
CREATE INDEX idx_kontakte_kunde ON crm.kontakte(kunde_id);
CREATE INDEX idx_kontakte_hauptkontakt ON crm.kontakte(ist_hauptkontakt);

-- Leads
CREATE INDEX idx_leads_status ON crm.leads(status);
CREATE INDEX idx_leads_quelle ON crm.leads(quelle);
CREATE INDEX idx_leads_prioritaet ON crm.leads(prioritaet);
CREATE INDEX idx_leads_verantwortlicher ON crm.leads(verantwortlicher_id);

-- VerkaufsaktivitÃ¤ten
CREATE INDEX idx_verkaufsaktivitaeten_kunde ON crm.verkaufsaktivitaeten(kunde_id);
CREATE INDEX idx_verkaufsaktivitaeten_typ ON crm.verkaufsaktivitaeten(aktivitaet_typ);
CREATE INDEX idx_verkaufsaktivitaeten_datum ON crm.verkaufsaktivitaeten(datum);
CREATE INDEX idx_verkaufsaktivitaeten_status ON crm.verkaufsaktivitaeten(status);

-- Verkaufschancen
CREATE INDEX idx_verkaufschancen_kunde ON crm.verkaufschancen(kunde_id);
CREATE INDEX idx_verkaufschancen_phase ON crm.verkaufschancen(phase);
CREATE INDEX idx_verkaufschancen_status ON crm.verkaufschancen(status);

-- Kommunikation
CREATE INDEX idx_kommunikation_kunde ON crm.kommunikation(kunde_id);
CREATE INDEX idx_kommunikation_datum ON crm.kommunikation(datum);
CREATE INDEX idx_kommunikation_typ ON crm.kommunikation(kommunikation_typ);

-- Kundenbewertungen
CREATE INDEX idx_kundenbewertungen_kunde ON crm.kundenbewertungen(kunde_id);
CREATE INDEX idx_kundenbewertungen_typ ON crm.kundenbewertungen(bewertung_typ);
CREATE INDEX idx_kundenbewertungen_datum ON crm.kundenbewertungen(datum);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger-Funktion fÃ¼r automatische Timestamp-Updates
CREATE OR REPLACE FUNCTION crm.update_geaendert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geaendert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers fÃ¼r alle Tabellen
CREATE TRIGGER trigger_kunden_update
    BEFORE UPDATE ON crm.kunden
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_kunden_adressen_update
    BEFORE UPDATE ON crm.kunden_adressen
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_kunden_bankverbindungen_update
    BEFORE UPDATE ON crm.kunden_bankverbindungen
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_kontakte_update
    BEFORE UPDATE ON crm.kontakte
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_leads_update
    BEFORE UPDATE ON crm.leads
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_verkaufsaktivitaeten_update
    BEFORE UPDATE ON crm.verkaufsaktivitaeten
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_verkaufschancen_update
    BEFORE UPDATE ON crm.verkaufschancen
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_kommunikation_update
    BEFORE UPDATE ON crm.kommunikation
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_notizen_update
    BEFORE UPDATE ON crm.notizen
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_kundenbewertungen_update
    BEFORE UPDATE ON crm.kundenbewertungen
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_kundenfeedback_update
    BEFORE UPDATE ON crm.kundenfeedback
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_kundensegmente_update
    BEFORE UPDATE ON crm.kundensegmente
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_kunden_segmente_update
    BEFORE UPDATE ON crm.kunden_segmente
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

-- =====================================================
-- FUNKTIONEN
-- =====================================================

-- Automatische Kundennummer-Generierung
CREATE OR REPLACE FUNCTION crm.generate_kundennummer()
RETURNS TRIGGER AS $$
DECLARE
    jahr INTEGER;
    naechste_nummer INTEGER;
    neue_nummer VARCHAR(20);
BEGIN
    jahr := EXTRACT(YEAR FROM CURRENT_DATE);
    
    SELECT COALESCE(MAX(CAST(SUBSTRING(kunden_nr FROM 9) AS INTEGER)), 0) + 1
    INTO naechste_nummer
    FROM crm.kunden
    WHERE kunden_nr LIKE 'K-' || jahr || '-%';
    
    neue_nummer := 'K-' || jahr || '-' || LPAD(naechste_nummer::TEXT, 4, '0');
    NEW.kunden_nr := neue_nummer;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r automatische Kundennummer-Generierung
CREATE TRIGGER trigger_generate_kundennummer
    BEFORE INSERT ON crm.kunden
    FOR EACH ROW EXECUTE FUNCTION crm.generate_kundennummer();

-- Automatische Kontaktnummer-Generierung
CREATE OR REPLACE FUNCTION crm.generate_kontaktnummer()
RETURNS TRIGGER AS $$
DECLARE
    jahr INTEGER;
    naechste_nummer INTEGER;
    neue_nummer VARCHAR(20);
BEGIN
    jahr := EXTRACT(YEAR FROM CURRENT_DATE);
    
    SELECT COALESCE(MAX(CAST(SUBSTRING(kontakt_nr FROM 9) AS INTEGER)), 0) + 1
    INTO naechste_nummer
    FROM crm.kontakte
    WHERE kontakt_nr LIKE 'KT-' || jahr || '-%';
    
    neue_nummer := 'KT-' || jahr || '-' || LPAD(naechste_nummer::TEXT, 4, '0');
    NEW.kontakt_nr := neue_nummer;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r automatische Kontaktnummer-Generierung
CREATE TRIGGER trigger_generate_kontaktnummer
    BEFORE INSERT ON crm.kontakte
    FOR EACH ROW EXECUTE FUNCTION crm.generate_kontaktnummer();

-- CRM-Statistiken berechnen
CREATE OR REPLACE FUNCTION crm.get_crm_statistiken(
    start_datum DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_datum DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    gesamt_kunden BIGINT,
    aktive_kunden BIGINT,
    neue_kunden BIGINT,
    verlorene_kunden BIGINT,
    durchschnittliche_bewertung DECIMAL(3,2),
    gesamt_leads BIGINT,
    gewonnene_leads BIGINT,
    verlorene_leads BIGINT,
    konversionsrate DECIMAL(5,2),
    gesamt_aktivitaeten BIGINT,
    durchgefuehrte_aktivitaeten BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(k.id)::BIGINT as gesamt_kunden,
        COUNT(CASE WHEN k.kundenstatus = 'AKTIV' THEN 1 END)::BIGINT as aktive_kunden,
        COUNT(CASE WHEN k.erstellt_am::DATE BETWEEN start_datum AND end_datum THEN 1 END)::BIGINT as neue_kunden,
        COUNT(CASE WHEN k.kundenstatus = 'GELOESCHT' AND k.geaendert_am::DATE BETWEEN start_datum AND end_datum THEN 1 END)::BIGINT as verlorene_kunden,
        ROUND(AVG(kb.bewertung), 2) as durchschnittliche_bewertung,
        COUNT(l.id)::BIGINT as gesamt_leads,
        COUNT(CASE WHEN l.status = 'GEWONNEN' THEN 1 END)::BIGINT as gewonnene_leads,
        COUNT(CASE WHEN l.status = 'VERLOREN' THEN 1 END)::BIGINT as verlorene_leads,
        ROUND(
            (COUNT(CASE WHEN l.status = 'GEWONNEN' THEN 1 END)::DECIMAL / 
             NULLIF(COUNT(l.id), 0)) * 100, 2
        ) as konversionsrate,
        COUNT(va.id)::BIGINT as gesamt_aktivitaeten,
        COUNT(CASE WHEN va.status = 'DURCHGEFÃœHRT' THEN 1 END)::BIGINT as durchgefuehrte_aktivitaeten
    FROM crm.kunden k
    LEFT JOIN crm.kundenbewertungen kb ON kb.kunde_id = k.id
    LEFT JOIN crm.leads l ON l.erstellt_am::DATE BETWEEN start_datum AND end_datum
    LEFT JOIN crm.verkaufsaktivitaeten va ON va.datum BETWEEN start_datum AND end_datum;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS
-- =====================================================

-- KundenÃ¼bersicht
CREATE VIEW crm.kunden_uebersicht AS
SELECT 
    k.id,
    k.kunden_nr,
    k.firmenname,
    k.kundentyp,
    k.kundenstatus,
    k.kundenbewertung,
    k.kundenseit,
    k.umsatzklasse,
    p.name as kundenbetreuer_name,
    ka.strasse,
    ka.plz,
    ka.ort,
    ka.telefon,
    ka.email,
    COUNT(kont.id) as anzahl_kontakte,
    COUNT(va.id) as anzahl_aktivitaeten,
    COUNT(vc.id) as anzahl_chancen,
    MAX(va.datum) as letzte_aktivitaet
FROM crm.kunden k
LEFT JOIN personal.mitarbeiter p ON p.id = k.kundenbetreuer_id
LEFT JOIN crm.kunden_adressen ka ON ka.kunde_id = k.id AND ka.ist_hauptadresse = true
LEFT JOIN crm.kontakte kont ON kont.kunde_id = k.id
LEFT JOIN crm.verkaufsaktivitaeten va ON va.kunde_id = k.id
LEFT JOIN crm.verkaufschancen vc ON vc.kunde_id = k.id
GROUP BY k.id, k.kunden_nr, k.firmenname, k.kundentyp, k.kundenstatus, k.kundenbewertung, 
         k.kundenseit, k.umsatzklasse, p.name, ka.strasse, ka.plz, ka.ort, ka.telefon, ka.email;

-- Lead-Ãœbersicht
CREATE VIEW crm.lead_uebersicht AS
SELECT 
    l.id,
    l.lead_nr,
    l.firmenname,
    l.ansprechpartner,
    l.email,
    l.telefon,
    l.quelle,
    l.status,
    l.prioritaet,
    l.wert,
    p.name as verantwortlicher_name,
    l.naechster_kontakt,
    COUNT(va.id) as anzahl_aktivitaeten,
    MAX(va.datum) as letzte_aktivitaet
FROM crm.leads l
LEFT JOIN personal.mitarbeiter p ON p.id = l.verantwortlicher_id
LEFT JOIN crm.verkaufsaktivitaeten va ON va.lead_id = l.id
GROUP BY l.id, l.lead_nr, l.firmenname, l.ansprechpartner, l.email, l.telefon, l.quelle, 
         l.status, l.prioritaet, l.wert, p.name, l.naechster_kontakt;

-- VerkaufsaktivitÃ¤ten-Ãœbersicht
CREATE VIEW crm.aktivitaeten_uebersicht AS
SELECT 
    va.id,
    va.aktivitaet_nr,
    va.aktivitaet_typ,
    va.titel,
    va.datum,
    va.uhrzeit,
    va.dauer,
    va.status,
    k.firmenname as kunde_name,
    l.firmenname as lead_name,
    p.name as verantwortlicher_name,
    va.ergebnis,
    va.naechste_aktion
FROM crm.verkaufsaktivitaeten va
LEFT JOIN crm.kunden k ON k.id = va.kunde_id
LEFT JOIN crm.leads l ON l.id = va.lead_id
LEFT JOIN personal.mitarbeiter p ON p.id = va.verantwortlicher_id;

-- =====================================================
-- BEISPIELDATEN
-- =====================================================

-- Kundensegmente
INSERT INTO crm.kundensegmente (segment_name, beschreibung, kriterien, durchschnittlicher_umsatz) VALUES
('Premium-Kunden', 'Kunden mit hohem Umsatz und guter BonitÃ¤t', 'Umsatzklasse = GROSS, Kundenseit = A', 150000.00),
('Mittelstand', 'Mittlere Unternehmen mit stabiler GeschÃ¤ftsbeziehung', 'Umsatzklasse = MITTEL, Kundenseit = B', 75000.00),
('Kleinbetriebe', 'Kleine landwirtschaftliche Betriebe', 'Umsatzklasse = KLEIN, Kundenseit = C', 25000.00),
('Neukunden', 'Kunden in der ersten GeschÃ¤ftsbeziehung', 'Erstellt_am >= CURRENT_DATE - INTERVAL 1 year', 15000.00);

-- Kunden (Beispiel)
INSERT INTO crm.kunden (firmenname, kundentyp, branche, umsatzklasse, kundenstatus, kundenbewertung, kundenseit, zahlungsziel, skonto_prozent) VALUES
('Agrarhof MÃ¼ller GmbH', 'GESCHAEFTSKUNDE', 'Landwirtschaft', 'GROSS', 'AKTIV', 5, 'A', 30, 2.00),
('Bauernhof Schmidt', 'PRIVATKUNDE', 'Landwirtschaft', 'KLEIN', 'AKTIV', 4, 'B', 14, 0.00),
('Landwirtschaftliche Genossenschaft', 'GESCHAEFTSKUNDE', 'Genossenschaft', 'GROSS', 'AKTIV', 5, 'A', 30, 3.00),
('Bio-Bauernhof Weber', 'GESCHAEFTSKUNDE', 'Bio-Landwirtschaft', 'MITTEL', 'AKTIV', 4, 'B', 30, 1.50),
('Testkunde Mustermann', 'TESTKUNDE', 'Test', 'KLEIN', 'INAKTIV', 3, 'C', 30, 0.00);

-- Kundenadressen
INSERT INTO crm.kunden_adressen (kunde_id, adress_typ, strasse, hausnummer, plz, ort, telefon, email, ist_hauptadresse) VALUES
((SELECT id FROM crm.kunden WHERE firmenname = 'Agrarhof MÃ¼ller GmbH'), 'HAUPTADRESSE', 'MusterstraÃŸe', '123', '12345', 'Musterstadt', '01234-567890', 'info@agrarhof-mueller.de', true),
((SELECT id FROM crm.kunden WHERE firmenname = 'Bauernhof Schmidt'), 'HAUPTADRESSE', 'DorfstraÃŸe', '45', '54321', 'Dorfstadt', '05432-123456', 'schmidt@bauernhof.de', true),
((SELECT id FROM crm.kunden WHERE firmenname = 'Landwirtschaftliche Genossenschaft'), 'HAUPTADRESSE', 'Genossenschaftsweg', '1', '67890', 'Genossenschaftsstadt', '06789-987654', 'info@lwg.de', true);

-- Kontakte
INSERT INTO crm.kontakte (kunde_id, anrede, vorname, nachname, position, telefon, email, ist_hauptkontakt) VALUES
((SELECT id FROM crm.kunden WHERE firmenname = 'Agrarhof MÃ¼ller GmbH'), 'HERR', 'Hans', 'MÃ¼ller', 'GeschÃ¤ftsfÃ¼hrer', '01234-567890', 'h.mueller@agrarhof-mueller.de', true),
((SELECT id FROM crm.kunden WHERE firmenname = 'Bauernhof Schmidt'), 'FRAU', 'Maria', 'Schmidt', 'Inhaberin', '05432-123456', 'm.schmidt@bauernhof.de', true),
((SELECT id FROM crm.kunden WHERE firmenname = 'Landwirtschaftliche Genossenschaft'), 'HERR', 'Peter', 'Weber', 'Vorstand', '06789-987654', 'p.weber@lwg.de', true);

-- Leads
INSERT INTO crm.leads (firmenname, ansprechpartner, email, telefon, quelle, status, prioritaet, wert, beschreibung) VALUES
('Neuer Landwirt GmbH', 'Max Mustermann', 'max@neuer-landwirt.de', '01234-111111', 'WEBSITE', 'NEU', 'HOCH', 50000.00, 'Interesse an Futtermitteln und DÃ¼nger'),
('Bio-Hof Meier', 'Anna Meier', 'anna@bio-hof-meier.de', '01234-222222', 'EMPFOHLUNG', 'KONTAKTIERT', 'NORMAL', 30000.00, 'Bio-Landwirtschaft mit Fokus auf QualitÃ¤t'),
('Test Lead', 'Test Person', 'test@test.de', '01234-333333', 'MESSE', 'INTERESSIERT', 'NIEDRIG', 15000.00, 'Test Lead fÃ¼r Demo-Zwecke');

-- VerkaufsaktivitÃ¤ten
INSERT INTO crm.verkaufsaktivitaeten (kunde_id, aktivitaet_typ, titel, beschreibung, datum, uhrzeit, dauer, status, ergebnis) VALUES
((SELECT id FROM crm.kunden WHERE firmenname = 'Agrarhof MÃ¼ller GmbH'), 'TELEFONAT', 'KundengesprÃ¤ch', 'Besprechung der neuen Produkte', '2024-01-15', '10:00:00', 30, 'DURCHGEFÃœHRT', 'Kunde interessiert an neuen Futtermitteln'),
((SELECT id FROM crm.kunden WHERE firmenname = 'Bauernhof Schmidt'), 'BESUCH', 'Hofbesuch', 'Vorstellung der Produktpalette', '2024-01-16', '14:00:00', 120, 'DURCHGEFÃœHRT', 'Positives Feedback, Bestellung geplant'),
((SELECT id FROM crm.leads WHERE firmenname = 'Neuer Landwirt GmbH'), 'EMAIL', 'Erstkontakt', 'Willkommens-E-Mail mit Produktinformationen', '2024-01-17', '09:00:00', 15, 'DURCHGEFÃœHRT', 'Interesse bekundet, RÃ¼ckruf gewÃ¼nscht');

-- Verkaufschancen
INSERT INTO crm.verkaufschancen (kunde_id, titel, beschreibung, phase, wahrscheinlichkeit, wert, erwarteter_abschluss, status) VALUES
((SELECT id FROM crm.kunden WHERE firmenname = 'Agrarhof MÃ¼ller GmbH'), 'Futtermittel-Liefervertrag', 'Langfristiger Liefervertrag fÃ¼r Premium-Futtermittel', 'VERHANDLUNG', 75, 120000.00, '2024-03-15', 'AKTIV'),
((SELECT id FROM crm.kunden WHERE firmenname = 'Bauernhof Schmidt'), 'DÃ¼nger-Bestellung', 'FrÃ¼hjahrsbestellung fÃ¼r NPK-DÃ¼nger', 'ANGEBOT', 60, 25000.00, '2024-02-28', 'AKTIV'),
((SELECT id FROM crm.leads WHERE firmenname = 'Neuer Landwirt GmbH'), 'Erstbestellung', 'Erste Bestellung nach erfolgreicher Beratung', 'ANALYSE', 40, 15000.00, '2024-02-15', 'AKTIV');

-- Kundenbewertungen
INSERT INTO crm.kundenbewertungen (kunde_id, bewertung_typ, bewertung, kommentar, datum) VALUES
((SELECT id FROM crm.kunden WHERE firmenname = 'Agrarhof MÃ¼ller GmbH'), 'GESAMT', 5, 'Sehr zufrieden mit der QualitÃ¤t und dem Service', '2024-01-10'),
((SELECT id FROM crm.kunden WHERE firmenname = 'Bauernhof Schmidt'), 'GESAMT', 4, 'Gute Produkte, schnelle Lieferung', '2024-01-12'),
((SELECT id FROM crm.kunden WHERE firmenname = 'Landwirtschaftliche Genossenschaft'), 'GESAMT', 5, 'Exzellente Zusammenarbeit, sehr professionell', '2024-01-08');

-- =====================================================
-- TAGESPROTOKOLL-ERWEITERUNG FÃœR AUSSENDIENST
-- =====================================================

-- Tagesprotokoll-Haupttabelle
CREATE TABLE crm.tagesprotokolle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protokoll_nr VARCHAR(20) UNIQUE NOT NULL,
    mitarbeiter_id UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    protokoll_datum DATE NOT NULL,
    zeitraum_start DATE,
    zeitraum_ende DATE,
    status VARCHAR(50) DEFAULT 'ENTWURF', -- 'ENTWURF', 'FREIGEGEBEN', 'ARCHIVIERT'
    freigegeben_von UUID REFERENCES personal.mitarbeiter(id),
    freigegeben_am TIMESTAMP,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tagesprotokoll-EintrÃ¤ge
CREATE TABLE crm.tagesprotokoll_eintraege (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protokoll_id UUID NOT NULL REFERENCES crm.tagesprotokolle(id) ON DELETE CASCADE,
    kunde_id UUID REFERENCES crm.kunden(id),
    kontakt_id UUID REFERENCES crm.kontakte(id),
    eintrag_typ VARCHAR(50) NOT NULL, -- 'BETRIEBSBESUCH', 'TELEFONAT', 'EMAIL', 'WHATSAPP', 'LIEFERUNG', 'BESTELLUNG', 'ANGEBOT', 'FELDBEGEHUNG', 'MESSE', 'SONSTIGES'
    kontakt_richtung VARCHAR(20) DEFAULT 'AUSGEHEND', -- 'EINGEHEND', 'AUSGEHEND'
    titel VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    ergebnis TEXT,
    naechste_aktion TEXT,
    termin_vereinbarung DATE,
    menge_vereinbarung DECIMAL(10,2),
    einheit_vereinbarung VARCHAR(20), -- 'TO', 'LTR', 'KG', 'SACK', 'PALETTE', 'STUECK'
    preis_vereinbarung DECIMAL(10,2),
    waehrung_vereinbarung VARCHAR(3) DEFAULT 'EUR',
    kundenspezifische_absprachen TEXT,
    zeitaufwand_minuten INTEGER,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tagesprotokoll-Vorlagen
CREATE TABLE crm.tagesprotokoll_vorlagen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vorlagen_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    eintrag_typ VARCHAR(50) NOT NULL,
    standard_titel VARCHAR(200),
    standard_beschreibung TEXT,
    standard_ergebnis TEXT,
    standard_naechste_aktion TEXT,
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tagesprotokoll-Kategorien
CREATE TABLE crm.tagesprotokoll_kategorien (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kategorie_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    farbe VARCHAR(7) DEFAULT '#1976d2',
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tagesprotokoll-Eintrag-Kategorien (Many-to-Many)
CREATE TABLE crm.tagesprotokoll_eintrag_kategorien (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    eintrag_id UUID NOT NULL REFERENCES crm.tagesprotokoll_eintraege(id) ON DELETE CASCADE,
    kategorie_id UUID NOT NULL REFERENCES crm.tagesprotokoll_kategorien(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXE FÃœR TAGESPROTOKOLL
-- =====================================================

CREATE INDEX idx_tagesprotokolle_mitarbeiter ON crm.tagesprotokolle(mitarbeiter_id);
CREATE INDEX idx_tagesprotokolle_datum ON crm.tagesprotokolle(protokoll_datum);
CREATE INDEX idx_tagesprotokolle_status ON crm.tagesprotokolle(status);
CREATE INDEX idx_tagesprotokolle_zeitraum ON crm.tagesprotokolle(zeitraum_start, zeitraum_ende);

CREATE INDEX idx_tagesprotokoll_eintraege_protokoll ON crm.tagesprotokoll_eintraege(protokoll_id);
CREATE INDEX idx_tagesprotokoll_eintraege_kunde ON crm.tagesprotokoll_eintraege(kunde_id);
CREATE INDEX idx_tagesprotokoll_eintraege_typ ON crm.tagesprotokoll_eintraege(eintrag_typ);
CREATE INDEX idx_tagesprotokoll_eintraege_richtung ON crm.tagesprotokoll_eintraege(kontakt_richtung);

-- =====================================================
-- TRIGGER FÃœR TAGESPROTOKOLL
-- =====================================================

CREATE TRIGGER trigger_tagesprotokolle_update_geaendert_am
    BEFORE UPDATE ON crm.tagesprotokolle
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

CREATE TRIGGER trigger_tagesprotokoll_eintraege_update_geaendert_am
    BEFORE UPDATE ON crm.tagesprotokoll_eintraege
    FOR EACH ROW EXECUTE FUNCTION crm.update_geaendert_am();

-- =====================================================
-- FUNKTIONEN FÃœR TAGESPROTOKOLL
-- =====================================================

-- Automatische Protokollnummer-Generierung
CREATE OR REPLACE FUNCTION crm.generate_protokollnummer()
RETURNS TRIGGER AS $$
DECLARE
    jahr INTEGER;
    monat INTEGER;
    naechste_nummer INTEGER;
    neue_nummer VARCHAR(20);
BEGIN
    jahr := EXTRACT(YEAR FROM CURRENT_DATE);
    monat := EXTRACT(MONTH FROM CURRENT_DATE);
    
    SELECT COALESCE(MAX(CAST(SUBSTRING(protokoll_nr FROM 12) AS INTEGER)), 0) + 1
    INTO naechste_nummer
    FROM crm.tagesprotokolle
    WHERE protokoll_nr LIKE 'TP-' || jahr || '-' || LPAD(monat::TEXT, 2, '0') || '-%';
    
    neue_nummer := 'TP-' || jahr || '-' || LPAD(monat::TEXT, 2, '0') || '-' || LPAD(naechste_nummer::TEXT, 3, '0');
    NEW.protokoll_nr := neue_nummer;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r automatische Protokollnummer-Generierung
CREATE TRIGGER trigger_generate_protokollnummer
    BEFORE INSERT ON crm.tagesprotokolle
    FOR EACH ROW EXECUTE FUNCTION crm.generate_protokollnummer();

-- Tagesprotokoll aus CRM-Daten generieren
CREATE OR REPLACE FUNCTION crm.generate_tagesprotokoll(
    p_mitarbeiter_id UUID,
    p_datum DATE DEFAULT CURRENT_DATE,
    p_zeitraum_start DATE DEFAULT NULL,
    p_zeitraum_ende DATE DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_protokoll_id UUID;
    v_zeitraum_start DATE;
    v_zeitraum_ende DATE;
BEGIN
    -- Zeitraum bestimmen
    IF p_zeitraum_start IS NULL THEN
        v_zeitraum_start := p_datum;
    ELSE
        v_zeitraum_start := p_zeitraum_start;
    END IF;
    
    IF p_zeitraum_ende IS NULL THEN
        v_zeitraum_ende := p_datum;
    ELSE
        v_zeitraum_ende := p_zeitraum_ende;
    END IF;
    
    -- Tagesprotokoll erstellen
    INSERT INTO crm.tagesprotokolle (mitarbeiter_id, protokoll_datum, zeitraum_start, zeitraum_ende)
    VALUES (p_mitarbeiter_id, p_datum, v_zeitraum_start, v_zeitraum_ende)
    RETURNING id INTO v_protokoll_id;
    
    -- VerkaufsaktivitÃ¤ten als EintrÃ¤ge hinzufÃ¼gen
    INSERT INTO crm.tagesprotokoll_eintraege (
        protokoll_id, kunde_id, kontakt_id, eintrag_typ, kontakt_richtung, 
        titel, beschreibung, ergebnis, naechste_aktion, zeitaufwand_minuten
    )
    SELECT 
        v_protokoll_id,
        va.kunde_id,
        va.kontakt_id,
        CASE 
            WHEN va.aktivitaet_typ = 'TELEFONAT' THEN 'TELEFONAT'
            WHEN va.aktivitaet_typ = 'EMAIL' THEN 'EMAIL'
            WHEN va.aktivitaet_typ = 'BESUCH' THEN 'BETRIEBSBESUCH'
            WHEN va.aktivitaet_typ = 'PRÃ„SENTATION' THEN 'ANGEBOT'
            ELSE 'SONSTIGES'
        END,
        'AUSGEHEND',
        va.titel,
        va.beschreibung,
        va.ergebnis,
        va.naechste_aktion,
        va.dauer
    FROM crm.verkaufsaktivitaeten va
    WHERE va.verantwortlicher_id = p_mitarbeiter_id
    AND va.datum BETWEEN v_zeitraum_start AND v_zeitraum_ende
    AND va.status = 'DURCHGEFÃœHRT';
    
    -- Kommunikation als EintrÃ¤ge hinzufÃ¼gen
    INSERT INTO crm.tagesprotokoll_eintraege (
        protokoll_id, kunde_id, kontakt_id, eintrag_typ, kontakt_richtung,
        titel, beschreibung, zeitaufwand_minuten
    )
    SELECT 
        v_protokoll_id,
        k.kunde_id,
        k.kontakt_id,
        CASE 
            WHEN k.kommunikation_typ = 'TELEFONAT' THEN 'TELEFONAT'
            WHEN k.kommunikation_typ = 'EMAIL' THEN 'EMAIL'
            WHEN k.kommunikation_typ = 'BESUCH' THEN 'BETRIEBSBESUCH'
            WHEN k.kommunikation_typ = 'CHAT' THEN 'WHATSAPP'
            ELSE 'SONSTIGES'
        END,
        k.richtung,
        COALESCE(k.betreff, k.kommunikation_typ),
        k.nachricht,
        k.dauer
    FROM crm.kommunikation k
    WHERE k.verantwortlicher_id = p_mitarbeiter_id
    AND k.datum BETWEEN v_zeitraum_start AND v_zeitraum_ende;
    
    RETURN v_protokoll_id;
END;
$$ LANGUAGE plpgsql;

-- Tagesprotokoll-Statistiken
CREATE OR REPLACE FUNCTION crm.get_tagesprotokoll_statistiken(
    p_mitarbeiter_id UUID DEFAULT NULL,
    p_start_datum DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    p_end_datum DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    gesamt_protokolle BIGINT,
    freigegebene_protokolle BIGINT,
    gesamt_eintraege BIGINT,
    durchschnitt_eintraege_pro_tag DECIMAL(5,2),
    haeufigste_eintrag_typen TEXT,
    gesamt_zeitaufwand_stunden DECIMAL(6,2),
    aktivste_kunden TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT tp.id)::BIGINT as gesamt_protokolle,
        COUNT(DISTINCT CASE WHEN tp.status = 'FREIGEGEBEN' THEN tp.id END)::BIGINT as freigegebene_protokolle,
        COUNT(tpe.id)::BIGINT as gesamt_eintraege,
        ROUND(COUNT(tpe.id)::DECIMAL / NULLIF(COUNT(DISTINCT tp.id), 0), 2) as durchschnitt_eintraege_pro_tag,
        STRING_AGG(DISTINCT tpe.eintrag_typ, ', ' ORDER BY tpe.eintrag_typ) as haeufigste_eintrag_typen,
        ROUND(SUM(tpe.zeitaufwand_minuten)::DECIMAL / 60, 2) as gesamt_zeitaufwand_stunden,
        STRING_AGG(DISTINCT k.firmenname, ', ' ORDER BY k.firmenname) as aktivste_kunden
    FROM crm.tagesprotokolle tp
    LEFT JOIN crm.tagesprotokoll_eintraege tpe ON tpe.protokoll_id = tp.id
    LEFT JOIN crm.kunden k ON k.id = tpe.kunde_id
    WHERE (p_mitarbeiter_id IS NULL OR tp.mitarbeiter_id = p_mitarbeiter_id)
    AND tp.protokoll_datum BETWEEN p_start_datum AND p_end_datum;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS FÃœR TAGESPROTOKOLL
-- =====================================================

-- Tagesprotokoll-Ãœbersicht
CREATE VIEW crm.tagesprotokoll_uebersicht AS
SELECT 
    tp.id,
    tp.protokoll_nr,
    tp.protokoll_datum,
    tp.zeitraum_start,
    tp.zeitraum_ende,
    tp.status,
    CONCAT(m.vorname, ' ', m.nachname) as mitarbeiter_name,
    CONCAT(f.vorname, ' ', f.nachname) as freigegeben_von_name,
    tp.freigegeben_am,
    COUNT(tpe.id) as anzahl_eintraege,
    SUM(tpe.zeitaufwand_minuten) as gesamt_zeitaufwand_minuten
FROM crm.tagesprotokolle tp
LEFT JOIN personal.mitarbeiter m ON m.id = tp.mitarbeiter_id
LEFT JOIN personal.mitarbeiter f ON f.id = tp.freigegeben_von
LEFT JOIN crm.tagesprotokoll_eintraege tpe ON tpe.protokoll_id = tp.id
GROUP BY tp.id, tp.protokoll_nr, tp.protokoll_datum, tp.zeitraum_start, tp.zeitraum_ende, 
         tp.status, m.vorname, m.nachname, f.vorname, f.nachname, tp.freigegeben_am;

-- Tagesprotokoll-EintrÃ¤ge-Ãœbersicht
CREATE VIEW crm.tagesprotokoll_eintraege_uebersicht AS
SELECT 
    tpe.id,
    tp.protokoll_nr,
    tp.protokoll_datum,
    CONCAT(m.vorname, ' ', m.nachname) as mitarbeiter_name,
    k.firmenname as kunde_name,
    CONCAT(kont.vorname, ' ', kont.nachname) as kontakt_name,
    tpe.eintrag_typ,
    tpe.kontakt_richtung,
    tpe.titel,
    tpe.beschreibung,
    tpe.ergebnis,
    tpe.naechste_aktion,
    tpe.termin_vereinbarung,
    tpe.menge_vereinbarung,
    tpe.einheit_vereinbarung,
    tpe.preis_vereinbarung,
    tpe.waehrung_vereinbarung,
    tpe.kundenspezifische_absprachen,
    tpe.zeitaufwand_minuten
FROM crm.tagesprotokoll_eintraege tpe
JOIN crm.tagesprotokolle tp ON tp.id = tpe.protokoll_id
JOIN personal.mitarbeiter m ON m.id = tp.mitarbeiter_id
LEFT JOIN crm.kunden k ON k.id = tpe.kunde_id
LEFT JOIN crm.kontakte kont ON kont.id = tpe.kontakt_id;

-- =====================================================
-- BEISPIELDATEN FÃœR TAGESPROTOKOLL
-- =====================================================

-- Tagesprotokoll-Kategorien
INSERT INTO crm.tagesprotokoll_kategorien (kategorie_name, beschreibung, farbe) VALUES
('Betriebsbesuch', 'PersÃ¶nliche Besuche bei Kunden', '#1976d2'),
('Telefonat', 'Telefonische Kontakte', '#388e3c'),
('Email', 'E-Mail-Kommunikation', '#f57c00'),
('WhatsApp', 'WhatsApp-Nachrichten', '#7b1fa2'),
('Lieferung', 'Produktlieferungen', '#d32f2f'),
('Bestellung', 'Kundenbestellungen', '#ff9800'),
('Angebot', 'Preisangebote und Verhandlungen', '#9c27b0'),
('Feldbegehung', 'Feldbesichtigungen und Beratung', '#4caf50'),
('Messe', 'Messe- und Veranstaltungsbesuche', '#795548'),
('Finanzen', 'Finanzielle Absprachen und Zahlungen', '#607d8b');

-- Tagesprotokoll-Vorlagen
INSERT INTO crm.tagesprotokoll_vorlagen (vorlagen_name, beschreibung, eintrag_typ, standard_titel, standard_beschreibung, standard_ergebnis, standard_naechste_aktion) VALUES
('Betriebsbesuch - Standard', 'Standard-Vorlage fÃ¼r Betriebsbesuche', 'BETRIEBSBESUCH', 'Betriebsbesuch', 'PersÃ¶nlicher Besuch beim Kunden', 'Kunde informiert Ã¼ber aktuelle Angebote', 'NÃ¤chsten Termin vereinbaren'),
('Telefonat - RÃ¼ckruf', 'Standard-Vorlage fÃ¼r RÃ¼ckrufe', 'TELEFONAT', 'RÃ¼ckruf', 'RÃ¼ckruf auf Kundenanfrage', 'Kunde erreicht, Anliegen besprochen', 'Angebot erstellen'),
('Email - Angebot', 'Standard-Vorlage fÃ¼r E-Mail-Angebote', 'EMAIL', 'Angebot per E-Mail', 'Preisangebot versendet', 'Angebot versendet', 'Auf RÃ¼ckmeldung warten'),
('Lieferung - Standard', 'Standard-Vorlage fÃ¼r Lieferungen', 'LIEFERUNG', 'Produktlieferung', 'Lieferung durchgefÃ¼hrt', 'Lieferung erfolgreich', 'Rechnung erstellen'),
('Feldbegehung - Beratung', 'Standard-Vorlage fÃ¼r Feldbegehungen', 'FELDBEGEHUNG', 'Feldbegehung', 'Feldbesichtigung und Beratung', 'Empfehlungen gegeben', 'Nachbereitung planen');

-- Beispiel-Tagesprotokoll (basierend auf dem Beispiel des Users)
INSERT INTO crm.tagesprotokolle (mitarbeiter_id, protokoll_datum, zeitraum_start, zeitraum_ende, status) VALUES
((SELECT id FROM personal.mitarbeiter LIMIT 1), '2024-05-28', '2024-05-28', '2024-06-04', 'FREIGEGEBEN');

-- Beispiel-Tagesprotokoll-EintrÃ¤ge (basierend auf dem Beispiel des Users)
INSERT INTO crm.tagesprotokoll_eintraege (protokoll_id, kunde_id, eintrag_typ, titel, beschreibung, ergebnis, naechste_aktion, kundenspezifische_absprachen) VALUES
((SELECT id FROM crm.tagesprotokolle LIMIT 1), (SELECT id FROM crm.kunden WHERE firmenname = 'Agrarhof MÃ¼ller GmbH' LIMIT 1), 'BETRIEBSBESUCH', 'Betriebsbesuch AuÃŸenstÃ¤nde', 'Betriebsbesuch bei Uwe Lay, Aynwolde', 'Interesse an MLF und Mehlmischung', 'Finanzielle Sicherheit mit TBK klÃ¤ren', 'Soll zuvor finanzielle Sicherheit mit TBK klÃ¤ren, bevor er von mir Angebote erhÃ¤lt'),
((SELECT id FROM crm.tagesprotokolle LIMIT 1), (SELECT id FROM crm.kunden WHERE firmenname = 'Bauernhof Schmidt' LIMIT 1), 'TELEFONAT', 'Telefonat Hero Fisser', 'Telefonat mit Hero Fisser', 'Nicht erreicht, Wuxal angeboten', 'Erneut versuchen', 'Wuxal angeboten'),
((SELECT id FROM crm.tagesprotokolle LIMIT 1), (SELECT id FROM crm.kunden WHERE firmenname = 'Landwirtschaftliche Genossenschaft' LIMIT 1), 'BESTELLUNG', 'Futter bestellt', 'Futterbestellung von Albert Koopmann', 'Futter bestellt', 'Lieferung planen', 'Albert Koopmann hat Futter bestellt'),
((SELECT id FROM crm.tagesprotokolle LIMIT 1), (SELECT id FROM crm.kunden WHERE firmenname = 'Bio-Bauernhof Weber' LIMIT 1), 'LIEFERUNG', 'PSM geliefert', 'PSM-Lieferung an Albert Ohling', 'PSM geliefert', 'Rechnung erstellen', 'Albert Ohling hat PSM geliefert bekommen');

-- =====================================================
-- KOMMENTARE
-- =====================================================

COMMENT ON TABLE crm.tagesprotokolle IS 'Tagesprotokolle fÃ¼r AuÃŸendienst-Mitarbeiter';
COMMENT ON TABLE crm.tagesprotokoll_eintraege IS 'Einzelne EintrÃ¤ge in Tagesprotokollen';
COMMENT ON TABLE crm.tagesprotokoll_vorlagen IS 'Vorlagen fÃ¼r hÃ¤ufige Eintragstypen';
COMMENT ON TABLE crm.tagesprotokoll_kategorien IS 'Kategorien fÃ¼r Tagesprotokoll-EintrÃ¤ge';
COMMENT ON FUNCTION crm.generate_tagesprotokoll IS 'Generiert automatisch ein Tagesprotokoll aus CRM-Daten';
COMMENT ON FUNCTION crm.get_tagesprotokoll_statistiken IS 'Berechnet Statistiken fÃ¼r Tagesprotokolle';

COMMIT; 
