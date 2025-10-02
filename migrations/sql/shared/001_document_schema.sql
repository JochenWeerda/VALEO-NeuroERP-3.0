-- =====================================================
-- VALEO NeuroERP - Dokumentenverwaltung Schema
-- =====================================================

-- Schema erstellen
CREATE SCHEMA IF NOT EXISTS dokumente;

-- =====================================================
-- DOKUMENTENSTAMMDATEN
-- =====================================================

-- Dokumentenkategorien
CREATE TABLE dokumente.dokumentenkategorien (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kategorie_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    ueberkategorie_id UUID REFERENCES dokumente.dokumentenkategorien(id),
    farbe VARCHAR(7) DEFAULT '#1976d2',
    icon VARCHAR(50),
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dokumente
CREATE TABLE dokumente.dokumente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_nr VARCHAR(20) UNIQUE NOT NULL,
    titel VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    kategorie_id UUID REFERENCES dokumente.dokumentenkategorien(id),
    dokument_typ VARCHAR(50) NOT NULL, -- 'PDF', 'DOC', 'DOCX', 'XLS', 'XLSX', 'PPT', 'PPTX', 'TXT', 'JPG', 'PNG', 'ZIP', 'SONSTIGES'
    dateiname VARCHAR(255) NOT NULL,
    original_dateiname VARCHAR(255) NOT NULL,
    dateigroesse BIGINT NOT NULL, -- Bytes
    mime_type VARCHAR(100),
    dateipfad VARCHAR(500),
    version VARCHAR(20) DEFAULT '1.0',
    status VARCHAR(50) DEFAULT 'ENTWURF', -- 'ENTWURF', 'FREIGEGEBEN', 'ARCHIVIERT', 'GELOESCHT'
    freigegeben_von UUID REFERENCES personal.mitarbeiter(id),
    freigegeben_am TIMESTAMP,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dokumenteigenschaften (Metadaten)
CREATE TABLE dokumente.dokumenteigenschaften (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    eigenschaft_name VARCHAR(100) NOT NULL,
    eigenschaft_wert TEXT,
    eigenschaft_typ VARCHAR(50) DEFAULT 'TEXT', -- 'TEXT', 'ZAHL', 'DATUM', 'BOOLEAN', 'JSON'
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dokument-Tags
CREATE TABLE dokumente.dokument_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    farbe VARCHAR(7) DEFAULT '#666666',
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dokument-Tag-Zuordnung (Many-to-Many)
CREATE TABLE dokumente.dokument_tag_zuordnung (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES dokumente.dokument_tags(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- VERSIONIERUNG
-- =====================================================

-- Dokumentversionen
CREATE TABLE dokumente.dokumentversionen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    dateiname VARCHAR(255) NOT NULL,
    original_dateiname VARCHAR(255) NOT NULL,
    dateigroesse BIGINT NOT NULL,
    dateipfad VARCHAR(500),
    aenderungsbeschreibung TEXT,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Versionshistorie
CREATE TABLE dokumente.versionshistorie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    alte_version VARCHAR(20),
    neue_version VARCHAR(20) NOT NULL,
    aenderung_typ VARCHAR(50) NOT NULL, -- 'ERSTELLT', 'AKTUALISIERT', 'GELOESCHT', 'WIDERHERGESTELLT'
    aenderungsbeschreibung TEXT,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- WORKFLOWS UND FREIGABEN
-- =====================================================

-- Workflow-Definitionen
CREATE TABLE dokumente.workflow_definitionen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    kategorie_id UUID REFERENCES dokumente.dokumentenkategorien(id),
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow-Schritte
CREATE TABLE dokumente.workflow_schritte (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES dokumente.workflow_definitionen(id) ON DELETE CASCADE,
    schritt_name VARCHAR(100) NOT NULL,
    schritt_reihenfolge INTEGER NOT NULL,
    rolle_id UUID REFERENCES personal.rollen(id),
    mitarbeiter_id UUID REFERENCES personal.mitarbeiter(id),
    aktion VARCHAR(50) NOT NULL, -- 'FREIGEBEN', 'GENEHMIGEN', 'PRÃœFEN', 'UNTERZEICHNEN'
    ist_optional BOOLEAN DEFAULT false,
    zeitlimit_tage INTEGER,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow-Instanzen
CREATE TABLE dokumente.workflow_instanzen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES dokumente.workflow_definitionen(id),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id),
    status VARCHAR(50) DEFAULT 'AKTIV', -- 'AKTIV', 'ABGESCHLOSSEN', 'ABGEBROCHEN'
    gestartet_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    gestartet_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    abgeschlossen_am TIMESTAMP,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow-Schritt-Instanzen
CREATE TABLE dokumente.workflow_schritt_instanzen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_instanz_id UUID NOT NULL REFERENCES dokumente.workflow_instanzen(id) ON DELETE CASCADE,
    workflow_schritt_id UUID NOT NULL REFERENCES dokumente.workflow_schritte(id),
    status VARCHAR(50) DEFAULT 'AUSSTEHEND', -- 'AUSSTEHEND', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN', 'ÃœBERSPRUNGEN'
    zugewiesen_an UUID REFERENCES personal.mitarbeiter(id),
    gestartet_am TIMESTAMP,
    abgeschlossen_am TIMESTAMP,
    kommentar TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ZUGRIFFSRECHTE UND BERECHTIGUNGEN
-- =====================================================

-- Dokumentberechtigungen
CREATE TABLE dokumente.dokumentberechtigungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    mitarbeiter_id UUID REFERENCES personal.mitarbeiter(id),
    rolle_id UUID REFERENCES personal.rollen(id),
    berechtigung_typ VARCHAR(50) NOT NULL, -- 'LESEN', 'BEARBEITEN', 'FREIGEBEN', 'LÃ–SCHEN', 'ADMIN'
    erteilt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erteilt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gueltig_bis DATE,
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dokumentzugriffe (Audit-Trail)
CREATE TABLE dokumente.dokumentzugriffe (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id),
    mitarbeiter_id UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    zugriff_typ VARCHAR(50) NOT NULL, -- 'ANGEZEIGT', 'HERUNTERGELADEN', 'BEARBEITET', 'GEDRUCKT', 'FREIGEGEBEN'
    ip_adresse INET,
    user_agent TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ARCHIVIERUNG UND BEREINIGUNG
-- =====================================================

-- Archivierungsregeln
CREATE TABLE dokumente.archivierungsregeln (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regel_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    kategorie_id UUID REFERENCES dokumente.dokumentenkategorien(id),
    dokument_typ VARCHAR(50),
    archivierung_nach_tagen INTEGER NOT NULL,
    loeschung_nach_tagen INTEGER,
    gesetzliche_frist_jahre INTEGER NOT NULL, -- Gesetzliche Aufbewahrungsfrist in Jahren
    gesetzliche_grundlage VARCHAR(200), -- z.B. "Â§ 147 AO", "Â§ 257 HGB"
    bereinigung_typ VARCHAR(50) DEFAULT 'ARCHIVIEREN', -- 'ARCHIVIEREN', 'EXPORTIEREN', 'LOESCHEN'
    export_format VARCHAR(50), -- 'PDF', 'ZIP', 'TAR.GZ'
    export_ziel VARCHAR(500), -- Pfad fÃ¼r Export
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Archivierte Dokumente
CREATE TABLE dokumente.archivierte_dokumente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_dokument_id UUID,
    dokument_nr VARCHAR(20) NOT NULL,
    titel VARCHAR(200) NOT NULL,
    kategorie_name VARCHAR(100),
    archivierungsgrund VARCHAR(100),
    archiviert_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    archiviert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    wiederherstellbar_bis DATE,
    gesetzliche_frist_bis DATE, -- Datum bis wann gesetzliche Aufbewahrungspflicht gilt
    bereinigung_am DATE, -- Datum der geplanten Bereinigung
    bereinigung_status VARCHAR(50) DEFAULT 'ARCHIVIERT', -- 'ARCHIVIERT', 'EXPORTIERT', 'LOESCHT'
    export_pfad VARCHAR(500), -- Pfad zum exportierten Dokument
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BereinigungsauftrÃ¤ge
CREATE TABLE dokumente.bereinigungsauftraege (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auftrag_nr VARCHAR(20) UNIQUE NOT NULL,
    auftrag_typ VARCHAR(50) NOT NULL, -- 'ARCHIVIERUNG', 'EXPORT', 'LOESCHUNG'
    regel_id UUID REFERENCES dokumente.archivierungsregeln(id),
    status VARCHAR(50) DEFAULT 'GEPLANT', -- 'GEPLANT', 'IN_BEARBEITUNG', 'ABGESCHLOSSEN', 'FEHLGESCHLAGEN'
    geplantes_datum DATE NOT NULL,
    ausgefuehrt_am TIMESTAMP,
    anzahl_dokumente INTEGER DEFAULT 0,
    erfolgreich_verarbeitet INTEGER DEFAULT 0,
    fehlgeschlagene_verarbeitung INTEGER DEFAULT 0,
    ausgefuehrt_von UUID REFERENCES personal.mitarbeiter(id),
    kommentar TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bereinigungsprotokoll
CREATE TABLE dokumente.bereinigungsprotokoll (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auftrag_id UUID NOT NULL REFERENCES dokumente.bereinigungsauftraege(id),
    dokument_id UUID REFERENCES dokumente.dokumente(id),
    archiviertes_dokument_id UUID REFERENCES dokumente.archivierte_dokumente(id),
    aktion VARCHAR(50) NOT NULL, -- 'ARCHIVIERT', 'EXPORTIERT', 'LOESCHT'
    status VARCHAR(50) NOT NULL, -- 'ERFOLGREICH', 'FEHLGESCHLAGEN'
    fehlermeldung TEXT,
    export_pfad VARCHAR(500),
    dateigroesse_vorher BIGINT,
    dateigroesse_nachher BIGINT,
    ausgefuehrt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gesetzliche Aufbewahrungsfristen (Referenztabelle)
CREATE TABLE dokumente.gesetzliche_fristen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_typ VARCHAR(100) NOT NULL,
    kategorie VARCHAR(100),
    gesetzliche_frist_jahre INTEGER NOT NULL,
    gesetzliche_grundlage VARCHAR(200) NOT NULL,
    beschreibung TEXT,
    bemerkungen TEXT,
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXE
-- =====================================================

-- Dokumente
CREATE INDEX idx_dokumente_kategorie ON dokumente.dokumente(kategorie_id);
CREATE INDEX idx_dokumente_status ON dokumente.dokumente(status);
CREATE INDEX idx_dokumente_typ ON dokumente.dokumente(dokument_typ);
CREATE INDEX idx_dokumente_erstellt_von ON dokumente.dokumente(erstellt_von);
CREATE INDEX idx_dokumente_erstellt_am ON dokumente.dokumente(erstellt_am);

-- Dokumenteigenschaften
CREATE INDEX idx_dokumenteigenschaften_dokument ON dokumente.dokumenteigenschaften(dokument_id);
CREATE INDEX idx_dokumenteigenschaften_name ON dokumente.dokumenteigenschaften(eigenschaft_name);

-- Dokumentversionen
CREATE INDEX idx_dokumentversionen_dokument ON dokumente.dokumentversionen(dokument_id);
CREATE INDEX idx_dokumentversionen_version ON dokumente.dokumentversionen(version);

-- Workflows
CREATE INDEX idx_workflow_instanzen_dokument ON dokumente.workflow_instanzen(dokument_id);
CREATE INDEX idx_workflow_instanzen_status ON dokumente.workflow_instanzen(status);
CREATE INDEX idx_workflow_schritt_instanzen_instanz ON dokumente.workflow_schritt_instanzen(workflow_instanz_id);
CREATE INDEX idx_workflow_schritt_instanzen_status ON dokumente.workflow_schritt_instanzen(status);

-- Berechtigungen
CREATE INDEX idx_dokumentberechtigungen_dokument ON dokumente.dokumentberechtigungen(dokument_id);
CREATE INDEX idx_dokumentberechtigungen_mitarbeiter ON dokumente.dokumentberechtigungen(mitarbeiter_id);
CREATE INDEX idx_dokumentberechtigungen_rolle ON dokumente.dokumentberechtigungen(rolle_id);

-- Zugriffe
CREATE INDEX idx_dokumentzugriffe_dokument ON dokumente.dokumentzugriffe(dokument_id);
CREATE INDEX idx_dokumentzugriffe_mitarbeiter ON dokumente.dokumentzugriffe(mitarbeiter_id);
CREATE INDEX idx_dokumentzugriffe_datum ON dokumente.dokumentzugriffe(erstellt_am);

-- =====================================================
-- INDEXE FÃœR ARCHIVIERUNG UND BEREINIGUNG
-- =====================================================

CREATE INDEX idx_archivierte_dokumente_bereinigung_am ON dokumente.archivierte_dokumente(bereinigung_am);
CREATE INDEX idx_archivierte_dokumente_gesetzliche_frist ON dokumente.archivierte_dokumente(gesetzliche_frist_bis);
CREATE INDEX idx_archivierte_dokumente_status ON dokumente.archivierte_dokumente(bereinigung_status);

CREATE INDEX idx_bereinigungsauftraege_status ON dokumente.bereinigungsauftraege(status);
CREATE INDEX idx_bereinigungsauftraege_datum ON dokumente.bereinigungsauftraege(geplantes_datum);
CREATE INDEX idx_bereinigungsauftraege_typ ON dokumente.bereinigungsauftraege(auftrag_typ);

CREATE INDEX idx_bereinigungsprotokoll_auftrag ON dokumente.bereinigungsprotokoll(auftrag_id);
CREATE INDEX idx_bereinigungsprotokoll_datum ON dokumente.bereinigungsprotokoll(ausgefuehrt_am);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger-Funktion fÃ¼r automatische Timestamp-Updates
CREATE OR REPLACE FUNCTION dokumente.update_geaendert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geaendert_am = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers fÃ¼r alle Tabellen
CREATE TRIGGER trigger_dokumentenkategorien_update_geaendert_am
    BEFORE UPDATE ON dokumente.dokumentenkategorien
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_dokumente_update_geaendert_am
    BEFORE UPDATE ON dokumente.dokumente
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_dokumenteigenschaften_update_geaendert_am
    BEFORE UPDATE ON dokumente.dokumenteigenschaften
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_dokument_tags_update_geaendert_am
    BEFORE UPDATE ON dokumente.dokument_tags
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_dokumentversionen_update_geaendert_am
    BEFORE UPDATE ON dokumente.dokumentversionen
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_workflow_definitionen_update_geaendert_am
    BEFORE UPDATE ON dokumente.workflow_definitionen
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_workflow_schritte_update_geaendert_am
    BEFORE UPDATE ON dokumente.workflow_schritte
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_workflow_instanzen_update_geaendert_am
    BEFORE UPDATE ON dokumente.workflow_instanzen
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_workflow_schritt_instanzen_update_geaendert_am
    BEFORE UPDATE ON dokumente.workflow_schritt_instanzen
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_dokumentberechtigungen_update_geaendert_am
    BEFORE UPDATE ON dokumente.dokumentberechtigungen
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_archivierungsregeln_update_geaendert_am
    BEFORE UPDATE ON dokumente.archivierungsregeln
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_bereinigungsauftraege_update_geaendert_am
    BEFORE UPDATE ON dokumente.bereinigungsauftraege
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

CREATE TRIGGER trigger_gesetzliche_fristen_update_geaendert_am
    BEFORE UPDATE ON dokumente.gesetzliche_fristen
    FOR EACH ROW EXECUTE FUNCTION dokumente.update_geaendert_am();

-- =====================================================
-- FUNKTIONEN
-- =====================================================

-- Automatische Dokumentnummer-Generierung
CREATE OR REPLACE FUNCTION dokumente.generate_dokumentnummer()
RETURNS TRIGGER AS $$
DECLARE
    jahr INTEGER;
    monat INTEGER;
    naechste_nummer INTEGER;
    neue_nummer VARCHAR(20);
BEGIN
    jahr := EXTRACT(YEAR FROM CURRENT_DATE);
    monat := EXTRACT(MONTH FROM CURRENT_DATE);
    
    SELECT COALESCE(MAX(CAST(SUBSTRING(dokument_nr FROM 12) AS INTEGER)), 0) + 1
    INTO naechste_nummer
    FROM dokumente.dokumente
    WHERE dokument_nr LIKE 'DOC-' || jahr || '-' || LPAD(monat::TEXT, 2, '0') || '-%';
    
    neue_nummer := 'DOC-' || jahr || '-' || LPAD(monat::TEXT, 2, '0') || '-' || LPAD(naechste_nummer::TEXT, 3, '0');
    NEW.dokument_nr := neue_nummer;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r automatische Dokumentnummer-Generierung
CREATE TRIGGER trigger_generate_dokumentnummer
    BEFORE INSERT ON dokumente.dokumente
    FOR EACH ROW EXECUTE FUNCTION dokumente.generate_dokumentnummer();

-- Dokument-Statistiken berechnen
CREATE OR REPLACE FUNCTION dokumente.get_dokument_statistiken(
    p_start_datum DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    p_end_datum DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    gesamt_dokumente BIGINT,
    neue_dokumente BIGINT,
    freigegebene_dokumente BIGINT,
    archivierte_dokumente BIGINT,
    gesamt_dateigroesse_mb DECIMAL(10,2),
    durchschnittliche_dateigroesse_mb DECIMAL(10,2),
    haeufigste_kategorien TEXT,
    haeufigste_typen TEXT,
    aktive_workflows BIGINT,
    abgeschlossene_workflows BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(d.id)::BIGINT as gesamt_dokumente,
        COUNT(CASE WHEN d.erstellt_am::DATE BETWEEN p_start_datum AND p_end_datum THEN 1 END)::BIGINT as neue_dokumente,
        COUNT(CASE WHEN d.status = 'FREIGEGEBEN' THEN 1 END)::BIGINT as freigegebene_dokumente,
        COUNT(CASE WHEN d.status = 'ARCHIVIERT' THEN 1 END)::BIGINT as archivierte_dokumente,
        ROUND(SUM(d.dateigroesse)::DECIMAL / (1024 * 1024), 2) as gesamt_dateigroesse_mb,
        ROUND(AVG(d.dateigroesse)::DECIMAL / (1024 * 1024), 2) as durchschnittliche_dateigroesse_mb,
        STRING_AGG(DISTINCT dk.kategorie_name, ', ' ORDER BY dk.kategorie_name) as haeufigste_kategorien,
        STRING_AGG(DISTINCT d.dokument_typ, ', ' ORDER BY d.dokument_typ) as haeufigste_typen,
        COUNT(CASE WHEN wi.status = 'AKTIV' THEN 1 END)::BIGINT as aktive_workflows,
        COUNT(CASE WHEN wi.status = 'ABGESCHLOSSEN' THEN 1 END)::BIGINT as abgeschlossene_workflows
    FROM dokumente.dokumente d
    LEFT JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
    LEFT JOIN dokumente.workflow_instanzen wi ON wi.dokument_id = d.id;
END;
$$ LANGUAGE plpgsql;

-- Dokument-Suche
CREATE OR REPLACE FUNCTION dokumente.search_dokumente(
    p_suchtext TEXT,
    p_kategorie_id UUID DEFAULT NULL,
    p_status VARCHAR(50) DEFAULT NULL,
    p_erstellt_von UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    dokument_nr VARCHAR(20),
    titel VARCHAR(200),
    beschreibung TEXT,
    kategorie_name VARCHAR(100),
    dokument_typ VARCHAR(50),
    status VARCHAR(50),
    erstellt_von_name TEXT,
    erstellt_am TIMESTAMP,
    dateigroesse_mb DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.dokument_nr,
        d.titel,
        d.beschreibung,
        dk.kategorie_name,
        d.dokument_typ,
        d.status,
        CONCAT(m.vorname, ' ', m.nachname) as erstellt_von_name,
        d.erstellt_am,
        ROUND(d.dateigroesse::DECIMAL / (1024 * 1024), 2) as dateigroesse_mb
    FROM dokumente.dokumente d
    LEFT JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
    LEFT JOIN personal.mitarbeiter m ON m.id = d.erstellt_von
    WHERE (
        p_suchtext IS NULL OR 
        d.titel ILIKE '%' || p_suchtext || '%' OR 
        d.beschreibung ILIKE '%' || p_suchtext || '%' OR
        d.dokument_nr ILIKE '%' || p_suchtext || '%'
    )
    AND (p_kategorie_id IS NULL OR d.kategorie_id = p_kategorie_id)
    AND (p_status IS NULL OR d.status = p_status)
    AND (p_erstellt_von IS NULL OR d.erstellt_von = p_erstellt_von)
    ORDER BY d.erstellt_am DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS
-- =====================================================

-- DokumentÃ¼bersicht
CREATE VIEW dokumente.dokument_uebersicht AS
SELECT 
    d.id,
    d.dokument_nr,
    d.titel,
    d.beschreibung,
    dk.kategorie_name,
    d.dokument_typ,
    d.status,
    d.version,
    CONCAT(m.vorname, ' ', m.nachname) as erstellt_von_name,
    CONCAT(f.vorname, ' ', f.nachname) as freigegeben_von_name,
    d.erstellt_am,
    d.freigegeben_am,
    ROUND(d.dateigroesse::DECIMAL / (1024 * 1024), 2) as dateigroesse_mb,
    COUNT(dv.id) as anzahl_versionen,
    COUNT(dt.tag_id) as anzahl_tags,
    COUNT(dz.id) as anzahl_zugriffe
FROM dokumente.dokumente d
LEFT JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
LEFT JOIN personal.mitarbeiter m ON m.id = d.erstellt_von
LEFT JOIN personal.mitarbeiter f ON f.id = d.freigegeben_von
LEFT JOIN dokumente.dokumentversionen dv ON dv.dokument_id = d.id
LEFT JOIN dokumente.dokument_tag_zuordnung dt ON dt.dokument_id = d.id
LEFT JOIN dokumente.dokumentzugriffe dz ON dz.dokument_id = d.id
GROUP BY d.id, d.dokument_nr, d.titel, d.beschreibung, dk.kategorie_name, d.dokument_typ, 
         d.status, d.version, m.vorname, m.nachname, f.vorname, f.nachname, d.erstellt_am, d.freigegeben_am, d.dateigroesse;

-- Workflow-Ãœbersicht
CREATE VIEW dokumente.workflow_uebersicht AS
SELECT 
    wi.id,
    wd.workflow_name,
    d.dokument_nr,
    d.titel as dokument_titel,
    wi.status as workflow_status,
    CONCAT(m.vorname, ' ', m.nachname) as gestartet_von_name,
    wi.gestartet_am,
    wi.abgeschlossen_am,
    COUNT(wsi.id) as anzahl_schritte,
    COUNT(CASE WHEN wsi.status = 'ABGESCHLOSSEN' THEN 1 END) as abgeschlossene_schritte
FROM dokumente.workflow_instanzen wi
JOIN dokumente.workflow_definitionen wd ON wd.id = wi.workflow_id
JOIN dokumente.dokumente d ON d.id = wi.dokument_id
JOIN personal.mitarbeiter m ON m.id = wi.gestartet_von
LEFT JOIN dokumente.workflow_schritt_instanzen wsi ON wsi.workflow_instanz_id = wi.id
GROUP BY wi.id, wd.workflow_name, d.dokument_nr, d.titel, wi.status, m.vorname, m.nachname, wi.gestartet_am, wi.abgeschlossen_am;

-- Zugriffsstatistiken
CREATE VIEW dokumente.zugriffsstatistiken AS
SELECT 
    d.id,
    d.dokument_nr,
    d.titel,
    dk.kategorie_name,
    COUNT(dz.id) as anzahl_zugriffe,
    COUNT(DISTINCT dz.mitarbeiter_id) as anzahl_benutzer,
    MAX(dz.erstellt_am) as letzter_zugriff,
    COUNT(CASE WHEN dz.zugriff_typ = 'HERUNTERGELADEN' THEN 1 END) as downloads,
    COUNT(CASE WHEN dz.zugriff_typ = 'ANGEZEIGT' THEN 1 END) as anzeigen
FROM dokumente.dokumente d
LEFT JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
LEFT JOIN dokumente.dokumentzugriffe dz ON dz.dokument_id = d.id
GROUP BY d.id, d.dokument_nr, d.titel, dk.kategorie_name;

-- =====================================================
-- FUNKTIONEN FÃœR ARCHIVIERUNG UND BEREINIGUNG
-- =====================================================

-- Automatische Auftragsnummer-Generierung fÃ¼r BereinigungsauftrÃ¤ge
CREATE OR REPLACE FUNCTION dokumente.generate_bereinigungsauftragnummer()
RETURNS TRIGGER AS $$
DECLARE
    jahr INTEGER;
    monat INTEGER;
    naechste_nummer INTEGER;
    neue_nummer VARCHAR(20);
BEGIN
    jahr := EXTRACT(YEAR FROM CURRENT_DATE);
    monat := EXTRACT(MONTH FROM CURRENT_DATE);
    
    SELECT COALESCE(MAX(CAST(SUBSTRING(auftrag_nr FROM 12) AS INTEGER)), 0) + 1
    INTO naechste_nummer
    FROM dokumente.bereinigungsauftraege
    WHERE auftrag_nr LIKE 'BA-' || jahr || '-' || LPAD(monat::TEXT, 2, '0') || '-%';
    
    neue_nummer := 'BA-' || jahr || '-' || LPAD(monat::TEXT, 2, '0') || '-' || LPAD(naechste_nummer::TEXT, 3, '0');
    NEW.auftrag_nr := neue_nummer;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r automatische Auftragsnummer-Generierung
CREATE TRIGGER trigger_generate_bereinigungsauftragnummer
    BEFORE INSERT ON dokumente.bereinigungsauftraege
    FOR EACH ROW EXECUTE FUNCTION dokumente.generate_bereinigungsauftragnummer();

-- Funktion zur Identifikation von Dokumenten fÃ¼r Bereinigung
CREATE OR REPLACE FUNCTION dokumente.identifiziere_bereinigungsbedarf(
    p_regel_id UUID DEFAULT NULL
)
RETURNS TABLE (
    dokument_id UUID,
    dokument_nr VARCHAR(20),
    titel VARCHAR(200),
    kategorie_name VARCHAR(100),
    erstellt_am TIMESTAMP,
    archivierung_faellig_am DATE,
    gesetzliche_frist_bis DATE,
    regel_id UUID,
    regel_name VARCHAR(100),
    bereinigung_typ VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id as dokument_id,
        d.dokument_nr,
        d.titel,
        dk.kategorie_name,
        d.erstellt_am,
        (d.erstellt_am::DATE + INTERVAL '1 day' * ar.archivierung_nach_tagen)::DATE as archivierung_faellig_am,
        (d.erstellt_am::DATE + INTERVAL '1 year' * ar.gesetzliche_frist_jahre)::DATE as gesetzliche_frist_bis,
        ar.id as regel_id,
        ar.regel_name,
        ar.bereinigung_typ
    FROM dokumente.dokumente d
    JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
    JOIN dokumente.archivierungsregeln ar ON ar.kategorie_id = dk.id
    WHERE ar.aktiv = true
    AND (p_regel_id IS NULL OR ar.id = p_regel_id)
    AND d.status != 'GELOESCHT'
    AND d.erstellt_am::DATE + INTERVAL '1 day' * ar.archivierung_nach_tagen <= CURRENT_DATE
    AND NOT EXISTS (
        SELECT 1 FROM dokumente.archivierte_dokumente ad 
        WHERE ad.original_dokument_id = d.id
    );
END;
$$ LANGUAGE plpgsql;

-- Funktion zur automatischen Archivierung
CREATE OR REPLACE FUNCTION dokumente.automatische_archivierung(
    p_regel_id UUID DEFAULT NULL,
    p_ausgefuehrt_von UUID DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_auftrag_id UUID;
    v_anzahl_archiviert INTEGER := 0;
    v_dokument RECORD;
BEGIN
    -- Bereinigungsauftrag erstellen
    INSERT INTO dokumente.bereinigungsauftraege (
        auftrag_typ, regel_id, status, geplantes_datum, ausgefuehrt_von
    )
    VALUES (
        'ARCHIVIERUNG', 
        p_regel_id, 
        'IN_BEARBEITUNG', 
        CURRENT_DATE,
        p_ausgefuehrt_von
    )
    RETURNING id INTO v_auftrag_id;
    
    -- Dokumente archivieren
    FOR v_dokument IN 
        SELECT * FROM dokumente.identifiziere_bereinigungsbedarf(p_regel_id)
    LOOP
        BEGIN
            -- Dokument archivieren
            INSERT INTO dokumente.archivierte_dokumente (
                original_dokument_id,
                dokument_nr,
                titel,
                kategorie_name,
                archivierungsgrund,
                archiviert_von,
                gesetzliche_frist_bis,
                bereinigung_am,
                bereinigung_status
            )
            VALUES (
                v_dokument.dokument_id,
                v_dokument.dokument_nr,
                v_dokument.titel,
                v_dokument.kategorie_name,
                'Automatische Archivierung nach Regel: ' || v_dokument.regel_name,
                p_ausgefuehrt_von,
                v_dokument.gesetzliche_frist_bis,
                v_dokument.gesetzliche_frist_bis,
                'ARCHIVIERT'
            );
            
            -- Protokoll eintragen
            INSERT INTO dokumente.bereinigungsprotokoll (
                auftrag_id, dokument_id, aktion, status, ausgefuehrt_am
            )
            VALUES (
                v_auftrag_id, v_dokument.dokument_id, 'ARCHIVIERT', 'ERFOLGREICH', CURRENT_TIMESTAMP
            );
            
            v_anzahl_archiviert := v_anzahl_archiviert + 1;
            
        EXCEPTION WHEN OTHERS THEN
            -- Fehler protokollieren
            INSERT INTO dokumente.bereinigungsprotokoll (
                auftrag_id, dokument_id, aktion, status, fehlermeldung, ausgefuehrt_am
            )
            VALUES (
                v_auftrag_id, v_dokument.dokument_id, 'ARCHIVIERT', 'FEHLGESCHLAGEN', SQLERRM, CURRENT_TIMESTAMP
            );
        END;
    END LOOP;
    
    -- Auftrag abschlieÃŸen
    UPDATE dokumente.bereinigungsauftraege 
    SET status = 'ABGESCHLOSSEN', 
        ausgefuehrt_am = CURRENT_TIMESTAMP,
        erfolgreich_verarbeitet = v_anzahl_archiviert
    WHERE id = v_auftrag_id;
    
    RETURN v_anzahl_archiviert;
END;
$$ LANGUAGE plpgsql;

-- Funktion zur endgÃ¼ltigen LÃ¶schung nach Ablauf der gesetzlichen Frist
CREATE OR REPLACE FUNCTION dokumente.endgueltige_loeschung(
    p_ausgefuehrt_von UUID DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_auftrag_id UUID;
    v_anzahl_geloescht INTEGER := 0;
    v_archiviertes_dokument RECORD;
BEGIN
    -- Bereinigungsauftrag erstellen
    INSERT INTO dokumente.bereinigungsauftraege (
        auftrag_typ, status, geplantes_datum, ausgefuehrt_von
    )
    VALUES (
        'LOESCHUNG', 
        'IN_BEARBEITUNG', 
        CURRENT_DATE,
        p_ausgefuehrt_von
    )
    RETURNING id INTO v_auftrag_id;
    
    -- Archivierte Dokumente lÃ¶schen, deren gesetzliche Frist abgelaufen ist
    FOR v_archiviertes_dokument IN 
        SELECT * FROM dokumente.archivierte_dokumente 
        WHERE gesetzliche_frist_bis < CURRENT_DATE
        AND bereinigung_status = 'ARCHIVIERT'
    LOOP
        BEGIN
            -- Status auf "GELÃ–SCHT" setzen
            UPDATE dokumente.archivierte_dokumente 
            SET bereinigung_status = 'LOESCHT',
                bereinigung_am = CURRENT_DATE
            WHERE id = v_archiviertes_dokument.id;
            
            -- Protokoll eintragen
            INSERT INTO dokumente.bereinigungsprotokoll (
                auftrag_id, archiviertes_dokument_id, aktion, status, ausgefuehrt_am
            )
            VALUES (
                v_auftrag_id, v_archiviertes_dokument.id, 'LOESCHT', 'ERFOLGREICH', CURRENT_TIMESTAMP
            );
            
            v_anzahl_geloescht := v_anzahl_geloescht + 1;
            
        EXCEPTION WHEN OTHERS THEN
            -- Fehler protokollieren
            INSERT INTO dokumente.bereinigungsprotokoll (
                auftrag_id, archiviertes_dokument_id, aktion, status, fehlermeldung, ausgefuehrt_am
            )
            VALUES (
                v_auftrag_id, v_archiviertes_dokument.id, 'LOESCHT', 'FEHLGESCHLAGEN', SQLERRM, CURRENT_TIMESTAMP
            );
        END;
    END LOOP;
    
    -- Auftrag abschlieÃŸen
    UPDATE dokumente.bereinigungsauftraege 
    SET status = 'ABGESCHLOSSEN', 
        ausgefuehrt_am = CURRENT_TIMESTAMP,
        erfolgreich_verarbeitet = v_anzahl_geloescht
    WHERE id = v_auftrag_id;
    
    RETURN v_anzahl_geloescht;
END;
$$ LANGUAGE plpgsql;

-- Funktion zur Berechnung des Speicherplatzes
CREATE OR REPLACE FUNCTION dokumente.berechne_speicherplatz()
RETURNS TABLE (
    gesamt_speicher_mb DECIMAL(10,2),
    aktive_dokumente_mb DECIMAL(10,2),
    archivierte_dokumente_mb DECIMAL(10,2),
    anzahl_aktive_dokumente BIGINT,
    anzahl_archivierte_dokumente BIGINT,
    einsparungspotential_mb DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ROUND(SUM(d.dateigroesse)::DECIMAL / (1024 * 1024), 2) as gesamt_speicher_mb,
        ROUND(SUM(CASE WHEN d.status != 'ARCHIVIERT' THEN d.dateigroesse ELSE 0 END)::DECIMAL / (1024 * 1024), 2) as aktive_dokumente_mb,
        ROUND(SUM(CASE WHEN d.status = 'ARCHIVIERT' THEN d.dateigroesse ELSE 0 END)::DECIMAL / (1024 * 1024), 2) as archivierte_dokumente_mb,
        COUNT(CASE WHEN d.status != 'ARCHIVIERT' THEN 1 END)::BIGINT as anzahl_aktive_dokumente,
        COUNT(CASE WHEN d.status = 'ARCHIVIERT' THEN 1 END)::BIGINT as anzahl_archivierte_dokumente,
        ROUND(SUM(CASE WHEN ad.gesetzliche_frist_bis < CURRENT_DATE THEN d.dateigroesse ELSE 0 END)::DECIMAL / (1024 * 1024), 2) as einsparungspotential_mb
    FROM dokumente.dokumente d
    LEFT JOIN dokumente.archivierte_dokumente ad ON ad.original_dokument_id = d.id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS FÃœR ARCHIVIERUNG UND BEREINIGUNG
-- =====================================================

-- BereinigungsÃ¼bersicht
CREATE VIEW dokumente.bereinigungs_uebersicht AS
SELECT 
    ba.id,
    ba.auftrag_nr,
    ba.auftrag_typ,
    ba.status,
    ba.geplantes_datum,
    ba.ausgefuehrt_am,
    ba.anzahl_dokumente,
    ba.erfolgreich_verarbeitet,
    ba.fehlgeschlagene_verarbeitung,
    CONCAT(m.vorname, ' ', m.nachname) as ausgefuehrt_von_name,
    ar.regel_name,
    ar.gesetzliche_grundlage
FROM dokumente.bereinigungsauftraege ba
LEFT JOIN personal.mitarbeiter m ON m.id = ba.ausgefuehrt_von
LEFT JOIN dokumente.archivierungsregeln ar ON ar.id = ba.regel_id;

-- Dokumente mit ablaufender gesetzlicher Frist
CREATE VIEW dokumente.dokumente_ablaufende_frist AS
SELECT 
    d.id,
    d.dokument_nr,
    d.titel,
    dk.kategorie_name,
    d.erstellt_am,
    ad.gesetzliche_frist_bis,
    (ad.gesetzliche_frist_bis - CURRENT_DATE) as tage_bis_ablauf,
    ar.gesetzliche_grundlage,
    ar.bereinigung_typ
FROM dokumente.archivierte_dokumente ad
JOIN dokumente.dokumente d ON d.id = ad.original_dokument_id
JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
JOIN dokumente.archivierungsregeln ar ON ar.kategorie_id = dk.id
WHERE ad.bereinigung_status = 'ARCHIVIERT'
AND ad.gesetzliche_frist_bis BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY ad.gesetzliche_frist_bis;

-- =====================================================
-- ERWEITERTE SICHERHEIT UND COMPLIANCE
-- =====================================================

-- VerschlÃ¼sselung fÃ¼r sensible Dokumente
CREATE TABLE dokumente.dokument_verschluesselung (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    verschluesselungs_typ VARCHAR(50) NOT NULL, -- 'AES256', 'RSA2048', 'KEINE'
    verschluesselungs_schluessel_hash VARCHAR(255),
    entschluesselung_erforderlich BOOLEAN DEFAULT false,
    verschluesselt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verschluesselt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DSGVO-Compliance und Datenschutz
CREATE TABLE dokumente.datenschutz_einstellungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    personenbezogene_daten BOOLEAN DEFAULT false,
    datenschutz_kategorie VARCHAR(50), -- 'NORMAL', 'SENSIBEL', 'BESONDERS_SENSIBEL'
    aufbewahrungsfrist_jahre INTEGER,
    automatische_loeschung BOOLEAN DEFAULT false,
    loeschung_am DATE,
    datenschutzbeauftragter_id UUID REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit-Trail fÃ¼r Compliance (GoBD-konform)
CREATE TABLE dokumente.audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id),
    benutzer_id UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    aktion VARCHAR(100) NOT NULL, -- 'ERSTELLT', 'GELESEN', 'BEARBEITET', 'GELOESCHT', 'FREIGEGEBEN', 'ARCHIVIERT', 'EXPORTIERT'
    aktion_details JSONB,
    ip_adresse INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    zeitstempel TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_wert VARCHAR(64), -- SHA256-Hash fÃ¼r IntegritÃ¤tsprÃ¼fung
    vorheriger_hash VARCHAR(64),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Erweiterte Zugriffsrechte mit Rollen-basierter Sicherheit
CREATE TABLE dokumente.dokument_rollen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rolle_name VARCHAR(100) NOT NULL UNIQUE,
    beschreibung TEXT,
    berechtigungen JSONB NOT NULL, -- {'lesen': true, 'bearbeiten': false, 'loeschen': false, 'freigeben': false}
    sicherheitsstufe INTEGER DEFAULT 1, -- 1-5 (niedrig bis hoch)
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dokument-Berechtigungen mit Rollen
CREATE TABLE dokumente.dokument_berechtigungen_erweitert (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    mitarbeiter_id UUID REFERENCES personal.mitarbeiter(id),
    rolle_id UUID REFERENCES dokumente.dokument_rollen(id),
    berechtigung_typ VARCHAR(50) NOT NULL, -- 'LESEN', 'BEARBEITEN', 'FREIGEBEN', 'LOESCHEN', 'ADMIN', 'ARCHIVIEREN'
    zeitliche_beschraenkung BOOLEAN DEFAULT false,
    gueltig_von TIMESTAMP,
    gueltig_bis TIMESTAMP,
    ip_beschraenkung BOOLEAN DEFAULT false,
    erlaubte_ip_bereiche TEXT[], -- Array von IP-Bereichen
    erteilt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erteilt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ERWEITERTE WORKFLOW-AUTOMATISIERUNG
-- =====================================================

-- Workflow-Templates fÃ¼r verschiedene Dokumenttypen
CREATE TABLE dokumente.workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(100) NOT NULL,
    beschreibung TEXT,
    dokument_typ VARCHAR(50),
    kategorie_id UUID REFERENCES dokumente.dokumentenkategorien(id),
    workflow_steps JSONB NOT NULL, -- Array von Workflow-Schritten
    automatische_ausloesung BOOLEAN DEFAULT false,
    ausloesung_bedingung JSONB, -- Bedingungen fÃ¼r automatische AuslÃ¶sung
    benachrichtigungen JSONB, -- E-Mail/SMS-Benachrichtigungen
    aktiv BOOLEAN DEFAULT true,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Automatische Benachrichtigungen
CREATE TABLE dokumente.benachrichtigungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID REFERENCES dokumente.dokumente(id),
    workflow_instanz_id UUID REFERENCES dokumente.workflow_instanzen(id),
    benachrichtigung_typ VARCHAR(50) NOT NULL, -- 'EMAIL', 'SMS', 'SYSTEM', 'PUSH'
    empfaenger_id UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    betreff VARCHAR(200),
    nachricht TEXT,
    status VARCHAR(50) DEFAULT 'GESENDET', -- 'GESENDET', 'GELESEN', 'FEHLGESCHLAGEN'
    gesendet_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gelesen_am TIMESTAMP,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ERWEITERTE SUCHFUNKTIONEN UND INDEXIERUNG
-- =====================================================

-- Volltext-Suche und Metadaten-Index
CREATE TABLE dokumente.such_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    volltext_inhalt TEXT, -- Extrahierter Text aus Dokumenten
    metadaten JSONB, -- Strukturierte Metadaten
    schluesselwoerter TEXT[], -- Array von SchlÃ¼sselwÃ¶rtern
    kategorien TEXT[], -- Array von Kategorien
    tags TEXT[], -- Array von Tags
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suchhistorie fÃ¼r Benutzer
CREATE TABLE dokumente.suchhistorie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    benutzer_id UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    suchbegriff TEXT NOT NULL,
    gefilterte_ergebnisse INTEGER,
    gesamt_ergebnisse INTEGER,
    ausgewaehlte_dokumente UUID[], -- Array von Dokument-IDs
    suchparameter JSONB, -- Gespeicherte Suchparameter
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- VERSIONIERUNG UND REVISIONSICHERHEIT
-- =====================================================

-- Erweiterte Versionshistorie mit Hash-Validierung
CREATE TABLE dokumente.versionshistorie_erweitert (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    aenderung_typ VARCHAR(50) NOT NULL, -- 'ERSTELLT', 'AKTUALISIERT', 'GELOESCHT', 'WIDERHERGESTELLT', 'FREIGEGEBEN'
    aenderungsbeschreibung TEXT,
    aenderungen JSONB, -- Detaillierte Ã„nderungen
    datei_hash VARCHAR(64) NOT NULL, -- SHA256-Hash der Datei
    vorheriger_hash VARCHAR(64),
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revisionssicher BOOLEAN DEFAULT true,
    archiviert BOOLEAN DEFAULT false
);

-- Digitale Signaturen fÃ¼r Revisionssicherheit
CREATE TABLE dokumente.digitale_signaturen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id),
    version_id UUID REFERENCES dokumente.versionshistorie_erweitert(id),
    signatur_typ VARCHAR(50) NOT NULL, -- 'ELEKTRONISCH', 'DIGITAL', 'TIMESTAMP'
    signatur_hash VARCHAR(64) NOT NULL,
    signiert_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    signiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gueltig_bis TIMESTAMP,
    zertifikat_info JSONB,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INTEGRATION UND API
-- =====================================================

-- API-Zugriffe und Integration
CREATE TABLE dokumente.api_zugriffe (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key VARCHAR(100) NOT NULL,
    system_name VARCHAR(100) NOT NULL,
    berechtigte_endpunkte TEXT[], -- Array von erlaubten API-Endpunkten
    rate_limit_per_minute INTEGER DEFAULT 100,
    aktiv BOOLEAN DEFAULT true,
    erstellt_von UUID NOT NULL REFERENCES personal.mitarbeiter(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    letzter_zugriff TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Integration mit externen Systemen
CREATE TABLE dokumente.system_integrationen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_name VARCHAR(100) NOT NULL,
    integration_typ VARCHAR(50) NOT NULL, -- 'ERP', 'CRM', 'EMAIL', 'CLOUD'
    konfiguration JSONB NOT NULL,
    webhook_url VARCHAR(500),
    api_credentials JSONB,
    synchronisation_aktiv BOOLEAN DEFAULT true,
    letzte_synchronisation TIMESTAMP,
    fehler_protokoll JSONB,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PERFORMANCE UND SKALIERBARKEIT
-- =====================================================

-- Cache fÃ¼r hÃ¤ufig abgerufene Dokumente
CREATE TABLE dokumente.dokument_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id UUID NOT NULL REFERENCES dokumente.dokumente(id),
    cache_typ VARCHAR(50) NOT NULL, -- 'THUMBNAIL', 'VORSCHAU', 'METADATEN'
    cache_daten BYTEA,
    cache_hash VARCHAR(64),
    ablauf_datum TIMESTAMP,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance-Monitoring
CREATE TABLE dokumente.performance_metriken (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metrik_typ VARCHAR(50) NOT NULL, -- 'SUCHZEIT', 'UPLOAD_ZEIT', 'DOWNLOAD_ZEIT'
    wert DECIMAL(10,3),
    einheit VARCHAR(20),
    benutzer_id UUID REFERENCES personal.mitarbeiter(id),
    dokument_id UUID REFERENCES dokumente.dokumente(id),
    system_info JSONB,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXE FÃœR ERWEITERTE FEATURES
-- =====================================================

-- Volltext-Suche Index
CREATE INDEX idx_such_index_volltext ON dokumente.such_index USING gin(to_tsvector('german', volltext_inhalt));
CREATE INDEX idx_such_index_schluesselwoerter ON dokumente.such_index USING gin(schluesselwoerter);
CREATE INDEX idx_such_index_metadaten ON dokumente.such_index USING gin(metadaten);

-- Audit-Trail Indexe
CREATE INDEX idx_audit_trail_dokument ON dokumente.audit_trail(dokument_id);
CREATE INDEX idx_audit_trail_benutzer ON dokumente.audit_trail(benutzer_id);
CREATE INDEX idx_audit_trail_zeitstempel ON dokumente.audit_trail(zeitstempel);
CREATE INDEX idx_audit_trail_aktion ON dokumente.audit_trail(aktion);

-- Berechtigungen Indexe
CREATE INDEX idx_berechtigungen_erweitert_dokument ON dokumente.dokument_berechtigungen_erweitert(dokument_id);
CREATE INDEX idx_berechtigungen_erweitert_mitarbeiter ON dokumente.dokument_berechtigungen_erweitert(mitarbeiter_id);
CREATE INDEX idx_berechtigungen_erweitert_rolle ON dokumente.dokument_berechtigungen_erweitert(rolle_id);
CREATE INDEX idx_berechtigungen_erweitert_gueltig ON dokumente.dokument_berechtigungen_erweitert(gueltig_von, gueltig_bis);

-- Workflow Indexe
CREATE INDEX idx_workflow_templates_typ ON dokumente.workflow_templates(dokument_typ);
CREATE INDEX idx_workflow_templates_kategorie ON dokumente.workflow_templates(kategorie_id);
CREATE INDEX idx_benachrichtigungen_empfaenger ON dokumente.benachrichtigungen(empfaenger_id);
CREATE INDEX idx_benachrichtigungen_status ON dokumente.benachrichtigungen(status);

-- Suchhistorie Indexe
CREATE INDEX idx_suchhistorie_benutzer ON dokumente.suchhistorie(benutzer_id);
CREATE INDEX idx_suchhistorie_zeitstempel ON dokumente.suchhistorie(erstellt_am);

-- Versionierung Indexe
CREATE INDEX idx_versionshistorie_erweitert_dokument ON dokumente.versionshistorie_erweitert(dokument_id);
CREATE INDEX idx_versionshistorie_erweitert_hash ON dokumente.versionshistorie_erweitert(datei_hash);
CREATE INDEX idx_digitale_signaturen_dokument ON dokumente.digitale_signaturen(dokument_id);
CREATE INDEX idx_digitale_signaturen_gueltig ON dokumente.digitale_signaturen(gueltig_bis);

-- Performance Indexe
CREATE INDEX idx_dokument_cache_ablauf ON dokumente.dokument_cache(ablauf_datum);
CREATE INDEX idx_performance_metriken_typ ON dokumente.performance_metriken(metrik_typ);
CREATE INDEX idx_performance_metriken_zeitstempel ON dokumente.performance_metriken(erstellt_am);

-- =====================================================
-- TRIGGERS FÃœR ERWEITERTE FEATURES
-- =====================================================

-- Trigger fÃ¼r automatische Audit-Trail-EintrÃ¤ge
CREATE OR REPLACE FUNCTION dokumente.audit_trail_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_hash VARCHAR(64);
    v_vorheriger_hash VARCHAR(64);
BEGIN
    -- Hash des aktuellen Zustands berechnen
    v_hash := encode(sha256(NEW::text::bytea), 'hex');
    
    -- Vorherigen Hash ermitteln
    IF TG_OP = 'UPDATE' THEN
        SELECT hash_wert INTO v_vorheriger_hash 
        FROM dokumente.audit_trail 
        WHERE dokument_id = NEW.id 
        ORDER BY zeitstempel DESC 
        LIMIT 1;
    END IF;
    
    -- Audit-Trail-Eintrag erstellen
    INSERT INTO dokumente.audit_trail (
        dokument_id, benutzer_id, aktion, aktion_details, 
        hash_wert, vorheriger_hash, ip_adresse, user_agent
    )
    VALUES (
        NEW.id,
        COALESCE(NEW.erstellt_von, current_setting('app.current_user_id', true)::UUID),
        TG_OP,
        jsonb_build_object(
            'alte_daten', CASE WHEN TG_OP = 'UPDATE' THEN to_jsonb(OLD) ELSE NULL END,
            'neue_daten', to_jsonb(NEW),
            'operation', TG_OP
        ),
        v_hash,
        v_vorheriger_hash,
        inet_client_addr(),
        current_setting('app.user_agent', true)
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r Dokumente
CREATE TRIGGER trigger_dokument_audit_trail
    AFTER INSERT OR UPDATE OR DELETE ON dokumente.dokumente
    FOR EACH ROW EXECUTE FUNCTION dokumente.audit_trail_trigger();

-- Trigger fÃ¼r automatische Benachrichtigungen
CREATE OR REPLACE FUNCTION dokumente.benachrichtigung_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Benachrichtigung bei Workflow-Status-Ã„nderung
    IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
        INSERT INTO dokumente.benachrichtigungen (
            workflow_instanz_id, benachrichtigung_typ, empfaenger_id, 
            betreff, nachricht
        )
        SELECT 
            NEW.id,
            'SYSTEM',
            wsi.zugewiesen_an,
            'Workflow-Status geÃ¤ndert: ' || NEW.status,
            'Der Workflow fÃ¼r Dokument ' || d.dokument_nr || ' hat den Status ' || NEW.status || ' erhalten.'
        FROM dokumente.workflow_schritt_instanzen wsi
        JOIN dokumente.dokumente d ON d.id = NEW.dokument_id
        WHERE wsi.workflow_instanz_id = NEW.id 
        AND wsi.status = 'AUSSTEHEND'
        AND wsi.zugewiesen_an IS NOT NULL;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger fÃ¼r Workflow-Instanzen
CREATE TRIGGER trigger_workflow_benachrichtigung
    AFTER UPDATE ON dokumente.workflow_instanzen
    FOR EACH ROW EXECUTE FUNCTION dokumente.benachrichtigung_trigger();

-- =====================================================
-- FUNKTIONEN FÃœR ERWEITERTE FEATURES
-- =====================================================

-- Funktion fÃ¼r Volltext-Suche
CREATE OR REPLACE FUNCTION dokumente.volltext_suche(
    p_suchtext TEXT,
    p_kategorie_id UUID DEFAULT NULL,
    p_erstellt_von UUID DEFAULT NULL,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    id UUID,
    dokument_nr VARCHAR(20),
    titel VARCHAR(200),
    kategorie_name VARCHAR(100),
    relevanz_score REAL,
    treffer_anzahl INTEGER,
    erstellt_am TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.dokument_nr,
        d.titel,
        dk.kategorie_name,
        ts_rank(to_tsvector('german', si.volltext_inhalt), plainto_tsquery('german', p_suchtext)) as relevanz_score,
        array_length(si.schluesselwoerter, 1) as treffer_anzahl,
        d.erstellt_am
    FROM dokumente.dokumente d
    JOIN dokumente.such_index si ON si.dokument_id = d.id
    LEFT JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
    WHERE (
        to_tsvector('german', si.volltext_inhalt) @@ plainto_tsquery('german', p_suchtext) OR
        si.schluesselwoerter && string_to_array(p_suchtext, ' ') OR
        d.titel ILIKE '%' || p_suchtext || '%'
    )
    AND (p_kategorie_id IS NULL OR d.kategorie_id = p_kategorie_id)
    AND (p_erstellt_von IS NULL OR d.erstellt_von = p_erstellt_von)
    ORDER BY relevanz_score DESC, d.erstellt_am DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Funktion fÃ¼r DSGVO-Compliance (Recht auf Vergessenwerden)
CREATE OR REPLACE FUNCTION dokumente.dsgvo_loeschung(
    p_benutzer_id UUID,
    p_ausgefuehrt_von UUID DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_anzahl_geloescht INTEGER := 0;
    v_dokument RECORD;
BEGIN
    -- Dokumente mit personenbezogenen Daten des Benutzers finden
    FOR v_dokument IN 
        SELECT d.id, d.dokument_nr, d.titel
        FROM dokumente.dokumente d
        JOIN dokumente.datenschutz_einstellungen ds ON ds.dokument_id = d.id
        WHERE ds.personenbezogene_daten = true
        AND ds.automatische_loeschung = true
        AND ds.loeschung_am <= CURRENT_DATE
        AND d.erstellt_von = p_benutzer_id
    LOOP
        BEGIN
            -- Dokument als gelÃ¶scht markieren (soft delete)
            UPDATE dokumente.dokumente 
            SET status = 'GELOESCHT',
                geaendert_am = CURRENT_TIMESTAMP
            WHERE id = v_dokument.id;
            
            -- Audit-Trail-Eintrag
            INSERT INTO dokumente.audit_trail (
                dokument_id, benutzer_id, aktion, aktion_details
            )
            VALUES (
                v_dokument.id,
                p_ausgefuehrt_von,
                'DSGVO_LOESCHUNG',
                jsonb_build_object(
                    'grund', 'Recht auf Vergessenwerden',
                    'betroffener_benutzer', p_benutzer_id,
                    'dokument_nr', v_dokument.dokument_nr,
                    'titel', v_dokument.titel
                )
            );
            
            v_anzahl_geloescht := v_anzahl_geloescht + 1;
            
        EXCEPTION WHEN OTHERS THEN
            -- Fehler protokollieren
            RAISE NOTICE 'Fehler beim LÃ¶schen von Dokument %: %', v_dokument.dokument_nr, SQLERRM;
        END;
    END LOOP;
    
    RETURN v_anzahl_geloescht;
END;
$$ LANGUAGE plpgsql;

-- Funktion fÃ¼r Performance-Monitoring
CREATE OR REPLACE FUNCTION dokumente.performance_metrik_speichern(
    p_metrik_typ VARCHAR(50),
    p_wert DECIMAL(10,3),
    p_einheit VARCHAR(20),
    p_benutzer_id UUID DEFAULT NULL,
    p_dokument_id UUID DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO dokumente.performance_metriken (
        metrik_typ, wert, einheit, benutzer_id, dokument_id, system_info
    )
    VALUES (
        p_metrik_typ,
        p_wert,
        p_einheit,
        p_benutzer_id,
        p_dokument_id,
        jsonb_build_object(
            'session_id', current_setting('app.session_id', true),
            'ip_adresse', inet_client_addr(),
            'user_agent', current_setting('app.user_agent', true),
            'timestamp', CURRENT_TIMESTAMP
        )
    );
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS FÃœR ERWEITERTE FEATURES
-- =====================================================

-- Compliance-Ãœbersicht
CREATE VIEW dokumente.compliance_uebersicht AS
SELECT 
    d.id,
    d.dokument_nr,
    d.titel,
    dk.kategorie_name,
    ds.personenbezogene_daten,
    ds.datenschutz_kategorie,
    ds.aufbewahrungsfrist_jahre,
    ds.automatische_loeschung,
    ds.loeschung_am,
    CONCAT(m.vorname, ' ', m.nachname) as datenschutzbeauftragter,
    COUNT(at.id) as audit_eintraege,
    MAX(at.zeitstempel) as letzter_audit_eintrag
FROM dokumente.dokumente d
LEFT JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
LEFT JOIN dokumente.datenschutz_einstellungen ds ON ds.dokument_id = d.id
LEFT JOIN personal.mitarbeiter m ON m.id = ds.datenschutzbeauftragter_id
LEFT JOIN dokumente.audit_trail at ON at.dokument_id = d.id
GROUP BY d.id, d.dokument_nr, d.titel, dk.kategorie_name, ds.personenbezogene_daten, 
         ds.datenschutz_kategorie, ds.aufbewahrungsfrist_jahre, ds.automatische_loeschung, 
         ds.loeschung_am, m.vorname, m.nachname;

-- Sicherheits-Ãœbersicht
CREATE VIEW dokumente.sicherheit_uebersicht AS
SELECT 
    d.id,
    d.dokument_nr,
    d.titel,
    dk.kategorie_name,
    dv.verschluesselungs_typ,
    dv.entschluesselung_erforderlich,
    COUNT(dbe.id) as anzahl_berechtigungen,
    COUNT(ds.id) as anzahl_signaturen,
    MAX(at.zeitstempel) as letzter_zugriff,
    d.status
FROM dokumente.dokumente d
LEFT JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
LEFT JOIN dokumente.dokument_verschluesselung dv ON dv.dokument_id = d.id
LEFT JOIN dokumente.dokument_berechtigungen_erweitert dbe ON dbe.dokument_id = d.id
LEFT JOIN dokumente.digitale_signaturen ds ON ds.dokument_id = d.id
LEFT JOIN dokumente.audit_trail at ON at.dokument_id = d.id
GROUP BY d.id, d.dokument_nr, d.titel, dk.kategorie_name, dv.verschluesselungs_typ, 
         dv.entschluesselung_erforderlich, d.status;

-- Performance-Ãœbersicht
CREATE VIEW dokumente.performance_uebersicht AS
SELECT 
    metrik_typ,
    AVG(wert) as durchschnitt_wert,
    MIN(wert) as min_wert,
    MAX(wert) as max_wert,
    COUNT(*) as anzahl_messungen,
    DATE_TRUNC('hour', erstellt_am) as stunde,
    COUNT(DISTINCT benutzer_id) as anzahl_benutzer
FROM dokumente.performance_metriken
WHERE erstellt_am >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY metrik_typ, DATE_TRUNC('hour', erstellt_am)
ORDER BY stunde DESC, metrik_typ;

-- =====================================================
-- BEISPIELDATEN FÃœR ERWEITERTE FEATURES
-- =====================================================

-- Dokument-Rollen
INSERT INTO dokumente.dokument_rollen (rolle_name, beschreibung, berechtigungen, sicherheitsstufe) VALUES
('Leser', 'Nur Leserechte auf Dokumente', '{"lesen": true, "bearbeiten": false, "loeschen": false, "freigeben": false}', 1),
('Bearbeiter', 'Lesen und Bearbeiten von Dokumenten', '{"lesen": true, "bearbeiten": true, "loeschen": false, "freigeben": false}', 2),
('Freigeber', 'Lesen, Bearbeiten und Freigeben von Dokumenten', '{"lesen": true, "bearbeiten": true, "loeschen": false, "freigeben": true}', 3),
('Administrator', 'Vollzugriff auf Dokumente', '{"lesen": true, "bearbeiten": true, "loeschen": true, "freigeben": true}', 4),
('Datenschutzbeauftragter', 'Spezielle Rechte fÃ¼r DSGVO-Compliance', '{"lesen": true, "bearbeiten": false, "loeschen": true, "freigeben": false}', 5);

-- Workflow-Templates
INSERT INTO dokumente.workflow_templates (template_name, beschreibung, dokument_typ, workflow_steps, automatische_ausloesung, benachrichtigungen) VALUES
('Standard-Freigabe', 'Standard-Freigabeprozess fÃ¼r alle Dokumente', 'ALL', 
 '[{"schritt": 1, "name": "Ersteller-PrÃ¼fung", "rolle": "Bearbeiter", "aktion": "PRÃœFEN", "zeitlimit": 2},
   {"schritt": 2, "name": "Abteilungsleiter-Freigabe", "rolle": "Freigeber", "aktion": "FREIGEBEN", "zeitlimit": 3}]',
 true,
 '{"email": true, "system": true}'),
('QS-Freigabe', 'QualitÃ¤tssicherungs-Freigabeprozess', 'PDF',
 '[{"schritt": 1, "name": "QS-PrÃ¼fung", "rolle": "Bearbeiter", "aktion": "PRÃœFEN", "zeitlimit": 5},
   {"schritt": 2, "name": "QS-Leiter-Freigabe", "rolle": "Freigeber", "aktion": "FREIGEBEN", "zeitlimit": 3}]',
 true,
 '{"email": true, "system": true}');

-- Datenschutz-Einstellungen fÃ¼r bestehende Dokumente
INSERT INTO dokumente.datenschutz_einstellungen (dokument_id, personenbezogene_daten, datenschutz_kategorie, aufbewahrungsfrist_jahre, automatische_loeschung)
SELECT 
    d.id,
    CASE 
        WHEN dk.kategorie_name IN ('Personal', 'VertrÃ¤ge') THEN true
        ELSE false
    END,
    CASE 
        WHEN dk.kategorie_name = 'Personal' THEN 'BESONDERS_SENSIBEL'
        WHEN dk.kategorie_name = 'VertrÃ¤ge' THEN 'SENSIBEL'
        ELSE 'NORMAL'
    END,
    CASE 
        WHEN dk.kategorie_name = 'Personal' THEN 6
        WHEN dk.kategorie_name = 'VertrÃ¤ge' THEN 10
        ELSE 5
    END,
    CASE 
        WHEN dk.kategorie_name IN ('Personal', 'Angebote') THEN true
        ELSE false
    END
FROM dokumente.dokumente d
JOIN dokumente.dokumentenkategorien dk ON dk.id = d.kategorie_id
WHERE NOT EXISTS (
    SELECT 1 FROM dokumente.datenschutz_einstellungen ds WHERE ds.dokument_id = d.id
);

-- =====================================================
-- KOMMENTARE FÃœR ERWEITERTE FEATURES
-- =====================================================

COMMENT ON TABLE dokumente.dokument_verschluesselung IS 'VerschlÃ¼sselung fÃ¼r sensible Dokumente';
COMMENT ON TABLE dokumente.datenschutz_einstellungen IS 'DSGVO-Compliance und Datenschutz-Einstellungen';
COMMENT ON TABLE dokumente.audit_trail IS 'VollstÃ¤ndiger Audit-Trail fÃ¼r GoBD-Compliance';
COMMENT ON TABLE dokumente.dokument_rollen IS 'Rollen-basierte Sicherheit fÃ¼r Dokumente';
COMMENT ON TABLE dokumente.dokument_berechtigungen_erweitert IS 'Erweiterte Zugriffsrechte mit zeitlichen und IP-BeschrÃ¤nkungen';
COMMENT ON TABLE dokumente.workflow_templates IS 'Workflow-Templates fÃ¼r Automatisierung';
COMMENT ON TABLE dokumente.benachrichtigungen IS 'Automatische Benachrichtigungen fÃ¼r Workflows';
COMMENT ON TABLE dokumente.such_index IS 'Volltext-Suche und Metadaten-Index';
COMMENT ON TABLE dokumente.versionshistorie_erweitert IS 'Erweiterte Versionshistorie mit Hash-Validierung';
COMMENT ON TABLE dokumente.digitale_signaturen IS 'Digitale Signaturen fÃ¼r Revisionssicherheit';
COMMENT ON TABLE dokumente.api_zugriffe IS 'API-Zugriffe und Integration';
COMMENT ON TABLE dokumente.performance_metriken IS 'Performance-Monitoring fÃ¼r Skalierbarkeit';

COMMENT ON FUNCTION dokumente.volltext_suche IS 'Volltext-Suche mit Relevanz-Scoring';
COMMENT ON FUNCTION dokumente.dsgvo_loeschung IS 'DSGVO-Compliance: Recht auf Vergessenwerden';
COMMENT ON FUNCTION dokumente.performance_metrik_speichern IS 'Performance-Monitoring fÃ¼r Metriken';

COMMIT; 
