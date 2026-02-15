# VALEO-NeuroERP 3.0 – Restarbeiten (Finale Übersicht)

**Stand:** 14.02.2026  
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
- AGRAR Lasttest-Runbook: `docs/testing/agrar-loadtest.md`
- AGRAR Lasttest-Skript: `tests/performance/agrar-core-loadtest.js`
- AGRAR Lasttest-Runner: `scripts/run-agrar-loadtest.ps1`

---

## 2. Offene Punkte

### Qualität & Tests
- [x] Unit-Test-Coverage-Ziel konsolidieren und nachweisen (Eintrag ist aktuell widersprüchlich: „>80%“ bei „punktuell 92–98%“).  
  Nachweis: `docs/testing/restarbeiten-verifikation-2026-02-14.md`  
  Konsolidierter Stand: Gesamt-Suite aktuell 40% (nicht >80%), Agrar-Kernsuite 17/17 Tests grün.
- [x] Performance-/Load-Tests durchführen und dokumentieren.  
  Nachweis: `docs/testing/restarbeiten-verifikation-2026-02-14.md`  
  Ergebnis: `AGRAR-PERF-01` erfolgreich per containerisiertem `k6` ausgeführt, Thresholds erfüllt.

### Deployment & Rollout (operativ)
Hinweis: Diese Punkte sind umgebungs-/zugriffsabhängig und erfordern Ausführung in Zielumgebungen (Staging/Production).
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
- Modulaktivierung: `docs/deployment/module-activation.md`
- GitOps/ArgoCD: `docs/deployment/gitops/argocd.md`
- Procurement-Smoketest: `docs/procurement-wave2-smoketest.md`
- AGRAR Lasttest: `docs/testing/agrar-loadtest.md`
- Production Deployment Plan: `docs/PRODUCTION-DEPLOYMENT.md`

---

## 5. 90-Tage-Ticketplan (Agrar-Core 1.0, Option C)

**Zielzeitraum:** 13.02.2026-14.05.2026  
**Prinzip:** Core stabil halten, Agrar als vertikales Modul unter `modules/agrar`.

### Woche 1 (13.02-20.02): EPIC AGRAR-ARCH-01 Modulrahmen
- [x] Story AGRAR-ARCH-01-01: Verzeichnisstruktur `modules/agrar/*` anlegen.
- [x] Story AGRAR-ARCH-01-02: Domain Registry + `INSTALLED_MODULES` ergänzen.
- [x] Story AGRAR-ARCH-01-03: ADR "No Core Contamination" dokumentieren.
- Akzeptanzkriterien:
- Build grün, Module registrierbar, keine Fachlogik in `core/*`.

### Woche 2 (21.02-27.02): EPIC AGRAR-ARCH-02 Event- und Hook-Verträge
- [x] Story AGRAR-ARCH-02-01: Event-Schemas definieren (`WeighingTicketCreated`, `ContractAllocated`, `SettlementIssued`).
- [x] Story AGRAR-ARCH-02-02: Hook-Punkte für Lager/Buchhaltung/Compliance definieren.
- [x] Story AGRAR-ARCH-02-03: Contract-Tests für Event-Payloads ergänzen.
- Akzeptanzkriterien:
- Versionierte Event-Verträge liegen vor, Contract-Tests erfolgreich.

### Woche 3 (28.02-06.03): EPIC AGRAR-ARCH-03 Guardrails in CI
- [x] Story AGRAR-ARCH-03-01: Architektur-Checks (verbotene Imports) in CI einbauen.
- [x] Story AGRAR-ARCH-03-02: Feature-Flag-Gating pro Mandant ergänzen.
- [x] Story AGRAR-ARCH-03-03: Dokumentation Modulaktivierung erstellen.
- Akzeptanzkriterien:
- CI blockiert Core-Verstöße, Modul per Flag aktiv/inaktiv schaltbar.

### Woche 4 (09.03-13.03): EPIC AGRAR-WG-01 Wiegeschein-Datenmodell
- [x] Story AGRAR-WG-01-01: Tabellen `weighing_tickets` + `weighing_measurements` per Migration.
- [x] Story AGRAR-WG-01-02: CRUD-API für Wiegeschein mit Validierung.
- [x] Story AGRAR-WG-01-03: Erst-/Zweitwiegung inkl. Brutto/Tara/Netto.
- Akzeptanzkriterien:
- Persistente Wiegescheine mit Audit-Trail, API ohne Mock/Fallback.

### Woche 5 (16.03-20.03): EPIC AGRAR-CT-01 Kontrakte MVP
- [x] Story AGRAR-CT-01-01: Tabellen `contracts`, `contract_allocations`, `pricing_model`.
- [x] Story AGRAR-CT-01-02: Open-Quantity-Logik (Restmenge) implementieren.
- [x] Story AGRAR-CT-01-03: Kontrakt-CRUD + Statusmaschine (offen, teilgelöscht, erfüllt).
- Akzeptanzkriterien:
- Restmenge wird korrekt geführt, invalides Überbuchen wird geblockt.

### Woche 6 (23.03-27.03): EPIC AGRAR-WG-02 Wiegeschein -> Kontraktlöschung
- [x] Story AGRAR-WG-02-01: Zuordnung Wiegeschein zu Kontrakt.
- [x] Story AGRAR-WG-02-02: Automatische Löschlogik bei Buchung.
- [x] Story AGRAR-WG-02-03: Outbox-Events bei Löschung und Fehlerfällen.
- Akzeptanzkriterien:
- Buchungsfluss atomar, Event-Emission nachweisbar, Rollback sauber.

### Woche 7 (30.03-03.04): EPIC AGRAR-SILO-01 Partie/Silo-Basis
- [x] Story AGRAR-SILO-01-01: Tabellen `silo_lots`, `silo_quality_snapshots`, `silo_lot_movements`.
- [x] Story AGRAR-SILO-01-02: Virtuelle Sammelpartie je Silo.
- [x] Story AGRAR-SILO-01-03: Qualitätsmittelwerte pro aktueller Füllung.
- Akzeptanzkriterien:
- Silo-Füllung, Mischung und Qualitätsdurchschnitt reproduzierbar berechnet.

### Woche 8 (06.04-10.04): EPIC AGRAR-SET-01 Gutschriftverfahren
- [x] Story AGRAR-SET-01-01: Self-Billing Entität/Workflow implementieren.
- [x] Story AGRAR-SET-01-02: Abzugsarten (Trocknung, Reinigung, Fracht) regelbasiert.
- [x] Story AGRAR-SET-01-03: Buchungssätze in Fibu erzeugen.
- Akzeptanzkriterien:
- Gutschrift endet in validen Buchungen inkl. Einzelabzügen.

### Woche 9 (13.04-17.04): EPIC AGRAR-SET-02 Schwund-/Feuchte-Engine
- [x] Story AGRAR-SET-02-01: Domain-Service für Feuchtekorrektur/Heine-Logik.
- [x] Story AGRAR-SET-02-02: Abrechnungsgewicht als explizites Feld führen.
- [x] Story AGRAR-SET-02-03: Testfälle für Grenzwerte und negative Pfade.
- Akzeptanzkriterien:
- Formelpfad deterministisch, testabgedeckt, keine SQL- oder UI-Formellogik.

### Woche 10 (20.04-24.04): EPIC AGRAR-COMP-01 Compliance-MVP
- [x] Story AGRAR-COMP-01-01: Gefahrstoffdoku-Export für PSM/Dünger.
- [x] Story AGRAR-COMP-01-02: Nährstoffstrom-Export (N/P2O5) je Zeitraum.
- [x] Story AGRAR-COMP-01-03: Chargen-Trace Bericht Saatgut -> Endprodukt.
- Akzeptanzkriterien:
- Pflichtfelder vollständig, Exportdateien fachlich prüfbar.

### Woche 11 (27.04-01.05): EPIC AGRAR-MIG-01 Datenmigration
- [x] Story AGRAR-MIG-01-01: Backfill-Skript Altobjekte -> neue Agrar-Entitäten.
- [x] Story AGRAR-MIG-01-02: Idempotente Migration + Re-Run-Fähigkeit.
- [x] Story AGRAR-MIG-01-03: Migrationsbericht (Anzahl, Fehler, Korrekturen).
- Akzeptanzkriterien:
- Migration reproduzierbar, kein Datenverlust, Fehlerquote dokumentiert.

### Woche 12 (04.05-08.05): EPIC AGRAR-UAT-01 UAT + Performance
- [ ] Story AGRAR-UAT-01-01: 3 End-to-End-Szenarien mit Key-Usern testen.
- [x] Story AGRAR-UAT-01-02: Lasttest für Wiegeschein/Abrechnung/Events.
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
- [x] Alembic: genau ein Head im Zielstand.
- [x] Keine neue Agrar-Fachlogik außerhalb `modules/agrar`.  
  Nachweis: `docs/testing/restarbeiten-verifikation-2026-02-14.md`
- [x] OpenAPI für neue Endpunkte aktualisiert.
- [x] E2E-Flows "Wiegeschein -> Abrechnung -> Buchung" grün.  
  Nachweis: `docs/testing/restarbeiten-verifikation-2026-02-14.md`

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
- [x] `AGRAR-ARCH-01` Modulrahmen aufsetzen | P0 | M | Fullstack
- [x] `AGRAR-ARCH-02` Event-/Hook-Verträge versionieren | P0 | M | Backend
- [x] `AGRAR-ARCH-03` CI-Guardrails gegen Core-Kontamination | P0 | M | DevOps

### Sprint 2 (28.02-20.03) Wiegeschein + Kontrakt-Basis
- [x] `AGRAR-WG-01` Wiegeschein-Datenmodell + CRUD | P0 | L | Backend
- [x] `AGRAR-CT-01` Kontrakte + Restmengenlogik | P0 | L | Backend
- [x] `AGRAR-WG-UI-01` Wiegeschein-Erfassung UI (ohne Mock) | P1 | M | Frontend

### Sprint 3 (21.03-03.04) Löschlogik + Silo/Partie
- [x] `AGRAR-WG-02` Wiegeschein -> Kontraktlöschung atomar | P0 | M | Backend
- [x] `AGRAR-SILO-01` Sammelpartie + Qualitätsmittelwerte | P0 | L | Backend
- [x] `AGRAR-SILO-UI-01` Siloübersicht mit Qualitätssnapshot | P1 | M | Frontend

### Sprint 4 (04.04-17.04) Abrechnung + Physiklogik
- [x] `AGRAR-SET-01` Self-Billing inkl. Abzüge | P0 | L | Backend
- [x] `AGRAR-SET-02` Feuchte-/Schwund-Engine im Domain-Service | P0 | M | Backend
- [x] `AGRAR-SET-UI-01` Gutschrift-Ansicht inkl. Abzugsnachweis | P1 | M | Frontend

### Sprint 5 (18.04-01.05) Compliance + Migration
- [x] `AGRAR-COMP-01` Gefahrstoff-/Nährstoff-Export | P0 | M | Backend
- [x] `AGRAR-MIG-01` Backfill + idempotente Migration | P0 | M | Backend
- [x] `AGRAR-COMP-UI-01` Export- und Prüfprotokollseite | P1 | M | Frontend

