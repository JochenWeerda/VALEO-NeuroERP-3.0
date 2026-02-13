# VALEO-NeuroERP 3.0 – Restarbeiten (Finale Übersicht)

**Stand:** 13.02.2026  
**Branch:** `develop`

## 1. Finaler Status (kompakt)

### Erledigt
- P0/P1 Kernlücken geschlossen (Procurement, GoBD, Eventing/Outbox, zentrale API-Pfade).
- Mock-Reduktion in Frontend-Modulen inkl. Error-State-Handling umgesetzt.
- Procurement P2/P3 API+UI-Welle umgesetzt:
  - Lieferantenbewertung
  - Lieferanten-Dokumente
  - PO-Kommunikation (E-Mail/Portal)
  - Retouren (inkl. Status-Update)
  - Service Entry Sheets
  - Gutschriften/Belastungen
  - Standardreports + Audit-Drilldown
  - EDI-Portal
- OpenAPI/Swagger vervollständigt:
  - `docs/api/openapi.md`
  - `docs/api/openapi.json`
  - `scripts/export_openapi.py`
- Multi-Tenancy technisch aktiviert (Header/Context/Filterpfad):
  - `X-Tenant-ID` Verarbeitung Backend + Frontend-Propagation.
- Redis-Caching für häufige Procurement-Lesezugriffe ergänzt.
- DB-Index-Optimierung per Alembic-Migration ergänzt.
- ArgoCD/GitOps-Basis (App-of-Apps) ergänzt:
  - `k8s/argocd/*`
  - `docs/deployment/gitops/argocd.md`
- Storybook-Dokumentation aktualisiert:
  - `docs/setup/storybook.md`

### Vorbereitet (Artefakte vorhanden, operativ noch auszuführen)
- Production-Secrets-Checkliste: `docs/deployment/production-secrets.md`
- Staging-Verifikations-Runbook: `docs/deployment/staging-verification.md`
- Staging-Check-Skript: `scripts/check-staging.ps1`
- Monitoring-Verifikation: `docs/operations/monitoring-dashboards-verification.md`

---

## 2. Offene Punkte

### Qualität & Tests
- [ ] Unit-Test-Coverage-Ziel konsolidieren und nachweisen (Eintrag ist aktuell widersprüchlich: „>80%“ bei „punktuell 92–98%“).
- [ ] Performance-/Load-Tests durchführen und dokumentieren.

### Deployment & Rollout (operativ)
- [ ] GitHub Secrets (8 Production-Secrets) in der Zielumgebung setzen.
- [ ] Staging-Deployment durchführen und mit Runbook verifizieren.
- [ ] UAT mit Key-Usern durchführen und Abnahme dokumentieren.
- [ ] Blue-Green Deployment durchführen.
- [ ] Monitoring-Dashboards nach Go-Live-Kriterien final verifizieren.

---

## 3. Nächste sinnvolle Reihenfolge
1. Secrets setzen + Staging verifizieren.
2. UAT durchführen und Findings schließen.
3. Load-/Performance-Test fahren.
4. Blue-Green Rollout + Monitoring-Freigabe.

---

## 4. Referenzen
- Abnahme-Template Deployment/Rollout: `docs/deployment/go-live-abnahme-template.md`
- OpenAPI: `docs/api/openapi.md`
- Multi-Tenancy: `docs/deployment/multi-tenancy.md`
- GitOps/ArgoCD: `docs/deployment/gitops/argocd.md`
- Procurement-Smoketest: `docs/procurement-wave2-smoketest.md`
- Production Deployment Plan: `docs/PRODUCTION-DEPLOYMENT.md`

---

## 5. 90-Tage-Ticketplan (Agrar-Core 1.0, Option C)

**Zielzeitraum:** 13.02.2026-14.05.2026  
**Prinzip:** Core stabil halten, Agrar als vertikales Modul unter `modules/agrar`.

### Woche 1 (13.02-20.02): EPIC AGRAR-ARCH-01 Modulrahmen
- [ ] Story AGRAR-ARCH-01-01: Verzeichnisstruktur `modules/agrar/*` anlegen.
- [ ] Story AGRAR-ARCH-01-02: Domain Registry + `INSTALLED_MODULES` ergänzen.
- [ ] Story AGRAR-ARCH-01-03: ADR "No Core Contamination" dokumentieren.
- Akzeptanzkriterien:
- Build grün, Module registrierbar, keine Fachlogik in `core/*`.

