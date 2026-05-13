# Deutsches HRM-Zielsystem und Gap-Plan

Stand: 2026-05-13

## Zweck

Dieses Dokument erweitert die bestehende HR-Time-Roadmap zu einem vollstaendigen
HRM-Betriebssystem fuer deutsche Buero- und ERP-Anwendungen.

HR-Time bleibt der belastbare Kern fuer Arbeitszeit, Abwesenheiten, Schicht,
Kalender, Fahrerzeit und Payroll-Readiness. Fuer ein modernes HRM-System fehlen
darueber hinaus Personalakte, eAU, Vertrags- und Dokumentenprozesse, Employee
Self Service, Manager Self Service, Recruiting, Performance, People Analytics,
Datenschutz-Governance, kontrollierte KI und Office-Connectoren.

Der maschinenlesbare Zielvertrag liegt in:

- `GET /api/v1/personal/hrm-readiness`

## Rechts- und Compliance-Anker

Diese Liste ist keine Rechtsberatung. Sie definiert die fachlichen
Mindestanker, gegen die Umsetzungsslices pruefbar bleiben muessen.

| Thema | Anker | Konsequenz fuer VALEO |
|-------|-------|-----------------------|
| Beschaeftigtendaten | BDSG Paragraph 26, DSGVO | Verarbeitung nur zweckgebunden und erforderlich; Rollen, Audit, Export und Loeschkonzept sind Pflicht. |
| Arbeitszeiterfassung | BAG 1 ABR 22/21, ArbSchG Paragraph 3 Abs. 2 Nr. 1 | Beginn und Ende der taeglichen Arbeitszeit muessen systematisch erfassbar sein. |
| eAU | SGB IV Paragraph 109 | Krankmeldung, eAU-Abfrage, Krankenkassen-Rueckmeldung, Fristen und Fehlerstatus brauchen einen eigenen Prozess. |
| Payroll | GoBD, Entgeltabrechnungs- und SV-Meldeprozesse | VALEO bereitet Payroll vor; das SV-Meldeportal ersetzt kein Entgeltabrechnungsprogramm. |
| Nachweise | Nachweisgesetz 2025 Textform-Ausbau | Digitale Nachweise sind weiter an Ausnahmen, Schriftformwuensche, Empfang und Archivierung gebunden. |
| KI im HR | EU AI Act, insbesondere Beschaeftigung/Personalmanagement als Hochrisikobereich | KI darf assistieren, aber nicht unkontrolliert entscheiden; Recruiting-/Bewertungs-KI braucht Governance. |
| Betriebsratsfaehigkeit | BetrVG-Mitbestimmung und Transparenz | Keine verdeckte Leistungsueberwachung; Auswertungen muessen transparent und begrenzt sein. |

## Mindest-Checkliste

| Nr. | Faehigkeit | VALEO-Status | Ziel-Slice |
|-----|------------|--------------|------------|
| 1 | Digitale Personalakte | Contract umgesetzt | `HRM-AKTE-001` |
| 2 | DSGVO-konformes Rechte- und Loeschkonzept | Teilweise | `HRM-PRIVACY-001` |
| 3 | Arbeitszeiterfassung | Umgesetzt | `HR-TIME-RULES-001` fuer Feinkalibrierung |
| 4 | Urlaubs- und Abwesenheitsmanagement | Umgesetzt als Contract | `HR-TIME-ABS-CONNECTOR-001` |
| 5 | eAU-Prozess | Gap | `HRM-EAU-001` |
| 6 | Payroll-/DATEV-Schnittstelle | Teilweise | `HRM-DATEV-001` |
| 7 | Vertrags- und Dokumentenvorlagen | Gap | `HRM-CONTRACTS-001` |
| 8 | Employee Self Service | Teilweise | `HRM-ESS-001` |
| 9 | Manager Self Service | Teilweise | `HRM-MSS-001` |
| 10 | Recruiting und Bewerbermanagement | Gap | `HRM-RECRUITING-001` |
| 11 | Onboarding und Offboarding | Teilweise | `HRM-OFFBOARDING-001` |
| 12 | Workflows mit Freigaben | Teilweise | `HRM-WORKFLOWS-001` |
| 13 | Reporting und HR-Dashboards | Teilweise | `HRM-ANALYTICS-001` |
| 14 | Microsoft-365-, LibreOffice- und Google-Workspace-Integration | Gap | `HRM-M365-001`, `HRM-GOOGLE-001`, `HRM-LIBREOFFICE-001` |
| 15 | Sichere KI-Funktionen mit menschlicher Kontrolle | Gap | `HRM-AI-GOV-001` |

