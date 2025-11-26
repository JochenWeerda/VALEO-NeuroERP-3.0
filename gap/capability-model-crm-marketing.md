***REMOVED*** CRM & Marketing Capability Model (Referenz für GAP-Analyse)

Version: 1.0

Zweck: Referenzmodell zur Funktionsabdeckung in Valero NeuroERP für CRM & Marketing

Baseline: Vollumfängliches CRM/ERP-Niveau (SAP CX/CRM, Oracle CX, Odoo CRM+Marketing, MS Dynamics)

Legende Priorität:

- MUSS = Kern für Vertrieb/Marketingbetrieb

- SOLL = Standard in großen CRM/ERPs

- KANN = nice-to-have / branchenspezifisch

Evidence:

- UI-Screenshots (ID/Dateiname)

- Playwright Traces/Videos

- Flow-IDs aus UI-Explorer JSON

- API/Events (falls vorhanden)

***REMOVED******REMOVED*** 1. Stammdaten & 360° Customer View

***REMOVED******REMOVED******REMOVED*** CRM-ACC-01 Accounts / Firmenstamm

Priorität: MUSS  

Inhalt:

- Firmenstamm, Klassifikation, Status, Owner/Team

- Mehrere Adressen (Rechnung/Lieferung), Länder, USt-ID

Evidence: Account-Create/Edit/History  

Akzeptanz:

- Dublettencheck + Änderungsprotokoll

***REMOVED******REMOVED******REMOVED*** CRM-CON-01 Kontakte / Personenstamm

Priorität: MUSS  

Inhalt:

- Kontakte pro Account, Rollen, Opt-ins

- Kommunikationskanäle, Präferenzen

Evidence: Contact-UI  

Akzeptanz:

- Opt-in/Opt-out sauber dokumentiert

***REMOVED******REMOVED******REMOVED*** CRM-REL-01 Beziehungen & Hierarchien

Priorität: SOLL  

Inhalt:

- Konzernhierarchie, Tochter/Partner/Standorte

Evidence: Relationship-UI  

Akzeptanz:

- Hierarchie in Reports nutzbar

***REMOVED******REMOVED******REMOVED*** CRM-360-01 Customer Timeline / Aktivitätenhistorie

Priorität: SOLL  

Inhalt:

- Alle Interaktionen zeitlich (Email, Call, Meeting, Ticket, Bestellung)

Evidence: Timeline-View  

Akzeptanz:

- Filterbar nach Typ/Datum/Owner

***REMOVED******REMOVED*** 2. Lead Management (Campaign/Lead-to-Opportunity)

***REMOVED******REMOVED******REMOVED*** CRM-LED-01 Lead-Erfassung & Quellen

Priorität: MUSS  

Inhalt:

- Leads manuell, Import, Webform, API

- Quelle, Kampagne, Status

Evidence: Lead-Create + Import  

Akzeptanz:

- Quelle/Kampagne nachvollziehbar

***REMOVED******REMOVED******REMOVED*** CRM-LED-02 Lead-Qualifizierung & Scoring

Priorität: SOLL  

Inhalt:

- Statusmodell (neu/qualifiziert/nurture/unqualifiziert)

- Regelbasiertes Scoring (Fit/Intent)

Evidence: Lead-Scoring UI  

Akzeptanz:

- Score beeinflusst Priorisierung

***REMOVED******REMOVED******REMOVED*** CRM-LED-03 Lead-Routing / Zuweisung

Priorität: SOLL  

Inhalt:

- Zuweisung nach Region/Produkt/Load

- SLA & Eskalation

Evidence: Routing-Regeln  

Akzeptanz:

- Leads landen automatisch im richtigen Team

***REMOVED******REMOVED******REMOVED*** CRM-LED-04 Dedupe & Merge

Priorität: SOLL  

Inhalt:

- Dubletten erkennen/zusammenführen

Evidence: Merge-UI  

Akzeptanz:

- Merge behält Historie/Audit

***REMOVED******REMOVED*** 3. Opportunity & Pipeline

***REMOVED******REMOVED******REMOVED*** CRM-OPP-01 Opportunities / Deals