### Woche 2 (21.02-27.02): EPIC AGRAR-ARCH-02 Event- und Hook-Verträge
- [ ] Story AGRAR-ARCH-02-01: Event-Schemas definieren (`WeighingTicketCreated`, `ContractAllocated`, `SettlementIssued`).
- [ ] Story AGRAR-ARCH-02-02: Hook-Punkte für Lager/Buchhaltung/Compliance definieren.
- [ ] Story AGRAR-ARCH-02-03: Contract-Tests für Event-Payloads ergänzen.
- Akzeptanzkriterien:
- Versionierte Event-Verträge liegen vor, Contract-Tests erfolgreich.

### Woche 3 (28.02-06.03): EPIC AGRAR-ARCH-03 Guardrails in CI
- [ ] Story AGRAR-ARCH-03-01: Architektur-Checks (verbotene Imports) in CI einbauen.
- [ ] Story AGRAR-ARCH-03-02: Feature-Flag-Gating pro Mandant ergänzen.
- [ ] Story AGRAR-ARCH-03-03: Dokumentation Modulaktivierung erstellen.
- Akzeptanzkriterien:
- CI blockiert Core-Verstöße, Modul per Flag aktiv/inaktiv schaltbar.

### Woche 4 (09.03-13.03): EPIC AGRAR-WG-01 Wiegeschein-Datenmodell
- [ ] Story AGRAR-WG-01-01: Tabellen `weighing_tickets` + `weighing_measurements` per Migration.
- [ ] Story AGRAR-WG-01-02: CRUD-API für Wiegeschein mit Validierung.
- [ ] Story AGRAR-WG-01-03: Erst-/Zweitwiegung inkl. Brutto/Tara/Netto.
- Akzeptanzkriterien:
- Persistente Wiegescheine mit Audit-Trail, API ohne Mock/Fallback.

### Woche 5 (16.03-20.03): EPIC AGRAR-CT-01 Kontrakte MVP
- [ ] Story AGRAR-CT-01-01: Tabellen `contracts`, `contract_allocations`, `pricing_model`.
- [ ] Story AGRAR-CT-01-02: Open-Quantity-Logik (Restmenge) implementieren.
- [ ] Story AGRAR-CT-01-03: Kontrakt-CRUD + Statusmaschine (offen, teilgelöscht, erfüllt).
- Akzeptanzkriterien:
- Restmenge wird korrekt geführt, invalides Überbuchen wird geblockt.

### Woche 6 (23.03-27.03): EPIC AGRAR-WG-02 Wiegeschein -> Kontraktlöschung
- [ ] Story AGRAR-WG-02-01: Zuordnung Wiegeschein zu Kontrakt.
- [ ] Story AGRAR-WG-02-02: Automatische Löschlogik bei Buchung.
- [ ] Story AGRAR-WG-02-03: Outbox-Events bei Löschung und Fehlerfällen.
- Akzeptanzkriterien:
- Buchungsfluss atomar, Event-Emission nachweisbar, Rollback sauber.

### Woche 7 (30.03-03.04): EPIC AGRAR-SILO-01 Partie/Silo-Basis
- [ ] Story AGRAR-SILO-01-01: Tabellen `silo_lots`, `silo_quality_snapshot`, `lot_movements`.
- [ ] Story AGRAR-SILO-01-02: Virtuelle Sammelpartie je Silo.
- [ ] Story AGRAR-SILO-01-03: Qualitätsmittelwerte pro aktueller Füllung.
- Akzeptanzkriterien:
- Silo-Füllung, Mischung und Qualitätsdurchschnitt reproduzierbar berechnet.

### Woche 8 (06.04-10.04): EPIC AGRAR-SET-01 Gutschriftverfahren
- [ ] Story AGRAR-SET-01-01: Self-Billing Entität/Workflow implementieren.
- [ ] Story AGRAR-SET-01-02: Abzugsarten (Trocknung, Reinigung, Fracht) regelbasiert.
- [ ] Story AGRAR-SET-01-03: Buchungssätze in Fibu erzeugen.
- Akzeptanzkriterien:
- Gutschrift endet in validen Buchungen inkl. Einzelabzügen.

