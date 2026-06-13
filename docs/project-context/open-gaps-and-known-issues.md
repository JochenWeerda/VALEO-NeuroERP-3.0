# Open Gaps and Known Issues

## Zweck

Ehrliche, aktuelle Bestandsaufnahme aller offenen Restthemen, fachlichen Duennstellen und bekannten Risiken.
Production-Readiness-Nachaudit: **2026-06-09** (CI/Security, Deployment,
simulierte externe Pruefer, POS-Fiskalisierung und CRM360/KIM).
Governance-Nachzug: **2026-06-11** (`COMPAT-GOV-001`, `INV-STOCK-MOVEMENTS-001`,
Release-Kompatibilitaetsmatrix, Toolchain-Pins, Lager-Altpfade bereinigt).
Domaenentiefe-Nachzug: **2026-06-12** (`DOM-*-004`-Welle: CON, SALES, FIN, DOC, PROC,
SUPPLY je auf voller Tiefe `.2`–`.5`). Uebersicht:
[dom-004-spine-buildout-2026-06-12.md](../dom-004-spine-buildout-2026-06-12.md).
Zuletzt vollstaendig auditiert: **2026-05-27** (Integrations-Gate Wave 18–22, Backend-Security, OpenAPI-Coverage).
Aggregierte Gesamtsicht: [PROJEKT-GESAMTSTAND-2026-05-27.md](../PROJEKT-GESAMTSTAND-2026-05-27.md).

---

## Build-Health (Stand 2026-06-11)

- **TypeScript**: 0 Fehler (`tsc --noEmit`) — Wave-22-Gate (letzter Nachweis 2026-05-27)
- **Backend-Tests**: 9527 collected (2026-06-11, `pytest --collect-only`); letzter Voll-Lauf mit Pass-Count: 9228 passed (2026-05-26, Commit `271bc5e12`) — massgeblich naechster gruener `quality-gate`-Lauf
- **Governance-Vertragstests (2026-06-11, lokal)**: 8/8 gruen (`test_release_compatibility_governance`, `test_inventory_stock_movements_canonical`)
- **Toolchain-Pins**: `scripts/check_toolchain_pins.py` gruen (pytest-cov/coverage repo-weit fixiert)
- **Release-Matrix**: Generator + CI-Upload in `quality-gate.yml` / `release-gates.yml`
- **OpenAPI-Routen mit `summary=`**: 2663 (100%, Wave-D2 Commit `554625ae7`)
- **Frontend-Imports**: 0 gebrochene Importe (letzter Nachweis 2026-05-27)
- **Alembic**: 1 Head (`merge_doc_proc_20260612`, 2026-06-12) — DOC-Branch (`doc_followup_20260611`) und PROC-Branch (`proc_rfq_20260611`) der DOM-*-004-Welle zusammengefuehrt; `init_db.py upgrade head` per Backend-Neustart verifiziert
- **DOM-*-004-Tiefenwelle (2026-06-11/12)**: ~90 neue reine Logik-Unit-Tests gruen; 5 Live-UAT-Skripte (`scripts/uat/{con_contract,sales_o2c,fin_op,doc_nachweisraum,proc_match}_lifecycle_uat.py`, `--execute` mit DB-Restore); Frontend `tsc 0` + ESLint clean je Slice
- **Docker-Erstinstallation**: Alembic-Bootstrap und Mehr-Domaenen-Struktur auf leerer DB abgesichert
- **Service-Layer**: Hauptwellen refaktoriert; Legacy-Endpunkte `harvest_acceptance.py`, `agrar_settlements.py` und `docflow.py` repo-seitig mit dedizierten Services nachgezogen (Stand 2026-05-21)
- **Backend-Security**: Globale Bearer-Token-Auth, RFC-7807 Problem-Details, 62 Endpoints mit nosec-S608-Annotierungen (Wave 22 Backend-Security, Commits `4ab228f92` + `732d84376`); CI-Gate `scripts/check_sql_fstrings.py` aktiv
- **Tenant-Isolation**: CI-Gate eingezogen (Wave-A3 Commit `c106f74e8`)
- **E2E-Tests Wave 18–22 + W11**: 23/23 grün (Integrations-Gate Commit `97c41d479`)

