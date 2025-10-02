-- =====================================================
-- VALEO NeuroERP - Reporting & Analytics Schema
-- =====================================================

-- Schema fÃ¼r Reporting und Analytics
CREATE SCHEMA IF NOT EXISTS reporting;

-- =====================================================
-- BERICHTSVERWALTUNG
-- =====================================================

-- Berichtskategorien
CREATE TABLE reporting.berichtskategorien (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kategorie_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    icon_name VARCHAR(50),
    farbe VARCHAR(7), -- Hex-Farbe
    sortierung INTEGER DEFAULT 0,
    aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_von UUID REFERENCES personal.mitarbeiter(id),
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Berichtsvorlagen
CREATE TABLE reporting.berichtsvorlagen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vorlagen_name VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    kategorie_id UUID NOT NULL REFERENCES reporting.berichtskategorien(id),
    bericht_typ VARCHAR(50) NOT NULL, -- 'TABELLE', 'DIAGRAMM', 'DASHBOARD', 'EXPORT'
    sql_query TEXT NOT NULL,
    parameter_definition JSONB, -- Definition der Parameter
    standard_parameter JSONB, -- Standardwerte fÃ¼r Parameter
    export_formate VARCHAR(100)[], -- ['PDF', 'EXCEL', 'CSV', 'JSON']
    refresh_intervall INTEGER, -- in Minuten, NULL = manuell
    letzter_refresh TIMESTAMP,
    naechster_refresh TIMESTAMP,
    aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_von UUID REFERENCES personal.mitarbeiter(id),
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BerichtsausfÃ¼hrungen
CREATE TABLE reporting.berichtsausfuehrungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vorlagen_id UUID NOT NULL REFERENCES reporting.berichtsvorlagen(id),
    ausfuehrungs_name VARCHAR(200),
    parameter_werte JSONB, -- TatsÃ¤chliche Parameterwerte
    ausfuehrungs_status VARCHAR(50) NOT NULL, -- 'GESTARTET', 'LAEUFT', 'ABGESCHLOSSEN', 'FEHLER'
    start_zeit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ende_zeit TIMESTAMP,
    dauer_sekunden INTEGER,
    ergebnis_anzahl INTEGER, -- Anzahl der DatensÃ¤tze
    fehlermeldung TEXT,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- DASHBOARD VERWALTUNG
-- =====================================================

-- Dashboard-Definitionen
CREATE TABLE reporting.dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_name VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    layout_definition JSONB NOT NULL, -- Grid-Layout Definition
    standard_dashboard BOOLEAN DEFAULT false,
    aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_von UUID REFERENCES personal.mitarbeiter(id),
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dashboard-Widgets
CREATE TABLE reporting.dashboard_widgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_id UUID NOT NULL REFERENCES reporting.dashboards(id),
    widget_name VARCHAR(200) NOT NULL,
    widget_typ VARCHAR(50) NOT NULL, -- 'KPI', 'DIAGRAMM', 'TABELLE', 'TEXT'
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    breite INTEGER NOT NULL DEFAULT 1,
    hoehe INTEGER NOT NULL DEFAULT 1,
    konfiguration JSONB, -- Widget-spezifische Konfiguration
    datenquelle_id UUID REFERENCES reporting.berichtsvorlagen(id),
    refresh_intervall INTEGER, -- in Sekunden
    letzter_refresh TIMESTAMP,
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- KPI VERWALTUNG
-- =====================================================

-- KPI-Definitionen
CREATE TABLE reporting.kpi_definitionen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_name VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    kategorie VARCHAR(100), -- 'FINANZEN', 'PRODUKTION', 'VERKAUF', 'LAGER', etc.
    berechnungs_formel TEXT NOT NULL, -- SQL-Formel fÃ¼r KPI-Berechnung
    einheit VARCHAR(50), -- 'EUR', 'STUECK', 'PROZENT', etc.
    ziel_wert DECIMAL(15,2),
    warnung_unter DECIMAL(15,2),
    warnung_ueber DECIMAL(15,2),
    trend_richtung VARCHAR(20), -- 'AUFWAERTS', 'ABWAERTS', 'NEUTRAL'
    refresh_intervall INTEGER DEFAULT 300, -- in Sekunden
    letzter_refresh TIMESTAMP,
    aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_von UUID REFERENCES personal.mitarbeiter(id),
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KPI-Werte (historisch)
CREATE TABLE reporting.kpi_werte (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id UUID NOT NULL REFERENCES reporting.kpi_definitionen(id),
    wert DECIMAL(15,2) NOT NULL,
    zeitstempel TIMESTAMP NOT NULL,
    kontext JSONB, -- ZusÃ¤tzliche Kontext-Informationen
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- EXPORT VERWALTUNG
-- =====================================================

-- Export-Jobs
CREATE TABLE reporting.export_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name VARCHAR(200) NOT NULL,
    berichtsvorlage_id UUID REFERENCES reporting.berichtsvorlagen(id),
    export_format VARCHAR(20) NOT NULL, -- 'PDF', 'EXCEL', 'CSV', 'JSON'
    parameter_werte JSONB,
    ziel_pfad VARCHAR(500),
    datei_name VARCHAR(200),
    job_status VARCHAR(50) NOT NULL, -- 'QUEUED', 'RUNNING', 'COMPLETED', 'FAILED'
    start_zeit TIMESTAMP,
    ende_zeit TIMESTAMP,
    dauer_sekunden INTEGER,
    datei_groesse_bytes BIGINT,
    fehlermeldung TEXT,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Export-Vorlagen
CREATE TABLE reporting.export_vorlagen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vorlagen_name VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    export_format VARCHAR(20) NOT NULL,
    vorlagen_definition JSONB NOT NULL, -- Format-spezifische Definition
    aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_von UUID REFERENCES personal.mitarbeiter(id),
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- AUTOMATISCHE BERICHTSVERSENDUNG
-- =====================================================

-- Berichtsversendung-Planung
CREATE TABLE reporting.berichtsversendung (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    berichtsvorlage_id UUID NOT NULL REFERENCES reporting.berichtsvorlagen(id),
    versand_typ VARCHAR(50) NOT NULL, -- 'EMAIL', 'SYSTEM', 'API'
    empfaenger_definition JSONB NOT NULL, -- EmpfÃ¤nger-Konfiguration
    parameter_werte JSONB,
    export_format VARCHAR(20) DEFAULT 'PDF',
    zeitplan_typ VARCHAR(50) NOT NULL, -- 'EINMAL', 'TAEGLICH', 'WOECHENTLICH', 'MONATLICH'
    zeitplan_konfiguration JSONB, -- Cron-Ã¤hnliche Konfiguration
    naechste_ausfuehrung TIMESTAMP,
    letzte_ausfuehrung TIMESTAMP,
    aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_von UUID REFERENCES personal.mitarbeiter(id),
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Berichtsversendung-Historie
CREATE TABLE reporting.versendung_historie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    versendung_id UUID NOT NULL REFERENCES reporting.berichtsversendung(id),
    ausfuehrungs_zeit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL, -- 'ERFOLGREICH', 'FEHLER', 'TEILWEISE'
    empfaenger_anzahl INTEGER,
    erfolgreich_versendet INTEGER,
    fehlgeschlagene_versendungen INTEGER,
    fehlermeldung TEXT,
    export_job_id UUID REFERENCES reporting.export_jobs(id)
);

-- =====================================================
-- DRILL-DOWN VERWALTUNG
-- =====================================================

-- Drill-Down-Definitionen
CREATE TABLE reporting.drill_down_definitionen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    quell_bericht_id UUID NOT NULL REFERENCES reporting.berichtsvorlagen(id),
    ziel_bericht_id UUID NOT NULL REFERENCES reporting.berichtsvorlagen(id),
    drill_down_felder JSONB NOT NULL, -- Mapping zwischen Quell- und Ziel-Feldern
    aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_von UUID REFERENCES personal.mitarbeiter(id),
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- BENUTZER-EINSTELLUNGEN
-- =====================================================

-- Benutzer-Dashboard-Einstellungen
CREATE TABLE reporting.benutzer_dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mitarbeiter_id UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    dashboard_id UUID NOT NULL REFERENCES reporting.dashboards(id),
    ist_standard BOOLEAN DEFAULT false,
    layout_anpassungen JSONB, -- Benutzer-spezifische Layout-Anpassungen
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mitarbeiter_id, dashboard_id)
);