Priorität: MUSS  

Inhalt:

- Deal mit Stage, Wert, Wahrscheinlichkeit, Close-Date

- Aktivitäten, Anhänge, Notizen

Evidence: Opportunity-Flow  

Akzeptanz:

- Pipeline aggregierbar

***REMOVED******REMOVED******REMOVED*** CRM-OPP-02 Stage-/Process-Templates

Priorität: SOLL  

Inhalt:

- Stage-Modelle je Produkt/Channel

- Pflichtfelder je Stage

Evidence: Stage-Setup  

Akzeptanz:

- Validierung schützt Prozessqualität

***REMOVED******REMOVED******REMOVED*** CRM-OPP-03 Forecasting

Priorität: SOLL/KANN je Unternehmen  

Inhalt:

- Forecast nach Stage/Owner/Periode

Evidence: Forecast-Report  

Akzeptanz:

- Export und periodische Snapshots

***REMOVED******REMOVED******REMOVED*** CRM-OPP-04 Angebots-/Auftragsbezug

Priorität: SOLL  

Inhalt:

- Link Opportunity → Quote/Order/Invoice

Evidence: Cross-Link UI  

Akzeptanz:

- Belegkette drilldown-fähig

***REMOVED******REMOVED*** 4. Aktivitäten & Aufgaben

***REMOVED******REMOVED******REMOVED*** CRM-ACT-01 Aufgaben, Calls, Meetings

Priorität: MUSS  

Inhalt:

- Aufgaben mit Fälligkeit/Reminder, Call-Logging, Meetings

Evidence: Activity-UI  

Akzeptanz:

- Aktivitäten sind Account/Lead/Deal zugeordnet

***REMOVED******REMOVED******REMOVED*** CRM-ACT-02 Kalender-/Email-Integration

Priorität: SOLL  

Inhalt:

- Sync Outlook/Google, Mail-Logging

Evidence: Integration-Settings  

Akzeptanz:

- Emails erscheinen in Timeline

***REMOVED******REMOVED******REMOVED*** CRM-ACT-03 Vorlagen / Sequenzen

Priorität: KANN/SOLL  

Inhalt:

- Email-Templates, Call-Skripte, Sequenzen

Evidence: Template-UI  

Akzeptanz:

- Sequenzen sind messbar

***REMOVED******REMOVED*** 5. Marketing Automation (Campaign-to-Lead)

***REMOVED******REMOVED******REMOVED*** MKT-CAM-01 Kampagnenmanagement

Priorität: MUSS  

Inhalt:

- Kampagnen anlegen, Zielgruppe, Budget, Zeitraum

- Status (plan/aktiv/pausiert/abgeschlossen)

Evidence: Campaign-Flow  

Akzeptanz:

- KPIs pro Kampagne berechenbar

***REMOVED******REMOVED******REMOVED*** MKT-SEG-01 Segmente & Zielgruppen

Priorität: MUSS  

Inhalt:

- Regelbasierte Segmente (Attribute, Verhalten)

- Import/Lookups

Evidence: Segment-Builder  

Akzeptanz:

- Segmente aktualisieren sich automatisch

***REMOVED******REMOVED******REMOVED*** MKT-AUT-01 Nurture / Journeys

Priorität: SOLL  

Inhalt:

- Multi-step Journeys (Email, Task, Wait, Branch)

Evidence: Journey-Editor  

Akzeptanz:

- Abbruch-/Fallback-Logik

***REMOVED******REMOVED******REMOVED*** MKT-EML-01 Email-Marketing

Priorität: MUSS  

Inhalt:

- Editor, Templates, Versand, A/B Tests

- Bounce/Unsubscribe/Opt-In Handling

Evidence: Email-Flow  

Akzeptanz:

- Zustell-/Opt-out-Events werden geloggt

***REMOVED******REMOVED******REMOVED*** MKT-LND-01 Landingpages & Forms

Priorität: SOLL  

Inhalt:

- Form Builder, Captchas, Double-Opt-In

Evidence: Form-UI  

Akzeptanz:

- Form erzeugt Lead + Quelle

***REMOVED******REMOVED******REMOVED*** MKT-EVT-01 Event-/Webinar-Marketing

