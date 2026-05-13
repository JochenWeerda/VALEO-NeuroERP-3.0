# HRM Go-live Templates

Stand: 2026-05-13

Dieses Verzeichnis enthaelt operative Mustervorlagen fuer die HRM-Betriebsfreigaben von VALEO NeuroERP.

Die Vorlagen dienen als Arbeitsmuster fuer HR, Payroll, IT, Datenschutz, Legal, Geschaeftsfuehrung und gegebenenfalls Betriebsrat. Sie ersetzen keine Rechtsberatung, Datenschutzberatung oder steuerliche Beratung.

## Vorlagen

| Datei | Zweck |
|---|---|
| `00_hrm_go_live_gesamtwerk.md` | Gesamtpaket mit Gate-Matrix, Freigabeprotokollen, Prueflisten und Evidence-/Auditvorlagen. |
| `01_hrm_go_live_freigabeprotokoll.md` | Management- und Go-live-Entscheidung fuer HRM. |
| `02_betriebsratsstatus_kein_betriebsrat.md` | Erklaerung, falls kein Betriebsrat besteht. |
| `03_mitarbeiterinformation_hrm.md` | Verstaendliche Mitarbeiterinformation zum realen HRM-Funktionsumfang. |
| `04_vvt_hrm_system.md` | Vorlage fuer das Verzeichnis der Verarbeitungstaetigkeit. |
| `05_avv_dpa_pruefprotokoll.md` | AVV-/DPA-Pruefung fuer Anbieter und Auftragsverarbeiter. |
| `06_dsfa_vorpruefung.md` | Datenschutz-Folgenabschaetzungs-Vorpruefung. |
| `07_rollen_berechtigungskonzept.md` | Rollen, Berechtigungen und Rezertifizierung. |
| `08_tom_it_sicherheitsfreigabe.md` | TOM- und IT-Sicherheitsfreigabe. |
| `09_retention_loeschkonzept.md` | Aufbewahrungs-, Sperr- und Loeschregeln. |
| `10_eau_freigabeprotokoll.md` | eAU-Kommunikationszugang und Krankenkassen-Testverfahren. |
| `11_datev_payroll_abnahme.md` | DATEV-/Payroll-Testexport und Steuerberaterfreigabe. |
| `12_office_sso_abnahme.md` | Microsoft 365, Google Workspace und SSO. |
| `13_dms_esignatur_rendering_abnahme.md` | LibreOffice-Rendering, DMS und E-Signatur. |
| `14_ki_assistenz_reporting_freigabe.md` | HR-Reporting und optional konkret freigegebene KI-Assistenz. |
| `15_evidence_auditprotokoll.md` | Evidence-Artefakt und Auditspur. |
| `16_geschaeftsfuehrungsfreigabe.md` | Entscheidungsvorlage fuer die Geschaeftsfuehrung. |
| `17_betriebsvereinbarung_optional.md` | Optionale Betriebsvereinbarung, falls ein Betriebsrat besteht. |

## Abgedeckte Gates

1. eAU-Kommunikationszugang und Krankenkassen-Testverfahren
2. DATEV-/Payroll-Zielformat und Steuerberaterfreigabe
3. Microsoft 365, Google Workspace und SSO
4. LibreOffice-Rendering, DMS und E-Signatur
5. AVV/DPA, Hosting, Subprozessoren und Datenexport
6. Betriebsrat, DSFA, HR-Reporting und optional freigegebene KI-Assistenz
7. Rechtsfreigabe fuer Retention und Dokumentklassen

## Nutzung

1. Gesamtwerk je Release kopieren oder in ein DMS ueberfuehren.
2. Platzhalter ausfuellen und pro Gate echte Evidence verlinken.
3. Freigaben durch die jeweils verantwortlichen Rollen einholen.
4. Blocker im HRM-Betriebsfreigaben-Cockpit nachhalten.
5. Produktivstart erst freigeben, wenn alle blockierenden Gates nachweisbar abgenommen sind.

## Pflegehinweis

`00_hrm_go_live_gesamtwerk.md` ist der fachliche Master. Die Einzeldateien sind Arbeitsauszuege fuer die operative Verwendung. Inhaltliche Aenderungen sollten zuerst im Master nachvollzogen und danach in den betroffenen Einzelvorlagen nachgezogen werden.