---

## P1 - Verbleibende offene Punkte

### PROD-READINESS-001: Repo-seitige P0-Haertung abgeschlossen, Live-Gates offen

- Kanonische Release-Gates tolerieren keine Fehler bei TypeScript, ESLint,
  Backendtests, Doku oder High/Critical Dependency-/Security-Befunden.
- CycloneDX-SBOM, produktiver Runtime-/Secret-Preflight und simulierte
  Prueferprofile sind Teil der Release-Evidenz.
- Staging und Produktion nutzen unveraenderliche SHA-Images,
  GitHub-Environments, separaten Migrationsjob, atomaren Helm-Rollout,
  `/healthz`-/`/readyz`-Smoke und Rollback.
- Die Simulation ist strenger als eine reine Dokumentenpruefung: fehlende
  technische Evidenz ist `fail`; fehlende Live-Evidenz bleibt
  `external_gate` und blockiert den Go-live.
- Extern offen bleiben GitHub-Environment-Reviewer/Branch-Protection,
  produktive Cluster-Secrets, beobachtete Backup-/Restore- und Incident-Drills,
  UAT-Unterschriften, Steuerberater-/DSB-Freigaben sowie reale
  TSE-/DSFinV-K-Pruefwerkzeug- und Hardwareabnahmen.
- Runbook:
  [production-readiness-runbook.md](../operations/production-readiness-runbook.md)

- **Lagerbewegungs-Altpfade:** `INV-STOCK-MOVEMENTS-001` (2026-06-11) hat
  `articles.py` und `pos_retoure.py` auf `inventory_stock_movements` umgestellt.
  **2026-06-13:** `pos_retoure.py` schreibt jetzt auch `bin_stock`-Update (Bestandsfortschreibung
  bei Retoure geschlossen; movement_type von `'in'` auf `'RETOURE'` korrigiert).
  Verbleibend: tieferes Chargen-/MHD-Modell jenseits von `charge`.

### COVERAGE-001: Backend-Testabdeckung repo-weit weiter zu niedrig

- Gesamtabdeckung 64,85% — ueber dem 60%-Ratchet, aber fuer ein ERP-System langfristig zu niedrig. `100%` repo-weit ist kein belastbares Ziel.
- Ratchet fuer kritische Kernpfade laeuft gruen: `scripts/check_critical_backend_coverage.py` und `.github/workflows/quality-gate.yml` sichern 18 kritische Pfade.
- Stand 2026-05-21: Service-Layer-Refaktorierung fuer die bekannten grossen Legacy-Endpunkte nachgezogen (`harvest_acceptance.py`, `agrar_settlements.py`, `docflow.py`); fokussierte Service-/Import-/Unit-Checks gruen.
- Die zuvor fehlschlagenden 6 Tests sind behoben: `agrar_settlement_service.get_approval_history` liest jetzt korrekt aus `drying_result["approval_history"]`; `CustomerService._crm_create/_crm_update` korrekt gepatch in Tests.
- Finance-Welle abgeschlossen: `test_finance_followup_api.py`, `test_fibu_connectors_api.py`, `test_finance_actions.py` haertet kritische Finance-Pfade mit 70%/80%/90%-Ratchet-Schwellen.
- Auch `booking_templates.py`, `chart_of_accounts.py`, `inventory_counts.py`, `inventory_operations.py`, `exchange_rates.py`, `finance_actions.py`, `finance_followup.py`, `fibu_connectors.py`, `secrets_vault.py`, `tenant_enforcement.py`, `domains/shared/events.py` und `integration_bootstrap.py` liegen ueber den aktuellen Ratchet-Schwellen.
- Naechster Schritt: Ratchet fuer weitere produktkritische Backend-Pfade anheben, insbesondere Integrations-Governance und externe Fehlerpfade.
- Konkrete Reihenfolge und Ratchet-Hinweise liegen in [critical-backend-coverage-plan-2026-04-24.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md).
- **COV-RATCHET-005 (2026-05-28):** 15 neue Wave-2026-05-17b-Endpoints in Ratchet aufgenommen: `gdpr_art30_ropa` (80%), `gdpr_art33_breach` (94%), `genossenschaft` (58%), `intrastat` (57%), `gelangensbestaetigung` (57%), `gs1_barcode` (63%), `kontrakt_hedging` (74%), `kontrakt_klassen` (75%), `price_calculation` (83%), `sanctions_compliance` (66%), `webhook_system` (61%), `erechnung_import` (78%), `sales_invoice_einvoice` (30%), `waagen_vorlagen` (50%), `rohware_sammelabrechnung` (32%). Gesamt: 33 Ratchet-Pfade in `scripts/check_critical_backend_coverage.py`.