Priorität: KANN/SOLL  

Inhalt:

- Registrierungen, Teilnehmerlisten, Follow-ups

Evidence: Event-Flow  

Akzeptanz:

- Teilnehmer → Leads/Kontakte

***REMOVED******REMOVED******REMOVED*** MKT-SOC-01 Social/Ads Tracking

Priorität: KANN  

Inhalt:

- UTM/Ads Import, Attribution

Evidence: Tracking-Setup  

Akzeptanz:

- Attribution nachvollziehbar

***REMOVED******REMOVED*** 6. Consent, Datenschutz & Compliance

***REMOVED******REMOVED******REMOVED*** CRM-CNS-01 Opt-in/Opt-out & Consent Log

Priorität: MUSS  

Inhalt:

- Double-Opt-In, Kanal-spezifisch

- Consent Historie revisionssicher

Evidence: Consent-View  

Akzeptanz:

- Jede Kommunikation prüft Consent

***REMOVED******REMOVED******REMOVED*** CRM-CNS-02 DSGVO-Funktionen

Priorität: MUSS  

Inhalt:

- Auskunft, Löschung/Anonymisierung, Export

Evidence: GDPR-Tools UI  

Akzeptanz:

- Requests workflowfähig & protokolliert

***REMOVED******REMOVED*** 7. Reporting & Analytics

***REMOVED******REMOVED******REMOVED*** CRM-REP-01 Standard-CRM-Reports

Priorität: MUSS  

Inhalt:

- Lead-Quellen, Conversion Funnel, Pipeline, Win-Rate

Evidence: Dashboards  

Akzeptanz:

- Filter, Export

***REMOVED******REMOVED******REMOVED*** CRM-REP-02 Marketing-KPIs

Priorität: SOLL  

Inhalt:

- Open/Click/CTR, CAC, ROI, Attribution

Evidence: MKT Dashboards  

Akzeptanz:

- KPIs pro Kampagne/Segment

***REMOVED******REMOVED******REMOVED*** CRM-REP-03 Drilldown Beleg-/Aktivitätskette

Priorität: SOLL  

Inhalt:

- Kampagne → Lead → Deal → Quote/Order

Evidence: Drilldown-Trace  

Akzeptanz:

- Kette ist lückenlos

***REMOVED******REMOVED*** 8. Rollen, Berechtigungen, Workflows

***REMOVED******REMOVED******REMOVED*** CRM-AUTH-01 Rollenmodell CRM/MKT

Priorität: MUSS  

Inhalt:

- Sales Rep, Sales Lead, Marketing User, Admin, Auditor

- Team-/Region-/Account-basierte Rechte

Evidence: Role-Setup  

Akzeptanz:

- RBAC greift in UI + API

***REMOVED******REMOVED******REMOVED*** CRM-AUTH-02 Workflow-Engines

Priorität: SOLL  

Inhalt:

- Lead/Deal/Consent Freigaben

- Eskalation/Vertretung

Evidence: Workflow UI  

Akzeptanz:

- Regeln konfigurierbar

***REMOVED******REMOVED*** 9. Integrationen & Datenflüsse

***REMOVED******REMOVED******REMOVED*** CRM-INT-01 API / Import / Export

Priorität: MUSS  

Inhalt:

- Accounts, Contacts, Leads, Deals, Campaigns

- CSV/Excel/API/Webhooks

Evidence: Import-UI + API  

Akzeptanz:

- Sync ohne Datenverlust

***REMOVED******REMOVED******REMOVED*** CRM-INT-02 Tracking/Event Bus

Priorität: SOLL  

Inhalt:

- Events für Öffnungen, Klicks, Webform, Orders

Evidence: Event Log  

Akzeptanz:

- Events sind auswertbar

***REMOVED******REMOVED******REMOVED*** CRM-INT-03 Dritttools (Ads, Email, Kalender)

Priorität: KANN/SOLL  

Inhalt:

- Connectoren (Meta/Google Ads, Mailchimp, Outlook/Google)

Evidence: Connector-UI  

Akzeptanz:

- Status + Fehlerhandling sichtbar

