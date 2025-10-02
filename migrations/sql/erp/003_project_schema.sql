-- =====================================================
-- PROJEKTMANAGEMENT SCHEMA
-- =====================================================

-- Schema erstellen
CREATE SCHEMA IF NOT EXISTS projekte;

-- =====================================================
-- PROJEKTE UND PROJEKTVERWALTUNG
-- =====================================================

-- Projektkategorien
CREATE TABLE projekte.projektkategorien (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kategorie_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    farbe VARCHAR(7) DEFAULT '#1976d2',
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projekte
CREATE TABLE projekte.projekte (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projektnummer VARCHAR(20) UNIQUE NOT NULL,
    projektname VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    kategorie_id UUID REFERENCES projekte.projektkategorien(id),
    status VARCHAR(50) DEFAULT 'planung' CHECK (status IN ('planung', 'aktiv', 'pausiert', 'abgeschlossen', 'abgebrochen')),
    prioritaet VARCHAR(20) DEFAULT 'normal' CHECK (prioritaet IN ('niedrig', 'normal', 'hoch', 'kritisch')),
    startdatum DATE,
    enddatum DATE,
    ist_abgeschlossen BOOLEAN DEFAULT FALSE,
    projektleiter_id UUID REFERENCES personal.mitarbeiter(id),
    kunde_id UUID REFERENCES crm.kunden(id),
    budget_geplant DECIMAL(15,2),
    budget_ist DECIMAL(15,2),
    stunden_geplant DECIMAL(10,2),
    stunden_ist DECIMAL(10,2),
    fortschritt_prozent DECIMAL(5,2) DEFAULT 0,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projektphasen
CREATE TABLE projekte.projektphasen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projekt_id UUID REFERENCES projekte.projekte(id) ON DELETE CASCADE,
    phasenname VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    reihenfolge INTEGER NOT NULL,
    startdatum DATE,
    enddatum DATE,
    status VARCHAR(50) DEFAULT 'geplant' CHECK (status IN ('geplant', 'aktiv', 'abgeschlossen')),
    fortschritt_prozent DECIMAL(5,2) DEFAULT 0,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meilensteine
CREATE TABLE projekte.meilensteine (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projekt_id UUID REFERENCES projekte.projekte(id) ON DELETE CASCADE,
    phasen_id UUID REFERENCES projekte.projektphasen(id) ON DELETE CASCADE,
    meilenstein_name VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    termin DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'offen' CHECK (status IN ('offen', 'erreicht', 'verschoben', 'verpasst')),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- AUFGABEN UND ARBEITSPAKETE
-- =====================================================

-- Aufgabentypen
CREATE TABLE projekte.aufgabentypen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    typ_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    standard_dauer_stunden DECIMAL(5,2),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aufgaben
CREATE TABLE projekte.aufgaben (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aufgabenname VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    projekt_id UUID REFERENCES projekte.projekte(id) ON DELETE CASCADE,
    phasen_id UUID REFERENCES projekte.projektphasen(id) ON DELETE CASCADE,
    aufgabentyp_id UUID REFERENCES projekte.aufgabentypen(id),
    status VARCHAR(50) DEFAULT 'offen' CHECK (status IN ('offen', 'in_arbeit', 'review', 'abgeschlossen', 'abgebrochen')),
    prioritaet VARCHAR(20) DEFAULT 'normal' CHECK (prioritaet IN ('niedrig', 'normal', 'hoch', 'kritisch')),
    zugewiesen_an UUID REFERENCES personal.mitarbeiter(id),
    erstellt_von UUID REFERENCES personal.mitarbeiter(id),
    startdatum DATE,
    enddatum DATE,
    geschaetzte_stunden DECIMAL(5,2),
    tatsaechliche_stunden DECIMAL(5,2),
    fortschritt_prozent DECIMAL(5,2) DEFAULT 0,
    vorgaenger_aufgaben TEXT[], -- Array von Aufgabennummern
    nachfolger_aufgaben TEXT[], -- Array von Aufgabennummern
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unteraufgaben
CREATE TABLE projekte.unteraufgaben (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aufgabe_id UUID REFERENCES projekte.aufgaben(id) ON DELETE CASCADE,
    unteraufgabenname VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    status VARCHAR(50) DEFAULT 'offen' CHECK (status IN ('offen', 'in_arbeit', 'abgeschlossen')),
    zugewiesen_an UUID REFERENCES personal.mitarbeiter(id),
    geschaetzte_stunden DECIMAL(5,2),
    tatsaechliche_stunden DECIMAL(5,2),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- RESSOURCEN UND ZUORDNUNGEN
-- =====================================================

-- Ressourcentypen
CREATE TABLE projekte.ressourcentypen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    typ_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    einheit VARCHAR(20) DEFAULT 'Stunden',
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projektressourcen
CREATE TABLE projekte.projektressourcen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projekt_id UUID REFERENCES projekte.projekte(id) ON DELETE CASCADE,
    ressourcentyp_id UUID REFERENCES projekte.ressourcentypen(id),
    ressourcen_name VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    verfuegbarkeit_prozent DECIMAL(5,2) DEFAULT 100,
    kosten_pro_einheit DECIMAL(10,2),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ressourcenzuordnungen
CREATE TABLE projekte.ressourcenzuordnungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projekt_id UUID REFERENCES projekte.projekte(id) ON DELETE CASCADE,
    aufgabe_id UUID REFERENCES projekte.aufgaben(id) ON DELETE CASCADE,
    ressourcen_id UUID REFERENCES projekte.projektressourcen(id),
    mitarbeiter_id UUID REFERENCES personal.mitarbeiter(id),
    startdatum DATE NOT NULL,
    enddatum DATE NOT NULL,
    stunden_pro_tag DECIMAL(4,2) DEFAULT 8,
    verfuegbarkeit_prozent DECIMAL(5,2) DEFAULT 100,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ZEITERFASSUNG
-- =====================================================

-- Zeiterfassung
CREATE TABLE projekte.zeiterfassung (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mitarbeiter_id UUID REFERENCES personal.mitarbeiter(id),
    projekt_id UUID REFERENCES projekte.projekte(id),
    aufgabe_id UUID REFERENCES projekte.aufgaben(id),
    unteraufgabe_id UUID REFERENCES projekte.unteraufgaben(id),
    datum DATE NOT NULL,
    startzeit TIME,
    endzeit TIME,
    pause_minuten INTEGER DEFAULT 0,
    arbeitsstunden DECIMAL(4,2),
    ueberstunden DECIMAL(4,2),
    beschreibung TEXT,
    status VARCHAR(50) DEFAULT 'offen' CHECK (status IN ('offen', 'genehmigt', 'abgelehnt')),
    genehmigt_von UUID REFERENCES personal.mitarbeiter(id),
    genehmigt_am TIMESTAMP,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Zeiterfassungskategorien
CREATE TABLE projekte.zeiterfassungskategorien (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kategorie_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    ist_ueberstunden BOOLEAN DEFAULT FALSE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- BUDGET UND KOSTEN
-- =====================================================

-- Projektbudgets
CREATE TABLE projekte.projektbudgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projekt_id UUID REFERENCES projekte.projekte(id) ON DELETE CASCADE,
    budget_jahr INTEGER NOT NULL,
    budget_typ VARCHAR(50) DEFAULT 'gesamt' CHECK (budget_typ IN ('gesamt', 'personal', 'material', 'extern')),
    budget_betrag DECIMAL(15,2) NOT NULL,
    verbraucht_betrag DECIMAL(15,2) DEFAULT 0,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projektkosten
CREATE TABLE projekte.projektkosten (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projekt_id UUID REFERENCES projekte.projekte(id),
    aufgabe_id UUID REFERENCES projekte.aufgaben(id),
    kostenart VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    betrag DECIMAL(15,2) NOT NULL,
    datum DATE NOT NULL,
    rechnung_id UUID, -- Referenz auf externe Rechnungen
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KOMMUNIKATION UND DOKUMENTATION
-- =====================================================

-- Projektnotizen
CREATE TABLE projekte.projektnotizen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projekt_id UUID REFERENCES projekte.projekte(id) ON DELETE CASCADE,
    aufgabe_id UUID REFERENCES projekte.aufgaben(id) ON DELETE CASCADE,
    autor_id UUID REFERENCES personal.mitarbeiter(id),
    titel VARCHAR(200) NOT NULL,
    inhalt TEXT NOT NULL,
    ist_oeffentlich BOOLEAN DEFAULT TRUE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projektdateien
CREATE TABLE projekte.projektdateien (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projekt_id UUID REFERENCES projekte.projekte(id) ON DELETE CASCADE,
    aufgabe_id UUID REFERENCES projekte.aufgaben(id) ON DELETE CASCADE,
    dateiname VARCHAR(255) NOT NULL,
    original_dateiname VARCHAR(255) NOT NULL,
    dateityp VARCHAR(50),
    groesse_bytes BIGINT,
    pfad VARCHAR(500) NOT NULL,
    hochgeladen_von UUID REFERENCES personal.mitarbeiter(id),
    beschreibung TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXE
-- =====================================================

-- Projekte Indexe
CREATE INDEX idx_projekte_status ON projekte.projekte(status);
CREATE INDEX idx_projekte_projektleiter ON projekte.projekte(projektleiter_id);
CREATE INDEX idx_projekte_kunde ON projekte.projekte(kunde_id);
CREATE INDEX idx_projekte_startdatum ON projekte.projekte(startdatum);
CREATE INDEX idx_projekte_enddatum ON projekte.projekte(enddatum);

-- Aufgaben Indexe
CREATE INDEX idx_aufgaben_projekt ON projekte.aufgaben(projekt_id);
CREATE INDEX idx_aufgaben_status ON projekte.aufgaben(status);
CREATE INDEX idx_aufgaben_zugewiesen ON projekte.aufgaben(zugewiesen_an);
CREATE INDEX idx_aufgaben_startdatum ON projekte.aufgaben(startdatum);
CREATE INDEX idx_aufgaben_enddatum ON projekte.aufgaben(enddatum);

-- Zeiterfassung Indexe
CREATE INDEX idx_zeiterfassung_mitarbeiter ON projekte.zeiterfassung(mitarbeiter_id);
CREATE INDEX idx_zeiterfassung_projekt ON projekte.zeiterfassung(projekt_id);
CREATE INDEX idx_zeiterfassung_datum ON projekte.zeiterfassung(datum);
CREATE INDEX idx_zeiterfassung_status ON projekte.zeiterfassung(status);

-- =====================================================
-- TRIGGER FÃœR AUTOMATISCHE TIMESTAMP-UPDATES
-- =====================================================

-- Trigger-Funktion fÃ¼r geaendert_am
CREATE OR REPLACE FUNCTION projekte.update_geaendert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geaendert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r alle Tabellen
CREATE TRIGGER trigger_projekte_update_geaendert_am
    BEFORE UPDATE ON projekte.projekte
    FOR EACH ROW EXECUTE FUNCTION projekte.update_geaendert_am();

CREATE TRIGGER trigger_aufgaben_update_geaendert_am
    BEFORE UPDATE ON projekte.aufgaben
    FOR EACH ROW EXECUTE FUNCTION projekte.update_geaendert_am();

CREATE TRIGGER trigger_zeiterfassung_update_geaendert_am
    BEFORE UPDATE ON projekte.zeiterfassung
    FOR EACH ROW EXECUTE FUNCTION projekte.update_geaendert_am();

-- =====================================================
-- FUNKTIONEN FÃœR AUTOMATISCHE NUMMERIERUNG
-- =====================================================

-- Projektnummern-Generierung
CREATE OR REPLACE FUNCTION projekte.generate_projektnummer()
RETURNS VARCHAR AS $$
DECLARE
    next_number INTEGER;
    project_number VARCHAR(20);
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(projektnummer FROM 4) AS INTEGER)), 0) + 1
    INTO next_number
    FROM projekte.projekte
    WHERE projektnummer LIKE 'PRJ%';
    
    project_number := 'PRJ' || LPAD(next_number::TEXT, 6, '0');
    RETURN project_number;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNKTIONEN FÃœR BERECHNUNGEN
-- =====================================================

-- Projektfortschritt berechnen
CREATE OR REPLACE FUNCTION projekte.calculate_project_progress(project_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    total_tasks INTEGER;
    completed_tasks INTEGER;
    progress DECIMAL(5,2);
BEGIN
    SELECT COUNT(*), COUNT(CASE WHEN status = 'abgeschlossen' THEN 1 END)
    INTO total_tasks, completed_tasks
    FROM projekte.aufgaben
    WHERE projekt_id = project_id;
    
    IF total_tasks = 0 THEN
        progress := 0;
    ELSE
        progress := (completed_tasks::DECIMAL / total_tasks::DECIMAL) * 100;
    END IF;
    
    RETURN ROUND(progress, 2);
END;
$$ LANGUAGE plpgsql;

-- Projektstatistiken
CREATE OR REPLACE FUNCTION projekte.get_project_statistics()
RETURNS TABLE (
    total_projects INTEGER,
    active_projects INTEGER,
    completed_projects INTEGER,
    overdue_projects INTEGER,
    total_hours_planned DECIMAL,
    total_hours_actual DECIMAL,
    total_budget_planned DECIMAL,
    total_budget_actual DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_projects,
        COUNT(CASE WHEN status = 'aktiv' THEN 1 END)::INTEGER as active_projects,
        COUNT(CASE WHEN status = 'abgeschlossen' THEN 1 END)::INTEGER as completed_projects,
        COUNT(CASE WHEN enddatum < CURRENT_DATE AND status NOT IN ('abgeschlossen', 'abgebrochen') THEN 1 END)::INTEGER as overdue_projects,
        COALESCE(SUM(stunden_geplant), 0) as total_hours_planned,
        COALESCE(SUM(stunden_ist), 0) as total_hours_actual,
        COALESCE(SUM(budget_geplant), 0) as total_budget_planned,
        COALESCE(SUM(budget_ist), 0) as total_budget_actual
    FROM projekte.projekte;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS FÃœR REPORTING
-- =====================================================

-- ProjektÃ¼bersicht
CREATE VIEW projekte.projekt_uebersicht AS
SELECT 
    p.id,
    p.projektnummer,
    p.projektname,
    pk.kategorie_name,
    p.status,
    p.prioritaet,
    p.startdatum,
    p.enddatum,
    p.ist_abgeschlossen,
    CONCAT(m.vorname, ' ', m.nachname) as projektleiter,
    c.firmenname as kunde,
    p.budget_geplant,
    p.budget_ist,
    p.stunden_geplant,
    p.stunden_ist,
    p.fortschritt_prozent,
    CASE 
        WHEN p.enddatum < CURRENT_DATE AND p.status NOT IN ('abgeschlossen', 'abgebrochen') THEN 'Ã¼berfÃ¤llig'
        WHEN p.enddatum = CURRENT_DATE THEN 'heute fÃ¤llig'
        ELSE 'pÃ¼nktlich'
    END as termin_status
FROM projekte.projekte p
LEFT JOIN projekte.projektkategorien pk ON p.kategorie_id = pk.id
LEFT JOIN personal.mitarbeiter m ON p.projektleiter_id = m.id
LEFT JOIN crm.kunden c ON p.kunde_id = c.id;

-- AufgabenÃ¼bersicht
CREATE VIEW projekte.aufgaben_uebersicht AS
SELECT 
    a.id,
    a.aufgabenname,
    p.projektnummer,
    p.projektname,
    pp.phasenname,
    at.typ_name as aufgabentyp,
    a.status,
    a.prioritaet,
    CONCAT(m.vorname, ' ', m.nachname) as zugewiesen_an,
    a.startdatum,
    a.enddatum,
    a.geschaetzte_stunden,
    a.tatsaechliche_stunden,
    a.fortschritt_prozent,
    CASE 
        WHEN a.enddatum < CURRENT_DATE AND a.status NOT IN ('abgeschlossen', 'abgebrochen') THEN 'Ã¼berfÃ¤llig'
        WHEN a.enddatum = CURRENT_DATE THEN 'heute fÃ¤llig'
        ELSE 'pÃ¼nktlich'
    END as termin_status
FROM projekte.aufgaben a
LEFT JOIN projekte.projekte p ON a.projekt_id = p.id
LEFT JOIN projekte.projektphasen pp ON a.phasen_id = pp.id
LEFT JOIN projekte.aufgabentypen at ON a.aufgabentyp_id = at.id
LEFT JOIN personal.mitarbeiter m ON a.zugewiesen_an = m.id;

-- ZeiterfassungsÃ¼bersicht
CREATE VIEW projekte.zeiterfassung_uebersicht AS
SELECT 
    z.id,
    CONCAT(m.vorname, ' ', m.nachname) as mitarbeiter,
    p.projektnummer,
    p.projektname,
    a.aufgabenname,
    z.datum,
    z.startzeit,
    z.endzeit,
    z.arbeitsstunden,
    z.ueberstunden,
    z.beschreibung,
    z.status
FROM projekte.zeiterfassung z
LEFT JOIN personal.mitarbeiter m ON z.mitarbeiter_id = m.id
LEFT JOIN projekte.projekte p ON z.projekt_id = p.id
LEFT JOIN projekte.aufgaben a ON z.aufgabe_id = a.id;

-- =====================================================
-- BEISPIEL-DATEN
-- =====================================================

-- Projektkategorien
INSERT INTO projekte.projektkategorien (kategorie_name, beschreibung, farbe) VALUES
('Software-Entwicklung', 'Entwicklung von Software-LÃ¶sungen', '#1976d2'),
('Beratung', 'Beratungsprojekte und Consulting', '#388e3c'),
('Schulung', 'Schulungs- und Trainingsprojekte', '#f57c00'),
('Wartung', 'Wartungs- und Support-Projekte', '#7b1fa2'),
('Migration', 'Datenmigration und Systemumstellung', '#d32f2f');

-- Aufgabentypen
INSERT INTO projekte.aufgabentypen (typ_name, beschreibung, standard_dauer_stunden) VALUES
('Analyse', 'Anforderungsanalyse und Konzeption', 8.0),
('Entwicklung', 'Programmierung und Implementierung', 16.0),
('Test', 'Testing und QualitÃ¤tssicherung', 4.0),
('Dokumentation', 'Erstellung von Dokumentation', 4.0),
('Schulung', 'Benutzerschulung und Training', 8.0),
('Deployment', 'Installation und Inbetriebnahme', 4.0);

-- Ressourcentypen
INSERT INTO projekte.ressourcentypen (typ_name, beschreibung, einheit) VALUES
('Personal', 'Mitarbeiterressourcen', 'Stunden'),
('Hardware', 'Hardware-Ressourcen', 'Stunden'),
('Software', 'Software-Lizenzen', 'Monate'),
('Externe', 'Externe Dienstleister', 'Stunden');

-- Zeiterfassungskategorien
INSERT INTO projekte.zeiterfassungskategorien (kategorie_name, beschreibung, ist_ueberstunden) VALUES
('Normale Arbeitszeit', 'RegulÃ¤re Arbeitszeiten', FALSE),
('Ãœberstunden', 'Ãœberstunden und Mehrarbeit', TRUE),
('Reisezeit', 'Zeit fÃ¼r Dienstreisen', FALSE),
('Schulung', 'Zeit fÃ¼r Schulungen und Weiterbildung', FALSE);

-- Beispiel-Projekte
INSERT INTO projekte.projekte (projektnummer, projektname, beschreibung, kategorie_id, status, prioritaet, startdatum, enddatum, budget_geplant, stunden_geplant) VALUES
(projekte.generate_projektnummer(), 'ERP-System Modernisierung', 'Modernisierung des bestehenden ERP-Systems', 1, 'aktiv', 'hoch', '2024-01-15', '2024-12-31', 500000.00, 2000.00),
(projekte.generate_projektnummer(), 'Kundenportal Entwicklung', 'Entwicklung eines Kundenportals', 1, 'planung', 'normal', '2024-03-01', '2024-08-31', 150000.00, 800.00),
(projekte.generate_projektnummer(), 'Prozessoptimierung Beratung', 'Beratung zur Prozessoptimierung', 2, 'abgeschlossen', 'normal', '2023-10-01', '2024-01-31', 75000.00, 400.00);

-- Beispiel-Aufgaben
INSERT INTO projekte.aufgaben (aufgabenname, beschreibung, projekt_id, aufgabentyp_id, status, prioritaet, geschaetzte_stunden) VALUES
('Anforderungsanalyse', 'Detaillierte Analyse der Anforderungen', (SELECT id FROM projekte.projekte WHERE projektname = 'ERP-System Modernisierung' LIMIT 1), 1, 'abgeschlossen', 'hoch', 40.0),
('Datenbank-Design', 'Entwicklung des neuen Datenbankschemas', (SELECT id FROM projekte.projekte WHERE projektname = 'ERP-System Modernisierung' LIMIT 1), 2, 'in_arbeit', 'hoch', 80.0),
('Frontend-Entwicklung', 'Entwicklung der BenutzeroberflÃ¤che', (SELECT id FROM projekte.projekte WHERE projektname = 'ERP-System Modernisierung' LIMIT 1), 2, 'offen', 'normal', 120.0);

-- Beispiel-Zeiterfassung
INSERT INTO projekte.zeiterfassung (mitarbeiter_id, projekt_id, aufgabe_id, datum, startzeit, endzeit, arbeitsstunden, beschreibung) VALUES
((SELECT id FROM personal.mitarbeiter LIMIT 1), (SELECT id FROM projekte.projekte WHERE projektname = 'ERP-System Modernisierung' LIMIT 1), (SELECT id FROM projekte.aufgaben WHERE aufgabenname = 'Datenbank-Design' LIMIT 1), CURRENT_DATE, '09:00', '17:00', 8.0, 'Datenbankschema-Entwicklung'),
((SELECT id FROM personal.mitarbeiter LIMIT 1), (SELECT id FROM projekte.projekte WHERE projektname = 'ERP-System Modernisierung' LIMIT 1), (SELECT id FROM projekte.aufgaben WHERE aufgabenname = 'Datenbank-Design' LIMIT 1), CURRENT_DATE - INTERVAL '1 day', '09:00', '18:00', 9.0, 'Tabellen-Design und Beziehungen');

-- =====================================================
-- KOMMENTARE
-- =====================================================

COMMENT ON SCHEMA projekte IS 'Projektmanagement-Modul fÃ¼r VALEO NeuroERP';
COMMENT ON TABLE projekte.projekte IS 'Haupttabelle fÃ¼r Projekte und Projektverwaltung';
COMMENT ON TABLE projekte.aufgaben IS 'Aufgaben und Arbeitspakete innerhalb von Projekten';
COMMENT ON TABLE projekte.zeiterfassung IS 'Zeiterfassung fÃ¼r Projekte und Aufgaben';
COMMENT ON TABLE projekte.projektressourcen IS 'Ressourcen (Personal, Hardware, etc.) fÃ¼r Projekte';
COMMENT ON TABLE projekte.meilensteine IS 'Meilensteine und wichtige Termine in Projekten';
COMMENT ON TABLE projekte.projektbudgets IS 'Budgetplanung und -verfolgung fÃ¼r Projekte'; 