### DOMAIN-PARITY-001: Fachliche Tiefe der Domains ist weiterhin ungleich

- Der Repo-Schnitt ist breit, aber nicht alle Domaenen haben dieselbe fachliche Tiefe, denselben Testgrad oder dieselbe Integrationshaerte.
- Das ist ein laufendes Ausbauprogramm, kein einzelner Bugfix.
- Service-Layer-Refaktorierung: Haupt-Endpunkt-Welle 2026-05-16 abgeschlossen; bekannte grosse Legacy-Endpunkte 2026-05-21 nachgezogen.
- Die naechste programmatische Vertiefung ist konkretisiert in [erp-reference-matrix-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/erp-reference-matrix-2026-04-12.md) und den daraus abgeleiteten Slices `DOM-FIN-003`, `DOM-SUPPLY-003`, `DOM-PROC-003`, `DOM-CON-003`, `DOM-CRM-003`, `DOM-DOC-003`.
- **`.004`-Tiefenwelle abgeschlossen (2026-06-11/12)** — die operative Endlogik dieser Domaenen ist nachgezogen (Detail: [dom-004-spine-buildout-2026-06-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/dom-004-spine-buildout-2026-06-12.md)):
  - **DOM-CON-004** (Kontrakte): Fixierungs-Arbeitsraum + MATIF-Marktwert, Engagement-Sicht, Kontraktmahnung, Settlement-Uebergabe + Storno (`contract_{fixing,engagement,settlement}_service.py`).
  - **DOM-SALES-004** (O2C): Positions-Match Auftrag↔Lieferschein, Kreditlimit-Pruefung, durchgaengiges Storno/Gutschrift (`sales_{match,credit,storno}_service.py`).
  - **DOM-FIN-004** (FIBU): Mahnlauf + Stufen-Eskalation, Zahlungseingang/OP-Auszifferung, Periodenabschluss + Storno-Konsistenz, DATEV-Buchungsstapel-Export (`finance_{dunning,clearing,period,datev}_service.py`).
  - **DOM-DOC-004** (Nachweisraum): Artefakt-Upload/Versionierung/Freigabe, Bescheid/Rueckmeldung/Wiedervorlage, GoBD-Exportpaket + Paperless-Liveprobe (`docflow_{artifact,followup,gobd}_service.py`).
  - **DOM-PROC-004** (P2P): 3-Wege-Match (Rechnungsstufe), Folgeaktionen/Reklamation, ERS, RFQ→PO (`procurement_match_service.py`, `rfq_service.py`).
  - **DOM-SUPPLY-004** (Lieferkette): durchgaengige Rueckverfolgbarkeit, Ketten-Event-Log, Lot-Folgeaktionen (Sperre/QS-Freigabe/Schwund), Ketten-Storno.
  - **Extern gegated (ehrlich, kein Schein-OK):** zertifizierter DATEV-EXTF + Steuerberater-Cutover, DMS-/Paperless-Liveprobe (`PAPERLESS_URL`), reale Rohware-/Waage-/Druck-UAT-Unterschriften.
