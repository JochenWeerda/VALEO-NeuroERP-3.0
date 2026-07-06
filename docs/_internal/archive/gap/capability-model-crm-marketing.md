# CRM & Marketing Capability Model (Referenz fÃ¼r GAP-Analyse)

Version: 1.0

Zweck: Referenzmodell zur Funktionsabdeckung in Valero NeuroERP fÃ¼r CRM & Marketing

Baseline: VollumfÃ¤ngliches CRM/ERP-Niveau (SAP CX/CRM, Oracle CX, Community ERP CRM+Marketing, MS Dynamics)

Legende PrioritÃ¤t:

- MUSS = Kern fÃ¼r Vertrieb/Marketingbetrieb

- SOLL = Standard in groÃŸen CRM/ERPs

- KANN = nice-to-have / branchenspezifisch

Evidence:

- UI-Screenshots (ID/Dateiname)

- Playwright Traces/Videos

- Flow-IDs aus UI-Explorer JSON

- API/Events (falls vorhanden)

## 1. Stammdaten & 360Â° Customer View

### CRM-ACC-01 Accounts / Firmenstamm

PrioritÃ¤t: MUSS

Inhalt:

- Firmenstamm, Klassifikation, Status, Owner/Team

- Mehrere Adressen (Rechnung/Lieferung), LÃ¤nder, USt-ID

Evidence: Account-Create/Edit/History

Akzeptanz:

- Dublettencheck + Ã„nderungsprotokoll

### CRM-CON-01 Kontakte / Personenstamm

PrioritÃ¤t: MUSS

Inhalt:

- Kontakte pro Account, Rollen, Opt-ins

- KommunikationskanÃ¤le, PrÃ¤ferenzen

Evidence: Contact-UI

Akzeptanz:

- Opt-in/Opt-out sauber dokumentiert

### CRM-REL-01 Beziehungen & Hierarchien

PrioritÃ¤t: SOLL

Inhalt:

- Konzernhierarchie, Tochter/Partner/Standorte

Evidence: Relationship-UI

Akzeptanz:

- Hierarchie in Reports nutzbar

### CRM-360-01 Customer Timeline / AktivitÃ¤tenhistorie

PrioritÃ¤t: SOLL

Inhalt:

- Alle Interaktionen zeitlich (Email, Call, Meeting, Ticket, Bestellung)

Evidence: Timeline-View

Akzeptanz:

- Filterbar nach Typ/Datum/Owner

## 2. Lead Management (Campaign/Lead-to-Opportunity)

### CRM-LED-01 Lead-Erfassung & Quellen

PrioritÃ¤t: MUSS

Inhalt:

- Leads manuell, Import, Webform, API

- Quelle, Kampagne, Status

Evidence: Lead-Create + Import

Akzeptanz:

- Quelle/Kampagne nachvollziehbar

### CRM-LED-02 Lead-Qualifizierung & Scoring

PrioritÃ¤t: SOLL

Inhalt:

- Statusmodell (neu/qualifiziert/nurture/unqualifiziert)

- Regelbasiertes Scoring (Fit/Intent)

Evidence: Lead-Scoring UI

Akzeptanz:

- Score beeinflusst Priorisierung

### CRM-LED-03 Lead-Routing / Zuweisung

PrioritÃ¤t: SOLL

Inhalt:

- Zuweisung nach Region/Produkt/Load

- SLA & Eskalation

Evidence: Routing-Regeln

Akzeptanz:

- Leads landen automatisch im richtigen Team

### CRM-LED-04 Dedupe & Merge

PrioritÃ¤t: SOLL

Inhalt:

- Dubletten erkennen/zusammenfÃ¼hren

Evidence: Merge-UI

Akzeptanz:

- Merge behÃ¤lt Historie/Audit

## 3. Opportunity & Pipeline

### CRM-OPP-01 Opportunities / Deals

PrioritÃ¤t: MUSS

Inhalt:

- Deal mit Stage, Wert, Wahrscheinlichkeit, Close-Date

- AktivitÃ¤ten, AnhÃ¤nge, Notizen

Evidence: Opportunity-Flow

Akzeptanz:

- Pipeline aggregierbar

### CRM-OPP-02 Stage-/Process-Templates

PrioritÃ¤t: SOLL

Inhalt:

- Stage-Modelle je Produkt/Channel

- Pflichtfelder je Stage

Evidence: Stage-Setup

Akzeptanz:

- Validierung schÃ¼tzt ProzessqualitÃ¤t

### CRM-OPP-03 Forecasting

PrioritÃ¤t: SOLL/KANN je Unternehmen

Inhalt:

- Forecast nach Stage/Owner/Periode

Evidence: Forecast-Report

Akzeptanz:

- Export und periodische Snapshots

### CRM-OPP-04 Angebots-/Auftragsbezug

PrioritÃ¤t: SOLL

Inhalt:

- Link Opportunity â†’ Quote/Order/Invoice

Evidence: Cross-Link UI

Akzeptanz:

- Belegkette drilldown-fÃ¤hig

## 4. AktivitÃ¤ten & Aufgaben

### CRM-ACT-01 Aufgaben, Calls, Meetings

PrioritÃ¤t: MUSS

Inhalt:

- Aufgaben mit FÃ¤lligkeit/Reminder, Call-Logging, Meetings

Evidence: Activity-UI

Akzeptanz:

- AktivitÃ¤ten sind Account/Lead/Deal zugeordnet

### CRM-ACT-02 Kalender-/Email-Integration

PrioritÃ¤t: SOLL

Inhalt:

- Sync Outlook/Google, Mail-Logging

Evidence: Integration-Settings

