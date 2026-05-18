# VALEO Finance Suite 2.0 – Roadmap mit Aufwandsschätzung

**Stand:** 2026-03-04
**Basis:** `gap/finance-fiori-gap-analysis.md`, `gap/finance-fiori-matrix.csv`, `gap/gaps.md`

## 1) Planungsannahmen

- Team: 1 Product Owner, 1 Architect/Lead, 2 Backend, 2 Frontend, 1 QA (shared)
- Velocity-Richtwert: `1 Story Point = 0,6–0,8 Personentage`
- Kapazität pro 2-Wochen-Sprint: `~45–55 SP` (gesamt, inkl. QA/Review)
- Parallelisierung: Phase-1-Pakete teilweise parallel möglich, aber Compliance-Pfad ist kritisch

## 2) Backlog nach Priorität (P0/P1/P2)

| ID | Arbeitspaket | Priorität | Aufwand (SP) | Aufwand (PT) | Abhängigkeit |
|---|---|---|---:|---:|---|
| R1 | Periodensteuerung E2E (UI + Posting Guards) | P0 | 24 | 14–19 | Journal-/Import-Pfade |
| R2 | AuditTrailWorkbench (Filter, Detail, Export, Prüfersicht) | P0 | 20 | 12–16 | Audit API stabil |
| R3 | Zahlungseingang & Matching UI inkl. Bankimport-Flow | P0 | 26 | 16–21 | Bankimport, OP-Modelle |
| R4 | Eingangsrechnungen E2E (Erfassung, Prüfung, Buchung) | P0 | 28 | 17–22 | AP-Invoice API |
| R5 | Abschluss-Kernreports (Trial Balance, Journal, OP) | P0 | 16 | 10–13 | Reporting API |
| R6 | Bankabgleich 2.0 (Reprocess, Auto/Manuell-Hybrid) | P1 | 22 | 13–18 | R3 |
| R7 | Credit Management (Limit/Exposure/Block/Freigabe) | P1 | 20 | 12–16 | Debitoren/OP |
| R8 | Anlagenbuchhaltung vertiefen (AfA, Abgang, Umbuchung) | P1 | 30 | 18–24 | Connector/Asset-Model |
| R9 | CO-Start: Kostenstellen + Innenaufträge | P1 | 24 | 14–19 | GL/Reporting |
| R10 | CO-Ausbau: Profit Center, Margin, Product Costing | P1 | 34 | 20–27 | R9 |
| R11 | Cashflow-Reporting | P1 | 14 | 8–11 | Reporting harmonisiert |
| R12 | Embedded Analytics Drilldown (3-Klick bis Beleg) | P1 | 16 | 10–13 | R5 |
| R13 | UX-Harmonisierung Web-ERP-Muster (PageToolbar/Worklist) | P2 | 14 | 8–11 | sukzessive |
| R14 | E-Rechnung Harmonisierung (XRechnung/ZUGFeRD Suite-weit) | P1 | 18 | 11–14 | Rechnungsflüsse |
| R15 | GoBD-Retention/WORM-Nachweis + Verfahrensdoku | P0 | 18 | 11–14 | Compliance |

**Gesamt:** `324 SP` (~`194–258 PT`)

## 3) Phasenplanung

### Phase 1 (0–12 Wochen, Sprints 1–6) – Compliance + Kernprozesse

Umfang:
- R1, R2, R3, R4, R5, R15

Aufwand:
- `132 SP` (~`79–105 PT`)

Zielbild Ende Phase 1:
- P0-Finance-Gaps aus `gap/finance-fiori-gap-analysis.md` operativ geschlossen
- GoBD-Prüfersicht, Periodensperren und Kern-R2R/P2P/O2C-Prozesse belastbar

### Phase 2 (12–24 Wochen, Sprints 7–12) – Struktureller Ausbau

Umfang:
- R6, R7, R8, R9, R14

Aufwand:
- `114 SP` (~`68–91 PT`)

Zielbild Ende Phase 2:
- Bank/AR/AP/Asset- und CO-Basisprozesse auf Suite-Niveau integriert

### Phase 3 (24+ Wochen, Sprints 13–16) – Analytics + Reifegrad

Umfang:
- R10, R11, R12, R13

Aufwand:
- `78 SP` (~`47–62 PT`)

Zielbild Ende Phase 3:
- Advanced Controlling + Analytics + UX-Harmonisierung abgeschlossen

## 4) Kritischer Pfad

1. R1 Periodensteuerung E2E
2. R2 AuditTrailWorkbench
3. R4 Eingangsrechnungen E2E
4. R3 Matching/Bank-Flow
5. R15 GoBD-Retention/WORM-Nachweis

Ohne diese fünf Pakete bleibt das Compliance- und Abschlussrisiko hoch.

## 5) Meilensteine

- **M1 (Woche 4):** Periodensperren backendseitig konsistent + UI steuerbar
- **M2 (Woche 8):** AuditTrailWorkbench inkl. Export für Prüferbetrieb
- **M3 (Woche 12):** P0-Prozesskette AR/AP/GL operativ stabil
- **M4 (Woche 20):** Bankabgleich2 + Credit Management + Anlagenkern live
- **M5 (Woche 28):** CO-Basis + Cashflow + Drilldown produktiv
- **M6 (Woche 32):** Finance Suite 2.0 Reifegradziel erreicht

## 6) Risiko- und Pufferplanung

- Integrationsrisiko (Bank/CAMT/MT940, DATEV, ELSTER): +`10–15%` Puffer
- Datenmodell-/Migrationsrisiko (Asset/CO): +`10%` Puffer
- Compliance-Abnahmezyklen (intern/extern): +`1 Sprint` Reserve in Phase 1

Empfohlener Gesamtpuffer: `15–20%` auf PT.

## 7) Umsetzungsempfehlung (Team-Schnitt)

- **Squad A (Core/Compliance):** R1, R2, R4, R15
- **Squad B (Bank/AR/Analytics):** R3, R5, R6, R12
- **Squad C (Struct/CO/Asset, optional ab Phase 2):** R7, R8, R9, R10, R11, R14

## 8) Definition of Done je Paket

- Fachlicher End-to-End-Test bestanden (inkl. Fehlerpfade)
- Audit-Event/Trace vollständig
- Rollen/Berechtigungen geprüft
- API + UI Dokumentation aktualisiert
- Smoke-Test in Zielumgebung durchgeführt

## 9) Operative Sprintplanung (S1–S6)

Detaillierte Umsetzung je Sprint (Epics/Stories/SP):
`docs/roadmap/finance-suite-sprint-plan-s1-s6.md`