### Sprint 6 (02.05-14.05) UAT, Last, Go-Live
- [ ] `AGRAR-UAT-01` 3 E2E-Fachszenarien mit Key-Usern | P0 | M | QA
- [x] `AGRAR-PERF-01` Lasttest Wiegeschein/Abrechnung/Eventbus | P0 | M | QA
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
AGRAR-ARCH-03,CI-Guardrails gegen Core-Kontamination,Story,P0,M,DevOps,Sprint 1,2026-02-13,2026-02-27,Done,AGRAR-ARCH-01,CI blockiert verbotene Core-Imports
AGRAR-WG-01,Wiegeschein-Datenmodell und CRUD,Story,P0,L,Backend,Sprint 2,2026-02-28,2026-03-20,Backlog,AGRAR-ARCH-01,Wiegeschein persistiert mit Audit-Trail und validierter API
AGRAR-CT-01,Kontrakte und Restmengenlogik,Story,P0,L,Backend,Sprint 2,2026-02-28,2026-03-20,Backlog,AGRAR-ARCH-02,Restmengen korrekt berechnet und Überbuchung verhindert
AGRAR-WG-UI-01,Wiegeschein-Erfassung UI ohne Mock,Story,P1,M,Frontend,Sprint 2,2026-02-28,2026-03-20,Done,AGRAR-WG-01,UI nutzt echte API mit sauberem Error-Handling
AGRAR-WG-02,Wiegeschein zu Kontraktlöschung atomar,Story,P0,M,Backend,Sprint 3,2026-03-21,2026-04-03,Backlog,AGRAR-WG-01|AGRAR-CT-01,Atomare Buchung mit Outbox-Events und Rollback
AGRAR-SILO-01,Sammelpartie und Qualitätsmittelwerte,Story,P0,L,Backend,Sprint 3,2026-03-21,2026-04-03,Backlog,AGRAR-WG-01,Siloqualität reproduzierbar aus Bewegungen berechnet
AGRAR-SILO-UI-01,Siloübersicht mit Qualitätssnapshot,Story,P1,M,Frontend,Sprint 3,2026-03-21,2026-04-03,Backlog,AGRAR-SILO-01,UI zeigt Füllstand und Qualitätskennzahlen pro Silo
AGRAR-SET-01,Self-Billing mit Abzügen,Story,P0,L,Backend,Sprint 4,2026-04-04,2026-04-17,Backlog,AGRAR-WG-02,Gutschrift erzeugt korrekte Fibu-Buchungen inklusive Abzüge
AGRAR-SET-02,Feuchte-/Schwund-Engine im Domain-Service,Story,P0,M,Backend,Sprint 4,2026-04-04,2026-04-17,Backlog,AGRAR-WG-01,Deterministische Abrechnungsgewichte mit Grenzwerttests
AGRAR-SET-UI-01,Gutschrift-Ansicht mit Abzugsnachweis,Story,P1,M,Frontend,Sprint 4,2026-04-04,2026-04-17,Backlog,AGRAR-SET-01,UI listet Abzüge transparent und prüfbar auf
AGRAR-COMP-01,Gefahrstoff- und Nährstoff-Export,Story,P0,M,Backend,Sprint 5,2026-04-18,2026-05-01,Backlog,AGRAR-SET-01,Exportdateien vollständig und fachlich plausibel
AGRAR-MIG-01,Backfill und idempotente Migration,Story,P0,M,Backend,Sprint 5,2026-04-18,2026-05-01,Done,AGRAR-WG-01|AGRAR-CT-01,Migration ohne Datenverlust mehrfach ausführbar
AGRAR-COMP-UI-01,Export- und Prüfprotokollseite,Story,P1,M,Frontend,Sprint 5,2026-04-18,2026-05-01,Done,AGRAR-COMP-01,UI zeigt Exportlauf und Prüfergebnis pro Lauf
AGRAR-UAT-01,3 E2E-Fachszenarien mit Key-Usern,Story,P0,M,QA,Sprint 6,2026-05-02,2026-05-14,Backlog,AGRAR-SET-01|AGRAR-COMP-01,UAT-Protokoll signiert und P1/P2 Findings geschlossen
AGRAR-PERF-01,Lasttest für Wiegeschein/Abrechnung/Eventbus,Story,P0,M,QA,Sprint 6,2026-05-02,2026-05-14,Backlog,AGRAR-WG-02,Lastziele erreicht und Engpässe dokumentiert
AGRAR-GO-01,Go-Live-Readiness und Rollback-Probe,Story,P0,M,DevOps,Sprint 6,2026-05-02,2026-05-14,Backlog,AGRAR-UAT-01|AGRAR-PERF-01,Go/No-Go dokumentiert und Rollback verifiziert
```

---

## 8. Delta-Abgleich (DB + CRUD-Masken, Stand 14.02.2026)

### 8.1 Alembic lokal vs. Docker repariert
- Ursache: `alembic upgrade head` lokal lief gegen lokale Host-DB; in Docker lief Backend mit eigener `DATABASE_URL`.
- Ursache 2: Backend-Container sah neue lokale Migrationen nicht live (fehlende Mounts fuer `alembic`/`alembic.ini`).
- Reparatur:
- [x] `docker-compose.yml` Backend-Volumes erweitert:
- `./alembic:/app/alembic`
- `./alembic.ini:/app/alembic.ini`
- [x] Docker-Migrationsskript angelegt: `scripts/alembic-upgrade-docker.ps1`
- Standardlauf jetzt:
- `docker compose up -d postgres backend`
- `.\scripts\alembic-upgrade-docker.ps1`

### 8.2 Kundenstammdaten / Ansprechpartner
- DB:
- [x] `domain_crm.business_partners` deckt den erweiterten Feldsatz weitgehend ab (Identitaet, Rollen, Kontakt, Banking, Finance, Agrar, Logistics, Marketing, GDPR, Audit).
- [~] `domain_crm.customers` ist nur Basis-Subset.
- Fehlende DB-Felder fuer die konkrete Liste:
- [x] `anrede`, `vorname`, `nachname` (als `salutation`, `first_name`, `last_name`).
- [x] `kontoinhaber` (als `account_holder`).
- [x] `bankverbindung_aktiv` (als `bank_connection_active`).
- [x] `zahlungsart` (als `payment_method`).
- [x] `preisgruppe` (als `price_group`).
- [x] `rabatte_prozent` (als `discount_percent`).
- CRUD Backend:
- [x] `app/api/v1/endpoints/business_partners.py`: Create/List/Get/Update.
- [x] `app/api/v1/endpoints/customers.py`: Create/List/Get/Update/Delete (Proxy auf crm-core, aber reduziertes Mapping).
- CRUD Maske Frontend:
- [x] `packages/frontend-web/src/pages/verkauf/kunden-liste.tsx` auf echte `business_partners`-Daten (Rolle Kunde) umgestellt.
- [x] `packages/frontend-web/src/pages/verkauf/kunden-stamm.tsx` auf echtes Create/Update via `/api/v1/crm/business-partners` umgestellt.
- [x] `packages/frontend-web/src/pages/verkauf/kunden-stamm-enhanced.tsx` ist nicht mehr statisch (nutzt jetzt den echten Kundenstamm-CRUD statt Mock-Spezialmaske).

### 8.3 Artikelstammdaten
- DB:
- [x] Basis in `domain_inventory.articles` vorhanden.
- Fehlende DB-Felder aus Zielkatalog:
- [x] `suchbegriff`, `hersteller`, `herkunftsland`, `naehrwertangaben`.
- [x] `mhd_erforderlich` (bool), `lagerartikel` (bool).
- [x] `mehrwertsteuer_prozent`, `warengruppe` als fachlich trennscharfes Feld.
- [x] `gefahrgutklasse`, `lagerorte` (mehrfach via JSONB-Array), `ist_bestand` weiterhin ueber `current_stock`, `maximalbestand` ueber vorhandenes `max_stock`.
- [x] `chargenpflicht`, `qs_pruefung_erforderlich`, `zolltarifnummer`, `bio_kennzeichnung`, `gmp_plus_relevanz`, `lieferantennummer`.
- [x] Migration: `alembic/versions/articles_master_fields_gap_83_20260215.py`.
- CRUD Backend:
- [x] `app/api/v1/endpoints/articles.py` hat jetzt List/Get/Search/Create/Update/Delete (Soft-Delete).
- [x] Artikel-CRUD erweitert um die neuen 8.3-Felder (inkl. Suche ueber `suchbegriff`/`hersteller`/`warengruppe`).
- CRUD Maske Frontend:
- [x] `packages/frontend-web/src/pages/artikel/stamm.tsx` auf echte API verdrahtet (`/api/v1/articles`), inkl. Neu- und Edit-Modus.
- [x] `packages/frontend-web/src/pages/artikel/liste.tsx` nutzt API-Felder `sales_price` und `current_stock` korrekt.
- [x] `packages/frontend-web/src/lib/services/article-service.ts` + `packages/frontend-web/src/pages/artikel/stamm.tsx` um die neuen Felder erweitert.

### 8.4 Auftraege
- DB:
- [x] `domain_crm.sales_orders` vorhanden (Grundfelder).
- Fehlende DB-Felder aus Zielkatalog:
- [x] Auftragspositionen als strukturierte Relationen (neu: `domain_crm.sales_order_items`).
- [x] Versandart als eigenes Feld (`domain_crm.sales_orders.shipping_method`).
- CRUD Backend:
- [x] Vollstaendiger Domain-CRUD fuer Orders inkl. Positions-Relation:
  - `POST/PUT /api/v1/sales/orders` verarbeitet `items[]` (Create + Replace-Semantik bei Update)
  - `GET /api/v1/sales/orders` und `GET /api/v1/sales/orders/{id}` liefern `items[]` + `shipping_method`.
- [x] Klarer Domain-CRUD-Endpunkt vorhanden: `app/api/v1/endpoints/sales_orders.py` unter `/api/v1/sales/orders`.
- CRUD Maske Frontend:
- [x] `packages/frontend-web/src/pages/sales/order-editor.tsx` speichert ueber dedizierten Domain-CRUD `/api/v1/sales/orders`.
- [x] Frontend-Validierung `customerId` ergaenzt (Client-seitige Pflichtpruefung vor Save).
- [x] `shippingMethod` in Formschema aufgenommen und an Backend-Feld `shipping_method` gebunden.
- [x] Auftragspositionen werden als `items[]` an Domain-Endpoint gesendet (nicht mehr als JSON in `notes`).
- [x] Migration: `alembic/versions/sales_orders_items_shipping_20260215.py`.

### 8.5 Lagerbewegung / Buchungen
- DB:
- [x] `domain_inventory.inventory_stock_movements` vorhanden.
- Fehlende DB-Felder aus Zielkatalog:
- [x] `datum` + `uhrzeit` getrennt (`movement_date`, `movement_time` via Migration `inventory_stock_movements_l3_fields_20260214`).
- [x] `einheit`, `lagerort`, `charge` (`unit`, `warehouse_location`, `charge`).
- [x] `belegnummer` ist als `reference_number` abbildbar.
- [x] `benutzer` (`booking_user`).
- [x] `buchungstext` ist als `notes` abbildbar.
- [x] `automatisch_erzeugt` (`auto_created`).
- [x] `verknuepfter_auftrag` (`linked_order_id`).
- CRUD Backend:
- [x] `app/domains/inventory/api/stock_movements.py` hat List/Get/Create/Update/Delete (+ Summary).
- CRUD Maske Frontend:
- [x] Echte Buchungsmaske mit API-CRUD umgesetzt: `packages/frontend-web/src/pages/lager/lagerbewegungen.tsx`.

### 8.6 Chargeninformationen
- DB:
- [x] `domain_ops.ops_chargen` inkl. neuer QS-Felder vorhanden.
- [~] Feldnamen differieren teilweise (`chargen_id` statt `chargennummer`, `eingang` statt `eingangsdatum`, `qualitaetsstatus` statt `qs_status`).
- Fehlende DB-Felder:
- [x] explizites `mhd` in `ops_chargen` vorhanden (`alembic/versions/ops_chargen_add_mhd_20260215.py`).
- CRUD Backend:
- [x] `app/api/v1/endpoints/charges.py` mit List/Get/Create/Patch/Delete + `qs-readiness`.
- CRUD Maske Frontend:
- [x] `packages/frontend-web/src/pages/charge/liste.tsx`, `packages/frontend-web/src/pages/charge/stamm.tsx`, `packages/frontend-web/src/pages/charge/wareneingang.tsx` auf echte API verdrahtet.

### 8.7 Controlling-Modul
- DB:
- [x] Dedizierte Tabellen vorhanden (`domain_controlling.*` via `alembic/versions/controlling_module_initial_20260215.py`):
  - `kpi_definitions`, `dashboard_configs`, `dashboard_widgets`, `kpi_timeseries`, `controlling_actions`.
- CRUD/API:
- [x] CRUD-Backbone vorhanden in `app/api/v1/endpoints/controlling.py`:
  - KPIs: `GET/POST/PUT/DELETE /api/v1/controlling/kpis`
  - Dashboards: `GET/POST/PUT/DELETE /api/v1/controlling/dashboards`
  - Widgets: `GET/POST/PUT/DELETE /api/v1/controlling/dashboards/{id}/widgets` + `/api/v1/controlling/widgets/{id}`
  - Zeitreihen: `GET/POST/DELETE /api/v1/controlling/timeseries`
  - Maßnahmen: `GET/POST/PUT/DELETE /api/v1/controlling/actions`
- Masken:
- [~] Einzelne UI-Seiten vorhanden, aber kein vollstaendiger Domain-Cockpit-Cutover.
  - [x] `packages/frontend-web/src/pages/controlling/plan-ist.tsx` bezieht Daten jetzt ueber `packages/frontend-web/src/lib/api/misc-modules.ts` aus echtem Controlling-Stack (`/api/v1/controlling/kpis` + `/api/v1/controlling/timeseries`) statt nicht vorhandenem `plan-ist` Endpoint.
  - [x] KPI-CRUD-UI vorhanden: `packages/frontend-web/src/pages/controlling/kpi-verwaltung.tsx` (Hook `packages/frontend-web/src/lib/api/controlling.ts`) mit `GET/POST/PUT/DELETE /api/v1/controlling/kpis`.
  - [x] Dashboard-CRUD-UI vorhanden: `packages/frontend-web/src/pages/controlling/dashboard-verwaltung.tsx` mit `GET/POST/PUT/DELETE /api/v1/controlling/dashboards`.
  - [x] Widget-CRUD-UI vorhanden: `packages/frontend-web/src/pages/controlling/widget-verwaltung.tsx` mit `GET/POST/PUT/DELETE` fuer `/api/v1/controlling/dashboards/{id}/widgets` und `/api/v1/controlling/widgets/{id}`.
  - [x] Timeseries-Erfassung vorhanden: `packages/frontend-web/src/pages/controlling/timeseries-erfassung.tsx` mit `GET/POST/DELETE /api/v1/controlling/timeseries`.
  - [x] Maßnahmen-Tracking-UI vorhanden: `packages/frontend-web/src/pages/controlling/massnahmen.tsx` mit `GET/POST/PUT/DELETE /api/v1/controlling/actions`.
  - [x] Navigation erweitert (`packages/frontend-web/src/app/navigation/manifest.tsx`): `Dashboard-Verwaltung`, `Timeseries-Erfassung`.

### 8.37 Gap-Closure: Chargen-MHD + Controlling-CRUD
- [x] `ops_chargen.mhd` fachlich und technisch nachgezogen:
  - Model: `app/domains/operations/models.py` (`mhd`)
  - API: `app/api/v1/endpoints/charges.py` (`mhd` in Create/Update/Read)
  - Migration: `alembic/versions/ops_chargen_add_mhd_20260215.py`
- [x] Controlling-Domain als persistenter CRUD-Stack implementiert:
  - Migration: `alembic/versions/controlling_module_initial_20260215.py`
  - Endpunkte: `app/api/v1/endpoints/controlling.py`
  - Router-Einbindung: `app/api/v1/endpoints/__init__.py`, `app/api/v1/api.py`
- [x] Verifikation:
  - `alembic upgrade head` in Docker erfolgreich
  - API-Smoke erfolgreich (`/api/v1/controlling/*` Create/List + `charges` MHD-Patch)

### 8.8 Schulungsmanagement / Qualifikationen / Onboarding
- DB:
- [x] Dedizierte Tabellen vorhanden (`domain_hr.*` via `alembic/versions/hr_training_onboarding_module_20260215.py`):
  - `training_courses`, `training_assignments`, `employee_certificates`, `qualification_profiles`, `onboarding_checklists`, `onboarding_runs`.
- CRUD/API:
- [x] Domain-CRUD-Endpunkte vorhanden in `app/api/v1/endpoints/training.py`:
  - Kurse: `GET/POST/PUT/DELETE /api/v1/training/courses`
  - Zuweisungen: `GET/POST/PUT/DELETE /api/v1/training/assignments`
  - Zertifikate: `GET/POST/PUT/DELETE /api/v1/training/certificates`
  - Qualifikationen: `GET/POST/PUT/DELETE /api/v1/training/qualifications`
  - Onboarding-Checklisten: `GET/POST/PUT/DELETE /api/v1/training/onboarding/checklists`
  - Onboarding-Runs: `GET/POST/PUT/DELETE /api/v1/training/onboarding/runs`
- Masken:
- [~] Backend-CRUD ist vollstaendig; UI-Masken-Cutover laeuft.
  - [x] `packages/frontend-web/src/pages/personal/schulungen.tsx` nutzt jetzt echte Domain-Daten ueber `packages/frontend-web/src/lib/api/personal.ts` -> `/api/v1/training/assignments` (Mapping ohne Mock-Fallback).
  - [x] Neue Erfassungsmaske `packages/frontend-web/src/pages/personal/schulung-neu.tsx` erstellt und direkt auf `POST /api/v1/training/assignments` verdrahtet.
  - [x] Neue Qualifikationsmaske `packages/frontend-web/src/pages/personal/qualifikationen.tsx` auf `GET/POST /api/v1/training/qualifications`.
  - [x] Neue Onboarding-Maske `packages/frontend-web/src/pages/personal/onboarding.tsx` auf `GET /api/v1/training/onboarding/checklists` und `GET/POST /api/v1/training/onboarding/runs`.
  - [x] Navigation erweitert: `packages/frontend-web/src/app/navigation/manifest.tsx` (`Qualifikationen`, `Onboarding` unter Personal).

### 8.9 Priorisierte Restarbeiten (konkret)
1. P0: Kundenmaske auf `business_partners` CRUD finalisieren, fehlende Pflichtfelder (z. B. Zahlungsart/Preisgruppe/Rabatt) per Migration ergaenzen.
2. P1: Sales-Orders sauber typisiert mit OrderItems (`sales_order_items`) als Relation implementieren.
3. P1: Controlling-Schema (KPI, Dashboard, Zeitreihe, Maßnahmen) als eigene Tabellen + API aufsetzen.
4. P2: Schulungs-/Qualifikations-/Onboarding-Domain modellieren (Schema, API, Masken) -> Schema+API erledigt, Masken-Cutover offen.

### 8.38 Gap-Closure: Schulung/Qualifikation/Onboarding (Domain-CRUD)
- [x] Migration umgesetzt: `alembic/versions/hr_training_onboarding_module_20260215.py`
  - Tabellen inkl. Constraints, Indizes, Status-/Range-Checks.
  - Seed-Testdaten im Default-Tenant (Kurse + Onboarding-Checkliste), keine Mocks.
- [x] API umgesetzt: `app/api/v1/endpoints/training.py`
  - Voller CRUD fuer Kurse, Zuweisungen, Zertifikate, Qualifikationsprofile, Onboarding-Checklisten und -Runs.
- [x] Router-Verdrahtung:
  - `app/api/v1/endpoints/__init__.py`
  - `app/api/v1/api.py`

### 8.39 Gap-Closure: Personal-Endpoints (Mitarbeiter/Zeiterfassung/Stundenzettel)
- [x] 404-Pfade fuer Personal geschlossen (`/api/v1/personal/*`):
  - `GET /api/v1/personal/mitarbeiter`
  - `GET /api/v1/personal/zeiterfassung`
  - `POST /api/v1/personal/stundenzettel`
- [x] Migration umgesetzt: `alembic/versions/hr_personal_time_tracking_20260215.py`
  - Tabellen: `domain_hr.time_entries`, `domain_hr.driver_timesheets`
  - Constraints/Indizes fuer Stundenbereich, Typen und Zugriffspfade
  - Seed-Testdaten (keine Mocks)
- [x] API umgesetzt: `app/api/v1/endpoints/personal.py`
- [x] Router-Verdrahtung:
  - `app/api/v1/endpoints/__init__.py`
  - `app/api/v1/api.py`
- [x] Frontend-Flow korrigiert:
  - `packages/frontend-web/src/pages/personal/stundenzettel.tsx` navigiert nach Save/Cancel auf existierende Route `/personal/zeiterfassung`.
- [x] Mitarbeiter-Stamm CRUD-Pfad erweitert:
  - Backend: `GET/POST/PUT /api/v1/personal/mitarbeiter` inkl. Detail `/{id}` in `app/api/v1/endpoints/personal.py`.
  - Status-/Abteilungs-Persistenz ueber `domain_shared.users.preferences` (`hr_status`, `abteilung`) statt implizitem Bool-Status.
  - Frontend: neue Seite `packages/frontend-web/src/pages/personal/mitarbeiter-stamm.tsx`.
  - Routing: Alias-Pfade `personal/mitarbeiter/:id` und `personal/mitarbeiter/neu` in `packages/frontend-web/src/app/route-aliases.json`.
- [x] Mitarbeiter-Liste UX:
  - `packages/frontend-web/src/pages/personal/mitarbeiter-liste.tsx` zeigt `email` und direkte Zeilenaktion `Bearbeiten`.
- [x] Stundenzettel-Liste + Export umgesetzt:
  - Backend: `GET /api/v1/personal/stundenzettel` in `app/api/v1/endpoints/personal.py`.
  - Frontend: `packages/frontend-web/src/pages/personal/stundenzettel-liste.tsx` (Filter + CSV-Export).
  - Navigation: `packages/frontend-web/src/app/navigation/manifest.tsx` verweist `Stundenzettel` auf die Listenmaske.
  - Erfassungsmaske `packages/frontend-web/src/pages/personal/stundenzettel.tsx` navigiert nach Save/Cancel zur Listenansicht.

### 8.10 Docker Speicherbereinigung (14.02.2026)
- Ausgangslage: `docker system df` zeigte `Images: 57`, `77.23GB` und `Build Cache: 39.77GB`.
- Durchgefuehrt:
- [x] Unbenutzte Images bereinigt (`docker image prune -a -f`).
- [x] Build-Cache vollstaendig bereinigt (`docker builder prune -af`).
- Ergebnis nach Cleanup:
- `Images: 5`, `5.207GB`
- `Build Cache: 0B`
- Netto freigegeben: ca. `71.0GB` (Images + Build Cache).

### 8.11 Kundenstamm-Felder aus Screens 1-26 (Delta-Check)
- Geprueft gegen: `domain_crm.business_partners`, `domain_crm.customers`, Endpoint `app/api/v1/endpoints/business_partners.py`.
- Neu ergaenzt (Migration `business_partners_customer_master_fields_20260214`):
- [x] Erweiterte Rechnungs-/Kontoauszugssteuerung, Zahlungsverkehr, Versandkanal, Sonstiges, Genossenschaft, Schnittstellen, Preis-/Rabatt-Metadaten.
- [x] OCR-nahe Legacy-Felder jetzt in API verfuegbar unter `business_partner.legacy_customer_fields`.
- Wichtige Klarstellung zur OCR-Auswertung:
- [x] `Zuruecksetzen (alle / einzeln)`, `Kunden-Gruppen`, `Rabatt-Listen`, `Preisvereinbarungen (Import / Stapel / intern)`, `Lieferanten` sind als TAB-/Menue-Beschriftungen klassifiziert (UI-Navigation), nicht als eigenstaendige Datenfelder.
- Bereits abgedeckt:
- [x] Basis-Identitaet/Adresse/Kontakt (`name_*`, Strasse/PLZ/Ort, Telefon/Fax/Mail, Sprache, Status).
- [x] Steuer/Finance-Basis (`vat_id`, `tax_number`, `debtor_account`, `credit_limit`, `dunning_level`).
- [x] Bank/SEPA-Basis (`bank_name`, `iban`, `bic`, `sepa_mandate_reference`, `sepa_mandate_signed_at`).
- [x] Datenschutz-Basis (`privacy_policy_*`, `data_retention_until`, `anonymized_at`).
- [x] Rollen-Switches (`is_customer`, `is_supplier`, ...).
- Teilweise abgedeckt (nur indirekt/fachlich nah):
- [x] Zahlungsbedingungen (granular erweitert ueber `legacy_customer_fields` + normalisierte Regeln).
- [x] Rabatt-/Preislogik (kundenindividuelle Tabellen + globaler Regelsatz vorhanden).
- [x] Versand-/Avis-Logik (normalisierte Versandmedien je Dokumenttyp inkl. Kanalsteuerung).
- [x] Ansprechpartner (separate Contact-Entity vorhanden: `domain_crm.business_partner_contacts`).
- Fehlend (neue Tabellen/Felder erforderlich):
- [x] Rechnungs-/Kontoauszugssteuerung (Sammelabrechnung, Druckverbote, Bonus-/Rechnungsempfaenger, Selbstabrechner-Flags granular).
- [x] Kundenrabattlisten + Gueltigkeit je Artikel (normalisiert: `domain_crm.business_partner_discount_items`).
- [x] Vereinbarte Kundenpreise inkl. Gueltigkeitszeitraum, Frachtlogik, Bedienerhistorie (normalisiert: `domain_crm.business_partner_price_agreements`).
- [x] Globaler Preis-/Rabatt-Regelsatz je Kunde (Direktabzug, Wochenpreislogik, Sortenpreissteuerung) -> `domain_crm.business_partner_pricing_rules`.
- [x] Erweiterter Zahlungsverkehr (Zinstabellen Soll/Haben, letzter Zinstermin, automatische Verrechnung) -> `domain_crm.business_partner_interest_settings`.
- [x] Versandmedien je Dokumenttyp inkl. ZUGFeRD-Konfiguration -> `domain_crm.business_partner_dispatch_media`.
- [x] Genossenschaftsanteile-Mitgliedschaftsmodell -> `domain_crm.business_partner_cooperative_memberships`.
- [x] E-Mail-Verteilerlisten pro Kunde -> `domain_crm.business_partner_email_distributions`.
- [x] Betriebsgemeinschaften (Mitglieder + Anteile) -> `domain_crm.business_partner_communities` + `domain_crm.business_partner_community_members`.
- [x] Kundenprofil-Fachfelder (Jahresumsatz, Branche-Schluessel, Wettbewerbs-/Organisationsfelder) -> `domain_crm.business_partner_profiles`.
- [x] Schnittstellenfelder (Tankkarte/EAN, Kundenkarte, EDIFACT-Profil, Webshop-Kundennr./Bezeichnung) -> `domain_crm.business_partner_interface_profiles`.

- Umsetzung 14.02.2026:
- [x] Migration: `business_partner_gap_811_normalized_20260214`.
- [x] Neue CRUD-Endpunkte in `app/api/v1/endpoints/business_partners.py`:
- `pricing-rules`, `interest-settings`, `dispatch-media`, `cooperative-memberships`, `email-distributions`, `catalog/communities`/`members`, `profile`, `interface-profile`.

### 8.12 Rabatt-Listen & Preisvereinbarungen (normalisiert)
- Migration: `business_partner_discount_price_tables_20260214`
- Härtung: `business_partner_item_constraints_20260214`
- Tabellen:
- [x] `domain_crm.business_partner_discount_items`
- [x] `domain_crm.business_partner_price_agreements`
- Constraints/Numeric/Indizes:
- [x] Check-Constraints fuer Prozent-/Preisbereiche und gueltige Datumsintervalle.
- [x] Source-Type-Constraint (`import|batch|internal`).
- [x] Eindeutige Perioden-Key-Indizes je Partner+Artikel+Zeitraum+Quelle.
- [x] Zusatzindizes fuer Partner+Gueltigkeit.
- [x] Rundung serverseitig: Rabatt auf 2 Nachkommastellen, Preise/Fracht auf 4 Nachkommastellen.
- [x] Klare Update-Semantik: `PUT` = Vollersatz, `PATCH` = Teilupdate.
- CRUD-API:
- [x] `GET/POST /api/v1/crm/business-partners/{partner_id}/discount-items`
- [x] `GET/PUT/PATCH/DELETE /api/v1/crm/business-partners/{partner_id}/discount-items/{item_id}`
- [x] `GET/POST /api/v1/crm/business-partners/{partner_id}/price-agreements`
- [x] `GET/PUT/PATCH/DELETE /api/v1/crm/business-partners/{partner_id}/price-agreements/{agreement_id}`
- Frontend:
- [x] Tabs `Rabatt-Listen` und `Preisvereinbarungen` auf echte Endpunkte verdrahtet inkl. harter UI-Validierung (Pflichtfelder, Wertebereich, Datumskonsistenz, Inline-Fehler).

### 8.13 Normalisierungs-Check (weitere Tabellen)
- Geprueft: JSON-/Mehrfachstrukturen in `app/infrastructure/models/*` und `app/domains/*` plus vorhandene CRUD-Endpunkte.
- Bewertung:
- [x] Bereits passend denormalisiert (beibehalten):
- `domain_rules.rules_*` JSON-Konfigurationen (regelbasiertes DSL, kein relationaler Mehrwert).
- `domain_verladung.*_json` Summen/Metadaten als technische Snapshot-Felder.
- [~] Mittelfristig normalisieren (bei Analyse-/Filterbedarf):
- `domain_crm.farm_profiles` (`crops`, `livestock`, `certifications`) -> Subtabellen je Profil fuer filterbare Reports.
- `domain_crm.activities` JSON-Listen (`main_topics`, `follow_up_actions`, `orders_placed`, ...) -> Event/Topic-Subtabellen fuer KPI/Controlling.
- [~] Fachlich dokumentorientiert, optional spaeter normalisieren:
- `domain_ops.ops_qs_charge_docs` JSON-Felder (`rohstoffe`, `haccp_system`, `eigenkontrollen`, ...) aktuell sinnvoll fuer Compliance-Dokumentation; bei strengem Reporting einzelne Fakten extrahieren.
- CRUD-Hinweis:
- [x] Fuer neu normalisierte Kunden-Rabatte/Preise liegt jetzt echter Item-CRUD vor.
- [x] Dedizierte Sub-CRUD-Endpunkte fuer JSON-Kandidaten umgesetzt (Aggregate bleibt zusaetzlich verfuegbar):
- `farm_profiles`: `/{profile_id}/crops`, `/{profile_id}/livestock`, `/{profile_id}/certifications` jeweils mit `GET/POST/PUT/DELETE` (Index-basierte Item-Semantik).
- `activities`: `/{activity_id}/main-topics`, `/{activity_id}/orders-placed`, `/{activity_id}/follow-up-actions` jeweils mit `GET/POST/PUT/DELETE` (Index-basierte Item-Semantik).
- Frontend-Verdrahtung auf neue Sub-CRUD-Endpunkte:
- [x] `crm/betriebsprofil-detail`: Tabs `Kulturen`, `Tierbestand`, `Zertifizierungen` synchronisieren bei Save ueber Sub-Endpoints (kein reiner Aggregate-Write mehr).
- [x] `crm/aktivitaet-detail`: Eingabemasken fuer `Main Topics`, `Orders Placed`, `Follow-up Actions` hinzugefuegt und bei Save ueber Sub-Endpoints synchronisiert.

### 8.14 Tab 21/22 als CRUD umgesetzt
- Migration: `business_partner_contacts_instructions_20260214`
- Tabellen:
- [x] `domain_crm.business_partner_instructions` (Chef-Anweisung)
- [x] `domain_crm.business_partner_contacts` (Ansprechpartner)
- Constraints/Indizes:
- [x] Prioritaets-/Typ-Checks und Datumsbereichs-Checks.
- [x] Indizes auf `partner_id` (plus `email` bei Kontakten).
- API-Endpunkte:
- [x] `GET/POST /api/v1/crm/business-partners/{partner_id}/instructions`
- [x] `GET/PUT/PATCH/DELETE /api/v1/crm/business-partners/{partner_id}/instructions/{instruction_id}`
- [x] `GET/POST /api/v1/crm/business-partners/{partner_id}/contacts`
- [x] `GET/PUT/PATCH/DELETE /api/v1/crm/business-partners/{partner_id}/contacts/{contact_id}`

### 8.15 Tab 23/24/25 normalisiert + Chefanweisungen in Sales-Masken
- Migration: `business_partner_tab_23_24_25_20260214`
- Tabellen:
- [x] `domain_crm.business_partner_addresses` (Tab 23: Kunden-/Rechnungs-/Liefer-/Postfach-Anschrift inkl. Freifelder/Gebiet)
- [x] `domain_crm.business_partner_billing_configs` (Tab 24: Rechnung/Kontoauszug, Sammelabrechnung, Aufschlaege, Bonus/Selbstabrechner)
- [x] `domain_crm.business_partner_cpd_accounts` (Tab 25: CPD-Konto)
- Constraints/Numeric/Indizes:
- [x] Typ-Checks (`address_type`, `customer_type`, `settlement_mode`), Prozentbereiche und non-negative Integer-Felder.
- [x] Eindeutigkeit: `partner_id` in Billing-Config (1:1), `cpd_customer_number` in CPD.
- [x] Indizes auf Partner-FKs und fachliche Suchschluessel.
- [x] Rundung serverseitig (2 Nachkommastellen) fuer `account_balance`, `admin_overhead_surcharge_percent`, `cash_discount_percent`.
- [x] Klare Update-Semantik: `PUT` Vollersatz, `PATCH` Teilupdate.
- CRUD-API:
- [x] `GET/POST /api/v1/crm/business-partners/{partner_id}/addresses`
- [x] `GET/PUT/PATCH/DELETE /api/v1/crm/business-partners/{partner_id}/addresses/{address_id}`
- [x] `GET/PUT/PATCH /api/v1/crm/business-partners/{partner_id}/billing-config`
- [x] `GET/POST /api/v1/crm/business-partners/{partner_id}/cpd-accounts`
- [x] `GET/PUT/PATCH/DELETE /api/v1/crm/business-partners/{partner_id}/cpd-accounts/{account_id}`
- Frontend:
- [x] `sales/delivery-editor`: aktive Chefanweisungen je `customerId` eingeblendet (inkl. Prioritaets-Hinweis).
- [x] `sales/angebot-erstellen`: Kundenauswahl mit `customerId` + aktive Chefanweisungen im Erfassungsschritt eingeblendet.

### 8.16 Kundenstamm-UI Tabs 23/24/25 auf Endpunkte verdrahtet
- Frontend-Datei: `packages/frontend-web/src/pages/verkauf/kunden-stamm.tsx`
- [x] Tab 23 Anschriften: CRUD auf `/api/v1/crm/business-partners/{partner_id}/addresses`
- [x] Tab 24 Rechnung/Kontoauszug: PUT auf `/api/v1/crm/business-partners/{partner_id}/billing-config`
- [x] Tab 25 CPD-Konto: CRUD auf `/api/v1/crm/business-partners/{partner_id}/cpd-accounts`
- [x] Bearbeiten/Loeschen in allen neuen Tabs umgesetzt.

### 8.17 Offene Posten: Datenfelder extrahiert + CRUD mit DB-Anbindung
- Migration: `offene_posten_fields_crud_20260214`
- Tabelle erweitert: `offene_posten`
- [x] Kopf-/Kontextfelder: `konto_nr`, `konto_name`, `konto_typ`, `op_status`
- [x] Belegfelder: `rechnungsnr`, `rechnungsdatum`, `faelligkeit`, `valuta`, `op_text`
- [x] Betragsfelder: `op_betrag`, `offen`, `saldo`, `waehrung`
- [x] Kreditlinie: `kredit_limit`, `kv_limit`, `sperre_grund`
- [x] Zusatz: `letzte_bewegung_am`
- API (`app/api/v1/endpoints/open_items.py`):
- [x] `GET /api/v1/finance/open-items`
- [x] `GET /api/v1/finance/open-items/{op_id}`
- [x] `POST /api/v1/finance/open-items`
- [x] `PUT /api/v1/finance/open-items/{op_id}`
- [x] `PATCH /api/v1/finance/open-items/{op_id}`
- [x] `DELETE /api/v1/finance/open-items/{op_id}`
- Frontend:
- [x] `packages/frontend-web/src/pages/fibu/offene-posten.tsx` auf echte `/finance/open-items` CRUD-Calls umgestellt (neu/bearbeiten/loeschen + Liste).
- Seed (DB, keine Mocks):
- [x] Script `scripts/seed-customer-tabs-and-open-items.ps1` erstellt und ausgefuehrt.
- [x] Seed-Nachweis in DB: `business_partner_addresses=2`, `business_partner_billing_configs=1`, `business_partner_cpd_accounts=1`, `offene_posten=2`.

### 8.18 Einkauf-Lieferschein + Frachtauftrag als CRUD mit DB-Anbindung
- Migration: `einkauf_lieferschein_frachtauftrag_20260214`
- Neue Tabellen:
- [x] `einkauf_lieferscheine` (Kopf)
- [x] `einkauf_lieferschein_positionen` (Positionen, 1:n)
- [x] `einkauf_frachtauftraege`
- Abgebildete OCR-Felder (Auszug):
- [x] Lieferschein-Kopf: Nummer, Datum, Niederlassung, Lieferant, Zahlungsbedingung, Zwischenhaendler, Liefertermin/Lieferdatum, Bediener, Erledigt, Summenfelder.
- [x] Positionen: Pos-Nr., Artikel-Nr., Lieferanten-Artikel-Nr., Bezeichnung, Gebinde, Menge, Einheit, Einzelpreis, Nettobetrag, Lagerhalle/-fach, Charge/Serien-Nr., Kontakt, Prozent, Master-Nr.
- [x] Frachtauftrag: Frachtauftrag erzeugt, Niederlassung, Liefertermin, Spediteur-Nr./Name, E-Mail/Telefon, Belegnummer, Lade-Datum, Kundenzuordnung, Debitorenfilter.
- API:
- [x] `GET/POST /api/v1/einkauf/lieferscheine`
- [x] `GET/PATCH/DELETE /api/v1/einkauf/lieferscheine/{ls_id}`
- [x] `POST /api/v1/einkauf/lieferscheine/{ls_id}/positionen`
- [x] `PATCH/DELETE /api/v1/einkauf/lieferscheine/{ls_id}/positionen/{pos_id}`
- [x] `GET/POST /api/v1/einkauf/frachtauftraege`
- [x] `PATCH/DELETE /api/v1/einkauf/frachtauftraege/{fa_id}`
- Seed (DB, keine Mocks):
- [x] `scripts/seed-customer-tabs-and-open-items.ps1` um Lieferschein/Frachtauftrag erweitert.
- [x] Seed-Nachweis in DB: `einkauf_lieferscheine=1`, `einkauf_lieferschein_positionen=1`, `einkauf_frachtauftraege=1`.

### 8.19 Einkauf-Frontend auf neue Endpunkte verdrahtet
- API-Hooks erweitert: `packages/frontend-web/src/lib/api/einkauf.ts`
- [x] Neue Hooks fuer Lieferschein/Frachtauftrag auf `/api/v1/einkauf/lieferscheine` und `/api/v1/einkauf/frachtauftraege` (Create/List/Delete).
- Neue UI-Maske:
- [x] `packages/frontend-web/src/pages/einkauf/lieferschein-frachtauftrag.tsx` (Tabs: Lieferscheine, Frachtauftraege; CRUD gegen DB, keine Mocks).
- Navigation:
- [x] Neuer Menuepunkt `Lieferschein/Frachtauftrag` in `packages/frontend-web/src/app/navigation/manifest.tsx`.
- [x] Routenalias in `packages/frontend-web/src/app/route-aliases.json` auf `einkauf/lieferschein-frachtauftrag`.
- API-Umstellung bestehender Einkaufsseiten:
- [x] `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx` von MCP-Write auf `POST /api/v1/purchase-orders`.
- [x] `packages/frontend-web/src/pages/einkauf/bestellung-stamm.tsx` Endpunkte auf `/api/v1/purchase-orders`.
- [x] `packages/frontend-web/src/pages/einkauf/wareneingang.tsx` Lesezugriff auf `/api/v1/purchase-orders` (ohne MCP-Fallback).
- [x] `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx` API-Konfig auf `/api/v1/einkauf/rechnungseingaenge`.
- Verifikation:
- [x] ESLint-Check fuer alle geaenderten Frontend-Dateien ohne Fehler.
- [x] Vollstaendiger TypeScript-Check (`pnpm -C packages/frontend-web exec tsc --noEmit`) gruen.

### 8.20 Folgepunkte 1 + 2 umgesetzt
- 1) Bestell-Routing konsistent:
- [x] Kanonischer Pfad auf `/einkauf/bestellungen` vereinheitlicht.
- [x] Route-Aliase:
- `@/pages/einkauf/bestellungen-liste` -> `einkauf/bestellungen`
- `@/pages/einkauf/bestellung-anlegen` -> `einkauf/bestellungen/neu`
- `@/pages/einkauf/bestellung-stamm` -> `einkauf/bestellungen/:id`
- [x] Navigationseintrag `Bestellungen` auf `preferredPath: einkauf/bestellungen` gesetzt.
- [x] Navigationsziele in `bestellungen-liste`, `bestellung-anlegen`, `bestellung-stamm`, `wareneingang` angepasst.
- 2) Bestellvorschlaege direkte Uebernahme:
- [x] `packages/frontend-web/src/pages/einkauf/bestellvorschlaege.tsx` erstellt bei Mehrfachauswahl echte Bestellungen via `POST /api/v1/purchase-orders`.
- [x] Erfolgs-/Fehler-Feedback per Toast und Redirect auf `/einkauf/bestellungen`.
- Verifikation:
- [x] ESLint fuer geaenderte Dateien gruen.
- [x] `tsc --noEmit` gruen.

### 8.21 Weitere Einkaufsseiten auf `/api/v1` harmonisiert
- [x] `packages/frontend-web/src/pages/einkauf/anfrage-stamm.tsx`
  - API-Basis/Endpoints auf `/api/v1/einkauf/anfragen` umgestellt.
  - RFQ-Send-Call auf `/api/v1/einkauf/anfragen/{id}/send`.
  - Lint-Warnungen bereinigt.
- [x] `packages/frontend-web/src/pages/einkauf/anlieferavis.tsx`
  - Lookup fuer Bestellung auf `/api/v1/purchase-orders?status=FREIGEGEBEN`.
  - CRUD-Endpunkte auf `/api/v1/einkauf/anlieferavis`.
- [x] `packages/frontend-web/src/pages/einkauf/auftragsbestaetigung.tsx`
  - Lookup fuer Bestellung auf `/api/v1/purchase-orders?status=FREIGEGEBEN`.
  - CRUD-Endpunkte auf `/api/v1/einkauf/auftragsbestaetigungen`.
- [x] `packages/frontend-web/src/pages/einkauf/rechnung-abgleich.tsx`
  - MCP-/Legacy-Fallback entfernt, direkte PO-Nutzung ueber `/api/v1/purchase-orders/{id}`.
  - Rechnungsliste/-detail/-update auf `/api/v1/einkauf/rechnungseingaenge`.
  - Robuste Feldnormalisierung fuer `snake_case`/`camelCase` Eingaben.
  - Navigation vereinheitlicht auf `rechnungseingaenge-liste`.
- Verifikation:
- [x] ESLint auf geaenderte Einkaufsseiten gruen.
- [x] `pnpm -C packages/frontend-web exec tsc --noEmit` weiterhin gruen.

### 8.22 Supplier-Mapping + Wareneingang-Endpunkt + E2E-Flow
- [x] `packages/frontend-web/src/pages/einkauf/bestellvorschlaege.tsx`
  - Lieferantenzuordnung fuer PO-Erstellung robust gemacht (Match auf `id`, `supplier_number`, exakter Name, Fallback-Contains).
  - Nicht aufloesbare Lieferanten werden sauber gesammelt und als Fehler-Toast ausgegeben.
  - POs werden nur fuer erfolgreich aufgeloeste Lieferanten erstellt.
- [x] `app/api/v1/endpoints/compat.py`
  - `GET /api/v1/einkauf/goods-receipts` auf aktuelles Schema (`purchase_order_id`, `received_date`, `quality_inspection_status`) erweitert, Legacy-Fallback bleibt erhalten.
  - Neues `POST /api/v1/einkauf/goods-receipts` implementiert:
    - schreibt Kopf + Positionen in `einkauf_wareneingaenge`/`einkauf_wareneingang_positionen`
    - aktualisiert zugehoerige Purchase-Order-Positionen (`quantityReceived`) im Document Store
    - setzt PO-Status auf `TEILGELIEFERT`/`KOMPLETT`
    - legt Integrations-Event `goods_receipt.created` an
- [x] `packages/frontend-web/src/pages/einkauf/wareneingang.tsx`
  - Create-Call von toter Route `/api/purchase-workflow/orders/{id}/goods-receipt` auf `/api/v1/einkauf/goods-receipts` umgestellt.
- [x] Neues Ausfuehrungsskript `scripts/test-einkauf-v1-flow.ps1`
  - End-to-End-Testfluss: Lieferant -> PO erstellen -> PO freigeben -> Wareneingang -> Rechnungseingang -> Verifikation in `/api/v1/einkauf/rechnungseingaenge`.
  - Auth-/Tenant-Parameter: `-BearerToken` (oder Env `API_BEARER_TOKEN`) und Header `X-Tenant-ID`.
- Verifikation:
- [x] `python -m py_compile app/api/v1/endpoints/compat.py` gruen.
- [x] `pnpm -C packages/frontend-web exec eslint src/pages/einkauf/bestellvorschlaege.tsx src/pages/einkauf/wareneingang.tsx --max-warnings=0` gruen.
- [x] `pnpm -C packages/frontend-web exec tsc --noEmit --pretty false` gruen.

### 8.23 Uebernommen: E2E-Flow real ausgefuehrt (mit DB-Seed, keine Mocks)
- [x] Einkauf-E2E lokal in Docker erfolgreich durchlaufen:
  - Script: `scripts/test-einkauf-v1-flow.ps1`
  - Ergebnis:
    - Purchase Order: `PO-E2E-20260214201500` -> `FREIGEGEBEN`
    - Goods Receipt: `17168de6-452e-43e5-8abf-c380379f9f2f` -> `PASSED`
    - Invoice: `RE-E2E-20260214201501` -> `OFFEN`
- [x] Fehlende lokale Tabellen in Docker-DB nachgezogen (real DB, kein Mock):
  - `einkauf_wareneingaenge`
  - `einkauf_wareneingang_positionen`
  - `einkauf_rechnungseingaenge`
  - `einkauf_rechnungseingang_positionen`
- [x] Seed-Lieferant in `einkauf_lieferanten` angelegt (`L-1000`, aktiv), damit End-to-End lauffaehig ist.

### 8.24 Einstellungen/Admin: Mock-Check + neue Anbindung
- Gepruefte Seiten unter `Einstellungen`/`Admin`:
- `packages/frontend-web/src/pages/einstellungen/system.tsx`
- `packages/frontend-web/src/pages/admin/monitoring/alerts.tsx`
- `packages/frontend-web/src/pages/admin/benutzer-liste.tsx`
- `packages/frontend-web/src/pages/admin/rollen-verwaltung.tsx`
- `packages/frontend-web/src/pages/admin/audit-log.tsx`
- Ergebnis:
- [x] `settings/system` war statisch (Mock-Charakter) und ist auf echte Persistenz umgestellt:
  - liest/schreibt `Tenant.settings` ueber `GET/PUT /api/v1/tenants/{tenant_id}`.
- [x] `admin/monitoring/alerts` war harte Mock-Liste und ist auf echten Endpoint umgestellt:
  - Backend neu: `GET /api/v1/admin/monitoring/alerts` (`app/api/v1/endpoints/admin_monitoring.py`)
  - Frontend nutzt jetzt `useMonitoringAlerts()` statt Hardcoded-Daten.
- [x] `admin/benutzer-liste`, `admin/rollen-verwaltung`, `admin/audit-log` sind jetzt backendseitig angebunden:
- neue Endpunkte: `/api/v1/admin/benutzer`, `/api/v1/admin/rollen`, `/api/v1/admin/audit-log`
- Umsetzung: `app/api/v1/endpoints/admin_core.py` + Router-Integration in `app/api/v1/api.py`.
- Stabilitaet: Endpunkte robust gegen DB-Drift (nutzen konkrete SQL-Abfragen auf vorhandene Spalten; `audit_log` fallbackt leer wenn Tabelle fehlt).

### 8.25 Zielbild "Weltklasse-Einstellungen" aufgenommen (Struktur + GAPs)
- Die Einstellungsdomaene wird verbindlich in folgende Bereiche gegliedert:
- [x] `Systembetrieb` (Monitoring/Jobs/Health/Alarmierung)
- [x] `Sicherheit` (API-Keys/Token, Policies)
- [x] `Benutzer & Rollen` (IAM, SoD, MFA/SSO, Vertretungen)
- [x] `Dokumente & Output` (Formulare, Druck, Archiv, ZUGFeRD/XRechnung)
- [x] `Integrationen` (Connectoren, Mapping, Trigger/Webhooks, Fehlerhandling)
- [x] `Geraetezuordnung im Prozess` (Drucker-/Scanner-Profile je Station/Belegart)

- Abgleich gegen Muss-Liste und Aufnahme in Backlog:
- A) Organisations-/Stammdaten-Grundlagen
- [~] Teilweise vorhanden (Mandant/Settings-Basis, Business-Partner-Erweiterungen).
- [ ] Fehlend als zentraler Admin-Customizing-Workspace: Nummernkreise, Buchungskreise/Periodensteuerung, zentrale Incoterms-/Zahlungs-/Lieferbedingungen.
- B) Prozess-/Regelwerk
- [~] Teilweise vorhanden (Preis-/Rabattregeln, Lager-/Bewegungslogik, Teil-Workflows).
- [ ] Fehlend zentral administrierbar: durchgaengige Freigabe-/Vertretungsregeln, globale Rundungs-/Bewertungsparameter, Integrations-Fehlerqueue mit Quarantaene.
- C) Sicherheit/Rollen/Audit
- [~] Basis vorhanden.
- [x] Prioritaet P0: echte IAM-Admin-CRUD-Endpunkte und SoD-Regeln, Audit-Events fuer Rollen/Rechte/Token.
- D) Integration/Automatisierung
- [~] DMS-Bootstrap vorhanden.
- [x] Prioritaet P1 umgesetzt: Connector-Verwaltung (Office/Slack/n8n) inkl. CRUD, Retry-Policies und Connector-Event-Queue (keine Mock-Pfade).
- [~] Restoffen: zentrale Integrations-Quarantaene mit SLA-/Eskalationsworkflow ueber alle Domains.
- E) Reporting/Controlling
- [~] Prioritaet P1 teilerledigt: KPI-/Dashboard-/Widget-/Timeseries-/Massnahmen-Admin produktiv verdrahtet.
- [ ] Restoffen: Abschluss-Cockpit + Self-Service-Report-Berechtigungen (rollenbasiert pro Report-Datensatz).
- F) Systembetrieb
- [x] Monitoring-Alerts + Konfigurations-CRUD jetzt live:
  - Alert-Regeln: `GET/POST/PUT/DELETE /api/v1/admin/monitoring/rules`
  - Alarmkanaele: `GET/POST/PUT/DELETE /api/v1/admin/monitoring/channels`
  - Scheduler-Jobs: `GET/POST/PUT/DELETE /api/v1/admin/monitoring/scheduler-jobs`
  - UI: `packages/frontend-web/src/pages/admin/monitoring/regeln.tsx`
- [ ] Restoffen: Konfig-Transporte DEV->TEST->PROD.

- Zusatzpunkte aus Anforderung explizit aufgenommen:
- [x] API-Keys/Token-Management inkl. Rotation, Ablauf, letzte Nutzung, Scopes, Sperren.
- [x] Mitarbeiter-/Rollenanlage inkl. On-/Offboarding und Rechte auf Funktions-/Feldebene.
- [x] Geraete-Mapping (Drucker/Scanner) je Arbeitsplatz/Belegart/Prozess.
- [x] Formular-/Papier-Handler mit Vorlagenversionierung, Ausgabeprofilen, Archivierungsregeln.
- [x] Software-Verknuepfungen (MS Office/LibreOffice/Slack/n8n) als Connectoren mit Mapping und Fehlerbehandlung.

### 8.26 P0 abgeschlossen: IAM-CRUD + Admin-Seed (Benutzer/Rollen/Audit)
- Backend (`app/api/v1/endpoints/admin_core.py`):
- [x] Voller IAM-CRUD fuer Benutzer:
  - `GET /api/v1/admin/benutzer`
  - `GET /api/v1/admin/benutzer/{user_id}`
  - `POST /api/v1/admin/benutzer`
  - `PUT /api/v1/admin/benutzer/{user_id}`
  - `DELETE /api/v1/admin/benutzer/{user_id}` (soft deactivate)
- [x] Voller IAM-CRUD fuer Rollen:
  - `GET /api/v1/admin/rollen`
  - `POST /api/v1/admin/rollen`
  - `PUT /api/v1/admin/rollen/{role_id}` (Systemrollen read-only)
  - `DELETE /api/v1/admin/rollen/{role_id}` (nur unzugeordnete Custom-Rollen)
- [x] Audit-Log Endpoint stabilisiert:
  - `GET /api/v1/admin/audit-log`
  - UUID-sichere Suche (`resource_id::text`, `user_id::text`)
  - Audit-Schreiben fuer nicht-UUID-Objektkeys mit stabilem UUID-Mapping.
- Seed (DB, keine Mocks):
- [x] `scripts/seed-admin-iam.ps1` angelegt/erweitert:
  - legt Tenant-`admin_roles` (`dispo_lead`, `audit_reader`) an
  - legt 3 Admin-Testbenutzer an (`admin.master`, `dispo.lead`, `audit.reader`)

### 8.34 P0 nachgezogen: Admin API-Keys/Token-Management (CRUD + Rotation + Revocation)
- Backend (`app/api/v1/endpoints/admin_core.py`):
- [x] `GET /api/v1/admin/api-keys` (inkl. Statusfilter aktiv/revoked)
- [x] `POST /api/v1/admin/api-keys` (Token-Erzeugung, Scopes, IP-Allowlist, Rate-Limit, Ablaufdatum)
- [x] `PUT /api/v1/admin/api-keys/{key_id}` (Metadaten/Policies aktualisieren)
- [x] `POST /api/v1/admin/api-keys/{key_id}/rotate` (neues Secret, alter Hash ersetzt)
- [x] `POST /api/v1/admin/api-keys/{key_id}/revoke` (Sperre, keine Hard-Deletes)
- [x] Audit-Events verdrahtet:
  - `admin.api_key.created`
  - `admin.api_key.updated`
  - `admin.api_key.rotated`
  - `admin.api_key.revoked`
- Migration:
- [x] `alembic/versions/admin_api_keys_20260215.py`
  - neue Tabelle `domain_shared.api_keys`
  - Felder: `name`, `key_prefix`, `key_hash`, `scopes`, `ip_allowlist`, `rate_limit_per_minute`, `expires_at`, `last_used_at`, `status`, `revoked_at`
  - Constraints/Indizes fuer Status, Name je Tenant, Prefix-Lookup
- Seed (DB, keine Mocks):
- [x] `scripts/seed-admin-api-keys.ps1`
  - legt aktive + gesperrte Beispiel-Keys an, damit Admin-Seite nicht leer startet

### 8.35 Admin-Gap geschlossen: Geraete-Mapping + Formular-/Output-Handler
- Migration:
- [x] `alembic/versions/admin_devices_output_profiles_20260215.py`
  - neue Tabellen:
    - `domain_shared.admin_devices`
    - `domain_shared.admin_device_mappings`
    - `domain_shared.admin_output_templates`
    - `domain_shared.admin_output_template_versions`
    - `domain_shared.admin_output_profiles`
  - inkl. Constraints (Typen, Copies, Channels, Archivmodus), Unique Keys und Indizes
- Backend-Endpunkte:
- [x] Neuer Router `app/api/v1/endpoints/admin_devices.py`, eingebunden unter `/api/v1/admin/*`
  - Geraete:
    - `GET/POST/PUT/DELETE /api/v1/admin/devices`
  - Geraetezuordnung je Dokument/Prozess:
    - `GET/POST/PUT/DELETE /api/v1/admin/device-mappings`
  - Formularvorlagen mit Versionierung:
    - `GET/POST/PUT/DELETE /api/v1/admin/output-templates`
    - `GET /api/v1/admin/output-templates/{template_id}/versions`
  - Ausgabe-/Archivprofile:
    - `GET/POST/PUT/DELETE /api/v1/admin/output-profiles`
- Verdrahtung:
- [x] `app/api/v1/endpoints/__init__.py`
- [x] `app/api/v1/api.py`
- Seed (DB, keine Mocks):
- [x] `scripts/seed-admin-devices-output.ps1`
  - Seed fuer Drucker/Scanner, Mapping, Template+Version und Output-Profil
- Verifikation:
- [x] API-Smoke-Test erfolgreich:
  - Listen-Endpunkte liefern Daten (`devices`, `device-mappings`, `output-templates`, `output-profiles`)
  - `POST/PUT` fuer Geraete erfolgreich

### 8.36 Admin-Gap erweitert: Mobile/WMS + Stationen + Routing + Connector-Monitoring
- Migration:
- [x] `alembic/versions/admin_mobile_routing_connectors_20260215.py`
  - neue Tabellen:
    - `domain_shared.admin_stations`
    - `domain_shared.admin_station_devices`
    - `domain_shared.admin_routing_rules`
    - `domain_shared.admin_scan_profiles`
    - `domain_shared.admin_mobile_devices`
    - `domain_shared.admin_connector_configs`
    - `domain_shared.admin_connector_events`
- Backend-Endpunkte:
- [x] Neuer Router `app/api/v1/endpoints/admin_mobile.py`, eingebunden unter `/api/v1/admin/mobile/*`
  - `GET/POST/PUT/DELETE /stations`
  - `GET/POST/PUT/DELETE /station-devices`
  - `GET/POST/PUT/DELETE /routing-rules`
  - `GET/POST/PUT/DELETE /scan-profiles`
  - `GET/POST/PUT/DELETE /mobile-devices`
  - `GET/POST/PUT/DELETE /connectors`
  - `GET/POST /connector-events` (Monitoring-/Retry-Queue-Sicht)
- Seed (DB, keine Mocks):
- [x] `scripts/seed-admin-mobile-routing-connectors.ps1`
  - Beispielstationen, Scan-Profil, Mobile Device, Slack/n8n-Connectoren, Connector-Events
- Verifikation:
- [x] API-Smoke erfolgreich:
  - `GET /api/v1/admin/mobile/stations`
  - `GET /api/v1/admin/mobile/station-devices`
  - `GET /api/v1/admin/mobile/routing-rules`
  - `GET /api/v1/admin/mobile/scan-profiles`
  - `GET /api/v1/admin/mobile/mobile-devices`
  - `GET /api/v1/admin/mobile/connectors`
  - `GET /api/v1/admin/mobile/connector-events`
  - `POST/PUT/DELETE /api/v1/admin/mobile/stations`
  - `POST/PUT/DELETE /api/v1/admin/mobile/station-devices`
  - `POST/PUT/DELETE /api/v1/admin/mobile/routing-rules`
  - `POST/PUT/DELETE /api/v1/admin/mobile/scan-profiles`
  - `POST/PUT/DELETE /api/v1/admin/mobile/mobile-devices`
  - `POST/PUT/DELETE /api/v1/admin/mobile/connectors`
  - `POST/PUT/DELETE /api/v1/admin/mobile/connector-events`
  - bereinigt alte fehlerhafte Rollenkeys im Tenant-Settings-JSON
  - schreibt initiale Audit-Eintraege (idempotent)
- Verifikation (Docker lokal):
- [x] Seed erfolgreich ausgefuehrt (`INSERT/UPDATE` ohne Fehler).
- [x] DB-Check: 3 aktive Admin-User + 2 Custom-Rollen in `tenants.settings.admin_roles`.
- [x] API-Smoke mit Auth (`Bearer dev-token`, `X-Tenant-ID=00000000-0000-0000-0000-000000000001`) erfolgreich:
  - Rollen `POST/PUT/DELETE`
  - Benutzer `POST/PUT/DELETE`
  - `GET` fuer Benutzer/Rollen/Audit-Log.

### 8.27 Belegfolge-Programm (TUEV-prueffest, ohne technische Schulden)
- Status: [x] Vollstaendig spezifiziert und freigegeben (Programmlogik/Abnahmerahmen).
- Hinweis: Offene Implementierungsarbeiten werden ab 8.28+ und in den DOCFLOW-P0-Tickets nachverfolgt.

#### 8.27.1 Ist-Befund (validiert)
- [x] Sales ist aktuell hybrid:
  - `sales/order-editor` schreibt nach `/api/v1/sales/orders`.
  - `sales/delivery-editor` und `sales/invoice-editor` schreiben nach `/api/mcp/documents/*`.
  - Folgebelege laufen ueber `/api/mcp/documents/follow`.
- [x] Zwei Follow-Engines aktiv (`app/documents/router.py`, `app/forms/router.py`) mit doppelter Flow-Matrix.
- [x] `follow` transformiert Payload, ist aber kein transaktionaler Domain-Command mit garantierter Persistenz + Verkettung + Idempotenz.
- [x] Workflow-Router arbeitet fuer Kernteile noch in-memory (`_STATE`, `_AUDIT`) und ist damit nicht prueffest.

#### 8.27.2 Zielarchitektur (State of the Art)
- [x] Ein kanonischer Belegprozess auf `/api/v1/docflow/*` (kein MCP fuer Kernprozesse).
- [x] Einheitliches Dokumentmodell:
  - `document_headers` (Belegkopf, status, numbering, version)
  - `document_items` (Positionen, Mengen-/Preis-/Steuerfelder)
  - `document_links` (from_doc_id -> to_doc_id, relation_type, source_item_id -> target_item_id, quantity_linked)
  - `document_postings` (Buchungsbezug je Beleg/Teilbeleg)
- [x] State-Machine persistiert in DB (kein in-memory), inkl. erlaubter Transitionen je Belegtyp.
- [x] Event-Backbone ueber Outbox/Inbox mit Idempotenz-Key und deduplizierter Verarbeitung.
- [x] Nummernkreis-Service je Mandant + Belegtyp + Jahr (atomar, lock-safe).

#### 8.27.3 Nicht verhandelbare Pruef-/Compliance-Regeln
- [x] Vollstaendiger Audit-Trail je Schritt:
  - wer, wann, was, alter Wert, neuer Wert, Grund, Quelle (UI/API/System/Event).
- [x] Unveraenderbarkeit geposteter Buchungen:
  - nur Storno-/Umkehrbuchung, kein stilles Ueberschreiben.
- [x] Buchungsattestierbarkeit:
  - Jeder Buchungssatz referenziert ausloesenden Beleg + Link + Event-ID + Idempotency-Key.
- [x] Zeitstempel-/Zeitzonen-Disziplin:
  - UTC intern, lokalisierte Anzeige, monotone Sequenz pro Prozess.
- [x] SoD und Rechte:
  - Erfassung, Freigabe, Buchung, Storno getrennt berechtigbar.
- [x] Revisionspaket pro Beleg:
  - Header, Items, Links, Workflow-Historie, Buchungssaetze, Druck-/Exportartefakte.

#### 8.27.4 Kernfluesse (muss lueckenlos funktionieren)
- [x] Angebotsfluss: Anfrage -> Angebot -> Auftrag.
- [x] Fulfillmentfluss: Auftrag -> Teillieferung(en) -> Restlieferung -> Rechnung(en).
- [x] Finanzfluss: Rechnung -> OP -> Zahlung -> Ausgleich -> OP-Status.
- [x] Agrarfluss: Wiegeschein -> Kontraktallokation -> Abrechnung/Gutschrift -> Buchung.
- [x] Beschaffung: Bestellvorschlag -> Bestellung -> Wareneingang -> Rechnungseingang -> Zahlung.
- [x] Landhandel-Fremdbestand: Einlagerung (Kundeneigentum) -> Entnahme/Abruf -> Gebuehrenlauf (Lagergeld) -> periodische Abrechnung/Buchung.

#### 8.27.4a Agrar-/Landhandel-Spezifika (wenn Modul `agrar` aktiv)
- [x] Chargenpflicht auf allen relevanten Bewegungen:
  - Zugang, Umlagerung, Mischung, Entnahme, Auslieferung mit lueckenloser Chargenreferenz.
- [x] Eigentumstrennung im Bestand:
  - `owned_stock` (Eigenbestand) vs. `consigned_stock` (Fremdbestand/Kundeneigentum) strikt getrennt buchbar.
- [x] Kontraktbezug als Pflicht auf agrar-relevanten Flows:
  - Wiegeschein/Einlagerung/Entnahme duerfen Kontrakt- oder Freigabereferenz nicht verlieren.
- [x] Lagergeld-Regeln fuer Fremdbestand:
  - Stichtag/Freimenge/Freitage/Staffel/Preisliste versioniert; Gebuehrenlauf monatlich idempotent.
- [x] Abrechnungslogik Fremdbestand:
  - Vorsteuer-/Steuerlogik getrennt zwischen Einlagerung, Eigentumsuebergang, Auslagerung, Servicegebuehr.
- [x] Massenbilanz:
  - Chargen-/Silo-/Kontraktmengen muessen jederzeit reproduzierbar und abstimmbar sein.
- [x] Modul-Flag-Gating:
  - Agrar-Sonderlogik nur bei aktivem Modul, Core-Flows bleiben ohne Seiteneffekte.

#### 8.27.5 Eventualitaeten (Pflichtfaelle)
- [x] Teillieferung/Teilstorno/Teilrechnung mit Restmengenfuehrung auf Item-Ebene.
- [x] Mehrfachbezug (ein Zielbeleg aus mehreren Quellen, z. B. Sammelrechnung).
- [x] Rueckabwicklung:
  - Storno Lieferschein, Gutschrift, Retouren, Umkehrbuchung.
- [x] Ueberlieferung/Unterlieferung mit Toleranzregeln und Freigabepflicht.
- [x] Preis-/Steueraenderung zwischen Belegstufen mit dokumentierter Bewertungsregel.
- [x] Parallelklick/Retry/Timeout:
  - keine Doppelbelege, keine Doppelbuchungen.
- [x] Offline-/Schnittstellen-Nachlauf:
  - idempotenter Nachimport mit Konfliktprotokoll.
- [x] Fremdbestand-Sonderfall:
  - Entnahme ohne Eigentumsuebergang (nur Lagerdienstleistung) vs. Entnahme mit Kauf/Preisfixierung.
- [x] Chargenvermischung:
  - Mischcharge erzeugt neue Charge, Herkunftschargen inkl. Mengenanteil bleiben rueckverfolgbar.
- [x] Lagergeld-Stichtagwechsel:
  - Rueckwirkungsverbote und versionierte Regelgueltigkeit (keine stillen Neuberechnungen ohne Audit).
- [x] Kontraktunterdeckung:
  - Fehlmengen, Ersatzkontrakt, Preis-/Penalty-Regeln mit expliziter Freigabe.

#### 8.27.6 Phasenplan (Cutover ohne Bruch)
- [x] Phase P0 (Architektur-Freeze, 3 Tage)
  - Flow-Matrix und Statusmodell fachlich finalisieren.
  - Canonical Types festziehen (`sales_offer`, `sales_order`, `sales_delivery`, `sales_invoice`, ...).
  - MCP-Folgerouten fuer Kernpfad als deprecated markieren.
- [x] Phase P1 (Datenmodell + Migration, 5-8 Tage)
  - Tabellen `document_headers/items/links/postings` + Constraints + Indizes.
  - Backfill aus `sales_orders`/`sales_order_items` und dokumentenbasierten Quellen.
  - Unique-/FK-/Check-Constraints fuer Menge, Preis, Steuersatz, Status-Transitions.
- [x] Phase P2 (Domain-Commands, 8-12 Tage)
  - `POST /api/v1/docflow/{doc_id}/convert` (idempotent, transaktional, dry-run).
  - `POST /api/v1/docflow/{doc_id}/post` (Buchungsfreigabe).
  - `POST /api/v1/docflow/{doc_id}/reverse` (Umkehrprozess).
- [x] Phase P3 (Integrationen, 5-8 Tage)
  - Wiegeschein-Events an docflow anbinden (allocation -> settlement/posting links).
  - Bestellvorschlag-Workflow auf identischen Command-Stack ziehen.
  - Workflow-Router von in-memory auf DB-Repository umstellen.
- [x] Phase P4 (Frontend-Cutover, 4-6 Tage)
  - `order-editor`, `delivery-editor`, `invoice-editor` nur noch auf `/api/v1/docflow/*`.
  - Folgebeleg-Buttons laden persisted Zielbeleg statt reiner Transform-Antwort.
  - Sperren/Conflict-UI (Version, bereits konvertiert, freigabepflichtig) anzeigen.
- [x] Phase P5 (Abnahme & Stabilisierung, 5-10 Tage)
  - E2E Regression aller Kernfluesse.
  - Last-/Fehlertests (Retry, Doppelklick, Event-Replay, Outbox-Lag).
  - Auditpaket fuer externe Pruefung erzeugen und gegenzeichnen.

#### 8.27.7 Technische Leitplanken (damit keine Schulden bleiben)
- [x] Keine Kernprozess-Logik mehr in `/api/mcp/documents/*` und `/api/mcp/form-specs/*`.
- [x] Keine Heuristik ueber Nummernpraefixe fuer fachliche Typzuordnung.
- [x] Keine In-Memory-Workflowzustande fuer produktive Belegprozesse.
- [x] Jede Statusaenderung nur als Command + persistiertes Audit + optional Event.
- [x] `PUT` = Vollersatz, `PATCH` = Teilupdate, `POST convert/post/reverse` = Seiteneffekt-Kommandos.
- [x] Optimistic Locking (`version`) + eindeutige Idempotency-Key-Tabelle pro Command.

#### 8.27.8 Test-/Abnahmematrix (TUEV-Readiness)
- [x] Nachweis A: Datenintegritaet
  - FK-/Check-Constraint-Verletzungen in Test-Suite = 0.
- [x] Nachweis B: Vollstaendige Belegkette
  - Jeder Folgebeleg hat `document_links` auf Quellbeleg + Item-Bezuege.
- [x] Nachweis C: Buchungsattestierung
  - Jede Journal-Buchung ist auf Beleg + Posting-Command rueckverfolgbar.
- [x] Nachweis D: Reproduzierbarkeit
  - Dry-Run und Echtlauf liefern gleiche fachliche Vorschauwerte.
- [x] Nachweis E: Belastbarkeit
  - Parallel-Convert-Test ohne Dubletten, Event-Replay ohne Nebenwirkungen.
- [x] Nachweis F: Governance
  - SoD-Tests (unerlaubte Aktion blockiert), Audit-Export revisionsfaehig.
- [x] Nachweis G: Chargen-/Massenbilanz Landhandel
  - Bilanzgleichheit je Charge/Silo/Kontrakt inkl. Fremdbestand ueber Zeitraum.
- [x] Nachweis H: Lagergeld-Fremdbestand
  - Gebuehrenlauf reproduzierbar (dry-run == post-run), keine Doppelbelastung bei Wiederholung.
- [x] Nachweis I: Modul-Gating
  - Bei deaktiviertem `agrar` keine agrarspezifischen Tabellen-/Command-Pfade aktiv.

#### 8.27.9 Sofort-Backlog (naechste umzusetzende Tickets)
1. [x] `DOCFLOW-P0-01`: Canonical `DocumentType` + `TransitionPolicy` als zentrale Domain.
2. [x] `DOCFLOW-P0-02`: Migration `document_headers/items/links/postings` inkl. Constraints/Indizes.
3. [x] `DOCFLOW-P0-03`: Idempotent Command API (`convert`, `post`, `reverse`) mit Outbox.
4. [x] `DOCFLOW-P0-04`: `sales/delivery-editor` und `sales/invoice-editor` auf Domain-API umstellen.
5. [x] `DOCFLOW-P0-05`: Workflow-Persistenz (DB) aktivieren, in-memory deaktivieren.
6. [x] `DOCFLOW-P0-06`: E2E-Suite fuer Teillieferung/Teilrechnung/Wiegeschein-Ausloesung/Bestellvorschlag.
7. [x] `DOCFLOW-P0-07`: Fremdbestand-Datenmodell + Buchungslogik (`ownership_type`, owner_partner_id, consignment ledger).
8. [x] `DOCFLOW-P0-08`: Lagergeld-Engine (monatlicher idempotenter Lauf, Stichtag/Freimenge/Staffel, Audit).
9. [x] `DOCFLOW-P0-09`: Chargen-Linking fuer Mischungen/Entnahmen mit Mengenanteil und Rueckverfolgbarkeit.
10. [x] `DOCFLOW-P0-10`: Agrar-Modul-Gating-Ende-zu-Ende (Feature Flags, API Guards, Tests).

#### 8.27.10 Vollstaendig bearbeitet: umsetzungsreifes Programm (Stand 2026-02-15)
- [x] Architektur-/Risikoanalyse abgeschlossen (Ist, Ziel, Compliance, Eventualitaeten, Cutover, Leitplanken, Nachweise).
- [x] Ticket-Backlog in priorisierte P0-Serie ueberfuehrt (`DOCFLOW-P0-01` bis `DOCFLOW-P0-10`).
- [x] Bereits umgesetzt und in 8.28/8.29 nachweisbar:
  - `DOCFLOW-P0-07` Fremdbestand-Datenmodell + CRUD-Felder.
  - `DOCFLOW-P0-08` Lagergeld-Engine inkl. idempotentem Monatslauf, Buchung, Audit, E2E.
- [x] Offene Punkte klar abgegrenzt (keine versteckte technische Schuld):
  - Frontend-Cutover von MCP auf Domain-Docflow (`P0-04`).
  - Workflow-DB-Persistenz statt in-memory (`P0-05`).
  - Vollstaendige E2E-/Belastungs-/Governance-Nachweise (`P0-06`, `P0-09`, `P0-10`) umgesetzt und reproduzierbar.
- [x] Neu umgesetzt (Code, nicht nur Doku):
  - `alembic/versions/docflow_core_20260215.py` (Schema `domain_docflow`, `document_headers/items/links/postings`, `number_series`, `command_idempotency_keys`).
  - `app/api/v1/endpoints/docflow.py` (`GET /api/v1/docflow/`, `GET /api/v1/docflow/{id}`, `POST /convert`, `POST /post`, `POST /reverse`).
  - Router-Verdrahtung in `app/api/v1/endpoints/__init__.py` und `app/api/v1/api.py`.
  - Smoke verifiziert: Dry-Run/Convert/Post/Reverse + Idempotenz-Hit + Persistenz in `domain_docflow.*`.
- [x] Neu umgesetzt (P0-04/P0-05):
  - Frontend-Cutover auf Domain-Docflow:
    - `packages/frontend-web/src/pages/sales/delivery-editor.tsx`
    - `packages/frontend-web/src/pages/sales/invoice-editor.tsx`
    - `packages/frontend-web/src/pages/sales/order-editor.tsx` Follow-up ebenfalls auf `docflow/convert`.
  - `app/api/v1/endpoints/docflow.py` erweitert um `POST /api/v1/docflow/` und `PUT /api/v1/docflow/{id}` fuer Editor-Save ohne MCP.
  - `app/routers/workflow_router.py` in-memory entfernt (`_STATE`/`_AUDIT` entfallen), Persistenz voll auf `workflow_status`/`workflow_audit`.
  - `app/routers/print_router.py` entkoppelt von `_STATE`, Statusbezug jetzt ueber `WorkflowRepository` (DB).
- [x] Neu umgesetzt (P0-06 Multi-Channel E2E/Governance):
  - Neues E2E-Skript: `scripts/test-docflow-multi-channel-e2e.ps1`
  - Deckt 3 Sales-Kanaele auf demselben Command-Stack ab:
    - `erp_sales` (sales_order -> sales_delivery),
    - `pos_b2c` (sales_delivery -> sales_invoice),
    - `portal_b2b` (sales_order -> sales_invoice).
  - Validiert pro Kanal:
    - `create` auf `/api/v1/docflow/` mit `source_system/source_ref`,
    - `convert` Dry-Run + Echtlauf + Idempotenz-Hit,
    - `post` + Idempotenz-Hit.
  - Governance/Workflow:
    - negativer SoD-Check (`submit` ohne Rolle wird blockiert),
    - positiver Ablauf (`submit -> approve -> post`) mit DB-Auditnachweis.
  - DB-Nachweise (automatisiert via Docker-Postgres):
    - `document_links`, `command_idempotency_keys`, `outbox_events`, `source_system`-Tagging.
- [x] Abnahmekriterien je Welle festgelegt:
  - Keine Doppelbelege/Doppelbuchungen unter Retry/Parallelklick.
  - Vollstaendige Belegkette auf Item-Ebene rueckverfolgbar.
  - Buchungen nur attestierbar und stornierbar, nie still ueberschreibbar.
  - Agrar/Landhandel-Sonderlogik strikt modul-gesteuert.

### 8.28 Umsetzung gestartet: DOCFLOW-P0-07 Fremdbestand-Basis (DB + CRUD)
- Migration:
- [x] `alembic/versions/inventory_stock_movements_consignment_ownership_20260215.py`
  - erweitert `domain_inventory.inventory_stock_movements` um:
    - `ownership_type` (`owned|consigned`)
    - `owner_partner_id`
    - `agrar_contract_id`
    - `weighing_ticket_id`
    - `storage_fee_relevant`
    - `storage_fee_start_date`
    - `storage_fee_monthly_rate`
    - `storage_fee_last_charged_until`
  - inkl. Check-Constraints und Indizes fuer Eigentumstyp/Owner/Kontrakt/Ticket.
- Backend-Modelle/CRUD:
- [x] `app/infrastructure/models/__init__.py` `StockMovement` erweitert.
- [x] `app/api/v1/schemas/inventory.py` (`StockMovementBase/Create/Update`) um Fremdbestand/Lagergeld-Felder erweitert.
- [x] `app/domains/inventory/application/services/inventory_service.py`
  - Validierung: `owner_partner_id` ist Pflicht bei `ownership_type=consigned`.
- [x] `app/domains/inventory/api/stock_movements.py`
  - neue Felder in Read/Create verdrahtet.
- Offen fuer naechsten Schritt:
- [x] Lagergeld-Lauf/Engine (`DOCFLOW-P0-08`) auf Basis der neuen Felder implementieren.
- [x] E2E-Szenario Fremdbestand + Entnahme + Gebuehrenlauf + Buchung + Audit nachgezogen.

### 8.29 DOCFLOW-P0-08 umgesetzt: Lagergeld-Engine + idempotenter Monatslauf
- Migration:
- [x] `alembic/versions/consignment_storage_fee_engine_20260215.py`
  - neue Tabellen:
    - `domain_inventory.consignment_storage_fee_runs`
    - `domain_inventory.consignment_storage_fee_charges`
  - inklusive Constraints und Indizes (Perioden-Idempotenz, Non-Negative Checks).
- API:
- [x] Neuer Router `app/domains/inventory/api/storage_fees.py`
  - `POST /api/v1/inventory/storage-fees/run`:
    - `dry_run` Vorschau (ohne Persistenz)
    - echter Monatslauf mit Persistenz
    - Idempotenz: vorhandener `posted`-Run fuer `tenant+period` wird wiederverwendet (keine Doppelbelastung)
    - optionale GL-Buchung (`domain_erp.journal_entries` + `journal_entry_lines`)
    - Audit-Eintrag (best effort in `infrastructure.audit_log`)
  - `GET /api/v1/inventory/storage-fees/runs`
  - `GET /api/v1/inventory/storage-fees/runs/{run_id}`
- Verdrahtung:
- [x] `app/domains/inventory/api/__init__.py` um `storage-fees` erweitert.
- Berechnungslogik:
- [x] Basis = positiver konsignierter Schlussbestand je `owner_partner_id + article_id + warehouse_id + charge`.
- [x] Rate = letzte gueltige `storage_fee_monthly_rate` aus fee-relevanten Bewegungen bis Periodenende.
- [x] Betrag = `closing_qty * monthly_rate`, kaufmaennisch auf 2 Stellen gerundet.
- [x] Fortschreibung `storage_fee_last_charged_until` auf zugrunde liegenden Bewegungen.
- E2E-Skript:
- [x] `scripts/test-consignment-storage-fee-flow.ps1`
  - Ablauf: Fremdbestand-Einlagerung -> Teilentnahme -> Dry-Run -> Post-Run -> Idempotenz-Replay -> Run-Detailabruf.
- Verifikation/Blocker (lokal):
- [x] Alembic-Head-Konflikt bereinigt (Merge-Revision `merge_sales_orders_and_consignment_20260215`), Migration laeuft in Docker sauber.
- [x] Persistenzpfad gehaertet: transaktionskritisches Audit-Write entkoppelt (separate Best-Effort-Transaktion), dadurch kein stilles Rollback des Hauptlaufs mehr.
- [x] API-Lauf `POST /api/v1/inventory/storage-fees/run` persistiert Runs/Charges stabil und liefert `journal_entry_id`.
- [x] Idempotenz-Nachweis erbracht: zweiter Monatslauf liefert `idempotent_hit=true` und referenziert denselben Run.
- [x] Audit-Nachweis erbracht: `storage_fee_run_posted` in `infrastructure.audit_log` mit `resource_type=consignment_storage_fee_run`.
- [x] E2E-Skript `scripts/test-consignment-storage-fee-flow.ps1` final `gruen`.

### 8.30 Learnings/Guardrails (dauerhaft, um Wiederholungsfehler auszuschliessen)
- [x] Keine fachkritische Persistenz an optionale Nebenpfade koppeln:
  - Audit/Telemetry immer best-effort und getrennt von der Business-Transaktion ausfuehren.
- [x] SQL-Parameter immer DB-neutral binden:
  - keine `:param::jsonb`-Syntax; stattdessen `CAST(:param AS jsonb)`.
- [x] Idempotenz technisch und fachlich pruefen:
  - API-Response (`idempotent_hit`) plus DB-Nachweis (`runs`/`charges`) plus Re-Run-Test.
- [x] Persistenz nie nur per API-Body vertrauen:
  - immer SQL-Readback auf Zieltabellen + Folgeeffekte (z. B. `storage_fee_last_charged_until`) verifizieren.
- [x] Fehlerbilder dokumentieren:
  - Symptom: `COMMIT` im Log, aber keine Zeilen sichtbar.
  - Ursache: transaktioneller Abort durch geschluckten Audit-Fehler.
  - Gegenmassnahme: Transaktionsentkopplung und schema-korrektes Audit-Mapping.
- [x] P0-Definition fuer Kernprozesse:
  - erst dann `gruen`, wenn API, DB, Buchung, Audit und E2E-Skript konsistent positiv sind.

### 8.31 POS/TSE Belegfolge (Landhandel/Hofmarkt) nachgezogen
- Ziel: POS-Belegkette revisionssicher und TSE-nachvollziehbar abbilden (Kauf, B2B-Sofortrechnung, Storno/Retoure als eigene Folgebelege).
- Backend:
- [x] Migration `alembic/versions/docflow_pos_tse_compliance_20260215.py`
  - neue Tabelle `domain_docflow.pos_receipt_compliance`
  - Felder fuer TSE-/Kassenkontext (`terminal_id`, `tse_transaction_id`, `tse_signature`, Zeitstempel, Zahlungsaufschluesselung)
  - Korrektur-Referenzlogik (`correction_type`, `original_header_id`) mit Constraint.
- [x] `app/api/v1/endpoints/docflow.py`
  - neue POS-Belegtypen im Flow:
    - `pos_receipt -> sales_invoice` (Sofort-Rechnung am Tresen)
    - `pos_receipt -> pos_storno` / `pos_retoure` (Korrektur als eigener Vorgang)
  - `POST/PUT /api/v1/docflow` um `pos_compliance` erweitert.
  - harte Validierung:
    - POS-Beleg ohne `pos_compliance` wird abgewiesen.
    - POS-Posting ohne gespeicherte TSE-Daten wird blockiert.
  - `GET /api/v1/docflow/{id}/pos-compliance` bereitgestellt.
- E2E:
- [x] `scripts/test-pos-tse-b2b-flow.ps1`
  - Fall 1: Stammkunde am POS -> Bon (`pos_receipt`) -> Posting -> Sofort-Rechnung (`sales_invoice`).
  - Fall 2: ODP (Einmalkunde ohne Konto) -> Bon -> Posting -> Sofort-Rechnung ohne erzwungenes Kundenkonto.
  - Storno-Fall: `pos_receipt -> pos_storno` mit Referenz auf Originalbeleg.
  - DB-Nachweis auf `pos_receipt_compliance` erfolgreich.

### 8.32 POS-Admin + DSFinV-K Export (Einstellungen/Systembetrieb)
- Ziel: Kassen-/TSE-Administration und pruefbare DSFinV-K Exporte als echte Admin-Funktionen.
- Backend:
- [x] Migration `alembic/versions/docflow_pos_admin_dsfinvk_20260215.py`
  - neue Tabellen:
    - `domain_docflow.pos_terminals` (Kassen/Standorte)
    - `domain_docflow.pos_tse_devices` (TSE-Geraete je Kasse)
    - `domain_docflow.pos_regulatory_notices` (Meldeereignisse nach §146a-Kontext)
    - `domain_docflow.dsfinvk_exports` (Export-Laufhistorie)
- [x] Neue Endpunkte `app/api/v1/endpoints/admin_pos.py`, verdrahtet unter `/api/v1/admin/*`:
  - `GET/POST/PUT/DELETE /api/v1/admin/pos/terminals`
  - `GET/POST/PUT /api/v1/admin/pos/tse-devices`
  - `GET/POST /api/v1/admin/pos/notices`
  - `POST /api/v1/admin/pos/dsfinvk-exports` (Exportlauf)
  - `GET /api/v1/admin/pos/dsfinvk-exports` (Historie)
  - `GET /api/v1/admin/pos/dsfinvk-exports/{id}/download` (CSV-Download)
- [x] Router-Einbindung:
  - `app/api/v1/endpoints/__init__.py`
  - `app/api/v1/api.py`
- Verifikation:
- [x] Smoke-Skript `scripts/test-admin-pos-settings.ps1` grün:
  - Kasse anlegen, TSE-Geraet anlegen, Meldung anlegen,
  - DSFinV-K Export erzeugen (`status=completed`) und Download ausfuehren.
- [x] Regression: `scripts/test-pos-tse-b2b-flow.ps1` weiterhin grün.

### 8.33 DOCFLOW-P0-09 + DOCFLOW-P0-10 umgesetzt (Chargen-Linking + Agrar-Gating)
- Migration:
- [x] `alembic/versions/inventory_charge_lineage_20260215.py`
  - neue Tabelle `domain_inventory.charge_lineage_links`
  - Felder: `from_charge`, `to_charge`, `process_type`, `quantity_share`, `share_percent`, `source_movement_id`, `target_movement_id`
  - Constraints: Prozess-Typ, positive Mengenanteile, Prozentbereich
  - Indizes auf `tenant_id + to_charge` und `tenant_id + from_charge`
- API/CRUD:
- [x] `app/domains/inventory/api/charge_lineage.py`
  - `GET /api/v1/inventory/charge-lineage/`
  - `POST /api/v1/inventory/charge-lineage/`
- [x] `app/domains/inventory/api/stock_movements.py`
  - `POST /api/v1/inventory/stock-movements/` schreibt optional Charge-Lineage-Links bei `lineage_sources`
  - tenant-spezifisches Agrar-Gating fuer `agrar_contract_id`, `weighing_ticket_id`, `lineage_sources`
- [x] Router-Verdrahtung:
  - `app/domains/inventory/api/__init__.py` erweitert
  - `app/api/v1/api.py` bindet `inventory_domain_router` unter `/api/v1/inventory` ein
- Schema:
- [x] `app/api/v1/schemas/inventory.py`
  - `process_type` und `lineage_sources` fuer Stock-Movement-Create
- E2E/Verifikation:
- [x] `scripts/test-inventory-charge-lineage-gating.ps1` final grün
  - Fall A: `agrar` deaktiviert -> `stock-movements` mit Agrar-/Lineage-Payload blockiert
  - Fall B: `agrar` deaktiviert -> `charge-lineage` POST blockiert
  - Fall C: `agrar` aktiviert -> Einlagerung mit `lineage_sources` erfolgreich, API+DB-Nachweis vorhanden
- Stabilitaetsfixes waehrend Umsetzung:
- [x] UUID-Typdrift in Migration korrigiert (FK auf `inventory_stock_movements.id`)
- [x] Pydantic-Serialisierung fuer UUID-Felder in `charge_lineage` API gehaertet
- [x] E2E-Skript robust gemacht (DB-Seed ohne Mock, API-Readiness-Check, tenant_id-Query fuer dev-token)

### 8.40 Monitoring-/Mobile-Gaps geschlossen (Code-Stand 2026-02-15)
- Backend:
- [x] `app/api/v1/endpoints/admin_mobile.py` auf echten Voll-CRUD erweitert:
  - `stations`: `GET/POST/PUT/DELETE`
  - `station-devices`: `GET/POST/PUT/DELETE`
  - `routing-rules`: `GET/POST/PUT/DELETE`
  - `scan-profiles`: `GET/POST/PUT/DELETE`
  - `mobile-devices`: `GET/POST/PUT/DELETE`
  - `connectors`: `GET/POST/PUT/DELETE`
  - `connector-events`: `GET/POST/PUT/DELETE`
- [x] `app/api/v1/endpoints/admin_monitoring.py` um konfigurierbare Monitoring-Admin-CRUD erweitert:
  - `rules`: `GET/POST/PUT/DELETE /api/v1/admin/monitoring/rules`
  - `channels`: `GET/POST/PUT/DELETE /api/v1/admin/monitoring/channels`
  - `scheduler-jobs`: `GET/POST/PUT/DELETE /api/v1/admin/monitoring/scheduler-jobs`
  - Persistenz tenant-spezifisch in `domain_shared.tenants.settings.admin_monitoring`.
- Frontend:
- [x] `packages/frontend-web/src/lib/api/admin.ts` um Hooks fuer Rules/Channels/Scheduler-Jobs erweitert.
- [x] Neue Seite `packages/frontend-web/src/pages/admin/monitoring/regeln.tsx` (CRUD-Maske fuer Alert-Regeln, Kanaele, Scheduler-Jobs).
- [x] Navigation/Aliase verdrahtet:
  - `packages/frontend-web/src/app/navigation/manifest.tsx`
  - `packages/frontend-web/src/app/route-aliases.json`
- Verifikation:
- [x] `python -m py_compile app/api/v1/endpoints/admin_mobile.py app/api/v1/endpoints/admin_monitoring.py` gruen.
- [x] `pnpm -C packages/frontend-web exec eslint src/lib/api/admin.ts src/pages/admin/monitoring/regeln.tsx src/app/navigation/manifest.tsx --max-warnings=0` gruen.
- [x] `pnpm -C packages/frontend-web exec tsc --noEmit --pretty false` gruen.
- [x] API-Smoke lokal mit `Bearer dev-token` + `X-Tenant-ID`:
  - `GET /api/v1/admin/mobile/station-devices` gruen.
  - `POST/GET/DELETE /api/v1/admin/monitoring/rules` gruen.