-- Benutzer-Berichts-Einstellungen
CREATE TABLE reporting.benutzer_berichtseinstellungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mitarbeiter_id UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    berichtsvorlage_id UUID NOT NULL REFERENCES reporting.berichtsvorlagen(id),
    standard_parameter JSONB, -- Benutzer-spezifische Standard-Parameter
    export_format VARCHAR(20) DEFAULT 'PDF',
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mitarbeiter_id, berichtsvorlage_id)
);

-- =====================================================
-- CACHE UND PERFORMANCE
-- =====================================================

-- Berichts-Cache
CREATE TABLE reporting.berichts_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(500) NOT NULL UNIQUE,
    berichtsvorlage_id UUID NOT NULL REFERENCES reporting.berichtsvorlagen(id),
    parameter_hash VARCHAR(64) NOT NULL,
    ergebnis_daten JSONB,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ablauf_am TIMESTAMP NOT NULL
);

-- Performance-Metriken
CREATE TABLE reporting.performance_metriken (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metrik_typ VARCHAR(50) NOT NULL, -- 'BERICHT_AUSFUEHRUNG', 'EXPORT', 'CACHE_HIT'
    berichtsvorlage_id UUID REFERENCES reporting.berichtsvorlagen(id),
    dauer_ms INTEGER,
    datensatz_anzahl INTEGER,
    cache_hit BOOLEAN,
    benutzer_id UUID REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXE
-- =====================================================

-- Berichtsvorlagen Indexe
CREATE INDEX idx_berichtsvorlagen_kategorie ON reporting.berichtsvorlagen(kategorie_id);
CREATE INDEX idx_berichtsvorlagen_typ ON reporting.berichtsvorlagen(bericht_typ);
CREATE INDEX idx_berichtsvorlagen_aktiv ON reporting.berichtsvorlagen(aktiv);
CREATE INDEX idx_berichtsvorlagen_refresh ON reporting.berichtsvorlagen(naechster_refresh);

-- BerichtsausfÃ¼hrungen Indexe
CREATE INDEX idx_berichtsausfuehrungen_vorlage ON reporting.berichtsausfuehrungen(vorlagen_id);
CREATE INDEX idx_berichtsausfuehrungen_status ON reporting.berichtsausfuehrungen(ausfuehrungs_status);
CREATE INDEX idx_berichtsausfuehrungen_zeit ON reporting.berichtsausfuehrungen(start_zeit);

-- Dashboard Indexe
CREATE INDEX idx_dashboard_widgets_dashboard ON reporting.dashboard_widgets(dashboard_id);
CREATE INDEX idx_dashboard_widgets_typ ON reporting.dashboard_widgets(widget_typ);
CREATE INDEX idx_dashboard_widgets_refresh ON reporting.dashboard_widgets(letzter_refresh);

-- KPI Indexe
CREATE INDEX idx_kpi_definitionen_kategorie ON reporting.kpi_definitionen(kategorie);
CREATE INDEX idx_kpi_definitionen_refresh ON reporting.kpi_definitionen(letzter_refresh);
CREATE INDEX idx_kpi_werte_kpi_zeit ON reporting.kpi_werte(kpi_id, zeitstempel);

-- Export Indexe
CREATE INDEX idx_export_jobs_status ON reporting.export_jobs(job_status);
CREATE INDEX idx_export_jobs_zeit ON reporting.export_jobs(start_zeit);

-- Berichtsversendung Indexe
CREATE INDEX idx_berichtsversendung_naechste ON reporting.berichtsversendung(naechste_ausfuehrung);
CREATE INDEX idx_berichtsversendung_aktiv ON reporting.berichtsversendung(aktiv);

-- Cache Indexe
CREATE INDEX idx_berichts_cache_ablauf ON reporting.berichts_cache(ablauf_am);
CREATE INDEX idx_berichts_cache_vorlage ON reporting.berichts_cache(berichtsvorlage_id);

-- Performance Indexe
CREATE INDEX idx_performance_metriken_typ ON reporting.performance_metriken(metrik_typ);
CREATE INDEX idx_performance_metriken_zeit ON reporting.performance_metriken(erstellt_am);

-- =====================================================
-- TRIGGER FÃœR AUTOMATISCHE TIMESTAMP-UPDATES
-- =====================================================

-- Trigger-Funktion fÃ¼r geaendert_am Updates
CREATE OR REPLACE FUNCTION reporting.update_geaendert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geaendert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r alle Tabellen mit geaendert_am
CREATE TRIGGER trigger_berichtskategorien_update_geaendert_am
    BEFORE UPDATE ON reporting.berichtskategorien
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_berichtsvorlagen_update_geaendert_am
    BEFORE UPDATE ON reporting.berichtsvorlagen
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_dashboards_update_geaendert_am
    BEFORE UPDATE ON reporting.dashboards
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_dashboard_widgets_update_geaendert_am
    BEFORE UPDATE ON reporting.dashboard_widgets
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_kpi_definitionen_update_geaendert_am
    BEFORE UPDATE ON reporting.kpi_definitionen
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_export_vorlagen_update_geaendert_am
    BEFORE UPDATE ON reporting.export_vorlagen
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_berichtsversendung_update_geaendert_am
    BEFORE UPDATE ON reporting.berichtsversendung
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_drill_down_definitionen_update_geaendert_am
    BEFORE UPDATE ON reporting.drill_down_definitionen
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_benutzer_dashboards_update_geaendert_am
    BEFORE UPDATE ON reporting.benutzer_dashboards
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

CREATE TRIGGER trigger_benutzer_berichtseinstellungen_update_geaendert_am
    BEFORE UPDATE ON reporting.benutzer_berichtseinstellungen
    FOR EACH ROW EXECUTE FUNCTION reporting.update_geaendert_am();

-- =====================================================
-- FUNKTIONEN FÃœR BERICHTSGENERIERUNG
-- =====================================================

-- Funktion zur KPI-Berechnung
CREATE OR REPLACE FUNCTION reporting.berechne_kpi(
    p_kpi_id UUID
)
RETURNS DECIMAL(15,2) AS $$
DECLARE
    v_formel TEXT;
    v_ergebnis DECIMAL(15,2);
BEGIN
    -- KPI-Formel abrufen
    SELECT berechnungs_formel INTO v_formel
    FROM reporting.kpi_definitionen
    WHERE id = p_kpi_id AND aktiv = true;
    
    IF v_formel IS NULL THEN
        RAISE EXCEPTION 'KPI mit ID % nicht gefunden oder inaktiv', p_kpi_id;
    END IF;
    
    -- Formel ausfÃ¼hren
    EXECUTE 'SELECT (' || v_formel || ')::DECIMAL(15,2)' INTO v_ergebnis;
    
    -- Ergebnis in KPI-Werte-Tabelle speichern
    INSERT INTO reporting.kpi_werte (kpi_id, wert, zeitstempel)
    VALUES (p_kpi_id, v_ergebnis, CURRENT_TIMESTAMP);
    
    -- Letzten Refresh aktualisieren
    UPDATE reporting.kpi_definitionen
    SET letzter_refresh = CURRENT_TIMESTAMP
    WHERE id = p_kpi_id;
    
    RETURN v_ergebnis;
END;
$$ LANGUAGE plpgsql;

-- Funktion zur BerichtsausfÃ¼hrung
CREATE OR REPLACE FUNCTION reporting.fuehre_bericht_aus(
    p_vorlagen_id UUID,
    p_parameter_werte JSONB DEFAULT '{}',
    p_benutzer_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_ausfuehrung_id UUID;
    v_sql_query TEXT;
    v_start_zeit TIMESTAMP;
    v_ende_zeit TIMESTAMP;
    v_ergebnis_anzahl INTEGER;
BEGIN
    -- BerichtsausfÃ¼hrung starten
    INSERT INTO reporting.berichtsausfuehrungen (
        vorlagen_id, 
        ausfuehrungs_name,
        parameter_werte, 
        ausfuehrungs_status, 
        start_zeit,
        erstellt_von
    ) VALUES (
        p_vorlagen_id,
        'BerichtsausfÃ¼hrung ' || CURRENT_TIMESTAMP,
        p_parameter_werte,
        'GESTARTET',
        CURRENT_TIMESTAMP,
        COALESCE(p_benutzer_id, '00000000-0000-0000-0000-000000000000'::UUID)
    ) RETURNING id INTO v_ausfuehrung_id;
    
    -- SQL-Query abrufen
    SELECT sql_query INTO v_sql_query
    FROM reporting.berichtsvorlagen
    WHERE id = p_vorlagen_id AND aktiv = true;
    
    IF v_sql_query IS NULL THEN
        UPDATE reporting.berichtsausfuehrungen
        SET ausfuehrungs_status = 'FEHLER',
            fehlermeldung = 'Berichtsvorlage nicht gefunden oder inaktiv',
            ende_zeit = CURRENT_TIMESTAMP
        WHERE id = v_ausfuehrung_id;
        RETURN v_ausfuehrung_id;
    END IF;
    
    -- Status auf "LÃ„UFT" setzen
    UPDATE reporting.berichtsausfuehrungen
    SET ausfuehrungs_status = 'LAEUFT'
    WHERE id = v_ausfuehrung_id;
    
    v_start_zeit := CURRENT_TIMESTAMP;
    
    BEGIN
        -- Query ausfÃ¼hren (hier wÃ¼rde die tatsÃ¤chliche AusfÃ¼hrung erfolgen)
        -- FÃ¼r Demo-Zwecke simulieren wir eine erfolgreiche AusfÃ¼hrung
        v_ergebnis_anzahl := 100; -- Simulierte Anzahl
        
        v_ende_zeit := CURRENT_TIMESTAMP;
        
        -- Erfolgreich abschlieÃŸen
        UPDATE reporting.berichtsausfuehrungen
        SET ausfuehrungs_status = 'ABGESCHLOSSEN',
            ende_zeit = v_ende_zeit,
            dauer_sekunden = EXTRACT(EPOCH FROM (v_ende_zeit - v_start_zeit))::INTEGER,
            ergebnis_anzahl = v_ergebnis_anzahl
        WHERE id = v_ausfuehrung_id;
        
    EXCEPTION WHEN OTHERS THEN
        -- Fehler behandeln
        UPDATE reporting.berichtsausfuehrungen
        SET ausfuehrungs_status = 'FEHLER',
            fehlermeldung = SQLERRM,
            ende_zeit = CURRENT_TIMESTAMP,
            dauer_sekunden = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - v_start_zeit))::INTEGER
        WHERE id = v_ausfuehrung_id;
    END;
    
    RETURN v_ausfuehrung_id;
