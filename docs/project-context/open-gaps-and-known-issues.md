# Open Gaps and Known Issues

## Zweck

Ehrliche, aktuelle Bestandsaufnahme aller offenen Restthemen, fachlichen Duennstellen und bekannten Risiken.
Zuletzt vollstaendig auditiert: **2026-05-16**.

---

## Build-Health (Stand 2026-05-16)

- **TypeScript**: 0 Fehler (`tsc --noEmit`)
- **Backend-Tests**: 8564 passed, 68 skipped, 1 xfailed, 0 failed — alle 18 Ratchet-Pfade gruen; Gesamtabdeckung 64,85%
- **Frontend-Imports**: 0 gebrochene Importe
- **Alembic**: 1 Head
- **Docker-Erstinstallation**: Alembic-Bootstrap und Mehr-Domaenen-Struktur auf leerer DB abgesichert
- **Service-Layer**: vollstaendig refaktoriert — alle Endpoints auf thin-router + Service-Klassen (Stand 2026-05-16)

---

## P1 - Verbleibende offene Punkte

### COVERAGE-001: Backend-Testabdeckung repo-weit weiter zu niedrig

- Gesamtabdeckung 64,85% — ueber dem 60%-Ratchet, aber fuer ein ERP-System langfristig zu niedrig. `100%` repo-weit ist kein belastbares Ziel.
- Ratchet fuer kritische Kernpfade laeuft gruen: `scripts/check_critical_backend_coverage.py` und `.github/workflows/quality-gate.yml` sichern 18 kritische Pfade.
- Stand 2026-05-16: Service-Layer-Refaktorierung abgeschlossen (`business_partners.py`, `customers.py`, `personal.py`, `controlling.py`, `agrar_contracts.py`, `einkauf_bestellvorschlag.py`). 0 failing Tests.
- Die zuvor fehlschlagenden 6 Tests sind behoben: `agrar_settlement_service.get_approval_history` liest jetzt korrekt aus `drying_result["approval_history"]`; `CustomerService._crm_create/_crm_update` korrekt gepatch in Tests.
- Finance-Welle abgeschlossen: `test_finance_followup_api.py`, `test_fibu_connectors_api.py`, `test_finance_actions.py` haertet kritische Finance-Pfade mit 70%/80%/90%-Ratchet-Schwellen.
- Auch `booking_templates.py`, `chart_of_accounts.py`, `inventory_counts.py`, `inventory_operations.py`, `exchange_rates.py`, `finance_actions.py`, `finance_followup.py`, `fibu_connectors.py`, `secrets_vault.py`, `tenant_enforcement.py`, `domains/shared/events.py` und `integration_bootstrap.py` liegen ueber den aktuellen Ratchet-Schwellen.
- Naechster Schritt: Ratchet fuer weitere produktkritische Backend-Pfade anheben, insbesondere Integrations-Governance und externe Fehlerpfade.
- Konkrete Reihenfolge und Ratchet-Hinweise liegen in [critical-backend-coverage-plan-2026-04-24.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md).

### DOMAIN-PARITY-001: Fachliche Tiefe der Domains ist weiterhin ungleich

- Der Repo-Schnitt ist breit, aber nicht alle Domaenen haben dieselbe fachliche Tiefe, denselben Testgrad oder dieselbe Integrationshaerte.
- Das ist ein laufendes Ausbauprogramm, kein einzelner Bugfix.
- Service-Layer-Refaktorierung 2026-05-16 abgeschlossen: alle 6 Haupt-Endpunkt-Dateien auf thin-router + Service-Klassen umgestellt.
- Die naechste programmatische Vertiefung ist konkretisiert in [erp-reference-matrix-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/erp-reference-matrix-2026-04-12.md) und den daraus abgeleiteten Slices `DOM-FIN-003`, `DOM-SUPPLY-003`, `DOM-PROC-003`, `DOM-CON-003`, `DOM-CRM-003`, `DOM-DOC-003`.
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

- Fachlich freigegebene Konten-/Steuer-/Kostenstellen-Mappings fuer die L3-Migration stehen noch aus.
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
- ~~HR-TIME-001 (Pilot-Slice)~~ -> `domain_hr.driver_time_events`-Tabelle, CRUD-Endpoints und Abwesenheitskollisions-Check repo-seitig implementiert.

## AMIC-Paritaets-Gaps (2026-05-17)

Vollstaendige Analyse in [amic-parity-matrix-2026-05-17.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/amic-parity-matrix-2026-05-17.md).

| Gap-ID | Kurzbeschreibung | Prioritaet | Status |
|--------|-----------------|------------|--------|
| AMIC-PARITY-001 | O2C/P2P/Partie-Kette — Browser-/CRUD-UAT-Pfad vollstaendig fehlt | P0 | offen |
| WAAGE-LIVE-001 | Waage: Live-Hardware-Import, Eich-Nachweis, Offline-Queue | P0 | offen |
| SILO-LEER-001 | Silo-Leermeldung, Schwundbuchung, Fehlermatrix, Waagenbeleg-Kopplung | P0 | offen |
| PARTIE-PFLICHT-001 | Partiepflicht-Validierung je Artikel/Wiegetyp fehlt zentral | P1 | offen |
| ROHWARE-SCHEMA-001 | Abrechnungsschema-Editor/Katalog mit Versionierung und Testrechnung | P1 | offen |
| CTS-H2S-UAT-001 | Rohware-UAT gegen echte Schemata, regionale Varianten, Nachtraege | P0 | offen |
| FIBU-CUTOVER-002 | Extern freigegebenes SKR03/SKR04-Mapping + Steuerberaterabnahme | P0 | offen (vgl. EXT-002) |
| DMS-DOC-002 | DMS-Live-Probe, Redirect-Failure, Audit-Paket | P1 | offen |
| POS-DSFINVK-001 | Produktive TSE-/DSFinV-K-Abnahme mit realem Exportpaket | P1 | offen |
| REPORT-PRINT-001 | Partie-Genealogie-Report, Wiegschein-Druck, Etikett-Ausgabe | P1 | offen |

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
