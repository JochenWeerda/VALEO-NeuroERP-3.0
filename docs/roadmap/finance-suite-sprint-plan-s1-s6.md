# VALEO Finance Suite 2.0 – Sprintplanung S1–S6 (Phase 1)

**Stand:** 2026-03-04  
**Basis:** `docs/roadmap/finance-suite-roadmap.md`, `gap/finance-fiori-gap-analysis.md`

## 1) Sprintziel Phase 1

- P0-Gaps operativ schließen: `FIBU-GL-05`, `FIBU-COMP-01`, `FIBU-AR-03`, `FIBU-AP-02`
- GoBD-Prüfbarkeit und Abschlussfähigkeit deutlich erhöhen

## 2) Kapazitätsrahmen

- Sprintdauer: 2 Wochen
- Geplante Gesamtlast pro Sprint: 45–55 SP
- Rollen: Squad A (Core/Compliance), Squad B (Bank/AR/Analytics)

## 3) Sprintplan (Epics → Stories)

## S1 – Fundament & Architektur (Target: 48 SP)

### Epic E1: Periodensteuerung Backend-Härtung (16 SP)
- Story E1-S1 (8): Zentraler `posting_guard` Service für Periodenstatus
- Story E1-S2 (5): Integration in Journal-Posting-Endpoints
- Story E1-S3 (3): Unit-Tests für OPEN/CLOSED/ADJUSTING

### Epic E2: AuditTrailWorkbench Backend-Basis (14 SP)
- Story E2-S1 (6): Audit API Filter erweitern (Zeitraum, Entity, User, Action)
- Story E2-S2 (5): Export-Endpoint (CSV) für gefilterte Sicht
- Story E2-S3 (3): Performance-Index-/Query-Review

### Epic E3: AP/AR Domain-Check (10 SP)
- Story E3-S1 (5): AP-Invoice Prozesskette dokumentiert + technische Lückenliste
- Story E3-S2 (5): Matching-Datenmodell/DTO-Abgleich

### Epic E4: QA & Compliance Guardrails (8 SP)
- Story E4-S1 (4): Smoke-Test-Set Phase 1
- Story E4-S2 (4): Audit-Trace-Checkliste (DoD-Erweiterung)

---

## S2 – FIBU-GL-05 sichtbar machen (Target: 50 SP)

### Epic E5: Periodenverwaltung UI E2E (22 SP)
- Story E5-S1 (8): Periodenliste inkl. Statusfilter/Sortierung
- Story E5-S2 (8): Statuswechsel (open/close/adjusting) inkl. Begründung
- Story E5-S3 (6): UI-Precheck vor Buchen (gesperrte Periode blockieren)

### Epic E6: Integrationspfade Periodensperre (18 SP)
- Story E6-S1 (8): Bulk-Import sperrlogisch anbinden
- Story E6-S2 (6): Bank-/AP-Postingpfade an Guard anschließen
- Story E6-S3 (4): End-to-End Tests für Sperrlogik

### Epic E7: Release Hardening (10 SP)
- Story E7-S1 (5): Fehlermeldungen standardisieren (DE/EN i18n)
- Story E7-S2 (5): Observability (Audit + Error Logs)

---

## S3 – FIBU-COMP-01 Kern (Target: 47 SP)

### Epic E8: AuditTrailWorkbench UI (24 SP)
- Story E8-S1 (8): Listenmaske (Filterkopf + Paging + Sort)
- Story E8-S2 (8): Detailansicht Vorher/Nachher mit Feld-Diff
- Story E8-S3 (8): Export-Dialog (CSV, Zeitraum, Entity Scope)

### Epic E9: Prüfermodus (13 SP)
- Story E9-S1 (6): Readonly-Rolle/Routeguard für Audit-Zugriff
- Story E9-S2 (4): Download-Protokollierung
- Story E9-S3 (3): Audit-UI Accessibility/Keyboard-Pass

### Epic E10: Testpaket Compliance (10 SP)
- Story E10-S1 (5): API Integrationstests Auditfilter/Export
- Story E10-S2 (5): UI Smoke (Filter → Detail → Export)

---