## Gap-Matrix

| Bereich | Bestehender Stand | Gap | Zielbild |
|---------|-------------------|-----|----------|
| Personalakte | Mitarbeiterliste, HR-Time-Profile und erster Personalakten-Contract existieren. | Produktive DMS-Ablage, DB-Migration, echte Signaturen und rechtlich freigegebene Retention-Fristen fehlen noch. | Akte mit Dokumentklassen, Rollenrechten, Fristen, Audit, Export und Loeschlauf. |
| eAU | Krankheit kann als Abwesenheit importiert werden. | Kein Arbeitgeberverfahren mit Abfrage, Rueckmeldung, Fristen und Statuscodes. | eAU-Workflow mit minimaler Speicherung, ohne Diagnosedaten. |
| Payroll/DATEV | Payroll-Exports und Readiness existieren. | Kein verbindliches DATEV-/Steuerberater-Zielformat, keine vollstaendigen Bewegungsdaten. | Monatsabschluss mit Lohnarten, Zuschlaegen, Fehlzeiten, Sachbezuegen, Kostenstellen und Auditpaket. |
| Dokumente und Verträge | Onboarding-Checklisten existieren. | Keine Vorlagenbibliothek, Textform-/Schriftformlogik, E-Signatur oder DMS-Akte. | Vertrags- und Nachweisprozess mit Vorlagenversion, Empfang, Signaturstatus und Archivierung. |
| ESS/MSS | Zeit- und Planungsfunktionen sind vorhanden. | Keine durchgaengigen Mitarbeiter- und Manager-Self-Service-Portale. | Mitarbeiter koennen Daten, Dokumente, Zeiten, Krankmeldungen und Bescheinigungen steuern; Manager sehen Teamkalender, Freigaben und Headcount. |
| Recruiting/Performance | Onboarding und Qualifikationen sind angebunden. | Bewerbermanagement, Talentpool, Zielvereinbarungen, Feedback, Nachfolge fehlen. | Getrennter Bewerberkontext mit Loeschfristen, Interviewplanung, Entwicklung und Skill-Matrix. |
| People Analytics | Time-Cockpit liefert operative KPIs. | HR-weite KPIs, Aggregationsgrenzen, DSFA-Workflow und Betriebsratsfaehigkeit fehlen. | Dashboards fuer Headcount, Fluktuation, Krankenstand, Resturlaub, Ueberstunden, Kosten und Weiterbildung ohne heimliche Leistungsueberwachung. |
| KI | NeuroASSIST-Muster existieren systemweit. | HR-spezifische AI-Governance fehlt. | Assistive KI nur mit Human-Gate, Protokollierung, Transparenz und Hochrisiko-Pruefung. |
| Office-Connectoren | Kalendervertrag ist provider-neutral. | Echte Microsoft-365-, Google-Workspace-, LibreOffice-, DMS- und E-Signatur-Connectoren fehlen. | Connectoren mit SSO, OAuth-Scopes, Busy-only Datenschutz, Dokumentvorlagen und Audit. |

## Zielarchitektur

```text
Keycloak / Entra ID / Google Directory
  |
  +-- HRM Core (/api/v1/personal)
  |     - Mitarbeiter
  |     - Digitale Personalakte
  |     - eAU
  |     - ESS / MSS
  |     - HR-Workflows
  |
  +-- HR-Time
  |     - Zeitbuchung
  |     - Abwesenheit
  |     - Schicht / Kalender / Driver-Time
  |     - Payroll-Readiness
  |
  +-- Dokumente
  |     - DMS
  |     - LibreOffice Templates
  |     - E-Signatur
  |
  +-- Payroll / DATEV / Steuerbuero
  |
  +-- Microsoft 365 / Google Workspace
```

## KI-Governance

Erlaubt als assistive Funktionen:

- Stellenanzeigen entwerfen
- Dokumente suchen und zusammenfassen
- HR-Chatbot mit Quellenangabe
- Lernempfehlungen und Skill-Matching als Vorschlag

Nicht erlaubt:

- automatische Ablehnung von Bewerbungen ohne menschliche Aufsicht
- Blackbox-Bewertung von Mitarbeitenden
- Emotionserkennung am Arbeitsplatz
- verdeckte Leistungsueberwachung

Pflichtkontrollen fuer Hochrisiko-Kontexte:

- Risikomanagement
- Datenqualitaet
- technische Dokumentation
- Protokollierung
- Transparenz fuer Betroffene
- menschliche Aufsicht
- Robustheit und Cybersecurity

