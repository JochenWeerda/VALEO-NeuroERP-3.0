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
    '7d06a5c2-7e00-4eb1-9a8a-000000000001',
    '1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg',
    'NaWaRo-Mitteilung drucken',
    'de',
    'en',
    'NaWaRo-Mitteilung drucken

Dokument: Ernteerklärung zum Anbau nachwachsender Rohstoffe
Ernte-Jahr: 2025
Artikel-Nr.: [...]
Debitor-Kto. von [...] bis [...]
Vollständige Ablieferung / Hoflagerung beim Erzeuger / Berichtigung / Nachmeldung
Formular: W12151
Anzahl: 1
Aktueller Drucker: Groothusen/Kyocera M3540dn Fach 1'
),
(
    '7d06a5c2-7e00-4eb1-9a8a-000000000002',
    '31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg',
    'Mitteilung des Aufkäufers über die Lieferung',
    'de',
    'en',
    'Dokument: Mitteilung des Aufkäufers über die Lieferung
Ernte-Jahr: 2025
Artikel-Nr.: [...]
Debitor-Kto. von [...] bis [...]
Vollständige Ablieferung / Hoflagerung beim Erzeuger / Berichtigung / Nachmeldung
Formular: W12151
Anzahl: 1'
),
(
    '7d06a5c2-7e00-4eb1-9a8a-000000000003',
    '8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg',
    'NaWaRo-Mitteilung drucken (Kurzdialog)',
    'de',
    'en',
    'NaWaRo-Mitteilung drucken
Vollständige Ablieferung / Hoflagerung beim Erzeuger / Berichtigung / Nachmeldung
Anzahl: 1
Drucker: Groothusen/Kyocera M3540dn Fach 1
Aktionen: Drucken, Vorschau'
),
(
    '7d06a5c2-7e00-4eb1-9a8a-000000000004',
    'FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg',
    'NaWaRo-Mitteilung drucken (Formularansicht)',
    'de',
    'en',
    'Artikel-Nr.: [...]
Debitor-Kto. von [...] bis [...]
Vollständige Ablieferung / Hoflagerung beim Erzeuger / Berichtigung / Nachmeldung
Anzahl: 1
Formular: W12151
Drucker: Groothusen/Kyocera M3540dn Fach 1'
),
(
    '7d06a5c2-7e00-4eb1-9a8a-000000000005',
    '12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg',
    'NaWaRo-Verträge',
    'de',
    'en',
    'NaWaRo-Verträge
Erntejahr: 2025
Artikel-Nr.: [...]
Sommer/Winter
Vertrag-Nr. | Kundenname | Name 1 | Ges. Fläche | Standard-Menge | Anz. Lief. | Liefermittel | Menge B. | Ernteerklärung'
),
(
    '7d06a5c2-7e00-4eb1-9a8a-000000000006',
    'E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg',
    'NaWaRo-Anbauflächen',
    'de',
    'en',
    'NaWaRo-Anbauflächen
Erntejahr von 2022 bis 2026
Artikel-Nr.: [...]
Sommer/Winter
Kundenname | Name 1 | Name 2 | PLZ | Ort | Telefon | Telefax
Summen Flächen: 2022, 2023, 2024, 2025, 2026
Formular: W12071
Aktionen: Drucken, Serienbrief erstellen'
)
ON CONFLICT (screenshot_file) DO UPDATE SET
    title = EXCLUDED.title,
    raw_markdown = EXCLUDED.raw_markdown;

DELETE FROM domain_ops.zvoove_ocr_screen_fields
WHERE screenshot_file IN (
    '1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg',
    '31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg',
    '8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg',
    'FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg',
    '12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg',
    'E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg'
);

INSERT INTO domain_ops.zvoove_ocr_screen_fields (id, screenshot_file, section_name, field_label, field_order)
VALUES
('8e06a5c2-7e00-4eb1-9a8a-000000000001','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Dokument',1),
('8e06a5c2-7e00-4eb1-9a8a-000000000002','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Ernte-Jahr',2),
('8e06a5c2-7e00-4eb1-9a8a-000000000003','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Artikel-Nr.',3),
('8e06a5c2-7e00-4eb1-9a8a-000000000004','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Debitor-Kto. von',4),
('8e06a5c2-7e00-4eb1-9a8a-000000000005','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Debitor-Kto. bis',5),
('8e06a5c2-7e00-4eb1-9a8a-000000000006','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Vollständige Ablieferung',6),
('8e06a5c2-7e00-4eb1-9a8a-000000000007','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Hoflagerung beim Erzeuger',7),
('8e06a5c2-7e00-4eb1-9a8a-000000000008','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Berichtigung',8),
('8e06a5c2-7e00-4eb1-9a8a-000000000009','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Nachmeldung',9),
('8e06a5c2-7e00-4eb1-9a8a-000000000010','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Formular',10),
('8e06a5c2-7e00-4eb1-9a8a-000000000011','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Anzahl',11),
('8e06a5c2-7e00-4eb1-9a8a-000000000012','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','nawaro_mitteilung','Aktueller Drucker',12),

