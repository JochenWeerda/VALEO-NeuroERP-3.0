-- =====================================================
-- VALEO NeuroERP - Lagerverwaltung Schema
-- =====================================================
-- Erstellt: MÃ¤rz 2024
-- Beschreibung: VollstÃ¤ndiges Lagerverwaltungs-System
-- L3-KonformitÃ¤t: LAGER, LAGERBEWEGUNGEN, LAGERPLAETZE
-- =====================================================

-- Schema fÃ¼r Lagerverwaltung erstellen
CREATE SCHEMA IF NOT EXISTS lager;

-- =====================================================
-- 1. LAGERSTRUKTUR
-- =====================================================

-- Lagerorte
CREATE TABLE lager.lagerorte (
    lagerort_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lagerort_nr VARCHAR(50) UNIQUE NOT NULL,
    bezeichnung VARCHAR(200) NOT NULL,
    lagerort_typ VARCHAR(50) NOT NULL CHECK (lagerort_typ IN ('HAUPTLAGER', 'NEBENLAGER', 'PRODUKTIONSLAGER', 'QUALITAETSLAGER', 'RETOURENLAGER')),
    standort VARCHAR(200),
    adresse_straÃŸe VARCHAR(200),
    adresse_plz VARCHAR(10),
    adresse_ort VARCHAR(100),
    adresse_land VARCHAR(50) DEFAULT 'Deutschland',
    telefon VARCHAR(50),
    email VARCHAR(100),
    lagerleiter_id UUID,
    kapazitaet_m3 DECIMAL(10,2),
    belegte_kapazitaet_m3 DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'AKTIV' CHECK (status IN ('AKTIV', 'INAKTIV', 'WARTUNG', 'GESPERRT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Lagerzonen
CREATE TABLE lager.lagerzonen (
    lagerzone_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lagerort_id UUID NOT NULL REFERENCES lager.lagerorte(lagerort_id),
    lagerzone_nr VARCHAR(50) NOT NULL,
    bezeichnung VARCHAR(200) NOT NULL,
    lagerzone_typ VARCHAR(50) NOT NULL CHECK (lagerzone_typ IN ('ROHSTOFFE', 'HALBFERTIGE', 'FERTIGPRODUKTE', 'HILFSSTOFFE', 'VERPACKUNG', 'RETOUREN')),
    temperatur_min DECIMAL(5,2),
    temperatur_max DECIMAL(5,2),
    feuchtigkeit_min DECIMAL(5,2),
    feuchtigkeit_max DECIMAL(5,2),
    kapazitaet_m3 DECIMAL(10,2),
    belegte_kapazitaet_m3 DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'AKTIV' CHECK (status IN ('AKTIV', 'INAKTIV', 'WARTUNG', 'GESPERRT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(lagerort_id, lagerzone_nr)
);

-- LagerplÃ¤tze
CREATE TABLE lager.lagerplaetze (
    lagerplatz_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lagerzone_id UUID NOT NULL REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_nr VARCHAR(50) NOT NULL,
    bezeichnung VARCHAR(200) NOT NULL,
    lagerplatz_typ VARCHAR(50) NOT NULL CHECK (lagerplatz_typ IN ('REGAL', 'BODENLAGER', 'HOCHREGAL', 'KLEINLAGER', 'PICKPLATZ')),
    regal_nr VARCHAR(20),
    ebene_nr VARCHAR(20),
    fach_nr VARCHAR(20),
    position_x DECIMAL(10,2),
    position_y DECIMAL(10,2),
    position_z DECIMAL(10,2),
    laenge_m DECIMAL(5,2),
    breite_m DECIMAL(5,2),
    hoehe_m DECIMAL(5,2),
    volumen_m3 DECIMAL(10,2),
    max_gewicht_kg DECIMAL(10,2),
    belegtes_gewicht_kg DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'FREI' CHECK (status IN ('FREI', 'BELEGT', 'RESERVIERT', 'WARTUNG', 'GESPERRT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(lagerzone_id, lagerplatz_nr)
);

-- =====================================================
-- 2. ARTIKEL UND BESTÃ„NDE
-- =====================================================

-- Artikel-BestÃ¤nde
CREATE TABLE lager.artikel_bestaende (
    bestand_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artikel_id UUID NOT NULL,
    lagerort_id UUID NOT NULL REFERENCES lager.lagerorte(lagerort_id),
    lagerzone_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    menge_verfuegbar DECIMAL(10,4) DEFAULT 0,
    menge_reserviert DECIMAL(10,4) DEFAULT 0,
    menge_in_qualitaet DECIMAL(10,4) DEFAULT 0,
    menge_gesperrt DECIMAL(10,4) DEFAULT 0,
    menge_gesamt DECIMAL(10,4) DEFAULT 0,
    einheit VARCHAR(20) NOT NULL,
    durchschnittspreis DECIMAL(10,2),
    letzte_bewegung TIMESTAMP,
    naechste_inventur DATE,
    mindestbestand DECIMAL(10,4) DEFAULT 0,
    optimalbestand DECIMAL(10,4) DEFAULT 0,
    max_bestand DECIMAL(10,4) DEFAULT 0,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(artikel_id, lagerort_id, lagerzone_id, lagerplatz_id)
);

-- Chargen/Los-Verwaltung
CREATE TABLE lager.chargen (
    charge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artikel_id UUID NOT NULL,
    lagerort_id UUID NOT NULL REFERENCES lager.lagerorte(lagerort_id),
    lagerzone_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    charge_nr VARCHAR(100) NOT NULL,
    los_nr VARCHAR(100),
    menge DECIMAL(10,4) NOT NULL,
    einheit VARCHAR(20) NOT NULL,
    herstellungsdatum DATE,
    verfallsdatum DATE,
    charge_status VARCHAR(20) DEFAULT 'VERFÃœGBAR' CHECK (charge_status IN ('VERFÃœGBAR', 'RESERVIERT', 'QUALITAET', 'GESPERRT', 'VERBRAUCHT')),
    qualitaetsstatus VARCHAR(20) DEFAULT 'FREIGEGEBEN' CHECK (qualitaetsstatus IN ('FREIGEGEBEN', 'IN_PRÃœFUNG', 'GESPERRT', 'VERWORFEN')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 3. LAGERBEWEGUNGEN
-- =====================================================

-- Lagerbewegungen
CREATE TABLE lager.lagerbewegungen (
    bewegung_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bewegungsnummer VARCHAR(50) UNIQUE NOT NULL,
    bewegungstyp VARCHAR(50) NOT NULL CHECK (bewegungstyp IN ('EINLAGERUNG', 'AUSLAGERUNG', 'UMLAGERUNG', 'INVENTUR', 'KOMMISSIONIERUNG', 'RETOURE')),
    artikel_id UUID NOT NULL,
    charge_id UUID REFERENCES lager.chargen(charge_id),
    lagerort_von_id UUID REFERENCES lager.lagerorte(lagerort_id),
    lagerzone_von_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_von_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    lagerort_nach_id UUID REFERENCES lager.lagerorte(lagerort_id),
    lagerzone_nach_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_nach_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    menge DECIMAL(10,4) NOT NULL,
    einheit VARCHAR(20) NOT NULL,
    bewegungsdatum TIMESTAMP NOT NULL,
    bewegungszeit TIMESTAMP NOT NULL,
    referenz_typ VARCHAR(50) CHECK (referenz_typ IN ('PRODUKTIONSAUFTRAG', 'BESTELLUNG', 'VERKAUFSAUFTRAG', 'INVENTUR', 'MANUELL')),
    referenz_id UUID,
    referenz_nr VARCHAR(50),
    personal_id UUID,
    status VARCHAR(20) DEFAULT 'GEPLANT' CHECK (status IN ('GEPLANT', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN', 'STORNIERT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Bewegungspositionen
CREATE TABLE lager.bewegungspositionen (
    position_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bewegung_id UUID NOT NULL REFERENCES lager.lagerbewegungen(bewegung_id),
    position INTEGER NOT NULL,
    artikel_id UUID NOT NULL,
    charge_id UUID REFERENCES lager.chargen(charge_id),
    menge DECIMAL(10,4) NOT NULL,
    einheit VARCHAR(20) NOT NULL,
    lagerplatz_von_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    lagerplatz_nach_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    status VARCHAR(20) DEFAULT 'OFFEN' CHECK (status IN ('OFFEN', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN', 'STORNIERT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 4. EIN- UND AUSLAGERUNGEN
-- =====================================================

-- Wareneingang
CREATE TABLE lager.wareneingang (
    wareneingang_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wareneingang_nr VARCHAR(50) UNIQUE NOT NULL,
    lieferant_id UUID,
    bestellung_id UUID,
    lieferant_referenz VARCHAR(100),
    lieferdatum DATE NOT NULL,
    erwartetes_lieferdatum DATE,
    lagerort_id UUID NOT NULL REFERENCES lager.lagerorte(lagerort_id),
    status VARCHAR(20) DEFAULT 'ERWARTET' CHECK (status IN ('ERWARTET', 'ANGEKÃœNDIGT', 'EINGETROFFEN', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN', 'STORNIERT')),
    qualitaetspruefung_erforderlich BOOLEAN DEFAULT FALSE,
    qualitaetspruefung_status VARCHAR(20) DEFAULT 'OFFEN' CHECK (qualitaetspruefung_status IN ('OFFEN', 'IN_BEARBEITUNG', 'BESTANDEN', 'NICHT_BESTANDEN')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Wareneingangspositionen
CREATE TABLE lager.wareneingang_positionen (
    position_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wareneingang_id UUID NOT NULL REFERENCES lager.wareneingang(wareneingang_id),
    position INTEGER NOT NULL,
    artikel_id UUID NOT NULL,
    bestellposition_id UUID,
    bestellmenge DECIMAL(10,4),
    gelieferte_menge DECIMAL(10,4) DEFAULT 0,
    einheit VARCHAR(20) NOT NULL,
    charge_nr VARCHAR(100),
    los_nr VARCHAR(100),
    verfallsdatum DATE,
    qualitaetspruefung_erforderlich BOOLEAN DEFAULT FALSE,
    qualitaetspruefung_status VARCHAR(20) DEFAULT 'OFFEN' CHECK (qualitaetspruefung_status IN ('OFFEN', 'IN_BEARBEITUNG', 'BESTANDEN', 'NICHT_BESTANDEN')),
    lagerzone_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    status VARCHAR(20) DEFAULT 'OFFEN' CHECK (status IN ('OFFEN', 'IN_BEARBEITUNG', 'EINGELAGERT', 'STORNIERT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Warenausgang
CREATE TABLE lager.warenausgang (
    warenausgang_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warenausgang_nr VARCHAR(50) UNIQUE NOT NULL,
    kunde_id UUID,
    verkaufsauftrag_id UUID,
    produktionsauftrag_id UUID,
    ausgangstyp VARCHAR(50) NOT NULL CHECK (ausgangstyp IN ('VERKAUF', 'PRODUKTION', 'INTERN', 'RETOURE', 'VERNICHTUNG')),
    ausgangsdatum DATE NOT NULL,
    lagerort_id UUID NOT NULL REFERENCES lager.lagerorte(lagerort_id),
    status VARCHAR(20) DEFAULT 'GEPLANT' CHECK (status IN ('GEPLANT', 'IN_BEARBEITUNG', 'KOMMISSIONIERT', 'VERPACKT', 'VERSENDET', 'ABGESCHLOSSEN', 'STORNIERT')),
    kommissionierung_erforderlich BOOLEAN DEFAULT TRUE,
    kommissionierung_status VARCHAR(20) DEFAULT 'OFFEN' CHECK (kommissionierung_status IN ('OFFEN', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Warenausgangspositionen
CREATE TABLE lager.warenausgang_positionen (
    position_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warenausgang_id UUID NOT NULL REFERENCES lager.warenausgang(warenausgang_id),
    position INTEGER NOT NULL,
    artikel_id UUID NOT NULL,
    verkaufsauftrag_position_id UUID,
    produktionsauftrag_position_id UUID,
    gewuenschte_menge DECIMAL(10,4) NOT NULL,
    verfuegbare_menge DECIMAL(10,4) DEFAULT 0,
    kommissionierte_menge DECIMAL(10,4) DEFAULT 0,
    ausgelagerte_menge DECIMAL(10,4) DEFAULT 0,
    einheit VARCHAR(20) NOT NULL,
    lagerzone_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    kommissionierung_erforderlich BOOLEAN DEFAULT TRUE,
    kommissionierung_status VARCHAR(20) DEFAULT 'OFFEN' CHECK (kommissionierung_status IN ('OFFEN', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN')),
    status VARCHAR(20) DEFAULT 'OFFEN' CHECK (status IN ('OFFEN', 'IN_BEARBEITUNG', 'KOMMISSIONIERT', 'AUSGELAGERT', 'STORNIERT')),
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 5. KOMMISSIONIERUNG
-- =====================================================

-- KommissionierauftrÃ¤ge
CREATE TABLE lager.kommissionierauftraege (
    kommissionierauftrag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kommissionierauftrag_nr VARCHAR(50) UNIQUE NOT NULL,
    warenausgang_id UUID REFERENCES lager.warenausgang(warenausgang_id),
    kommissionierauftrag_typ VARCHAR(50) NOT NULL CHECK (kommissionierauftrag_typ IN ('VERKAUF', 'PRODUKTION', 'INTERN', 'INVENTUR')),
    prioritaet INTEGER DEFAULT 5 CHECK (prioritaet BETWEEN 1 AND 10),
    kommissionierer_id UUID,
    lagerort_id UUID NOT NULL REFERENCES lager.lagerorte(lagerort_id),
    status VARCHAR(20) DEFAULT 'GEPLANT' CHECK (status IN ('GEPLANT', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN', 'STORNIERT')),
    geplante_startzeit TIMESTAMP,
    tatsaechliche_startzeit TIMESTAMP,
    tatsaechliche_endzeit TIMESTAMP,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Kommissionierpositionen
CREATE TABLE lager.kommissionierpositionen (
    position_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kommissionierauftrag_id UUID NOT NULL REFERENCES lager.kommissionierauftraege(kommissionierauftrag_id),
    position INTEGER NOT NULL,
    artikel_id UUID NOT NULL,
    charge_id UUID REFERENCES lager.chargen(charge_id),
    gewuenschte_menge DECIMAL(10,4) NOT NULL,
    kommissionierte_menge DECIMAL(10,4) DEFAULT 0,
    einheit VARCHAR(20) NOT NULL,
    lagerzone_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    kommissionierer_id UUID,
    status VARCHAR(20) DEFAULT 'OFFEN' CHECK (status IN ('OFFEN', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN', 'STORNIERT')),
    kommissionierungszeit TIMESTAMP,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 6. INVENTUR
-- =====================================================

-- Inventur
CREATE TABLE lager.inventur (
    inventur_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventur_nr VARCHAR(50) UNIQUE NOT NULL,
    inventur_typ VARCHAR(50) NOT NULL CHECK (inventur_typ IN ('VOLLINVENTUR', 'STICHPROBENINVENTUR', 'PERMANENTE_INVENTUR')),
    lagerort_id UUID NOT NULL REFERENCES lager.lagerorte(lagerort_id),
    lagerzone_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    inventur_datum DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'GEPLANT' CHECK (status IN ('GEPLANT', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN', 'STORNIERT')),
    verantwortlicher_id UUID,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erstellt_von UUID,
    geaendert_von UUID
);

-- Inventurpositionen
CREATE TABLE lager.inventur_positionen (
    position_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventur_id UUID NOT NULL REFERENCES lager.inventur(inventur_id),
    position INTEGER NOT NULL,
    artikel_id UUID NOT NULL,
    charge_id UUID REFERENCES lager.chargen(charge_id),
    lagerzone_id UUID REFERENCES lager.lagerzonen(lagerzone_id),
    lagerplatz_id UUID REFERENCES lager.lagerplaetze(lagerplatz_id),
    buchbestand DECIMAL(10,4) NOT NULL,
    istbestand DECIMAL(10,4),
    differenz DECIMAL(10,4),
    einheit VARCHAR(20) NOT NULL,
    inventur_status VARCHAR(20) DEFAULT 'OFFEN' CHECK (inventur_status IN ('OFFEN', 'GEPRÃœFT', 'ABGESCHLOSSEN')),
    pruefer_id UUID,
    pruefdatum TIMESTAMP,
    bemerkung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 7. INDEXE UND CONSTRAINTS
-- =====================================================

-- Indexe fÃ¼r bessere Performance
CREATE INDEX idx_lagerorte_lagerort_nr ON lager.lagerorte(lagerort_nr);
CREATE INDEX idx_lagerorte_status ON lager.lagerorte(status);
CREATE INDEX idx_lagerzonen_lagerort ON lager.lagerzonen(lagerort_id);
CREATE INDEX idx_lagerplaetze_lagerzone ON lager.lagerplaetze(lagerzone_id);
CREATE INDEX idx_lagerplaetze_status ON lager.lagerplaetze(status);
CREATE INDEX idx_artikel_bestaende_artikel ON lager.artikel_bestaende(artikel_id);
CREATE INDEX idx_artikel_bestaende_lagerort ON lager.artikel_bestaende(lagerort_id);
CREATE INDEX idx_chargen_artikel ON lager.chargen(artikel_id);
CREATE INDEX idx_chargen_verfallsdatum ON lager.chargen(verfallsdatum);
CREATE INDEX idx_lagerbewegungen_artikel ON lager.lagerbewegungen(artikel_id);
CREATE INDEX idx_lagerbewegungen_datum ON lager.lagerbewegungen(bewegungsdatum);
CREATE INDEX idx_lagerbewegungen_typ ON lager.lagerbewegungen(bewegungstyp);
CREATE INDEX idx_wareneingang_lieferant ON lager.wareneingang(lieferant_id);
CREATE INDEX idx_wareneingang_status ON lager.wareneingang(status);
CREATE INDEX idx_warenausgang_kunde ON lager.warenausgang(kunde_id);
CREATE INDEX idx_warenausgang_status ON lager.warenausgang(status);
CREATE INDEX idx_kommissionierauftraege_warenausgang ON lager.kommissionierauftraege(warenausgang_id);
CREATE INDEX idx_kommissionierauftraege_status ON lager.kommissionierauftraege(status);
CREATE INDEX idx_inventur_lagerort ON lager.inventur(lagerort_id);
CREATE INDEX idx_inventur_status ON lager.inventur(status);

-- =====================================================
-- 8. TRIGGER FÃœR AUTOMATISCHE UPDATES
-- =====================================================

-- Trigger fÃ¼r geaendert_am
CREATE OR REPLACE FUNCTION update_lager_geaendert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geaendert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger auf alle Tabellen anwenden
CREATE TRIGGER trigger_lagerorte_geaendert_am
    BEFORE UPDATE ON lager.lagerorte
    FOR EACH ROW EXECUTE FUNCTION update_lager_geaendert_am();

CREATE TRIGGER trigger_lagerzonen_geaendert_am
    BEFORE UPDATE ON lager.lagerzonen
    FOR EACH ROW EXECUTE FUNCTION update_lager_geaendert_am();

CREATE TRIGGER trigger_lagerplaetze_geaendert_am
    BEFORE UPDATE ON lager.lagerplaetze
    FOR EACH ROW EXECUTE FUNCTION update_lager_geaendert_am();

CREATE TRIGGER trigger_artikel_bestaende_geaendert_am
    BEFORE UPDATE ON lager.artikel_bestaende
    FOR EACH ROW EXECUTE FUNCTION update_lager_geaendert_am();

-- =====================================================
-- 9. FUNKTIONEN FÃœR BERECHNUNGEN
-- =====================================================

-- Funktion fÃ¼r automatische Bewegungsnummern
CREATE OR REPLACE FUNCTION generate_bewegungsnummer()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_number INTEGER;
    new_number VARCHAR(50);
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(bewegungsnummer FROM 4) AS INTEGER)), 0) + 1
    INTO next_number
    FROM lager.lagerbewegungen
    WHERE bewegungsnummer LIKE 'LAG%';
    
    new_number := 'LAG' || LPAD(next_number::TEXT, 6, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Funktion fÃ¼r automatische Wareneingangsnummern
CREATE OR REPLACE FUNCTION generate_wareneingangsnummer()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_number INTEGER;
    new_number VARCHAR(50);
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(wareneingang_nr FROM 4) AS INTEGER)), 0) + 1
    INTO next_number
    FROM lager.wareneingang
    WHERE wareneingang_nr LIKE 'WEI%';
    
    new_number := 'WEI' || LPAD(next_number::TEXT, 6, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Funktion fÃ¼r automatische Warenausgangsnummern
CREATE OR REPLACE FUNCTION generate_warenausgangsnummer()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_number INTEGER;
    new_number VARCHAR(50);
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(warenausgang_nr FROM 4) AS INTEGER)), 0) + 1
    INTO next_number
    FROM lager.warenausgang
    WHERE warenausgang_nr LIKE 'WAU%';
    
    new_number := 'WAU' || LPAD(next_number::TEXT, 6, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Funktion fÃ¼r Bestandsberechnung
CREATE OR REPLACE FUNCTION get_artikel_bestand(artikel_uuid UUID, lagerort_uuid UUID)
RETURNS DECIMAL(10,4) AS $$
DECLARE
    bestand DECIMAL(10,4);
BEGIN
    SELECT COALESCE(SUM(menge_verfuegbar), 0)
    INTO bestand
    FROM lager.artikel_bestaende
    WHERE artikel_id = artikel_uuid AND lagerort_id = lagerort_uuid;
    
    RETURN bestand;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 10. VIEWS FÃœR BERICHTE
-- =====================================================

-- LagerÃ¼bersicht
CREATE VIEW lager.lageruebersicht AS
SELECT 
    lo.lagerort_id,
    lo.lagerort_nr,
    lo.bezeichnung as lagerort_bezeichnung,
    lo.lagerort_typ,
    lo.status as lagerort_status,
    COUNT(lz.lagerzone_id) as anzahl_zonen,
    COUNT(lp.lagerplatz_id) as anzahl_plaetze,
    COUNT(CASE WHEN lp.status = 'BELEGT' THEN 1 END) as belegte_plaetze,
    ROUND(
        COUNT(CASE WHEN lp.status = 'BELEGT' THEN 1 END) * 100.0 / COUNT(lp.lagerplatz_id), 2
    ) as auslastung_prozent,
    lo.kapazitaet_m3,
    lo.belegte_kapazitaet_m3,
    ROUND(
        lo.belegte_kapazitaet_m3 * 100.0 / NULLIF(lo.kapazitaet_m3, 0), 2
    ) as kapazitaetsauslastung_prozent
FROM lager.lagerorte lo
LEFT JOIN lager.lagerzonen lz ON lo.lagerort_id = lz.lagerort_id
LEFT JOIN lager.lagerplaetze lp ON lz.lagerzone_id = lp.lagerzone_id
GROUP BY lo.lagerort_id, lo.lagerort_nr, lo.bezeichnung, lo.lagerort_typ, lo.status, lo.kapazitaet_m3, lo.belegte_kapazitaet_m3
ORDER BY lo.lagerort_nr;

-- BestandsÃ¼bersicht
CREATE VIEW lager.bestandsuebersicht AS
SELECT 
    ab.artikel_id,
    ab.lagerort_id,
    lo.lagerort_nr,
    lo.bezeichnung as lagerort_bezeichnung,
    ab.lagerzone_id,
    lz.lagerzone_nr,
    lz.bezeichnung as lagerzone_bezeichnung,
    ab.menge_verfuegbar,
    ab.menge_reserviert,
    ab.menge_in_qualitaet,
    ab.menge_gesperrt,
    ab.menge_gesamt,
    ab.einheit,
    ab.durchschnittspreis,
    ab.mindestbestand,
    ab.optimalbestand,
    ab.max_bestand,
    CASE 
        WHEN ab.menge_verfuegbar <= ab.mindestbestand THEN 'KRITISCH'
        WHEN ab.menge_verfuegbar <= ab.optimalbestand THEN 'NIEDRIG'
        ELSE 'OK'
    END as bestandsstatus,
    ab.letzte_bewegung,
    ab.naechste_inventur
FROM lager.artikel_bestaende ab
JOIN lager.lagerorte lo ON ab.lagerort_id = lo.lagerort_id
LEFT JOIN lager.lagerzonen lz ON ab.lagerzone_id = lz.lagerzone_id
ORDER BY lo.lagerort_nr, lz.lagerzone_nr;

-- Bewegungsstatistiken
CREATE VIEW lager.bewegungsstatistiken AS
SELECT 
    DATE_TRUNC('day', lb.bewegungsdatum) as tag,
    lb.bewegungstyp,
    COUNT(*) as anzahl_bewegungen,
    SUM(lb.menge) as gesamtmenge,
    COUNT(DISTINCT lb.artikel_id) as anzahl_artikel,
    COUNT(DISTINCT lb.personal_id) as anzahl_personal
FROM lager.lagerbewegungen lb
WHERE lb.bewegungsdatum >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', lb.bewegungsdatum), lb.bewegungstyp
ORDER BY tag DESC, lb.bewegungstyp;

-- =====================================================
-- 11. BEISPIELDATEN
-- =====================================================

-- Beispiel-Lagerorte
INSERT INTO lager.lagerorte (lagerort_nr, bezeichnung, lagerort_typ, standort, kapazitaet_m3) VALUES
('LAG-001', 'Hauptlager MÃ¼nchen', 'HAUPTLAGER', 'MÃ¼nchen', 5000.0),
('LAG-002', 'Produktionslager', 'PRODUKTIONSLAGER', 'MÃ¼nchen', 2000.0),
('LAG-003', 'QualitÃ¤tslager', 'QUALITAETSLAGER', 'MÃ¼nchen', 500.0);

-- Beispiel-Lagerzonen
INSERT INTO lager.lagerzonen (lagerort_id, lagerzone_nr, bezeichnung, lagerzone_typ, kapazitaet_m3) VALUES
((SELECT lagerort_id FROM lager.lagerorte WHERE lagerort_nr = 'LAG-001'), 'ZONE-001', 'Rohstoffe Zone A', 'ROHSTOFFE', 1000.0),
((SELECT lagerort_id FROM lager.lagerorte WHERE lagerort_nr = 'LAG-001'), 'ZONE-002', 'Halbfertige Zone B', 'HALBFERTIGE', 800.0),
((SELECT lagerort_id FROM lager.lagerorte WHERE lagerort_nr = 'LAG-001'), 'ZONE-003', 'Fertigprodukte Zone C', 'FERTIGPRODUKTE', 1200.0),
((SELECT lagerort_id FROM lager.lagerorte WHERE lagerort_nr = 'LAG-002'), 'ZONE-004', 'Produktionslager Zone A', 'ROHSTOFFE', 800.0);

-- Beispiel-LagerplÃ¤tze
INSERT INTO lager.lagerplaetze (lagerzone_id, lagerplatz_nr, bezeichnung, lagerplatz_typ, regal_nr, ebene_nr, fach_nr, volumen_m3, max_gewicht_kg) VALUES
((SELECT lagerzone_id FROM lager.lagerzonen WHERE lagerzone_nr = 'ZONE-001'), 'PLATZ-001', 'Regal A1-Ebene 1-Fach 1', 'REGAL', 'A1', '1', '1', 2.0, 500.0),
((SELECT lagerzone_id FROM lager.lagerzonen WHERE lagerzone_nr = 'ZONE-001'), 'PLATZ-002', 'Regal A1-Ebene 1-Fach 2', 'REGAL', 'A1', '1', '2', 2.0, 500.0),
((SELECT lagerzone_id FROM lager.lagerzonen WHERE lagerzone_nr = 'ZONE-002'), 'PLATZ-003', 'Regal B1-Ebene 1-Fach 1', 'REGAL', 'B1', '1', '1', 1.5, 300.0),
((SELECT lagerzone_id FROM lager.lagerzonen WHERE lagerzone_nr = 'ZONE-003'), 'PLATZ-004', 'Bodenlager C1', 'BODENLAGER', NULL, NULL, NULL, 5.0, 1000.0);

COMMIT; 
