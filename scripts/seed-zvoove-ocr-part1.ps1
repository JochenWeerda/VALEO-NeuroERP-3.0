param(
    [string]$DbContainer = "valeo-neuro-erp-postgres",
    [string]$DbUser = "valeo_dev",
    [string]$DbName = "valeo_neuro_erp"
)

$ErrorActionPreference = "Stop"

$sql = @"
CREATE SCHEMA IF NOT EXISTS domain_ops;

CREATE TABLE IF NOT EXISTS domain_ops.zvoove_ocr_screens (
    id VARCHAR(36) PRIMARY KEY,
    screenshot_file VARCHAR(64) NOT NULL UNIQUE,
    title VARCHAR(255),
    source_language VARCHAR(16) NOT NULL DEFAULT 'de',
    ocr_fallback_language VARCHAR(16),
    raw_markdown TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS domain_ops.zvoove_ocr_screen_fields (
    id VARCHAR(36) PRIMARY KEY,
    screenshot_file VARCHAR(64) NOT NULL,
    section_name VARCHAR(120),
    field_label VARCHAR(255) NOT NULL,
    field_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS domain_ops.zvoove_print_form_templates (
    id VARCHAR(36) PRIMARY KEY,
    screenshot_file VARCHAR(64) NOT NULL,
    form_code VARCHAR(16) NOT NULL,
    form_name VARCHAR(255) NOT NULL,
    enabled_by_default BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (screenshot_file, form_code)
);

INSERT INTO domain_ops.zvoove_ocr_screens (id, screenshot_file, title, source_language, ocr_fallback_language, raw_markdown)
VALUES
(
    '4a06a5c2-7e00-4eb1-9a8a-000000000001',
    'D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg',
    'Streckenliste / Disposition',
    'de',
    'en',
    'Lieferant Nr Lieferant-Name Tag Letzte PLZ Letzter Ort Info
Enlade-Zeit Belade-P. Belade-Ort Entlade-Zeit Entlade-Ort Frachtrate Artikel Fahrzeug Lieferant

Strecke Vorgang Niederlassung Belade-Datum Entlade-Datum Kunden Preis EK Preis VK Frachtkosten Info'
),
(
    '4a06a5c2-7e00-4eb1-9a8a-000000000002',
    'DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg',
    'Vorläufige Strecken',
    'de',
    'en',
    'Vorläufige Strecken
Niederlassung | Vorl. Strecke-Nr | Erstellung-Datum | Belade-Datum | Entlade-Datum | LKW-Kennzeichen

Artikel-Bezeichnung | Preis EK | Preis VK | Info | Fahrzeug-Nr | Strecke-Nr'
),
(
    '4a06a5c2-7e00-4eb1-9a8a-000000000003',
    '34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg',
    'Dokumente Drucken/Faxen',
    'de',
    'en',
    'Dokumente Drucken / Faxen

Frachtauftrag an Spedition (W95041)
Rohstofferklärung an Spedition (W95045)
Freistellung an Kunde (W95051)
Freistellung an Lieferant (W95052)
Freistellung an Beladestelle (W95053)
Freigabe (W95101)
Reklamation an Kunde (W95081)
Reklamation an Lieferant (W95082)
Konformitätsbestätigung Kunde (W95091)
Konformitätsbestätigung Lieferant (W95092)

Drucker: Groothusen/Kyocera M3540dn Fach 1'
),
(
    '4a06a5c2-7e00-4eb1-9a8a-000000000004',
    '9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg',
    'Qualitätsabweichung',
    'de',
    'en',
    'Qualitätsabweichung

Strecke-Nr: [ ... ]

Qualitäts-Abweichungen lt. Filter:
Bezeichnung | Einheit | Soll EK | Ist EK | Abw. EK | Soll VK | Ist VK | Abw. VK | Ja'
)
ON CONFLICT (screenshot_file) DO UPDATE SET
    title = EXCLUDED.title,
    raw_markdown = EXCLUDED.raw_markdown;

DELETE FROM domain_ops.zvoove_ocr_screen_fields
WHERE screenshot_file IN (
    'D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg',
    'DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg',
    '9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg'
);

INSERT INTO domain_ops.zvoove_ocr_screen_fields (id, screenshot_file, section_name, field_label, field_order)
VALUES
('5b06a5c2-7e00-4eb1-9a8a-000000000001','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','kopf','Lieferant Nr',1),
('5b06a5c2-7e00-4eb1-9a8a-000000000002','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','kopf','Lieferant-Name',2),
('5b06a5c2-7e00-4eb1-9a8a-000000000003','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','kopf','Tag',3),
('5b06a5c2-7e00-4eb1-9a8a-000000000004','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','kopf','Letzte PLZ',4),
('5b06a5c2-7e00-4eb1-9a8a-000000000005','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','kopf','Letzter Ort',5),
('5b06a5c2-7e00-4eb1-9a8a-000000000006','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','kopf','Info',6),
('5b06a5c2-7e00-4eb1-9a8a-000000000007','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Enlade-Zeit',7),
('5b06a5c2-7e00-4eb1-9a8a-000000000008','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Belade-P.',8),
('5b06a5c2-7e00-4eb1-9a8a-000000000009','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Belade-Ort',9),
('5b06a5c2-7e00-4eb1-9a8a-000000000010','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Entlade-Zeit',10),
('5b06a5c2-7e00-4eb1-9a8a-000000000011','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Entlade-Ort',11),
('5b06a5c2-7e00-4eb1-9a8a-000000000012','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Frachtrate',12),
('5b06a5c2-7e00-4eb1-9a8a-000000000013','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Artikel',13),
('5b06a5c2-7e00-4eb1-9a8a-000000000014','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Fahrzeug',14),
('5b06a5c2-7e00-4eb1-9a8a-000000000015','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','strecke','Lieferant',15),
('5b06a5c2-7e00-4eb1-9a8a-000000000016','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Strecke',16),
('5b06a5c2-7e00-4eb1-9a8a-000000000017','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Vorgang',17),
('5b06a5c2-7e00-4eb1-9a8a-000000000018','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Niederlassung',18),
('5b06a5c2-7e00-4eb1-9a8a-000000000019','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Belade-Datum',19),
('5b06a5c2-7e00-4eb1-9a8a-000000000020','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Entlade-Datum',20),
('5b06a5c2-7e00-4eb1-9a8a-000000000021','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Kunden',21),
('5b06a5c2-7e00-4eb1-9a8a-000000000022','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Preis EK',22),
('5b06a5c2-7e00-4eb1-9a8a-000000000023','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Preis VK',23),
('5b06a5c2-7e00-4eb1-9a8a-000000000024','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Frachtkosten',24),
('5b06a5c2-7e00-4eb1-9a8a-000000000025','D6DF72DB-353F-4663-83FC-9563C79B9CE2.jpeg','abrechnung','Info',25),

('5b06a5c2-7e00-4eb1-9a8a-000000000026','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','vorlaeufige_strecken','Niederlassung',1),
('5b06a5c2-7e00-4eb1-9a8a-000000000027','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','vorlaeufige_strecken','Vorl. Strecke-Nr',2),
('5b06a5c2-7e00-4eb1-9a8a-000000000028','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','vorlaeufige_strecken','Erstellung-Datum',3),
('5b06a5c2-7e00-4eb1-9a8a-000000000029','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','vorlaeufige_strecken','Belade-Datum',4),
('5b06a5c2-7e00-4eb1-9a8a-000000000030','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','vorlaeufige_strecken','Entlade-Datum',5),
('5b06a5c2-7e00-4eb1-9a8a-000000000031','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','vorlaeufige_strecken','LKW-Kennzeichen',6),
('5b06a5c2-7e00-4eb1-9a8a-000000000032','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','positionsliste','Artikel-Bezeichnung',7),
('5b06a5c2-7e00-4eb1-9a8a-000000000033','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','positionsliste','Preis EK',8),
('5b06a5c2-7e00-4eb1-9a8a-000000000034','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','positionsliste','Preis VK',9),
('5b06a5c2-7e00-4eb1-9a8a-000000000035','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','positionsliste','Info',10),
('5b06a5c2-7e00-4eb1-9a8a-000000000036','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','positionsliste','Fahrzeug-Nr',11),
('5b06a5c2-7e00-4eb1-9a8a-000000000037','DA0BF2D8-4838-4238-AFEF-C1D6FB976C23.jpeg','positionsliste','Strecke-Nr',12),

('5b06a5c2-7e00-4eb1-9a8a-000000000038','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Strecke-Nr',1),
('5b06a5c2-7e00-4eb1-9a8a-000000000039','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Bezeichnung',2),
('5b06a5c2-7e00-4eb1-9a8a-000000000040','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Einheit',3),
('5b06a5c2-7e00-4eb1-9a8a-000000000041','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Soll EK',4),
('5b06a5c2-7e00-4eb1-9a8a-000000000042','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Ist EK',5),
('5b06a5c2-7e00-4eb1-9a8a-000000000043','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Abw. EK',6),
('5b06a5c2-7e00-4eb1-9a8a-000000000044','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Soll VK',7),
('5b06a5c2-7e00-4eb1-9a8a-000000000045','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Ist VK',8),
('5b06a5c2-7e00-4eb1-9a8a-000000000046','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Abw. VK',9),
('5b06a5c2-7e00-4eb1-9a8a-000000000047','9119B98F-1211-4007-AE08-6D9CEF6769F7.jpeg','qualitaetsabweichung','Ja',10);

DELETE FROM domain_ops.zvoove_print_form_templates
WHERE screenshot_file = '34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg';

INSERT INTO domain_ops.zvoove_print_form_templates (id, screenshot_file, form_code, form_name, enabled_by_default)
VALUES
('6c06a5c2-7e00-4eb1-9a8a-000000000001','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95041','Frachtauftrag an Spedition',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000002','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95045','Rohstofferklärung an Spedition',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000003','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95051','Freistellung an Kunde',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000004','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95052','Freistellung an Lieferant',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000005','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95053','Freistellung an Beladestelle',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000006','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95101','Freigabe',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000007','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95081','Reklamation an Kunde',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000008','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95082','Reklamation an Lieferant',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000009','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95091','Konformitätsbestätigung Kunde',TRUE),
('6c06a5c2-7e00-4eb1-9a8a-000000000010','34D4D002-5CEA-433C-B83D-5F07D6B458E1.jpeg','W95092','Konformitätsbestätigung Lieferant',TRUE);
"@

$sql | docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1

Write-Host "Seed completed: zvoove OCR part 1 (screens, fields, print templates)"