## Naechste Slices

| Slice | Ziel | Abnahme |
|-------|------|---------|
| `HRM-AKTE-001` | Digitale Personalakte mit Dokumentklassen, Fristen und Audit. | Erster Contract umgesetzt: `GET /api/v1/personal/employee-files/{employee_ref}` und `POST /api/v1/personal/employee-files/{employee_ref}/documents`. |
| `HRM-AKTE-DB-001` | Persistente Personalakten-Migration und DMS-Anbindung. | `domain_hr.employee_file_documents` ist migriert, DMS-Referenzen werden produktiv validiert. |
| `HRM-EAU-001` | eAU-Prozessvertrag. | Krankmeldung, Abfrage, Rueckmeldung, Frist und Fehlerstatus sind API-seitig sichtbar. |
| `HRM-DATEV-001` | DATEV-/Steuerberater-Zielformat. | Exportpaket enthaelt Lohnarten, Fehlzeiten, Kostenstellen und Monatsabschlussprotokoll. |
| `HRM-CONTRACTS-001` | Vertrags- und Nachweisvorlagen. | Vorlage, Textform-/Schriftformentscheidung, E-Signaturstatus und Archiv-Ref sind dokumentiert. |
| `HRM-ESS-001` | Employee Self Service. | Mitarbeitende koennen Zeiten, Abwesenheiten, Datenantraege und Dokumentabrufe starten. |
| `HRM-MSS-001` | Manager Self Service. | Manager erhalten Teamkalender, Freigaben, Probezeit- und Headcount-Sicht. |
| `HRM-RECRUITING-001` | Bewerbermanagement. | Bewerberdaten besitzen Zweck, Status, Talentpool-Einwilligung und Loeschfrist. |
| `HRM-ANALYTICS-001` | People Analytics. | Dashboards nutzen Aggregationsschwellen und zeigen keine Einzel-Leistungsueberwachung. |
| `HRM-AI-GOV-001` | HR-KI-Governance. | KI-Funktionen sind klassifiziert, protokolliert und mit Human-Gate versehen. |
| `HRM-M365-001` | Microsoft 365 Connector. | SSO, Teams, Outlook-Kalender und Busy-only Datenschutz sind als Contract verfuegbar. |
| `HRM-GOOGLE-001` | Google Workspace Connector. | Directory- und Kalender-Mapping mit OAuth-Scopes und Busy-only Datenschutz. |
| `HRM-LIBREOFFICE-001` | LibreOffice Template Connector. | ODT/DOCX-Vorlagen koennen mit HR-Daten zu PDF-Nachweisen gerendert werden. |

## Quellenstand

Geprueft am 2026-05-13:

- BDSG Paragraph 26: https://www.gesetze-im-internet.de/bdsg_2018/__26.html
- SGB IV Paragraph 109: https://www.gesetze-im-internet.de/sgb_4/__109.html
- BAG 1 ABR 22/21: https://www.bundesarbeitsgericht.de/entscheidung/1-abr-22-21/
- EU AI Act Annex III / Beschaeftigung: https://artificialintelligenceact.eu/annex/3/

## Umsetzungsstand HRM-AKTE-001

Stand 2026-05-13:

- `GET /api/v1/personal/employee-files/{employee_ref}` liefert Aktenmetadaten, Dokumentklassen, Rollenfilter, Exportpaket und Retention-Sicht.
- `POST /api/v1/personal/employee-files/{employee_ref}/documents` nimmt Dokumentmetadaten mit Dokumentklasse, DMS-Referenz, Sichtbarkeit, Ausstellungsdatum und Audit-Ref an.
- Dokumentklassen: Arbeitsvertrag, Payroll-Dokument, Zertifikat, Abwesenheitsnachweis, Datenschutz-/Verpflichtungsnachweis und Abmahnung/Personalnotiz.
- Rollenfilter: `employee`, `manager`, `hr`, `payroll`, `admin`; HR/Admin sehen alles, Payroll nur Payroll/Employee-Sicht, Manager nur Manager/Employee-Sicht, Employee nur Employee-Sicht.
- Retention bleibt ein Contract-Hinweis, keine automatische Loeschung.

Nicht erledigt in HRM-AKTE-001:

- produktive DB-Migration fuer `domain_hr.employee_file_documents`
- Upload/Download ins DMS
- E-Signatur
- rechtlich final freigegebene Aufbewahrungsfristen je Dokumentklasse
- echte DSGVO-Auskunfts- und Loeschlauf-Ausfuehrung
