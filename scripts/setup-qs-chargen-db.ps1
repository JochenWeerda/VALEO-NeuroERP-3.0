param(
    [string]$DbContainer = "valeo-neuro-erp-postgres",
    [string]$DbUser = "valeo_dev",
    [string]$DbName = "valeo_neuro_erp"
)

$ErrorActionPreference = "Stop"

$sql = @'
CREATE SCHEMA IF NOT EXISTS domain_ops;

CREATE TABLE IF NOT EXISTS domain_ops.ops_chargen (
    id VARCHAR PRIMARY KEY,
    chargen_id VARCHAR(50) UNIQUE NOT NULL,
    artikel VARCHAR(100) NOT NULL,
    artikel_id VARCHAR(100) NOT NULL,
    menge DOUBLE PRECISION NOT NULL,
    lagerort VARCHAR(100) NOT NULL,
    eingang TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'erfasst',
    qualitaetsstatus VARCHAR(30) DEFAULT 'in-pruefung',
    freigabe_datum TIMESTAMPTZ,
    herkunft VARCHAR(255),
    bemerkungen TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS losnummer VARCHAR(50);
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS produktbezeichnung VARCHAR(255);
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS herstellungsdatum TIMESTAMPTZ;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS rueckverfolgbar_bis_stunden INTEGER DEFAULT 4;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS rohstoffe JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS lieferant_info JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS kunden_info JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS produktionsprozess JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS digitales_mischbuch JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS haccp_system JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS eigenkontrollen JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS warentrennung_qs_nicht_qs BOOLEAN DEFAULT FALSE;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS krisenmanagement JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS futtermittelmonitoring JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS qualitaetspersonal JSONB;
ALTER TABLE domain_ops.ops_chargen ADD COLUMN IF NOT EXISTS qs_datenbank JSONB;

INSERT INTO domain_ops.ops_chargen (
    id,
    chargen_id,
    losnummer,
    artikel,
    artikel_id,
    produktbezeichnung,
    menge,
    lagerort,
    eingang,
    herstellungsdatum,
    status,
    qualitaetsstatus,
    herkunft,
    bemerkungen,
    rueckverfolgbar_bis_stunden,
    rohstoffe,
    lieferant_info,
    kunden_info,
    produktionsprozess,
    digitales_mischbuch,
    haccp_system,
    eigenkontrollen,
    warentrennung_qs_nicht_qs,
    krisenmanagement,
    futtermittelmonitoring,
    qualitaetspersonal,
    qs_datenbank,
    created_by,
    updated_by
)
SELECT
    'CH-QS-2025-RAPS-001',
    'QS-RAPS-2025-001',
    'LOS-RAPS-2025-001',
    'Raps NaWaRo',
    'ART-RAPS-NAWARO-001',
    'Raps fuer energetische Nutzung (Biodiesel)',
    110.5,
    'Silo 3',
    TIMESTAMPTZ '2025-08-15 10:00:00+00',
    TIMESTAMPTZ '2025-08-15 09:20:00+00',
    'erfasst',
    'in-pruefung',
    'Agrarhof Meyer',
    'QS-Seedcharge fuer fahrbare Mahl- und Mischanlage',
    4,
    jsonb_build_array(
        jsonb_build_object('name','Raps-Saat', 'menge', 100.0, 'einheit','t', 'lieferant_id','LIEF-0001'),
        jsonb_build_object('name','Mineralstoffmix', 'menge', 10.5, 'einheit','t', 'lieferant_id','LIEF-0002')
    ),
    jsonb_build_object(
        'name','Agrarhandel Nord GmbH',
        'anschrift','Hafenstrasse 8, 26409 Wittmund',
        'qs_id','QS-LIEF-7788',
        'qs_lieferberechtigt', true
    ),
    jsonb_build_object(
        'name','Gefluegelmast Janssen',
        'anschrift','Moorweg 12, 26419 Schortens',
        'qs_id','QS-KD-4455',
        'vvvo','03-455-112233'
    ),
    jsonb_build_object(
        'reihenfolge', jsonb_build_array('Raps-Saat', 'Mineralstoffmix', 'Spuelcharge'),
        'spuelchargen', jsonb_build_array('SP-2025-08-15-01'),
        'mischzeiten', jsonb_build_array('00:10:00', '00:04:00'),
        'anlage', 'Fahrbare Mahl- und Mischanlage FM-07'
    ),
    jsonb_build_object(
        'eintraege', jsonb_build_array(
            jsonb_build_object('zeitpunkt','2025-08-15T10:15:00Z', 'aktion','Mischung gestartet', 'user','meister'),
            jsonb_build_object('zeitpunkt','2025-08-15T10:29:00Z', 'aktion','Mischung beendet', 'user','meister')
        ),
        'signatur','qs-digital-sign-001'
    ),
    jsonb_build_object(
        'gefahrenanalyse','Kreuzkontamination und Salmonellen-Risiko bewertet',
        'ccp', jsonb_build_array('Magnetabscheider', 'Mischzeit >= 10min'),
        'ueberwachung', jsonb_build_array('Sichtkontrolle je Charge', 'Temperaturprobe je Tour'),
        'korrekturen', jsonb_build_array('Spuelcharge', 'Sperrung bei Abweichung'),
        'verifizierung','Jaehrliche HACCP-Verifizierung 2025-12-10'
    ),
    jsonb_build_array(
        jsonb_build_object('datum','2025-08-15', 'art','Wareneingang', 'ergebnis','ok', 'massnahme','keine'),
        jsonb_build_object('datum','2025-08-15', 'art','Freigabepruefung', 'ergebnis','ok', 'massnahme','Freigabe')
    ),
    true,
    jsonb_build_object(
        'krisenmanager', jsonb_build_object('name','Ines Becker', 'telefon','+49-4462-1234-90'),
        'ereignisfallblatt','QMS-CRISIS-2025-08',
        'rueckrufverfahren','QMS-RUECKRUF-V2'
    ),
    jsonb_build_object(
        'proben', jsonb_build_array(jsonb_build_object('probe_id','QS-P-2025-0815', 'labor','LUFA', 'status','uebermittelt')),
        'freigabepruefungen', jsonb_build_array('Feuchte', 'Protein', 'Mikrobiologie'),
        'oele_fette_teilnahme', true
    ),
    jsonb_build_object(
        'qualitaetsbeauftragter', jsonb_build_object('name','Ines Becker', 'rolle','QMB'),
        'schulungsplan', jsonb_build_array('HACCP Basis', 'QS Leitfaden 2025'),
        'schulungsnachweise', jsonb_build_array('SCH-2025-01', 'SCH-2025-09')
    ),
    jsonb_build_object(
        'anlagen', jsonb_build_array('FM-07'),
        'stammdaten_sync', true,
        'auditberichte', jsonb_build_array('QS-AUDIT-2025-44'),
        'korrekturmassnahmen', jsonb_build_array('CAPA-2025-18')
    ),
    'seed',
    'seed'
WHERE NOT EXISTS (
    SELECT 1
    FROM domain_ops.ops_chargen c
    WHERE c.chargen_id = 'QS-RAPS-2025-001'
);
'@

$sql | docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1

Write-Host "QS-Chargen DB setup completed (columns + seed)"
