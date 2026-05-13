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
- `GET /api/v1/personal/hrm-operating-system`
- `GET /api/v1/personal/hrm-operations-gates`

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
| 2 | DSGVO-konformes Rechte- und Loeschkonzept | Contract umgesetzt | `HRM-PRIVACY-001` |
| 3 | Arbeitszeiterfassung | Umgesetzt | `HR-TIME-RULES-001` fuer Feinkalibrierung |
| 4 | Urlaubs- und Abwesenheitsmanagement | Umgesetzt als Contract | `HR-TIME-ABS-CONNECTOR-001` |
| 5 | eAU-Prozess | Contract umgesetzt | `HRM-EAU-001` |
| 6 | Payroll-/DATEV-Schnittstelle | Contract umgesetzt | `HRM-DATEV-001` |
| 7 | Vertrags- und Dokumentenvorlagen | Contract umgesetzt | `HRM-CONTRACTS-001` |
| 8 | Employee Self Service | Contract umgesetzt | `HRM-ESS-001` |
| 9 | Manager Self Service | Contract umgesetzt | `HRM-MSS-001` |
| 10 | Recruiting und Bewerbermanagement | Contract umgesetzt | `HRM-RECRUITING-001` |
| 11 | Onboarding und Offboarding | Contract umgesetzt | `HRM-OFFBOARDING-001` |
| 12 | Workflows mit Freigaben | Contract umgesetzt | `HRM-WORKFLOWS-001` |
| 13 | Reporting und HR-Dashboards | Contract umgesetzt | `HRM-ANALYTICS-001` |
| 14 | Microsoft-365-, LibreOffice- und Google-Workspace-Integration | Contract umgesetzt | `HRM-M365-001`, `HRM-GOOGLE-001`, `HRM-LIBREOFFICE-001` |
| 15 | Sichere KI-Funktionen mit menschlicher Kontrolle | Contract umgesetzt | `HRM-AI-GOV-001` |

## Gap-Matrix

| Bereich | Bestehender Stand | Gap | Zielbild |
|---------|-------------------|-----|----------|
| Personalakte | Mitarbeiterliste, HR-Time-Profile und Personalakten-Contract existieren. | Kein fachlicher Repo-Gap; produktive DMS-/DB-/Signaturfreigabe bleibt external gate. | Akte mit Dokumentklassen, Rollenrechten, Fristen, Audit, Export und Loeschlauf. |
| eAU | Contract ist im HRM-Betriebssystem sichtbar; Krankheit bleibt Abwesenheit in `time_entries`. | Kein fachlicher Repo-Gap; produktiver eAU-Kommunikationszugang bleibt external gate. | eAU-Workflow mit minimaler Speicherung, ohne Diagnosedaten. |
| Payroll/DATEV | Payroll-Exports, Readiness und Operating-System-Closeout existieren. | Kein fachlicher Repo-Gap; DATEV-Zielformat und Steuerberaterfreigabe bleiben external gate. | Monatsabschluss mit Lohnarten, Zuschlaegen, Fehlzeiten, Sachbezuegen, Kostenstellen und Auditpaket. |
| Dokumente und Verträge | Personalakte und HRM-Betriebssystemvertrag fuehren Vorlagen, Archiv-Ref und Signaturstatus. | Kein fachlicher Repo-Gap; LibreOffice-Rendering und E-Signatur-Anbieter bleiben external gate. | Vertrags- und Nachweisprozess mit Vorlagenversion, Empfang, Signaturstatus und Archivierung. |
| ESS/MSS | Self-Service-Funktionen sind ueber Akte, Zeit, Work-Plan und Time-Cockpit vertraglich geschlossen. | Kein fachlicher Repo-Gap; SSO-Rollen und Betriebsvereinbarung bleiben external gate. | Mitarbeiter koennen Daten, Dokumente, Zeiten, Krankmeldungen und Bescheinigungen steuern; Manager sehen Teamkalender, Freigaben und Headcount. |
| Recruiting/Performance | Training, Onboarding, Qualifikationen und HRM-Operating-System-Contract decken Retention, Talentpool und Human-in-the-loop ab. | Kein fachlicher Repo-Gap; Karriereseite und Interviewkommunikation bleiben external gate. | Getrennter Bewerberkontext mit Loeschfristen, Interviewplanung, Entwicklung und Skill-Matrix. |
| People Analytics | Readiness und Operating-System-Contract erzwingen Aggregationsschwellen, DSFA und Betriebsratsfaehigkeit. | Kein fachlicher Repo-Gap; DSFA- und Betriebsratsfreigaben bleiben external gate. | Dashboards fuer Headcount, Fluktuation, Krankenstand, Resturlaub, Ueberstunden, Kosten und Weiterbildung ohne heimliche Leistungsueberwachung. |
| KI | HR-spezifische AI-Governance ist als Contract mit Human-Gate, Hochrisiko-Klassifizierung und Verbot Emotionserkennung geschlossen. | Kein fachlicher Repo-Gap; konkrete AI-Act-Konformitaetspruefung je Tool bleibt external gate. | Assistive KI nur mit Human-Gate, Protokollierung, Transparenz und Hochrisiko-Pruefung. |
| Office-Connectoren | Kalendercontract und Operating-System-Contract decken Microsoft 365, Google Workspace, LibreOffice, DMS und E-Signatur ab. | Kein fachlicher Repo-Gap; produktive Tenant-Secrets und AVV/DPA bleiben external gate. | Connectoren mit SSO, OAuth-Scopes, Busy-only Datenschutz, Dokumentvorlagen und Audit. |

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
| `HRM-GAP-CLOSURE-001` | Alle fachlichen Repo-Gaps im HRM-Plan schliessen. | Umgesetzt: `GET /api/v1/personal/hrm-operating-system` weist alle Module als `contract_complete` aus. |
| `HRM-OPERATIONS-GATES-001` | Externe Betriebsfreigaben professionell abschliessen. | Umgesetzt: `GET /api/v1/personal/hrm-operations-gates` fuehrt Evidenz, Owner, Go-live-Blocker, Abnahme und Auditspur je Gate. |

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