- Erste Codewelle aktiv: FIBU-Abschluss, Rechnungsabgleich, Kontraktsteuerung, moderner CRM-Stamm, Servicefall, Dokumentenablage, Meldewesen sowie Waage/Tourenplanung nutzen bereits gemeinsame Domain-Zusammenfassungen fuer Operator-, Uebergabe- und Nachweisdruck.
- Zweite Codewelle eingezogen: `fibu/schnittstellen-center.tsx`, `charge/wareneingang.tsx`, `einkauf/rechnungseingang.tsx`, `kontrakte/KontraktPositionsmonitor.tsx`, `crm/opportunity-detail.tsx` und `fibu/atlas.tsx`.
- Dritte Codewelle aktiv: `finance/mahnwesen.tsx`, `fibu/zahlungslaeufe.tsx`, `waage/wiegeschein-detail.tsx`, `annahme/rohware.tsx`, `logistik/frachtbriefe.tsx`, `einkauf/lieferanten-dokumente.tsx`, `einkauf/anlieferavis.tsx`, `einkauf/auftragsbestaetigung.tsx`, `kontrakte/FrmKontraktDetail.tsx`, `kontrakte/KontraktAlarmDashboard.tsx`, `crm/kontakt-management.tsx` und `dokumente/ablage.tsx`.
- Messbare Domaenenparitaet wird in [domain-parity-roadmap-2026-04-24.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/domain-parity-roadmap-2026-04-24.md) gefuehrt.
- UX-Paritaet wird ueber [ux-excellence-operating-standard-2026-05-13.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/ux-excellence-operating-standard-2026-05-13.md) gefuehrt. Stand 2026-05-16: systemweiter UX-Baukasten-Rollout abgeschlossen.

---

## P2 - Architektonisch offen / mittelfristig relevant

### HR-TIME-001: Deutsche Abwesenheit, Zeiterfassung und Fahrerzeit

- Fuer 27 Mitarbeitende mit relevantem LKW-Fahreranteil ist klassische Zeiterfassung allein fachlich nicht ausreichend.
- Die Zielarchitektur ist dokumentiert in [hr-time-absence-driver-integration-2026-05-07.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/hr-time-absence-driver-integration-2026-05-07.md).
- Lizenzlinie: `urlaubsverwaltung/urlaubsverwaltung` wird wegen Apache-2.0 als Abwesenheitskandidat geprueft; AGPL-/GPL-Zeiterfassung wird nicht als VALEO-Codebasis uebernommen.
- **Repo-seitig abgeschlossen (2026-05-16)**: Pilot-Slice implementiert — `domain_hr.driver_time_events`-Tabelle (Migration `driver_time_events_20260516`), CRUD-Endpoints `POST/GET/PATCH/DELETE /api/v1/personal/driver-time/events`, Abwesenheitskollisions-Check `GET /api/v1/personal/driver-time/events/absences/collisions`. Tour-/Fahrzeugbezug (`vehicle_id`, `tour_ref`) und Quellenfeld (`source`: MANUAL/TACHO/IMPORT/SYSTEM) sind im Datenmodell abgebildet.
- Offene externe Risiken (nicht repo-seitig loesbar): Rechtspruefung Arbeitszeitgesetz, Anbieter-AVV/DPA, Tacho-/Telematik-Schnittstellen-Anbindung, Payroll-/DATEV-Zielformat.

---

## P4 - Externe Abhaengigkeiten (nicht repo-seitig loesbar)

### EXT-001: Live-Credentials und Zielsystem-URLs

- Superglue-Connectors, L3-Import, Erstinstallation und Finance-Export brauchen produktive Tenant-Secrets, Zielsystem-URLs und Ops-Alerting-Werte, die ausserhalb des Repos gepflegt werden.
- Repo-seitig vollstaendig vorbereitet: `.env.example`, `scripts/check_integration_bootstrap.py` und [integration-bootstrap-readiness-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/integration-bootstrap-readiness-2026-04-12.md).
- `python scripts/check_integration_bootstrap.py --probe-plan` zeigt je Integration den produktionsnahen Live-Pruefpfad inklusive Ziel, Command-Hinweis und Blockern.
- `python scripts/check_integration_bootstrap.py --strict-live` blockiert, solange ein Probe nicht `ready` ist.