### Woche 9 (13.04-17.04): EPIC AGRAR-SET-02 Schwund-/Feuchte-Engine
- [ ] Story AGRAR-SET-02-01: Domain-Service für Feuchtekorrektur/Heine-Logik.
- [ ] Story AGRAR-SET-02-02: Abrechnungsgewicht als explizites Feld führen.
- [ ] Story AGRAR-SET-02-03: Testfälle für Grenzwerte und negative Pfade.
- Akzeptanzkriterien:
- Formelpfad deterministisch, testabgedeckt, keine SQL- oder UI-Formellogik.

### Woche 10 (20.04-24.04): EPIC AGRAR-COMP-01 Compliance-MVP
- [ ] Story AGRAR-COMP-01-01: Gefahrstoffdoku-Export für PSM/Dünger.
- [ ] Story AGRAR-COMP-01-02: Nährstoffstrom-Export (N/P2O5) je Zeitraum.
- [ ] Story AGRAR-COMP-01-03: Chargen-Trace Bericht Saatgut -> Endprodukt.
- Akzeptanzkriterien:
- Pflichtfelder vollständig, Exportdateien fachlich prüfbar.

### Woche 11 (27.04-01.05): EPIC AGRAR-MIG-01 Datenmigration
- [ ] Story AGRAR-MIG-01-01: Backfill-Skript Altobjekte -> neue Agrar-Entitäten.
- [ ] Story AGRAR-MIG-01-02: Idempotente Migration + Re-Run-Fähigkeit.
- [ ] Story AGRAR-MIG-01-03: Migrationsbericht (Anzahl, Fehler, Korrekturen).
- Akzeptanzkriterien:
- Migration reproduzierbar, kein Datenverlust, Fehlerquote dokumentiert.

### Woche 12 (04.05-08.05): EPIC AGRAR-UAT-01 UAT + Performance
- [ ] Story AGRAR-UAT-01-01: 3 End-to-End-Szenarien mit Key-Usern testen.
- [ ] Story AGRAR-UAT-01-02: Lasttest für Wiegeschein/Abrechnung/Events.
- [ ] Story AGRAR-UAT-01-03: Befunde priorisieren und Hotfix-Batch schließen.
- Akzeptanzkriterien:
- UAT-Protokoll signiert, P1/P2 Findings geschlossen.

### Woche 13 (11.05-14.05): EPIC AGRAR-GO-01 Go-Live Readiness
- [ ] Story AGRAR-GO-01-01: Go-Live-Checkliste + Rollback-Plan finalisieren.
- [ ] Story AGRAR-GO-01-02: Monitoring- und Alerting-Schwellen verifizieren.
- [ ] Story AGRAR-GO-01-03: Produktionsfreigabe mit Abnahmeprotokoll.
- Akzeptanzkriterien:
- Go/No-Go-Entscheidung dokumentiert, Betriebshandbuch vollständig.

### Übergreifende Gate-Kriterien (für alle Wochen)
- [ ] Alembic: genau ein Head im Zielstand.
- [ ] Keine neue Agrar-Fachlogik außerhalb `modules/agrar`.
- [ ] OpenAPI für neue Endpunkte aktualisiert.
- [ ] E2E-Flows "Wiegeschein -> Abrechnung -> Buchung" grün.

---

## 6. Sprint-Board-Version (direkt übernehmbar)

### Board-Spalten
- Backlog
- Ready
- In Progress
- Review
- QA/UAT
- Done

### Ticket-Template (für alle Stories)
- ID: `AGRAR-<EPIC>-<NN>`
- Titel: Kurz + fachlich eindeutig
- Typ: Story
- Priorität: P0, P1, P2
- Aufwand: S (1-2 Tage), M (3-5 Tage), L (6-10 Tage)
- Owner-Rolle: Backend, Frontend, Fullstack, DevOps, QA
- Abhängigkeiten: Ticket-IDs
- Akzeptanzkriterien: messbar, testbar, ohne "sollte"