END;
$$ LANGUAGE plpgsql;

-- Funktion zur automatischen Berichtsversendung
CREATE OR REPLACE FUNCTION reporting.fuehre_berichtsversendung_aus(
    p_versendung_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_historie_id UUID;
    v_empfaenger_anzahl INTEGER;
    v_erfolgreich_versendet INTEGER;
    v_fehlgeschlagene_versendungen INTEGER;
BEGIN
    -- Versendung-Historie erstellen
    INSERT INTO reporting.versendung_historie (
        versendung_id,
        status,
        empfaenger_anzahl,
        erfolgreich_versendet,
        fehlgeschlagene_versendungen
    ) VALUES (
        p_versendung_id,
        'ERFOLGREICH',
        5, -- Simulierte Anzahl
        5, -- Simulierte erfolgreiche Versendungen
        0  -- Simulierte fehlgeschlagene Versendungen
    ) RETURNING id INTO v_historie_id;
    
    -- Letzte AusfÃ¼hrung aktualisieren
    UPDATE reporting.berichtsversendung
    SET letzte_ausfuehrung = CURRENT_TIMESTAMP,
        naechste_ausfuehrung = CURRENT_TIMESTAMP + INTERVAL '1 day' -- Beispiel fÃ¼r tÃ¤gliche Versendung
    WHERE id = p_versendung_id;
    
    RETURN v_historie_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS FÃœR DASHBOARDS UND ÃœBERSICHTEN
-- =====================================================

-- Dashboard-Ãœbersicht
CREATE VIEW reporting.dashboard_uebersicht AS
SELECT 
    d.id,
    d.dashboard_name,
    d.beschreibung,
    d.standard_dashboard,
    d.aktiv,
    COUNT(w.id) as widget_anzahl,
    d.erstellt_von,
    m.vorname || ' ' || m.nachname as erstellt_von_name,
    d.erstellt_am,
    d.geaendert_am
FROM reporting.dashboards d
LEFT JOIN reporting.dashboard_widgets w ON d.id = w.dashboard_id AND w.aktiv = true
LEFT JOIN personal.mitarbeiter m ON d.erstellt_von = m.id
GROUP BY d.id, d.dashboard_name, d.beschreibung, d.standard_dashboard, d.aktiv, d.erstellt_von, m.vorname, m.nachname, d.erstellt_am, d.geaendert_am;

-- KPI-Ãœbersicht
CREATE VIEW reporting.kpi_uebersicht AS
SELECT 
    k.id,
    k.kpi_name,
    k.beschreibung,
    k.kategorie,
    k.einheit,
    k.ziel_wert,
    k.warnung_unter,
    k.warnung_ueber,
    k.trend_richtung,
    k.letzter_refresh,
    kw.wert as aktueller_wert,
    kw.zeitstempel as letzter_wert_zeitstempel,
    k.aktiv,
    k.erstellt_von,
    m.vorname || ' ' || m.nachname as erstellt_von_name
FROM reporting.kpi_definitionen k
LEFT JOIN LATERAL (
    SELECT wert, zeitstempel
    FROM reporting.kpi_werte
    WHERE kpi_id = k.id
    ORDER BY zeitstempel DESC
    LIMIT 1
) kw ON true
LEFT JOIN personal.mitarbeiter m ON k.erstellt_von = m.id
WHERE k.aktiv = true;

-- Berichtsversendung-Ãœbersicht
CREATE VIEW reporting.versendung_uebersicht AS
SELECT 
    bv.id,
    bv.name,
    bv.beschreibung,
    bv.versand_typ,
    bv.zeitplan_typ,
    bv.naechste_ausfuehrung,
    bv.letzte_ausfuehrung,
    bv.aktiv,
    bv.erstellt_von,
    m.vorname || ' ' || m.nachname as erstellt_von_name,
    bv.erstellt_am,
    bv.geaendert_am
FROM reporting.berichtsversendung bv
LEFT JOIN personal.mitarbeiter m ON bv.erstellt_von = m.id;

-- Performance-Ãœbersicht
CREATE VIEW reporting.performance_uebersicht AS
SELECT 
    pm.metrik_typ,
    pm.berichtsvorlage_id,
    bv.vorlagen_name,
    AVG(pm.dauer_ms) as durchschnitt_dauer_ms,
    MAX(pm.dauer_ms) as max_dauer_ms,
    MIN(pm.dauer_ms) as min_dauer_ms,
    COUNT(*) as anzahl_ausfuehrungen,
    AVG(pm.datensatz_anzahl) as durchschnitt_datensÃ¤tze,
    COUNT(CASE WHEN pm.cache_hit = true THEN 1 END) as cache_hits,
    COUNT(CASE WHEN pm.cache_hit = false THEN 1 END) as cache_misses
FROM reporting.performance_metriken pm
LEFT JOIN reporting.berichtsvorlagen bv ON pm.berichtsvorlage_id = bv.id
WHERE pm.erstellt_am >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY pm.metrik_typ, pm.berichtsvorlage_id, bv.vorlagen_name;

-- =====================================================
-- BEISPIEL-DATEN
-- =====================================================

-- Berichtskategorien
INSERT INTO reporting.berichtskategorien (kategorie_name, beschreibung, icon_name, farbe, sortierung) VALUES
('Finanzen', 'Finanzberichte und Kennzahlen', 'account_balance', '#1976d2', 1),
('Produktion', 'Produktionsberichte und -statistiken', 'factory', '#388e3c', 2),
('Verkauf', 'Verkaufsberichte und -analysen', 'trending_up', '#f57c00', 3),
('Lager', 'Lagerberichte und Bestandsanalysen', 'inventory', '#7b1fa2', 4),
('Personal', 'Personalberichte und -statistiken', 'people', '#d32f2f', 5),
('QualitÃ¤t', 'QualitÃ¤tsberichte und -analysen', 'verified', '#388e3c', 6),
('Projekte', 'Projektberichte und -fortschritte', 'assignment', '#1976d2', 7),
('Dokumente', 'Dokumentenberichte und -statistiken', 'description', '#616161', 8);

-- Standard-Dashboard
INSERT INTO reporting.dashboards (dashboard_name, beschreibung, layout_definition, standard_dashboard, erstellt_von) VALUES
('VALEO NeuroERP Dashboard', 'Hauptdashboard mit allen wichtigen KPIs', 
'{"grid": {"columns": 12, "rows": 8}, "widgets": []}', true, 
(SELECT id FROM personal.mitarbeiter LIMIT 1));

-- KPI-Definitionen
INSERT INTO reporting.kpi_definitionen (kpi_name, beschreibung, kategorie, berechnungs_formel, einheit, ziel_wert, trend_richtung, erstellt_von) VALUES
('Umsatz (Monat)', 'Monatlicher Umsatz', 'Finanzen', 
'(SELECT COALESCE(SUM(betrag), 0) FROM finance.buchungen WHERE buchungstyp = ''ERLOES'' AND erstellt_am >= DATE_TRUNC(''month'', CURRENT_DATE))', 
'EUR', 100000, 'AUFWAERTS', (SELECT id FROM personal.mitarbeiter LIMIT 1)),

('ProduktionsauftrÃ¤ge (Offen)', 'Anzahl offener ProduktionsauftrÃ¤ge', 'Produktion',
'(SELECT COUNT(*) FROM produktion.produktionsauftraege WHERE status = ''OFFEN'')',
'StÃ¼ck', 50, 'ABWAERTS', (SELECT id FROM personal.mitarbeiter LIMIT 1)),

('Lagerbestand (Wert)', 'Gesamtwert des Lagerbestands', 'Lager',
'(SELECT COALESCE(SUM(bestand * einstandspreis), 0) FROM lager.artikel_bestand ab JOIN lager.artikel a ON ab.artikel_id = a.id)',
'EUR', 500000, 'NEUTRAL', (SELECT id FROM personal.mitarbeiter LIMIT 1)),

('Kunden (Aktiv)', 'Anzahl aktiver Kunden', 'Verkauf',
'(SELECT COUNT(*) FROM verkauf.kunden WHERE status = ''AKTIV'')',
'Kunden', 200, 'AUFWAERTS', (SELECT id FROM personal.mitarbeiter LIMIT 1));

-- Berichtsvorlagen
INSERT INTO reporting.berichtsvorlagen (vorlagen_name, beschreibung, kategorie_id, bericht_typ, sql_query, export_formate, erstellt_von) VALUES
('Umsatzbericht (Monatlich)', 'Detaillierter monatlicher Umsatzbericht', 
(SELECT id FROM reporting.berichtskategorien WHERE kategorie_name = 'Finanzen'),
'TABELLE', 
'SELECT datum, summe, kategorie FROM finance.umsatz_monatlich WHERE monat = $1',
ARRAY['PDF', 'EXCEL'], (SELECT id FROM personal.mitarbeiter LIMIT 1)),

('ProduktionsauftrÃ¤ge (Status)', 'Ãœbersicht aller ProduktionsauftrÃ¤ge nach Status',
(SELECT id FROM reporting.berichtskategorien WHERE kategorie_name = 'Produktion'),
'TABELLE',
'SELECT auftragsnummer, produkt_name, status, start_datum, end_datum FROM produktion.produktionsauftraege ORDER BY erstellt_am DESC',
ARRAY['PDF', 'EXCEL', 'CSV'], (SELECT id FROM personal.mitarbeiter LIMIT 1)),

('Lagerbestand (Detailliert)', 'Detaillierte LagerbestandsÃ¼bersicht',
(SELECT id FROM reporting.berichtskategorien WHERE kategorie_name = 'Lager'),
'TABELLE',
'SELECT artikel_name, lagerort, bestand, einstandspreis, gesamt_wert FROM lager.bestand_uebersicht ORDER BY gesamt_wert DESC',
ARRAY['PDF', 'EXCEL'], (SELECT id FROM personal.mitarbeiter LIMIT 1));

-- =====================================================
-- KOMMENTARE
-- =====================================================

COMMENT ON SCHEMA reporting IS 'Reporting und Analytics Schema fÃ¼r VALEO NeuroERP';
COMMENT ON TABLE reporting.berichtskategorien IS 'Kategorien fÃ¼r Berichte und Dashboards';
COMMENT ON TABLE reporting.berichtsvorlagen IS 'Vorlagen fÃ¼r Berichte mit SQL-Queries und Parametern';
COMMENT ON TABLE reporting.berichtsausfuehrungen IS 'AusfÃ¼hrungen von Berichten mit Ergebnissen';
COMMENT ON TABLE reporting.dashboards IS 'Dashboard-Definitionen mit Layout';
COMMENT ON TABLE reporting.dashboard_widgets IS 'Widgets innerhalb von Dashboards';
COMMENT ON TABLE reporting.kpi_definitionen IS 'Definitionen fÃ¼r Key Performance Indicators';
COMMENT ON TABLE reporting.kpi_werte IS 'Historische KPI-Werte';
COMMENT ON TABLE reporting.export_jobs IS 'Export-Jobs fÃ¼r Berichte';
COMMENT ON TABLE reporting.berichtsversendung IS 'Automatische Berichtsversendung';
COMMENT ON TABLE reporting.versendung_historie IS 'Historie der Berichtsversendungen';
COMMENT ON TABLE reporting.drill_down_definitionen IS 'Drill-Down-Definitionen zwischen Berichten';
COMMENT ON TABLE reporting.berichts_cache IS 'Cache fÃ¼r Berichtsergebnisse';
COMMENT ON TABLE reporting.performance_metriken IS 'Performance-Metriken fÃ¼r Berichte'; 