Akzeptanz:

- Emails erscheinen in Timeline

### CRM-ACT-03 Vorlagen / Sequenzen

PrioritÃ¤t: KANN/SOLL

Inhalt:

- Email-Templates, Call-Skripte, Sequenzen

Evidence: Template-UI

Akzeptanz:

- Sequenzen sind messbar

## 5. Marketing Automation (Campaign-to-Lead)

### MKT-CAM-01 Kampagnenmanagement

PrioritÃ¤t: MUSS

Inhalt:

- Kampagnen anlegen, Zielgruppe, Budget, Zeitraum

- Status (plan/aktiv/pausiert/abgeschlossen)

Evidence: Campaign-Flow

Akzeptanz:

- KPIs pro Kampagne berechenbar

### MKT-SEG-01 Segmente & Zielgruppen

PrioritÃ¤t: MUSS

Inhalt:

- Regelbasierte Segmente (Attribute, Verhalten)

- Import/Lookups

Evidence: Segment-Builder

Akzeptanz:

- Segmente aktualisieren sich automatisch

### MKT-AUT-01 Nurture / Journeys

PrioritÃ¤t: SOLL

Inhalt:

- Multi-step Journeys (Email, Task, Wait, Branch)

Evidence: Journey-Editor

Akzeptanz:

- Abbruch-/Fallback-Logik

### MKT-EML-01 Email-Marketing

PrioritÃ¤t: MUSS

Inhalt:

- Editor, Templates, Versand, A/B Tests

- Bounce/Unsubscribe/Opt-In Handling

Evidence: Email-Flow

Akzeptanz:

- Zustell-/Opt-out-Events werden geloggt

### MKT-LND-01 Landingpages & Forms

PrioritÃ¤t: SOLL

Inhalt:

- Form Builder, Captchas, Double-Opt-In

Evidence: Form-UI

Akzeptanz:

- Form erzeugt Lead + Quelle

### MKT-EVT-01 Event-/Webinar-Marketing

PrioritÃ¤t: KANN/SOLL

Inhalt:

- Registrierungen, Teilnehmerlisten, Follow-ups

Evidence: Event-Flow

Akzeptanz:

- Teilnehmer â†’ Leads/Kontakte

### MKT-SOC-01 Social/Ads Tracking

PrioritÃ¤t: KANN

Inhalt:

- UTM/Ads Import, Attribution

Evidence: Tracking-Setup

Akzeptanz:

- Attribution nachvollziehbar

## 6. Consent, Datenschutz & Compliance

### CRM-CNS-01 Opt-in/Opt-out & Consent Log

PrioritÃ¤t: MUSS

Inhalt:

- Double-Opt-In, Kanal-spezifisch

- Consent Historie revisionssicher

Evidence: Consent-View

Akzeptanz:

- Jede Kommunikation prÃ¼ft Consent

### CRM-CNS-02 DSGVO-Funktionen

PrioritÃ¤t: MUSS

Inhalt:

- Auskunft, LÃ¶schung/Anonymisierung, Export

Evidence: GDPR-Tools UI

Akzeptanz:

- Requests workflowfÃ¤hig & protokolliert

## 7. Reporting & Analytics

### CRM-REP-01 Standard-CRM-Reports

PrioritÃ¤t: MUSS

Inhalt:

- Lead-Quellen, Conversion Funnel, Pipeline, Win-Rate

Evidence: Dashboards

Akzeptanz:

- Filter, Export

### CRM-REP-02 Marketing-KPIs

PrioritÃ¤t: SOLL

Inhalt:

- Open/Click/CTR, CAC, ROI, Attribution

Evidence: MKT Dashboards

Akzeptanz:

- KPIs pro Kampagne/Segment

### CRM-REP-03 Drilldown Beleg-/AktivitÃ¤tskette

PrioritÃ¤t: SOLL

Inhalt:

- Kampagne â†’ Lead â†’ Deal â†’ Quote/Order

Evidence: Drilldown-Trace

Akzeptanz:

- Kette ist lÃ¼ckenlos

## 8. Rollen, Berechtigungen, Workflows

### CRM-AUTH-01 Rollenmodell CRM/MKT

PrioritÃ¤t: MUSS

Inhalt:

- Sales Rep, Sales Lead, Marketing User, Admin, Auditor

- Team-/Region-/Account-basierte Rechte

Evidence: Role-Setup

Akzeptanz:

- RBAC greift in UI + API

### CRM-AUTH-02 Workflow-Engines

PrioritÃ¤t: SOLL

Inhalt:

- Lead/Deal/Consent Freigaben

- Eskalation/Vertretung

Evidence: Workflow UI

Akzeptanz:

- Regeln konfigurierbar

## 9. Integrationen & DatenflÃ¼sse

### CRM-INT-01 API / Import / Export

PrioritÃ¤t: MUSS

Inhalt:

- Accounts, Contacts, Leads, Deals, Campaigns

- CSV/Excel/API/Webhooks

Evidence: Import-UI + API

Akzeptanz:

- Sync ohne Datenverlust

### CRM-INT-02 Tracking/Event Bus

PrioritÃ¤t: SOLL

Inhalt:

- Events fÃ¼r Ã–ffnungen, Klicks, Webform, Orders

Evidence: Event Log

Akzeptanz:

- Events sind auswertbar

### CRM-INT-03 Dritttools (Ads, Email, Kalender)

PrioritÃ¤t: KANN/SOLL

Inhalt:

- Connectoren (Meta/Google Ads, Mailchimp, Outlook/Google)

Evidence: Connector-UI

Akzeptanz:

- Status + Fehlerhandling sichtbar