### EXT-002: FIBU-Mappings fuer Cutover

- Fachlich freigegebene Konten-/Steuer-/Kostenstellen-Mappings fuer die ERP-Migration stehen noch aus.
- Repo-seitig vollstaendig vorbereitet: `config/fibu_cutover_mapping.template.yaml` plus `python scripts/check_fibu_cutover_mapping.py --mapping <datei> --strict`.

---

## Infrastruktur-Status (Kurzreferenz)

| Komponente | Status | Bemerkung |
|------------|--------|-----------|
| PostgreSQL 15 | produktiv | Multi-Schema, Alembic-Migrationen |
| Redis 7 | produktiv | Session/Cache |
| NATS JetStream | Dev-auto / ops-konfigurierbar | Docker-Dev startet NATS automatisch |
| Keycloak/OIDC | produktiv | RS256/JWKS, dev-Bypass via `API_DEV_TOKEN` |
| Paperless-ngx DMS | produktiv | HTTP-Client mit Retry |
| ChromaDB/RAG | produktiv (erweitert) | Artikel + Kunden + Kontrakte + Futtermittel + Knowledge + Obsidian-Sync |
| Superglue Self-Host | verdrahtet | Upstream-Contract aktuell, 3 Pilot-Tools provisioniert |
| Voice-Kanal | provider-ready | Whisper/Azure/OpenAI TTS konfigurierbar, Browser-Fallback |
| Tenant-Enforcement | Middleware | `TenantEnforcementMiddleware` validiert `X-Tenant-ID` zentral |
| Event-Bus-Monitoring | repo-seitig komplett | Grafana-Dashboard + Prometheus-Alerting-Regeln in `monitoring/` |

---

## Zuletzt geschlossene Punkte (2026-05-16)

- ~~UX-GAP-CLOSURE-001~~ -> UX-Baukasten-Rollout systemweit abgeschlossen. Portal-Dokumente auf Self-Service-Niveau reduziert. Seitentyp-Logik statt pauschaler Vollausstattung. Keine offenen Rollout-Gaps.
- ~~HRM-GERMANY-GAP-001~~ -> Alle fachlichen Repo-Gaps aus dem HRM-Plan geschlossen: Personalakte, eAU-Gate, Vertrags-/Dokumentenmanagement, ESS/MSS-Gates, DSFA/KI-Gates, Go-live-Vorlagenpaket (17 Einzelvorlagen). Externe Nachweise laufen als persistente Betriebsfreigabe-Gates im Frontend.
- ~~EXT-003: Externes Monitoring/Alerting~~ -> Grafana-Dashboard `monitoring/grafana/dashboards/event-bus-dashboard.json` und Prometheus-Alerting-Regeln `monitoring/prometheus/alerts-event-bus.yml` fuer alle `valeo_event_bus_*`-Metriken dem Repo hinzugefuegt. Ops-seitige Aktivierung bleibt externe Konfiguration (Grafana-URL, Alertmanager).
- ~~Service-Layer-Refaktorierung~~ -> Alle 6 Haupt-Endpunkt-Dateien auf thin-router + Service-Klassen umgestellt: `business_partners.py`, `customers.py`, `personal.py` (Zeiteintraege + Abwesenheiten), `controlling.py`, `agrar_contracts.py`, `einkauf_bestellvorschlag.py`.
- ~~Service-Layer-Legacy-Endpunkte~~ -> `harvest_acceptance.py`, `agrar_settlements.py` und `docflow.py` haben dedizierte Services; verbliebene Router sind auf Schema-/Dependency-Wiring und HTTP-Fehler-Mapping reduziert.
- ~~HR-TIME-001 (Pilot-Slice)~~ -> `domain_hr.driver_time_events`-Tabelle, CRUD-Endpoints und Abwesenheitskollisions-Check repo-seitig implementiert.

## Agrar-Spezialsoftware/Externe-Plattform Paritaets-Gaps (2026-05-17, aktualisiert)