('8e06a5c2-7e00-4eb1-9a8a-000000000013','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Dokument',1),
('8e06a5c2-7e00-4eb1-9a8a-000000000014','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Ernte-Jahr',2),
('8e06a5c2-7e00-4eb1-9a8a-000000000015','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Artikel-Nr.',3),
('8e06a5c2-7e00-4eb1-9a8a-000000000016','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Debitor-Kto. von',4),
('8e06a5c2-7e00-4eb1-9a8a-000000000017','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Debitor-Kto. bis',5),
('8e06a5c2-7e00-4eb1-9a8a-000000000018','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Vollständige Ablieferung',6),
('8e06a5c2-7e00-4eb1-9a8a-000000000019','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Hoflagerung beim Erzeuger',7),
('8e06a5c2-7e00-4eb1-9a8a-000000000020','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Berichtigung',8),
('8e06a5c2-7e00-4eb1-9a8a-000000000021','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Nachmeldung',9),
('8e06a5c2-7e00-4eb1-9a8a-000000000022','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Formular',10),
('8e06a5c2-7e00-4eb1-9a8a-000000000023','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','nawaro_mitteilung','Anzahl',11),

('8e06a5c2-7e00-4eb1-9a8a-000000000024','8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg','nawaro_mitteilung_kurz','Vollständige Ablieferung',1),
('8e06a5c2-7e00-4eb1-9a8a-000000000025','8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg','nawaro_mitteilung_kurz','Hoflagerung beim Erzeuger',2),
('8e06a5c2-7e00-4eb1-9a8a-000000000026','8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg','nawaro_mitteilung_kurz','Berichtigung',3),
('8e06a5c2-7e00-4eb1-9a8a-000000000027','8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg','nawaro_mitteilung_kurz','Nachmeldung',4),
('8e06a5c2-7e00-4eb1-9a8a-000000000028','8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg','nawaro_mitteilung_kurz','Anzahl',5),
('8e06a5c2-7e00-4eb1-9a8a-000000000029','8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg','nawaro_mitteilung_kurz','Drucker',6),
('8e06a5c2-7e00-4eb1-9a8a-000000000030','8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg','nawaro_mitteilung_kurz','Drucken',7),
('8e06a5c2-7e00-4eb1-9a8a-000000000031','8114F263-44B0-4476-9B38-18CD48C1FCE7.jpeg','nawaro_mitteilung_kurz','Vorschau',8),

('8e06a5c2-7e00-4eb1-9a8a-000000000032','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Artikel-Nr.',1),
('8e06a5c2-7e00-4eb1-9a8a-000000000033','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Debitor-Kto. von',2),
('8e06a5c2-7e00-4eb1-9a8a-000000000034','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Debitor-Kto. bis',3),
('8e06a5c2-7e00-4eb1-9a8a-000000000035','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Vollständige Ablieferung',4),
('8e06a5c2-7e00-4eb1-9a8a-000000000036','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Hoflagerung beim Erzeuger',5),
('8e06a5c2-7e00-4eb1-9a8a-000000000037','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Berichtigung',6),
('8e06a5c2-7e00-4eb1-9a8a-000000000038','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Nachmeldung',7),
('8e06a5c2-7e00-4eb1-9a8a-000000000039','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Anzahl',8),
('8e06a5c2-7e00-4eb1-9a8a-000000000040','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Formular',9),
('8e06a5c2-7e00-4eb1-9a8a-000000000041','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','nawaro_mitteilung_formular','Drucker',10),