### Sprint 1 (13.02-27.02) Architektur & Verträge
- [ ] `AGRAR-ARCH-01` Modulrahmen aufsetzen | P0 | M | Fullstack
- [ ] `AGRAR-ARCH-02` Event-/Hook-Verträge versionieren | P0 | M | Backend
- [ ] `AGRAR-ARCH-03` CI-Guardrails gegen Core-Kontamination | P0 | M | DevOps

### Sprint 2 (28.02-20.03) Wiegeschein + Kontrakt-Basis
- [ ] `AGRAR-WG-01` Wiegeschein-Datenmodell + CRUD | P0 | L | Backend
- [ ] `AGRAR-CT-01` Kontrakte + Restmengenlogik | P0 | L | Backend
- [ ] `AGRAR-WG-UI-01` Wiegeschein-Erfassung UI (ohne Mock) | P1 | M | Frontend

### Sprint 3 (21.03-03.04) Löschlogik + Silo/Partie
- [ ] `AGRAR-WG-02` Wiegeschein -> Kontraktlöschung atomar | P0 | M | Backend
- [ ] `AGRAR-SILO-01` Sammelpartie + Qualitätsmittelwerte | P0 | L | Backend
- [ ] `AGRAR-SILO-UI-01` Siloübersicht mit Qualitätssnapshot | P1 | M | Frontend

### Sprint 4 (04.04-17.04) Abrechnung + Physiklogik
- [ ] `AGRAR-SET-01` Self-Billing inkl. Abzüge | P0 | L | Backend
- [ ] `AGRAR-SET-02` Feuchte-/Schwund-Engine im Domain-Service | P0 | M | Backend
- [ ] `AGRAR-SET-UI-01` Gutschrift-Ansicht inkl. Abzugsnachweis | P1 | M | Frontend

### Sprint 5 (18.04-01.05) Compliance + Migration
- [ ] `AGRAR-COMP-01` Gefahrstoff-/Nährstoff-Export | P0 | M | Backend
- [ ] `AGRAR-MIG-01` Backfill + idempotente Migration | P0 | M | Backend
- [ ] `AGRAR-COMP-UI-01` Export- und Prüfprotokollseite | P1 | M | Frontend

### Sprint 6 (02.05-14.05) UAT, Last, Go-Live
- [ ] `AGRAR-UAT-01` 3 E2E-Fachszenarien mit Key-Usern | P0 | M | QA
- [ ] `AGRAR-PERF-01` Lasttest Wiegeschein/Abrechnung/Eventbus | P0 | M | QA
- [ ] `AGRAR-GO-01` Go-Live-Readiness + Rollback-Probe | P0 | M | DevOps

### Definition of Done (DoD)
- [ ] Code + Tests + OpenAPI aktualisiert.
- [ ] Kein Mock/Fallback auf produktiven Pfaden.
- [ ] Observability vorhanden (Logs, Metriken, Fehlercodes).
- [ ] Fachliche Akzeptanzkriterien erfüllt und dokumentiert.
- [ ] Migration/Rollback beschrieben (falls Schemaänderung).

---

## 7. CSV-Import (Jira/GitHub Projects)

**Hinweis:** UTF-8 speichern, Trennzeichen `,`, Datumsformat `YYYY-MM-DD`.