Analysen:
- [agrar-parity-matrix-2026-05-17.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/agrar-parity-matrix-2026-05-17.md)
- [agrar-erp-gap-matrix-2026-05-17.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/agrar-erp-gap-matrix-2026-05-17.md) — NEU 2026-05-17

Quellen: Browser-Analyse externer Agrar-Spezialsoftware (vollstaendiger Modulbaum) und externer Agrar-ERP-Plattform (165 Endpoints, 24 Module).

Stand Wave 2026-05-17 (P0/P1 Gaps implementiert):
- `WAAGE-LIVE-001`, `SILO-LEER-001`, `PARTIE-PFLICHT-001`, `ROHWARE-SCHEMA-001`: implementiert (Wellen 05-17)
- `L3-WAAGE-001` (Doppelwiegung/Gosse): in Arbeit (Wave 2026-05-17b)
- `L3-DISP-001` (Kontrakt Disposition sub-resource): in Arbeit
- `L3-KONTRAKT-001/002` (Klassen/Hedging): in Arbeit
- `L3-ERECHNUNG-001` (XRechnung/ZUGFeRD Import): in Arbeit
- `L3-PREIS-001` (Preis berechnen Endpoint): in Arbeit
- `VALEO-COMP-001` (Sanktionsliste): in Arbeit
- `VALEO-GEN-001` (Genossenschaftsverwaltung): in Arbeit
- `VALEO-FIBU-001/002` (Gelangensbestaetigung, Intrastat): in Arbeit

| Gap-ID | Kurzbeschreibung | Prioritaet | Status |
|--------|-----------------|------------|--------|
| VALEO-PARITY-001 | O2C/P2P/Partie-Kette — UAT-Pfad fehlt | P0 | repo-seitig vorbereitet; UAT-Unterschrift extern |
| WAAGE-LIVE-001 | Waage: Live-Hardware, Eich-Nachweis | P0 | implementiert (Repo), UAT offen |
| SILO-LEER-001 | Silo-Leermeldung, Schwundbuchung | P0 | implementiert |
| L3-WAAGE-001 | Doppelwiegung (Wiegung1/2), Gosse, WaageId | P0 | implementiert |
| L3-DISP-001 | Kontrakt Disposition sub-resource + Freigabe | P1 | implementiert |
| L3-KONTRAKT-001 | Kontraktklassen/Varianten (Fixpreis/Basis/Praemie) | P1 | implementiert |
| L3-KONTRAKT-002 | Kontrakt-Hedging (MATIF mark-to-market) | P1 | implementiert |
| L3-ROHWARE-001 | Rohware-Sammelabrechnung | P1 | implementiert |
| L3-ERECHNUNG-001 | e-Rechnung Import ZUGFeRD/XRechnung | P1 | implementiert |
| L3-PREIS-001 | Preis berechnen Endpoint (Kalkulationsengine) | P1 | implementiert |
| L3-CRM-002 | Interessent → Kunde Konvertierung | P1 | implementiert |
| VALEO-COMP-001 | Sanktionsliste / Verbotsliste | P1 | implementiert |
| VALEO-GEN-001 | Aktionaers-/Gesellschafterverwaltung (Genossenschaft) | P1 | implementiert |
| VALEO-FIBU-001 | Gelangensbestaetigung (§17a UStDV) | P1 | implementiert |
| VALEO-FIBU-002 | Intrastat EU-Handelsstatistik | P1 | implementiert |
| PARTIE-PFLICHT-001 | Partiepflicht-Validierung je Artikel/Wiegetyp | P1 | implementiert |
| ROHWARE-SCHEMA-001 | Abrechnungsschema-Editor + Testrechnung | P1 | implementiert |
| CTS-H2S-UAT-001 | Rohware-UAT Schemata, Varianten, Nachtraege | P0 | offen (UAT extern) |
| FIBU-CUTOVER-002 | SKR03/SKR04-Mapping + Steuerberaterabnahme | P0 | offen (extern) |
| DMS-DOC-002 | DMS-Live-Probe, Redirect-Failure, Audit-Paket | P1 | repo-seitig vorbereitet; Live-Probe extern |
| POS-DSFINVK-001 | TSE-/DSFinV-K-Abnahme | P1 | Provider, Admin, Tagesabschluss und simuliertes Prueferprofil repo-seitig implementiert; reale TSE-/DSFinV-K-2.4-Pruefwerkzeug-Abnahme extern |
| REPORT-PRINT-001 | Partie-Genealogie, Wiegschein-PDF, Etikett | P1 | repo-seitig implementiert; Drucker-/UAT-Abnahme extern |
| VALEO-FIBU-006 | eBilanz/ELSTER-Direktschnittstelle | P1 | repo-seitig implementiert; ERiC-/Steuerberater-Gate extern |
| VALEO-FIBU-003 | ATLAS Zollausfuhr | P2 | implementiert; ATLAS-Zertifikat extern |
| L3-CRM-001 | Umkreissuche Kunden (Geo-Radius) | P2 | implementiert |
| L3-WEBHOOK-001 | Outbound Webhook-Registrierung | P2 | implementiert |
| L3-WEBSHOP-001 | Webshop B2B-Bestellintegration | P2 | implementiert |
| L3-GS1-001 | GS1 Barcode Parse Service | P2 | implementiert |
| L3-LAGER-001 | Ruestliste (Kommissioniervorbereitung) | P2 | implementiert |
| VALEO-WAAGE-VORL | Waagenvorlagen/Wiederholfall-Anlieferungen | P2 | implementiert |
| VALEO-SAATZ-001 | Saatzucht-Modul | P2 | implementiert |