('8e06a5c2-7e00-4eb1-9a8a-000000000042','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Erntejahr',1),
('8e06a5c2-7e00-4eb1-9a8a-000000000043','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Artikel-Nr.',2),
('8e06a5c2-7e00-4eb1-9a8a-000000000044','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Sommer',3),
('8e06a5c2-7e00-4eb1-9a8a-000000000045','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Winter',4),
('8e06a5c2-7e00-4eb1-9a8a-000000000046','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Vertrag-Nr.',5),
('8e06a5c2-7e00-4eb1-9a8a-000000000047','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Kundenname',6),
('8e06a5c2-7e00-4eb1-9a8a-000000000048','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Name 1',7),
('8e06a5c2-7e00-4eb1-9a8a-000000000049','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Ges. Fläche',8),
('8e06a5c2-7e00-4eb1-9a8a-000000000050','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Standard-Menge',9),
('8e06a5c2-7e00-4eb1-9a8a-000000000051','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Anz. Lief.',10),
('8e06a5c2-7e00-4eb1-9a8a-000000000052','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Liefermittel',11),
('8e06a5c2-7e00-4eb1-9a8a-000000000053','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Menge B.',12),
('8e06a5c2-7e00-4eb1-9a8a-000000000054','12EDB82D-A1C0-4BC1-A2FB-91AD3D0391D9.jpeg','nawaro_vertraege','Ernteerklärung',13),

('8e06a5c2-7e00-4eb1-9a8a-000000000055','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Erntejahr von',1),
('8e06a5c2-7e00-4eb1-9a8a-000000000056','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Erntejahr bis',2),
('8e06a5c2-7e00-4eb1-9a8a-000000000057','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Artikel-Nr.',3),
('8e06a5c2-7e00-4eb1-9a8a-000000000058','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Sommer',4),
('8e06a5c2-7e00-4eb1-9a8a-000000000059','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Winter',5),
('8e06a5c2-7e00-4eb1-9a8a-000000000060','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Kundenname',6),
('8e06a5c2-7e00-4eb1-9a8a-000000000061','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Name 1',7),
('8e06a5c2-7e00-4eb1-9a8a-000000000062','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Name 2',8),
('8e06a5c2-7e00-4eb1-9a8a-000000000063','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','PLZ',9),
('8e06a5c2-7e00-4eb1-9a8a-000000000064','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Ort',10),
('8e06a5c2-7e00-4eb1-9a8a-000000000065','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Telefon',11),
('8e06a5c2-7e00-4eb1-9a8a-000000000066','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Telefax',12),
('8e06a5c2-7e00-4eb1-9a8a-000000000067','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Summen Flächen 2022',13),
('8e06a5c2-7e00-4eb1-9a8a-000000000068','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Summen Flächen 2023',14),
('8e06a5c2-7e00-4eb1-9a8a-000000000069','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Summen Flächen 2024',15),
('8e06a5c2-7e00-4eb1-9a8a-000000000070','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Summen Flächen 2025',16),
('8e06a5c2-7e00-4eb1-9a8a-000000000071','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Summen Flächen 2026',17),
('8e06a5c2-7e00-4eb1-9a8a-000000000072','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Formular',18),
('8e06a5c2-7e00-4eb1-9a8a-000000000073','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Drucken',19),
('8e06a5c2-7e00-4eb1-9a8a-000000000074','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','nawaro_anbauflaechen','Serienbrief erstellen',20);

DELETE FROM domain_ops.zvoove_print_form_templates
WHERE screenshot_file IN (
    '1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg',
    '31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg',
    'FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg',
    'E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg'
);

INSERT INTO domain_ops.zvoove_print_form_templates (id, screenshot_file, form_code, form_name, enabled_by_default)
VALUES
('9f06a5c2-7e00-4eb1-9a8a-000000000001','1E2B9B74-1208-4373-B9A3-C8F43F1F6E5A.jpeg','W12151','Ernteerklärung zum Anbau nachwachsender Rohstoffe',TRUE),
('9f06a5c2-7e00-4eb1-9a8a-000000000002','31F312EC-E9FD-4C84-B297-C05D4CB81FAA.jpeg','W12151','Mitteilung des Aufkäufers über die Lieferung',TRUE),
('9f06a5c2-7e00-4eb1-9a8a-000000000003','FDC938FF-9BE6-4518-8C33-0D8197797170.jpeg','W12151','NaWaRo-Mitteilung Formular',TRUE),
('9f06a5c2-7e00-4eb1-9a8a-000000000004','E18B7209-FE91-46D0-BE18-B1F54EB37526.jpeg','W12071','NaWaRo-Anbauflächen',TRUE);
"@

$sql | docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1

Write-Host "Seed completed: zvoove OCR part 2 (screens, fields, print templates)"
