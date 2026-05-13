# Open Gaps and Known Issues

## Zweck

Ehrliche, aktuelle Bestandsaufnahme aller offenen Restthemen, fachlichen Duennstellen und bekannten Risiken.
Zuletzt vollstaendig auditiert: **2026-05-05**.

---

## Build-Health (Stand 2026-05-05)

- **TypeScript**: 0 Fehler (`tsc --noEmit`)
- **Backend-Tests**: kritische Pfade werden per Ratchet gesichert; 18 von 18 Ratchet-Pfaden laufen ueber Schwelle (Stand 2026-05-05)
- **Frontend-Imports**: 0 gebrochene Importe
- **Alembic**: 1 Head
- **Docker-Erstinstallation**: Alembic-Bootstrap und Mehr-Domaenen-Struktur auf leerer DB abgesichert

---

## P1 - Verbleibende offene Punkte

### COVERAGE-001: Backend-Testabdeckung repo-weit weiter zu niedrig

- Gesamtabdeckung ist fuer ein ERP-System weiterhin zu niedrig. `100%` repo-weit ist kurzfristig kein belastbares Ziel.
- Neu ist ein Ratchet fuer kritische Kernpfade ueber `scripts/check_critical_backend_coverage.py` und `.github/workflows/quality-gate.yml`.
- Die naechste Finance-Welle ist angelaufen: `tests/test_finance_followup_api.py` haertet Preview-, Export-, Download-, DMS-Redirect- und Upload-Metadatenpfade von `app/api/v1/endpoints/finance_followup.py`; `tests/test_fibu_connectors_api.py` deckt Profile, Import-Laeufe, Run-Items und Folgeaktionen in `app/api/v1/endpoints/fibu_connectors.py` ab; `tests/test_finance_actions.py` deckt jetzt reale Finance-Aktionspfade in `app/api/v1/endpoints/finance_actions.py` ab. Die drei Pfade haengen jetzt mit Mindestabdeckung (`70%`, `80%`, `90%`) im kritischen Coverage-Ratchet.
- Die frueheren `skipped`-Faelle in Mahnwesen, Wechselkursen und Zahlungslaufen sind nicht mehr an eine zufaellige Live-DB gekoppelt. Die API-Tests laufen jetzt mit deterministischen Test-Doubles, und eine Reparaturmigration zieht die fehlenden Finance-API-Tabellen (`dunning_*`, `payment_*`, `exchange_rates`) auch auf Bestandsdatenbanken nach.
- Der naechste sinnvolle Schritt ist das Anheben oder Erweitern des Ratchets fuer weitere produktkritische Backend-Pfade, insbesondere Integrations-Governance und externe Fehlerpfade.
- Konkrete Reihenfolge und Ratchet-Hinweise liegen jetzt in [critical-backend-coverage-plan-2026-04-24.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md).
- Stand 2026-05-05: `python scripts/check_critical_backend_coverage.py` ist nach der dokumentierten Sammelsuite gruen. Auch `booking_templates.py`, `chart_of_accounts.py`, `inventory_counts.py`, `inventory_operations.py`, `exchange_rates.py`, `finance_actions.py`, `finance_followup.py`, `fibu_connectors.py`, `secrets_vault.py`, `tenant_enforcement.py`, `domains/shared/events.py` und `integration_bootstrap.py` liegen ueber den aktuellen Ratchet-Schwellen.

### DOMAIN-PARITY-001: Fachliche Tiefe der Domains ist weiterhin ungleich

- Der Repo-Schnitt ist breit, aber nicht alle Domaenen haben dieselbe fachliche Tiefe, denselben Testgrad oder dieselbe Integrationshaerte.
- Das ist ein laufendes Ausbauprogramm, kein einzelner Bugfix.
- Die naechste programmatische Vertiefung ist jetzt konkretisiert in [erp-reference-matrix-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/erp-reference-matrix-2026-04-12.md) und den daraus abgeleiteten Slices `DOM-FIN-003`, `DOM-SUPPLY-003`, `DOM-PROC-003`, `DOM-CON-003`, `DOM-CRM-003`, `DOM-DOC-003`.
- Erste Codewelle ist aktiv: FIBU-Abschluss, Rechnungsabgleich, Kontraktsteuerung, moderner CRM-Stamm, Servicefall, Dokumentenablage, Meldewesen sowie Waage/Tourenplanung nutzen bereits gemeinsame Domain-Zusammenfassungen fuer Operator-, Uebergabe- und Nachweisdruck.
- Zweite Codewelle ist ebenfalls eingezogen: `fibu/schnittstellen-center.tsx`, `charge/wareneingang.tsx`, `einkauf/rechnungseingang.tsx`, `kontrakte/KontraktPositionsmonitor.tsx`, `crm/opportunity-detail.tsx` und `fibu/atlas.tsx` bilden dieselbe Verdichtung jetzt direkt in den operativen Folgepfaden ab.
- Dritte Codewelle ist jetzt ebenfalls aktiv: `finance/mahnwesen.tsx`, `fibu/zahlungslaeufe.tsx`, `waage/wiegeschein-detail.tsx`, `annahme/rohware.tsx`, `logistik/frachtbriefe.tsx`, `einkauf/lieferanten-dokumente.tsx`, `einkauf/anlieferavis.tsx`, `einkauf/auftragsbestaetigung.tsx`, `kontrakte/FrmKontraktDetail.tsx`, `kontrakte/KontraktAlarmDashboard.tsx`, `crm/kontakt-management.tsx` und die vertiefte `dokumente/ablage.tsx` sind auf dasselbe leichte Operator- und Nachweisbild gezogen.
- Messbare Domaenenparitaet wird jetzt in [domain-parity-roadmap-2026-04-24.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/domain-parity-roadmap-2026-04-24.md) gefuehrt.