## Enterprise-Domain-Gap-Closure (Marktführende ERP-Systeme/Odoo/Agrar-Spezialsoftware) 2026-05-17

Repo-seitig ergaenzt und registriert:

- CRM: Opportunity-Pipeline, Forecast, 360-Grad-Kundensicht, Account-Hierarchie und Service-Case-SLA.
- Finance: Anlagenbuchhaltung, Budgetierung und Liquiditaetsplanung.
- Logistik: Tourenplanung, Frachtkosten, Track & Trace, ePOD und Transportstatistik.
- Einkauf: DOM-PROC-004 + RFQ (PROC-RFQ-001, 2026-06-11) abgeschlossen: Match-Spine, Folgeaktionen, ERS, RFQ→PO mit Alembic + Integrationstests.
- Verkauf/Kontrakte: Rahmenauftraege, Kreditlimit, Sammelbelege und zentrale Contract-/Obligation-Engine.
- Futtermittel: Rohwaren-API, Rezepturverwaltung, Naehrstoffanalyse, Deklaration und Etikett-Vertrag.
- HRM: Org-Chart, Bewerberpipeline, Arbeitszeitkonto, Whistleblower (anonym), DSGVO-Loeschkonzept.
- POS: Split-Payment (Multi-Tender), Promotions CRUD + Check (PROZENT/BETRAG/BOGO), X/Z-Berichte.
- HRM/Compliance/POS: Organigramm, Arbeitszeitkonto, Bewerberpipeline, DSGVO-Loeschantraege, Whistleblower, LkSG, POS-Split-Payment und Promotions-Preview.
- Webshop: B2B-Bestellsync mit idempotentem Import, Dubletten-Erkennung, fachlichen Blockern fuer Kunden-/Positions-/Summenkontext, Lesepfad und ERP-Verarbeitungsreferenz.
- Phase 2/3 Closure: eBilanz/ELSTER-Readiness mit ERiC-Gates, GS1/SSCC im Barcode-Parser, DSFinV-K-v2.3-ZIP-Nachweis, ATLAS-Zollausfuhr, Saatzucht und Futtermittel-API-Regressionen sind repo-seitig abgesichert.
- Report/Print: Partie-Genealogie mit Rueckverfolgungsknoten, Wiegeschein-PDF-Preview/Artefaktmetadaten und GS1-Label-Vertrag fuer Partie/Charge/Artikel/SSCC/GTIN.
- O2C/P2P/Partie-UAT: `/uat/o2c/readiness` weist repo-seitige Abdeckung fuer O2C, P2P und Partie-Kette aus; vorhandener 7-Schritt-Szenario-Runner bleibt kompatibel.

