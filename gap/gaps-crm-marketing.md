# GAP-Liste CRM & Marketing – Valero NeuroERP

Stand: 2025-01-27

Scope: Stammdaten → Leads → Opportunities → Aktivitäten → Kampagnen/Journeys → Consent → Analytics

Evidence:

- /evidence/screenshots/crm-marketing/*

- /swarm/handoffs/ui-explorer-crm-marketing-*.md

- Playwright traces/videos

Referenz:

- gap/capability-model-crm-marketing.md

- gap/matrix-crm-marketing.csv

---

## 1) Priorisierungslogik

PS = (BI × PF × RC) / IA

BI (Business Impact): 1–5  

PF (Pflichtgrad): MUSS=5, SOLL=3, KANN=1  

RC (Risk/Compliance): 1–5  

IA (Implementierungsaufwand): 1–5

---

## 2) TOP-Gaps nach Score

| Rank | Capability_ID | Gap-Titel | Status | PS | Lösungstyp | Owner |
|---|---|---|---|---:|---|---|
| 1 | CRM-OPP-01 | Opportunities / Deals | No | 25.0 | C | Sales-Team |
| 2 | CRM-CNS-01 | Opt-in/Opt-out & Consent Log | No | 25.0 | C | Compliance-Team |
| 3 | CRM-CNS-02 | DSGVO-Funktionen | No | 25.0 | C | Compliance-Team |
| 4 | MKT-SEG-01 | Segmente & Zielgruppen | No | 10.0 | C | Marketing-Team |
| 5 | CRM-LED-03 | Lead-Routing / Zuweisung | No | 7.5 | C | CRM-Team |
| 6 | CRM-REP-01 | Standard-CRM-Reports | Partial | 6.25 | B | CRM-Team |
| 7 | MKT-CAM-01 | Kampagnenmanagement | Partial | 5.0 | B | Marketing-Team |
| 8 | CRM-ACC-01 | Accounts / Firmenstamm | Partial | 4.17 | B | CRM-Team |
| 9 | CRM-360-01 | Customer Timeline | Partial | 3.75 | B | CRM-Team |
| 10 | CRM-OPP-04 | Angebots-/Auftragsbezug | Partial | 3.75 | B | Sales-Team |

---

## 3) GAP-Details (Solution-Cards)

### CARD CRM-MKT-001 — Opportunities / Deals (Sales Pipeline)

**Capability_ID(s):** CRM-OPP-01  

**Status:** No  

**Priorität:** MUSS  

**Score:** BI=5, PF=5, RC=1, IA=1 → PS=25.0



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `keine vorhanden`  

- Flow(s): `keine vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Sales Pipeline komplett fehlend. Keine Möglichkeit, Deals zu verwalten, Stages zu tracken oder Forecasts zu erstellen.



**Gap-Beschreibung**  

- Fehlende Sales Pipeline mit Opportunities/Deals

- Keine Stage-Management (z.B. Qualifizierung, Angebot, Verhandlung, Abschluss)

- Keine Wahrscheinlichkeiten pro Stage

- Keine Forecast-Funktionalität

- Keine Win/Loss-Analyse

- Keine Pipeline-Visualisierung (Kanban/Funnel)



**Zielverhalten / Akzeptanzkriterien**  

- Given ein Sales-Rep erstellt eine Opportunity

- When er Stage, Wert, Wahrscheinlichkeit und Close-Date eingibt

- Then wird die Opportunity in der Pipeline angezeigt

- And Forecast-Reports aggregieren alle Opportunities nach Stage/Owner/Periode

- And Pipeline-Visualisierung zeigt Funnel mit Conversion-Rates



**Lösungstyp:** C (New Module)  

**Owner:** Sales-Team



**Technische Umsetzung (Skizze)**  

- UI: `opportunities-liste.tsx` (ListReport), `opportunity-detail.tsx` (ObjectPage), `pipeline-kanban.tsx` (Kanban-View)

- Workflow/RBAC: Sales Rep kann eigene Opportunities verwalten, Sales Lead kann Team-Pipeline sehen

- Backend/API: `services/crm-sales/` mit `Opportunity` Entity, Stages, Probabilities, Forecast-Logik

- Tracking/Events: `crm.opportunity.created`, `crm.opportunity.stage-changed`, `crm.opportunity.won/lost`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/opportunities.spec.ts`



**Abhängigkeiten / DoD**

- CRM-OPP-02 (Stage-Templates) sollte parallel entwickelt werden

- Integration mit Sales-Modul (Quote/Order) erforderlich

- Tests grün, Evidence aktualisiert, Pipeline-Visualisierung funktional

---

### CARD CRM-MKT-002 — Opt-in/Opt-out & Consent Log

**Capability_ID(s):** CRM-CNS-01  

**Status:** No  

**Priorität:** MUSS  

**Score:** BI=5, PF=5, RC=5, IA=1 → PS=25.0



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `keine vorhanden`  

- Flow(s): `keine vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Kein Consent-Management vorhanden. Keine Möglichkeit, Opt-in/Opt-out zu verwalten oder Consent-Historie zu führen.



**Gap-Beschreibung**  

- Fehlendes Consent-Management-System

- Keine Double-Opt-In-Funktionalität

- Keine Kanal-spezifischen Opt-ins (Email, SMS, Telefon, Post)

- Keine revisionssichere Consent-Historie

- Keine automatische Prüfung vor Kommunikation



**Zielverhalten / Akzeptanzkriterien**  

- Given ein Kontakt gibt Opt-in für Email-Marketing

- When Double-Opt-In aktiviert ist

- Then wird Bestätigungs-Email gesendet

- And nach Bestätigung wird Consent in Historie geloggt

- And jede Marketing-Kommunikation prüft Consent vor Versand

- And Opt-out wird sofort wirksam und in Historie dokumentiert



**Lösungstyp:** C (New Module)  

**Owner:** Compliance-Team



**Technische Umsetzung (Skizze)**  

- UI: `consent-management.tsx` (ObjectPage), `consent-history.tsx` (Timeline-View)

- Workflow/RBAC: Compliance-Officer kann Consent verwalten, Marketing kann nur prüfen

- Backend/API: `services/crm-consent/` mit `Consent` Entity, Historie, Validierung

- Tracking/Events: `crm.consent.opt-in`, `crm.consent.opt-out`, `crm.consent.verified`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/consent.spec.ts`



**Abhängigkeiten / DoD**

- Integration mit Email-Service erforderlich (Double-Opt-In)

- Integration mit Marketing-Automation erforderlich (Consent-Prüfung)

- Tests grün, Evidence aktualisiert, DSGVO-konform

---

### CARD CRM-MKT-003 — DSGVO-Funktionen

**Capability_ID(s):** CRM-CNS-02  

**Status:** No  

**Priorität:** MUSS  

**Score:** BI=5, PF=5, RC=5, IA=1 → PS=25.0



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `keine vorhanden`  

- Flow(s): `keine vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Keine DSGVO-Tools vorhanden. Keine Möglichkeit, Auskunftsanfragen, Löschungen oder Anonymisierungen zu verwalten.



**Gap-Beschreibung**  

- Fehlende DSGVO-Compliance-Tools

- Keine Auskunftsanfrage-Verwaltung (Art. 15 DSGVO)

- Keine Löschungs-/Anonymisierungs-Workflows (Art. 17 DSGVO)

- Keine Datenexport-Funktion (Art. 20 DSGVO)

- Keine Widerspruchs-Verwaltung (Art. 21 DSGVO)

- Keine Protokollierung von DSGVO-Requests



**Zielverhalten / Akzeptanzkriterien**  

- Given ein Kontakt stellt Auskunftsanfrage

- When Request erfasst wird

- Then wird Workflow gestartet

- And alle personenbezogenen Daten werden exportiert

- And Request wird protokolliert mit Fristen

- And bei Löschungsanfrage werden Daten anonymisiert/gelöscht

- And Historie ist revisionssicher



**Lösungstyp:** C (New Module)  

**Owner:** Compliance-Team



**Technische Umsetzung (Skizze)**  

- UI: `gdpr-requests.tsx` (ListReport), `gdpr-request-detail.tsx` (ObjectPage), `gdpr-export.tsx` (Wizard)

- Workflow/RBAC: Compliance-Officer verwaltet Requests, automatische Fristenüberwachung

- Backend/API: `services/crm-gdpr/` mit `GDPRRequest` Entity, Export-Logik, Anonymisierung

- Tracking/Events: `crm.gdpr.request.created`, `crm.gdpr.request.completed`, `crm.gdpr.data.exported`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/gdpr.spec.ts`



**Abhängigkeiten / DoD**

- Integration mit allen CRM-Modulen erforderlich (Datenexport)

- Anonymisierungs-Logik für alle Entitäten

- Tests grün, Evidence aktualisiert, DSGVO-konform

---

### CARD CRM-MKT-004 — Segmente & Zielgruppen

**Capability_ID(s):** MKT-SEG-01  

**Status:** No  

**Priorität:** MUSS  

**Score:** BI=5, PF=5, RC=1, IA=2 → PS=10.0



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `keine vorhanden`  

- Flow(s): `keine vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Keine Segmentierungs-Funktionalität vorhanden. Keine Möglichkeit, regelbasierte Zielgruppen zu erstellen oder automatisch zu aktualisieren.



**Gap-Beschreibung**  

- Fehlender Segment-Builder

- Keine regelbasierte Segmentierung (Attribute, Verhalten)

- Keine automatische Segment-Aktualisierung

- Keine Segment-Import-Funktionalität

- Keine Segment-Performance-Tracking



**Zielverhalten / Akzeptanzkriterien**  

- Given ein Marketing-User erstellt Segment

- When er Regeln definiert (z.B. "Kunden mit Umsatz > 10k EUR")

- Then wird Segment automatisch berechnet

- And Segment aktualisiert sich bei Datenänderungen

- And Segment kann für Kampagnen verwendet werden

- And Segment-Performance wird getrackt



**Lösungstyp:** C (New Module)  

**Owner:** Marketing-Team



**Technische Umsetzung (Skizze)**  

- UI: `segmente-liste.tsx` (ListReport), `segment-builder.tsx` (Wizard), `segment-detail.tsx` (ObjectPage)

- Workflow/RBAC: Marketing-User kann Segmente erstellen, Admin kann alle verwalten

- Backend/API: `services/crm-marketing/` mit `Segment` Entity, Regel-Engine, Materialisierung

- Tracking/Events: `crm.segment.created`, `crm.segment.materialized`, `crm.segment.updated`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/segments.spec.ts`



**Abhängigkeiten / DoD**

- Integration mit CRM-Datenmodell erforderlich

- Regel-Engine für komplexe Segmentierungen

- Tests grün, Evidence aktualisiert, Performance akzeptabel

---

### CARD CRM-MKT-005 — Lead-Routing / Zuweisung

**Capability_ID(s):** CRM-LED-03  

**Status:** No  

**Priorität:** SOLL  

**Score:** BI=3, PF=3, RC=1, IA=2 → PS=7.5



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `keine vorhanden`  

- Flow(s): `keine vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Keine automatische Lead-Zuweisung vorhanden. Leads müssen manuell zugewiesen werden.



**Gap-Beschreibung**  

- Fehlende automatische Lead-Zuweisung

- Keine Routing-Regeln (Region, Produkt, Load)

- Keine SLA-Überwachung

- Keine Eskalations-Logik

- Keine Round-Robin-Zuweisung



**Zielverhalten / Akzeptanzkriterien**  

- Given ein neuer Lead wird erfasst

- When Routing-Regeln definiert sind

- Then wird Lead automatisch zugewiesen

- And SLA-Timer startet

- And bei Überschreitung wird eskaliert

- And Load-Balancing berücksichtigt aktuelle Auslastung



**Lösungstyp:** C (New Module)  

**Owner:** CRM-Team



**Technische Umsetzung (Skizze)**  

- UI: `lead-routing.tsx` (ObjectPage), `routing-regeln.tsx` (ListReport)

- Workflow/RBAC: Sales Lead kann Routing-Regeln konfigurieren

- Backend/API: `services/crm-core/` mit Routing-Engine, SLA-Timer, Eskalation

- Tracking/Events: `crm.lead.routed`, `crm.lead.sla-warning`, `crm.lead.escalated`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/lead-routing.spec.ts`



**Abhängigkeiten / DoD**

- Integration mit Lead-Management erforderlich

- SLA-Engine für Fristenüberwachung

- Tests grün, Evidence aktualisiert

---

### CARD CRM-MKT-006 — Standard-CRM-Reports

**Capability_ID(s):** CRM-REP-01  

**Status:** Partial  

**Priorität:** MUSS  

**Score:** BI=5, PF=5, RC=1, IA=4 → PS=6.25



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `crm-dashboard.tsx vorhanden`  

- Flow(s): `Basis-Reports vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Basis-Reports vorhanden, aber fehlen: Conversion Funnel, Pipeline-Reports, Win-Rate-Analyse.



**Gap-Beschreibung**  

- Fehlende Conversion Funnel-Visualisierung

- Keine Pipeline-Reports (Stage-Analyse, Forecast)

- Keine Win/Loss-Analyse

- Keine Lead-Quellen-Analyse

- Keine Export-Funktionalität für Reports



**Zielverhalten / Akzeptanzkriterien**  

- Given ein Sales Lead öffnet Pipeline-Report

- When er Filter setzt (Zeitraum, Team, Produkt)

- Then sieht er Stage-Verteilung, Conversion-Rates, Forecast

- And kann Report exportieren (PDF/Excel)

- And Win/Loss-Analyse zeigt Gründe für verlorene Deals



**Lösungstyp:** B (Integration/Extension)  

**Owner:** CRM-Team



**Technische Umsetzung (Skizze)**  

- UI: `crm-reports.tsx` (OverviewPage), `pipeline-report.tsx` (Chart-View), `funnel-report.tsx` (Funnel-Visualisierung)

- Workflow/RBAC: Sales Lead kann Reports sehen, Admin kann alle Reports verwalten

- Backend/API: `services/crm-reports/` mit Report-Engine, Aggregation, Export

- Tracking/Events: `crm.report.generated`, `crm.report.exported`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/reports.spec.ts`



**Abhängigkeiten / DoD**

- Abhängig von CRM-OPP-01 (Opportunities) für Pipeline-Reports

- Chart-Library für Visualisierungen

- Tests grün, Evidence aktualisiert

---

### CARD CRM-MKT-007 — Kampagnenmanagement (Erweiterung)

**Capability_ID(s):** MKT-CAM-01  

**Status:** Partial  

**Priorität:** MUSS  

**Score:** BI=5, PF=5, RC=1, IA=5 → PS=5.0



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `kampagnen.tsx vorhanden`  

- Flow(s): `Basis-Kampagnen-Liste vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Basis-Kampagnen-Liste vorhanden, aber fehlen: KPIs, Tracking, Budget-Management, Performance-Analyse.



**Gap-Beschreibung**  

- Fehlende KPI-Berechnung (Open-Rate, Click-Rate, Conversion)

- Kein Budget-Management (Plan vs. Ist)

- Keine Performance-Analyse pro Kampagne

- Keine A/B-Test-Funktionalität

- Keine Kampagnen-Templates



**Zielverhalten / Akzeptanzkriterien**  

- Given eine Kampagne wird gestartet

- When Emails versendet werden

- Then werden Opens, Clicks, Conversions getrackt

- And KPIs werden in Echtzeit aktualisiert

- And Budget wird überwacht (Plan vs. Ist)

- And Performance-Report zeigt ROI



**Lösungstyp:** B (Integration/Extension)  

**Owner:** Marketing-Team



**Technische Umsetzung (Skizze)**  

- UI: `kampagne-detail.tsx` (ObjectPage mit KPIs), `kampagnen-analyse.tsx` (OverviewPage)

- Workflow/RBAC: Marketing-User kann Kampagnen verwalten, Budget-Freigabe durch Manager

- Backend/API: `services/crm-marketing/` erweitern mit Tracking, KPI-Berechnung, Budget-Management

- Tracking/Events: `crm.campaign.launched`, `crm.campaign.email.opened`, `crm.campaign.email.clicked`, `crm.campaign.converted`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/campaigns.spec.ts`



**Abhängigkeiten / DoD**

- Integration mit Email-Service erforderlich (Tracking)

- Integration mit Lead-Management erforderlich (Conversions)

- Tests grün, Evidence aktualisiert

---

### CARD CRM-MKT-008 — Accounts / Firmenstamm (Erweiterung)

**Capability_ID(s):** CRM-ACC-01  

**Status:** Partial  

**Priorität:** MUSS  

**Score:** BI=5, PF=5, RC=2, IA=6 → PS=4.17



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `kunden-stamm.tsx vorhanden`  

- Flow(s): `Basis-Account-Management vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Basis-Account-Management vorhanden, aber fehlen: Mehrere Adressen, Dublettencheck, Änderungsprotokoll.



**Gap-Beschreibung**  

- Fehlende Mehrfach-Adressen (Rechnung, Lieferung, Hauptsitz)

- Kein Dublettencheck bei Erstellung

- Kein Änderungsprotokoll (Audit-Trail)

- Keine Klassifikation (Kunde, Lieferant, Partner)

- Keine Owner/Team-Zuordnung



**Zielverhalten / Akzeptanzkriterien**  

- Given ein User erstellt neuen Account

- When er Name eingibt

- Then wird Dublettencheck durchgeführt

- And bei möglicher Dublette wird Warnung angezeigt

- And alle Änderungen werden protokolliert

- And mehrere Adressen können verwaltet werden



**Lösungstyp:** B (Integration/Extension)  

**Owner:** CRM-Team



**Technische Umsetzung (Skizze)**  

- UI: `kunden-stamm.tsx` erweitern mit Adressen-Tab, Audit-Trail-View

- Workflow/RBAC: Sales Rep kann Accounts verwalten, Audit-Trail nur lesbar

- Backend/API: `services/crm-core/` erweitern mit Dublettencheck, Audit-Logging, Mehrfach-Adressen

- Tracking/Events: `crm.account.created`, `crm.account.duplicate-detected`, `crm.account.updated`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/accounts.spec.ts`



**Abhängigkeiten / DoD**

- Audit-Logging-System erforderlich

- Dublettencheck-Algorithmus

- Tests grün, Evidence aktualisiert

---

### CARD CRM-MKT-009 — Customer Timeline

**Capability_ID(s):** CRM-360-01  

**Status:** Partial  

**Priorität:** SOLL  

**Score:** BI=3, PF=3, RC=1, IA=4 → PS=3.75



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `aktivitaeten.tsx vorhanden`  

- Flow(s): `Aktivitäten-Liste vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Aktivitäten vorhanden, aber fehlt: Vollständige Timeline-View, Filter nach Typ/Datum/Owner, Integration aller Interaktionen.



**Gap-Beschreibung**  

- Fehlende Timeline-View (chronologische Darstellung)

- Keine Integration aller Interaktionen (Email, Call, Meeting, Ticket, Bestellung)

- Keine Filter-Funktionalität (Typ, Datum, Owner)

- Keine Suche in Timeline

- Keine Export-Funktionalität



**Zielverhalten / Akzeptanzkriterien**  

- Given ein User öffnet Customer Timeline

- When er Filter setzt (Typ: Email, Datum: letzte 30 Tage)

- Then sieht er alle Interaktionen chronologisch

- And kann nach Text suchen

- And kann Timeline exportieren

- And alle Interaktionen sind verlinkt



**Lösungstyp:** B (Integration/Extension)  

**Owner:** CRM-Team



**Technische Umsetzung (Skizze)**  

- UI: `customer-timeline.tsx` (Timeline-View), Integration in `kunden-stamm.tsx`

- Workflow/RBAC: Alle CRM-User können Timeline sehen

- Backend/API: `services/crm-core/` erweitern mit Timeline-Aggregation, Filter, Suche

- Tracking/Events: `crm.timeline.viewed`, `crm.timeline.filtered`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/timeline.spec.ts`



**Abhängigkeiten / DoD**

- Integration mit allen CRM-Modulen erforderlich (Email, Activities, Orders)

- Timeline-Komponente für chronologische Darstellung

- Tests grün, Evidence aktualisiert

---

### CARD CRM-MKT-010 — Angebots-/Auftragsbezug

**Capability_ID(s):** CRM-OPP-04  

**Status:** Partial  

**Priorität:** SOLL  

**Score:** BI=3, PF=3, RC=1, IA=4 → PS=3.75



**Ist-Beobachtung (Evidence)**  

- Screenshot(s): `Sales-Module vorhanden`  

- Flow(s): `Quote/Order-Flows vorhanden`  

- Trace(s): `keine vorhanden`  

- Aktueller Zustand: Sales-Module vorhanden, aber fehlt: Verknüpfung Opportunity → Quote/Order, Belegkette-Drilldown.



**Gap-Beschreibung**  

- Fehlende Verknüpfung Opportunity → Quote/Order

- Keine Belegkette-Visualisierung

- Keine Drilldown-Funktionalität

- Keine Revenue-Attribution



**Zielverhalten / Akzeptanzkriterien**  

- Given eine Opportunity wird zu Quote konvertiert

- When Quote erstellt wird

- Then ist Verknüpfung sichtbar

- And Belegkette zeigt: Opportunity → Quote → Order → Invoice

- And Drilldown zeigt alle verknüpften Belege

- And Revenue wird korrekt attribuiert



**Lösungstyp:** B (Integration/Extension)  

**Owner:** Sales-Team



**Technische Umsetzung (Skizze)**  

- UI: `opportunity-detail.tsx` erweitern mit Related-Belege-Tab, Belegkette-View

- Workflow/RBAC: Sales Rep kann Belege verknüpfen

- Backend/API: `services/crm-sales/` erweitern mit Verknüpfungs-Logik, Belegkette-Aggregation

- Tracking/Events: `crm.opportunity.converted-to-quote`, `crm.belegkette.viewed`



**Playwright-Nachweis**  

- Tests: `tests/e2e/crm-marketing/opportunity-links.spec.ts`



**Abhängigkeiten / DoD**

- Abhängig von CRM-OPP-01 (Opportunities)

- Integration mit Sales-Modul erforderlich

- Tests grün, Evidence aktualisiert

---

## 4) Zusammenfassung

**Gesamt-Gaps:** 30 Capabilities

- **Yes (Vollständig):** 2 (7%)

- **Partial (Teilweise):** 8 (27%)

- **No (Fehlend):** 20 (67%)

**Kritische Gaps (MUSS, Status=No):**

1. CRM-OPP-01: Opportunities / Deals

2. CRM-CNS-01: Opt-in/Opt-out & Consent Log

3. CRM-CNS-02: DSGVO-Funktionen

4. MKT-SEG-01: Segmente & Zielgruppen

**Implementierungsplan:**

Siehe: `swarm/missions/crm-marketing-implementation.md`

**Phasen:**

1. **Phase 1 (Weeks 1-8):** Kritische MUSS-Gaps
   - Opportunities / Deals (Sales Pipeline)
   - Consent-Management (DSGVO)
   - DSGVO-Funktionen
   - Segmente & Zielgruppen

2. **Phase 2 (Weeks 9-12):** Erweiterungen bestehender Funktionen
   - Reports erweitern
   - Kampagnen erweitern
   - Accounts erweitern
   - Timeline-View

3. **Phase 3 (Weeks 13-16):** SOLL-Gaps
   - Lead-Routing / Zuweisung
   - Forecasting
   - Nurture / Journeys

4. **Phase 4 (Weeks 17-20):** KANN-Gaps
   - Event-/Webinar-Marketing
   - Social/Ads Tracking
   - Dritttools/Connectoren