---

## P2 - Architektonisch offen / mittelfristig relevant

### HR-TIME-001: Deutsche Abwesenheit, Zeiterfassung und Fahrerzeit

- Fuer 27 Mitarbeitende mit relevantem LKW-Fahreranteil ist klassische Zeiterfassung allein fachlich nicht ausreichend.
- Die Zielarchitektur ist dokumentiert in [hr-time-absence-driver-integration-2026-05-07.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/hr-time-absence-driver-integration-2026-05-07.md).
- Lizenzlinie: `urlaubsverwaltung/urlaubsverwaltung` wird wegen Apache-2.0 als Abwesenheitskandidat geprueft; AGPL-/GPL-Zeiterfassung wird nicht als VALEO-Codebasis uebernommen.
- Der naechste sinnvolle Umsetzungsschritt ist ein Pilot-Slice fuer Driver-Time-Datenmodell, manuelle Fahrerzeitereignisse, Tour-/Fahrzeugbezug und Abwesenheitskollisionen.
- Offene externe Risiken: Rechtspruefung, Anbieter-AVV/DPA, Tacho-/Telematik-Schnittstellen und Payroll-/DATEV-Zielformat.

### HRM-GERMANY-GAP-001: Deutsches HRM-Betriebssystem ueber HR-Time hinaus

- HR-Time deckt Arbeitszeit, Abwesenheit, Schicht, Kalender, Fahrerzeit und Payroll-Readiness bereits als operativen Kern ab; ein vollstaendiges deutsches HRM-System braucht zusaetzlich Personalakte, eAU, Vertrags-/Dokumentenmanagement, ESS/MSS, Recruiting, Performance, People Analytics, Datenschutz-Governance, kontrollierte KI und Office-Connectoren.
- Der Zielvertrag und die Gap-Matrix liegen in [hrm-germany-operating-system-gap-plan-2026-05-13.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md).
- Repo-seitig sind die maschinenlesbaren Vertraege unter `GET /api/v1/personal/hrm-readiness`, `GET /api/v1/personal/hrm-operating-system` und `GET/POST /api/v1/personal/employee-files/...` verfuegbar.
- Stand 2026-05-13: Die fachlichen Repo-Gaps aus dem HRM-Plan sind ueber `HRM-GERMANY-GAP-001`, `HRM-AKTE-001` und `HRM-GAP-CLOSURE-001` geschlossen; verbliebene Punkte sind externe Betriebsfreigaben.
- Offene externe Risiken: Rechtsfeinpruefung, Betriebsvereinbarungen, AVV/DPA, echte eAU-/DATEV-/Office-Zugangsdaten, Hosting-/Subprozessorenpruefung und DSFA fuer risikoreiche Analytics oder KI.

---

## P4 - Externe Abhaengigkeiten (nicht repo-seitig loesbar)

### EXT-001: Live-Credentials und Zielsystem-URLs

- Superglue-Connectors, L3-Import, Erstinstallation und Finance-Export brauchen produktive Tenant-Secrets, Zielsystem-URLs und Ops-Alerting-Werte, die ausserhalb des Repos gepflegt werden.
- Repo-seitig ist die Bootstrap-Reife jetzt besser vorbereitet ueber `.env.example`, `scripts/check_integration_bootstrap.py` und [integration-bootstrap-readiness-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/integration-bootstrap-readiness-2026-04-12.md).
- Der Bootstrap-Bericht liefert jetzt zusaetzlich `probe_plan`; `python scripts/check_integration_bootstrap.py --probe-plan` zeigt je Integration den produktionsnahen Live-Pruefpfad inklusive Ziel, Command-Hinweis und Blockern. Echte Requests bleiben bewusst ops-seitig, weil produktive Tenant-Secrets und Zielsysteme extern sind.
- Fuer Live-Gates mit echten Werten steht `python scripts/check_integration_bootstrap.py --strict-live` bereit; der Befehl blockiert, solange ein Probe nicht `ready` ist.

### EXT-002: FIBU-Mappings fuer Cutover