## Umsetzungsstand HRM-GAP-CLOSURE-001

Stand 2026-05-13:

- `GET /api/v1/personal/hrm-operating-system` schliesst alle fachlichen Repo-Gaps aus diesem Plan als `contract_complete`.
- Der Contract deckt eAU, DATEV/Payroll-Closeout, Vertragsvorlagen, ESS, MSS, Recruiting/Entwicklung, Analytics/Privacy, AI-Governance und Office-Connectoren ab.
- HR-Time-Modellregeln sind festgeschrieben:
  - Tabellenname `domain_hr.time_entries`
  - Datumsspalte `entry_date`
  - Stundenfeld `hours`
  - Abwesenheiten ueber `entry_type IN ('Urlaub','Krank','Unbezahlt','Sonstiges')`
  - keine separate `time_bookings`- oder `absences`-Tabelle
  - Schreibpfade mit `RETURNING`

Keine fachlichen Repo-Gaps bleiben in diesem Plan offen. Verbleibende Punkte sind externe Betriebsfreigaben und werden ueber `GET /api/v1/personal/hrm-operations-gates` als Go-live-Gates gefuehrt:

- echte eAU-/DATEV-/Microsoft-/Google-/LibreOffice-/E-Signatur-Zugangsdaten
- AVV/DPA, Hostingort und Subprozessoren
- Betriebsvereinbarungen
- DSFA fuer risikoreiche Auswertungen oder KI-Funktionen
- Rechtsfreigabe konkreter Retention- und Dokumentklassen

## Umsetzungsstand HRM-OPERATIONS-GATES-001

Stand 2026-05-13:

- `GET /api/v1/personal/hrm-operations-gates` fuehrt alle externen Betriebsfreigaben als strukturierte Gates.
- Go-live bleibt blockiert, solange ein blockierendes Gate nicht `approved` ist.
- Jedes Gate besitzt Owner-Rolle, Evidenzanforderungen, Abnahmekriterien, Auditspur und Professional-Practice-Regeln.
- `HRM-OPERATIONS-GATES-002` ergaenzt die technische Workflow-Schicht:
  - Alembic-Migration `hrm_operations_gates_20260513` fuer `domain_hr.hrm_operations_gates`, `hrm_operations_gate_evidence`, `hrm_operations_gate_probes` und `hrm_operations_gate_audit`
  - `POST /api/v1/personal/hrm-operations-gates/{gate_id}/evidence`
  - `POST /api/v1/personal/hrm-operations-gates/{gate_id}/probe`
  - `POST /api/v1/personal/hrm-operations-gates/{gate_id}/decision`
  - `GET /api/v1/personal/hrm-operations-gates/go-live-policy`
- Der statische Gate-Katalog ist nur noch Seed/Fallback. Produktivstatus, Evidence, Probe-Ergebnisse, Approval/Reject und Go-live-Policy werden tenant-spezifisch persistent gefuehrt.

| Gate | Owner | Abschlussdefinition |
|------|-------|---------------------|
| eAU-Kommunikation | HR/Ops | eAU-Zugang, Testverfahren, Status-/Fehlerprotokoll und Nachweis ohne Diagnosedaten. |
| DATEV/Payroll | Payroll/Finance | Zielformat, Testexport, Lohnarten/Kostenstellen/Fehlzeiten und Steuerberaterfreigabe. |
| Office/SSO | IT/Ops | Tenant, OAuth-Scopes, MFA/SSO-Rollen, Busy-only Kalenderdatenschutz und Connector-Probe. |
| LibreOffice/DMS/E-Signatur | HR/Ops/Legal | Vorlagenversion, DMS-Ablage, Signaturstatus, Archiv-Ref und AVV/DPA. |
| Privacy/Vendor | Datenschutz/Ops | AVV/DPA, Hostingort, Subprozessoren, Export und Loeschprozess. |
| Betriebsrat/DSFA/KI | HR/Datenschutz/Betriebsrat | Mitbestimmung, DSFA, keine verdeckte Leistungsueberwachung, Human-Gate fuer KI. |
| Retention Legal | Legal/HR | Freigegebene Dokumentklassen, Aufbewahrungsfristen, Zweckfortfall und Loeschblocker. |

Damit ist auch das Verbleibende fachlich abgeschlossen: Es gibt keine unspezifizierten Restpunkte mehr, sondern nur noch blockierende, evidenzbasierte Betriebsfreigaben.

Technischer Abschluss 2026-05-13:

- Repo-seitig sind die Gates nicht mehr nur dokumentiert, sondern als steuerbarer Workflow implementiert.
- Produktive externe Zugangsdaten und reale Rechts-/Betriebsratsfreigaben bleiben notwendige Betriebsnachweise; ohne sie koennen Gates nicht fachlich `approved` werden.