Checks: `pytest tests/test_crm_pipeline_360.py tests/test_einkauf_3way_match_ers_rfq.py tests/test_finance_asset_budget_liquidity.py tests/test_logistics_tour_freight.py tests/test_major_domain_router_registration.py tests/test_personal_major_gap_extensions.py tests/test_compliance_pos_gap_extensions.py tests/test_process_kernel_wave100_settlement_completion.py tests/test_process_kernel_wave31_dq_extended_write_paths.py -q --no-cov --tb=short` -> 70 gruen.

Nicht repo-seitig schliessbar bleiben echte externe Abnahmen und Zugangsdaten: Steuerberater-/DATEV-Mapping, DMS-Live-Probe, reale TSE-/DSFinV-K-Pruefwerkzeugvalidierung und UAT-Unterschriften mit echten Rohwaren-/Waage-/Druckdaten.

---

## Zuletzt geschlossene Punkte (2026-04-13)

- ~~DB-BOOT-001~~ -> `python scripts/init_db.py` laeuft jetzt auf leerer Postgres-DB bis `head`; `scripts/check_required_domain_schemas.py` prueft die Mehr-Domaenen-Struktur; `scripts/smoke_first_install_docker.ps1/.sh` liefern den reproduzierbaren Docker-Smoke.
- ~~ARCH-DOM-001~~ -> `scripts/check_domain_table_ownership.py` prueft jetzt fachliche Tabellen-Zuordnung inklusive dokumentierter Legacy-Placements.
- ~~COVERAGE-ERP-001~~ -> `scripts/check_critical_backend_coverage.py` fuehrt einen CI-Ratchet fuer kritische Kernpfade ein; neue Tests decken Event-Bus-Runtime, Integrations-Bootstrap und Tenant-Enforcement ab.
- ~~NATS-DEV-001~~ -> `docker-compose.yml`, `docker-compose.dev.yml` und `.env.example` starten und konfigurieren NATS im Dev-Betrieb automatisch.
- ~~INT-BOOT-001~~ -> `app/services/integration_bootstrap.py`, `scripts/check_integration_bootstrap.py` und [integration-bootstrap-readiness-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/integration-bootstrap-readiness-2026-04-12.md) liefern den repo-seitigen Bootstrap- und Readiness-Pfad fuer OIDC, NATS, Superglue, Voice und CRM-Downstream.
- ~~OP-ROLL-049 bis OP-ROLL-072~~ -> alle 24 Slices abgeschlossen: Dunning-Editor, 6 Lager-Masken, Terminal, 3 Qualitaet-Masken, Frachtbriefe und Wiegungen tragen denselben leichten operativen Fallkopf.
- ~~NATS-001~~ -> Docker-Dev-Stack startet NATS automatisch (`EVENT_BUS_ENABLED=true`); Nicht-Docker-Betrieb laeuft mit `EVENT_BUS_ENABLED=false` (Default) sauber ohne NATS.
- ~~RAG-002~~ -> `scripts/obsidian_to_rag.py` liest Markdown-Dateien aus `OBSIDIAN_VAULT_PATH`, upserted sie idempotent in `domain_shared.knowledge_objects` / `knowledge_versions`.
- ~~DOC-REF-002~~ -> neutrale Community-ERP-Bezeichnungen; kein repo-weiter Treffer fuer das zuvor diskutierte Produkt mehr.

---

## Analysepflicht

Wenn in Code, Tests oder UI ein Widerspruch zwischen Doku, Implementierung, Fachlogik oder Benutzerfuehrung auftaucht, ist das hier oder in der passenden Workflow-Datei zu dokumentieren.

## Verweis

Formale Projekt- und Lieferstaende liegen weiterhin in:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/roadmap/status/*.md`
- `docs/project-context/operational-rollout-scope-2026-04-09.md`
- `docs/roadmap/status/2026-04-03-security-hardening-phase-2.md`