- Fachlich freigegebene Konten-/Steuer-/Kostenstellen-Mappings fuer die L3-Migration stehen noch aus.
- Repo-seitig existieren jetzt Vorlage und Gate: `config/fibu_cutover_mapping.template.yaml` plus `python scripts/check_fibu_cutover_mapping.py --mapping <datei> --strict`.

### EXT-003: Externes Monitoring/Alerting

- Prometheus-Metriken (`valeo_event_bus_*`) werden exportiert, aber Grafana-Dashboards und Alerting-Regeln sind nicht im Repo und muessen ops-seitig aufgesetzt werden.

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

---

## Zuletzt geschlossene Punkte (2026-04-13)

- ~~DB-BOOT-001: Erstinstallation ueber Docker/Alembic war nicht deterministisch abgesichert~~ -> `python scripts/init_db.py` laeuft jetzt auf leerer Postgres-DB bis `head`; `scripts/check_required_domain_schemas.py` prueft die Mehr-Domaenen-Struktur; `scripts/smoke_first_install_docker.ps1/.sh` liefern den reproduzierbaren Docker-Smoke.
- ~~ARCH-DOM-001 war offen~~ -> `scripts/check_domain_table_ownership.py` prueft jetzt fachliche Tabellen-Zuordnung inklusive dokumentierter Legacy-Placements.
- ~~COVERAGE-ERP-001 war offen~~ -> `scripts/check_critical_backend_coverage.py` fuehrt einen CI-Ratchet fuer kritische Kernpfade ein; neue Tests decken Event-Bus-Runtime, Integrations-Bootstrap und Tenant-Enforcement ab.
- ~~NATS-DEV-001 war offen~~ -> `docker-compose.yml`, `docker-compose.dev.yml` und `.env.example` starten und konfigurieren NATS im Dev-Betrieb automatisch.
- ~~INT-BOOT-001 war offen~~ -> `app/services/integration_bootstrap.py`, `scripts/check_integration_bootstrap.py` und [integration-bootstrap-readiness-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/integration-bootstrap-readiness-2026-04-12.md) liefern den repo-seitigen Bootstrap- und Readiness-Pfad fuer OIDC, NATS, Superglue, Voice und CRM-Downstream.
- ~~OP-ROLL-049 bis OP-ROLL-072 (Fallkopf-Rollout Welle 3) waren reserviert~~ -> alle 24 Slices abgeschlossen: Dunning-Editor, 6 Lager-Masken (Bestandsuebersicht, Korrektur, Ein-/Auslagerung, Bewegungen, Inventur), Terminal, 3 Qualitaet-Masken (Ausnahmen, Reklamationen, Labor-Detail), Frachtbriefe und Wiegungen tragen jetzt denselben leichten operativen Fallkopf. 11 weitere Finance/FIBU-Masken hatten den Header bereits aus frueheren Sessions.
- ~~NATS-001 war offen~~ -> Docker-Dev-Stack startet NATS automatisch (`EVENT_BUS_ENABLED=true`); Nicht-Docker-Betrieb laeuft mit `EVENT_BUS_ENABLED=false` (Default) sauber ohne NATS — graceful Fallback auf Memory-Provider. Ops-Profile bleiben externe Konfiguration.
- ~~RAG-002 war offen~~ -> `scripts/obsidian_to_rag.py` liest Markdown-Dateien aus `OBSIDIAN_VAULT_PATH`, upserted sie idempotent in `domain_shared.knowledge_objects` / `knowledge_versions` und triggert RAG-Reindex via `indexer.index_knowledge()`. Konfiguration ueber `OBSIDIAN_VAULT_PATH` in `.env.example` und `app/core/config.py`. Frontmatter-Parser extrahiert Titel, Typ, Tags und Zielrollen.
- ~~ARCH-DOM-001 war offen~~ -> `scripts/check_domain_table_ownership.py` prueft fachliche Tabellen-Zuordnung; Legacy-Placements (`domain_crm.sales_*`, `domain_inventory.agrar_*`, `domain_shared.agrar_sorten`, `domain_einkauf.kontrakte`) sind dokumentiert und bewusst toleriert. Ownership ist pruefbar und transparent.
- ~~DOC-REF-002 war offen~~ -> die aktive Referenzanalyse und die betroffenen Doku-/Archivpfade nutzen jetzt neutrale Community-ERP-Bezeichnungen; ein repo-weiter Textscan liefert keine direkte Nennung des zuvor diskutierten Produkts mehr.

---

## Analysepflicht

Wenn in Code, Tests oder UI ein Widerspruch zwischen Doku, Implementierung, Fachlogik oder Benutzerfuehrung auftaucht, ist das hier oder in der passenden Workflow-Datei zu dokumentieren.

## Verweis

Formale Projekt- und Lieferstaende liegen weiterhin in:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/roadmap/status/*.md`
- `docs/project-context/operational-rollout-scope-2026-04-09.md`
- `docs/roadmap/status/2026-04-03-security-hardening-phase-2.md`
