param(
    [string]$DbContainer = "valeo-neuro-erp-postgres",
    [string]$DbUser = "valeo_dev",
    [string]$DbName = "valeo_neuro_erp"
)

$ErrorActionPreference = "Stop"

$sql = @'
CREATE SCHEMA IF NOT EXISTS domain_ops;

ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS ro_nummer VARCHAR(50);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS is_neu BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS betrieb VARCHAR(120);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS bereich VARCHAR(120);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS pol_kennzeichen VARCHAR(30);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS verwendung VARCHAR(255);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kfz_brief_nummer VARCHAR(120);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS schadstoffgruppe VARCHAR(80);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leistung_kw DOUBLE PRECISION;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kraftstoff VARCHAR(80);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS fahrgestellnummer VARCHAR(120);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS erstzulassung TIMESTAMPTZ;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS ausstattung TEXT;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS fahrtenschreiber_vorhanden BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS ahk_vorhanden BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS ladekran_vorhanden BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS fahrer_name VARCHAR(120);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS fahrer_vorname VARCHAR(120);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS km_stand_alle_eintraege BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS bestellnummer VARCHAR(80);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS bestelldatum TIMESTAMPTZ;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS haendler VARCHAR(160);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS zustand VARCHAR(20);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kaufsumme_eur DECIMAL(14,2);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kaufdatum TIMESTAMPTZ;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS verkaufsdatum TIMESTAMPTZ;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kostenstelle VARCHAR(80);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS abschreibungsart VARCHAR(80);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS afa_jahre INTEGER;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS afa_eur_jaehrlich DECIMAL(14,2);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS afa_eur_monatlich DECIMAL(14,2);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leasingdauer_monate INTEGER;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leasinggesellschaft VARCHAR(160);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leasingrate_eur DECIMAL(14,2);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kfz_steuer_eur DECIMAL(14,2);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kfz_steuernummer VARCHAR(80);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kontierung VARCHAR(80);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS finanzamt VARCHAR(160);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherungs_gesellschaft VARCHAR(160);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherungsschein_nr VARCHAR(120);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherung_satz_eur_monat DECIMAL(14,2);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherung_haftpflicht BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherung_kasko BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS naechster_tuev_termin TIMESTAMPTZ;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS naechster_asu_termin TIMESTAMPTZ;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leergewicht_kg DOUBLE PRECISION;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS nutzlast_kg DOUBLE PRECISION;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS gesamtgewicht_kg DOUBLE PRECISION;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS anhaengerlast_kg DOUBLE PRECISION;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS winterreifen_vorhanden BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS winterreifen_eingelagert BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS handy_freisprecheinrichtung BOOLEAN DEFAULT FALSE;
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS handy_fabrikat VARCHAR(120);
ALTER TABLE IF EXISTS domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS handy_rufnummer VARCHAR(80);

INSERT INTO domain_ops.ops_fahrzeuge (
    id, ro_nummer, is_neu, betrieb, bereich, pol_kennzeichen, kennzeichen, typ, marke, modell, baujahr,
    verwendung, kfz_brief_nummer, schadstoffgruppe, leistung_kw, kraftstoff, fahrgestellnummer, erstzulassung,
    ausstattung, fahrtenschreiber_vorhanden, ahk_vorhanden, ladekran_vorhanden, fahrer_name, fahrer_vorname,
    kilometerstand, km_stand_alle_eintraege, bestellnummer, bestelldatum, haendler, zustand, kaufsumme_eur,
    kaufdatum, kostenstelle, abschreibungsart, afa_jahre, afa_eur_jaehrlich, afa_eur_monatlich,
    leasingdauer_monate, leasinggesellschaft, leasingrate_eur, kfz_steuer_eur, kfz_steuernummer, kontierung,
    finanzamt, versicherungs_gesellschaft, versicherungsschein_nr, versicherung_satz_eur_monat, versicherung_haftpflicht,
    versicherung_kasko, naechster_tuev_termin, naechster_asu_termin, leergewicht_kg, nutzlast_kg, gesamtgewicht_kg,
    anhaengerlast_kg, winterreifen_vorhanden, winterreifen_eingelagert, handy_freisprecheinrichtung, handy_fabrikat,
    handy_rufnummer, status
)
VALUES (
    'F-ZVOOVE01', 'RO-2026-001', TRUE, 'Hauptbetrieb', 'Logistik', 'WTM-LH-101', 'WTM-LH 101', 'LKW 18t',
    'MAN', 'TGS', 2024, 'Getreide-Transport', 'KFZB-88271', 'Euro 6', 294, 'Diesel', 'WMA18T12345678901',
    TIMESTAMPTZ '2024-02-01 00:00:00+00', 'AHK, Ladekran, Telematik', TRUE, TRUE, TRUE, 'Meyer', 'Jan',
    78500, FALSE, 'PO-2024-445', TIMESTAMPTZ '2024-01-10 00:00:00+00', 'MAN Truck Center', 'neu', 158000.00,
    TIMESTAMPTZ '2024-02-15 00:00:00+00', 'KST-LOG-100', 'linear', 8, 19750.00, 1645.83,
    60, 'LeasePlan', 1890.00, 950.00, 'KFZ-2024-991', '4400', 'Finanzamt Wittmund', 'R+V',
    'VS-778899', 245.00, TRUE, TRUE, TIMESTAMPTZ '2026-05-20 00:00:00+00', TIMESTAMPTZ '2026-05-20 00:00:00+00',
    8200, 9800, 18000, 12000, TRUE, TRUE, TRUE, 'Samsung', '+49 171 5550001', 'verfuegbar'
)
ON CONFLICT (id) DO NOTHING;
'@

$sql | docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1

Write-Host "Fuhrpark DB setup completed (columns + seed)"