```csv
id,title,type,priority,effort,owner_role,sprint,start_date,end_date,status,dependencies,acceptance_criteria
AGRAR-ARCH-01,Modulrahmen aufsetzen,Story,P0,M,Fullstack,Sprint 1,2026-02-13,2026-02-27,Backlog,,modules/agrar Struktur vorhanden und registrierbar
AGRAR-ARCH-02,Event-/Hook-Verträge versionieren,Story,P0,M,Backend,Sprint 1,2026-02-13,2026-02-27,Backlog,AGRAR-ARCH-01,Versionierte Events mit Contract-Tests grün
AGRAR-ARCH-03,CI-Guardrails gegen Core-Kontamination,Story,P0,M,DevOps,Sprint 1,2026-02-13,2026-02-27,Backlog,AGRAR-ARCH-01,CI blockiert verbotene Core-Imports
AGRAR-WG-01,Wiegeschein-Datenmodell und CRUD,Story,P0,L,Backend,Sprint 2,2026-02-28,2026-03-20,Backlog,AGRAR-ARCH-01,Wiegeschein persistiert mit Audit-Trail und validierter API
AGRAR-CT-01,Kontrakte und Restmengenlogik,Story,P0,L,Backend,Sprint 2,2026-02-28,2026-03-20,Backlog,AGRAR-ARCH-02,Restmengen korrekt berechnet und Überbuchung verhindert
AGRAR-WG-UI-01,Wiegeschein-Erfassung UI ohne Mock,Story,P1,M,Frontend,Sprint 2,2026-02-28,2026-03-20,Backlog,AGRAR-WG-01,UI nutzt echte API mit sauberem Error-Handling
AGRAR-WG-02,Wiegeschein zu Kontraktlöschung atomar,Story,P0,M,Backend,Sprint 3,2026-03-21,2026-04-03,Backlog,AGRAR-WG-01|AGRAR-CT-01,Atomare Buchung mit Outbox-Events und Rollback
AGRAR-SILO-01,Sammelpartie und Qualitätsmittelwerte,Story,P0,L,Backend,Sprint 3,2026-03-21,2026-04-03,Backlog,AGRAR-WG-01,Siloqualität reproduzierbar aus Bewegungen berechnet
AGRAR-SILO-UI-01,Siloübersicht mit Qualitätssnapshot,Story,P1,M,Frontend,Sprint 3,2026-03-21,2026-04-03,Backlog,AGRAR-SILO-01,UI zeigt Füllstand und Qualitätskennzahlen pro Silo
AGRAR-SET-01,Self-Billing mit Abzügen,Story,P0,L,Backend,Sprint 4,2026-04-04,2026-04-17,Backlog,AGRAR-WG-02,Gutschrift erzeugt korrekte Fibu-Buchungen inklusive Abzüge
AGRAR-SET-02,Feuchte-/Schwund-Engine im Domain-Service,Story,P0,M,Backend,Sprint 4,2026-04-04,2026-04-17,Backlog,AGRAR-WG-01,Deterministische Abrechnungsgewichte mit Grenzwerttests
AGRAR-SET-UI-01,Gutschrift-Ansicht mit Abzugsnachweis,Story,P1,M,Frontend,Sprint 4,2026-04-04,2026-04-17,Backlog,AGRAR-SET-01,UI listet Abzüge transparent und prüfbar auf
AGRAR-COMP-01,Gefahrstoff- und Nährstoff-Export,Story,P0,M,Backend,Sprint 5,2026-04-18,2026-05-01,Backlog,AGRAR-SET-01,Exportdateien vollständig und fachlich plausibel
AGRAR-MIG-01,Backfill und idempotente Migration,Story,P0,M,Backend,Sprint 5,2026-04-18,2026-05-01,Backlog,AGRAR-WG-01|AGRAR-CT-01,Migration ohne Datenverlust mehrfach ausführbar
AGRAR-COMP-UI-01,Export- und Prüfprotokollseite,Story,P1,M,Frontend,Sprint 5,2026-04-18,2026-05-01,Backlog,AGRAR-COMP-01,UI zeigt Exportlauf und Prüfergebnis pro Lauf
AGRAR-UAT-01,3 E2E-Fachszenarien mit Key-Usern,Story,P0,M,QA,Sprint 6,2026-05-02,2026-05-14,Backlog,AGRAR-SET-01|AGRAR-COMP-01,UAT-Protokoll signiert und P1/P2 Findings geschlossen
AGRAR-PERF-01,Lasttest für Wiegeschein/Abrechnung/Eventbus,Story,P0,M,QA,Sprint 6,2026-05-02,2026-05-14,Backlog,AGRAR-WG-02,Lastziele erreicht und Engpässe dokumentiert
AGRAR-GO-01,Go-Live-Readiness und Rollback-Probe,Story,P0,M,DevOps,Sprint 6,2026-05-02,2026-05-14,Backlog,AGRAR-UAT-01|AGRAR-PERF-01,Go/No-Go dokumentiert und Rollback verifiziert
```