## S4 – FIBU-AP-02 End-to-End (Target: 53 SP)

### Epic E11: Eingangsrechnungen Prozessflow (28 SP)
- Story E11-S1 (9): Erfassungsmaske (Kopf + Positionen + Pflichtvalidierung)
- Story E11-S2 (8): Prüf-/Freigabezustände inkl. Rollen
- Story E11-S3 (11): Buchung/AP-OP-Erzeugung mit Audit

### Epic E12: AP-Integration (15 SP)
- Story E12-S1 (7): OP-Kreditoren Synchronisierung
- Story E12-S2 (4): Zahlungslauf-Vormerkung
- Story E12-S3 (4): Fehler-/Rollback-Pfade

### Epic E13: Qualität & UAT (10 SP)
- Story E13-S1 (5): E2E Smoke AP-Flow
- Story E13-S2 (5): Fachlicher UAT-Workshop + Fixes

---

## S5 – FIBU-AR-03 Matching (Target: 51 SP)

### Epic E14: Zahlungseingangs-Matching UI (24 SP)
- Story E14-S1 (8): Worklist „Unzugeordnete Zahlungen“
- Story E14-S2 (8): Match-Dialog (Vorschlag + manuelle Zuordnung)
- Story E14-S3 (8): Clearing buchen + Audit

### Epic E15: Bankimport-Anbindung (17 SP)
- Story E15-S1 (8): CAMT/MT940 Importpfad an Matching anbinden
- Story E15-S2 (5): Reprocess-Flow bei Parse-/Zuordnungsfehlern
- Story E15-S3 (4): Importprotokoll inkl. Korrelation-ID

### Epic E16: Abschlussnahe Stabilisierung (10 SP)
- Story E16-S1 (5): Konfliktfälle (Teilzahlung, Überzahlung) behandeln
- Story E16-S2 (5): Regressionstests AR/AP/GL

---

## S6 – Abschluss Kernreports + GoLive Readiness (Target: 49 SP)

### Epic E17: Abschluss-Kernreports (20 SP)
- Story E17-S1 (8): Trial Balance konsolidiert
- Story E17-S2 (6): Journal-/OP-Report Konsistenzcheck
- Story E17-S3 (6): Drilldown aus Report zu Beleg

### Epic E18: GoBD-Retention/WORM Nachweis (15 SP)
- Story E18-S1 (7): Technischer Nachweis Retention/WORM dokumentiert
- Story E18-S2 (4): Verfahrensdokumentation Finance aktualisiert
- Story E18-S3 (4): Prüferpaket „Abnahme-Set“

### Epic E19: GoLive Readiness (14 SP)
- Story E19-S1 (5): Cutover-Plan + Rollback
- Story E19-S2 (5): Monitoring/Dashboard für Kernprozesse
- Story E19-S3 (4): Hypercare-Plan (2 Wochen)

## 4) Abhängigkeiten & Reihenfolge

1. E1/E6 müssen vor produktiver AP/AR-Buchungsaktivierung stabil sein.
2. E2/E8/E9 müssen vor Compliance-Abnahme abgeschlossen sein.
3. E11 (AP) und E14 (AR) bauen auf stabiler Perioden-/Auditbasis auf.
4. E17/E18 sind Voraussetzung für Phase-1-Abnahme.

## 5) Definition of Ready (DoR) für Stories

- Fachlicher Scope klar (Input/Output/Statusübergang)
- API-Vertrag spezifiziert
- Rollen- und Berechtigungskonzept definiert
- Testfall (Happy + Error Path) benannt

## 6) Definition of Done (DoD) für Stories

- Code + Tests + Review abgeschlossen
- Audit-Trace vorhanden (bei buchungsrelevantem Vorgang)
- Fehlermeldungen fachlich verständlich
- Dokumentation/Runbook aktualisiert

## 7) Abnahmekriterien Phase 1

- P0-Funktionen in produktionsnaher Umgebung erfolgreich getestet
- Kein Buchungspfad umgeht Periodensperren
- AuditTrailWorkbench ist prüferfähig (Filter, Detail, Export)
- AR/AP Kernprozess von Erfassung bis Buchung/Ausgleich verfügbar

