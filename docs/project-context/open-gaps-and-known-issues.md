# Open Gaps and Known Issues

## Zweck

Diese Datei sammelt die fuer neue Analysen wichtigsten offenen Restthemen und bekannten Unsicherheiten.

## Aktuell besonders relevant

- einzelne Prozessstarts muessen weiter auf Praxisrealismus gegen Landhandelsablaeufe geprueft werden
- Browser-Use- und CRUD-Pruefungen muessen pro Workflow fortgeschrieben werden
- Security-Triage 2026-03-31: `SEC-001` ist abgearbeitet (harte Repo-Secrets und kritische Credential-Defaults entfernt), `SEC-002` liefert lokale zentrale Secret-Pflege ueber Vault + optionales OS-Keyring + CLI, `SEC-003` haertet Metrics und Copilot-WebSocket gegen unauthentifizierten Zugriff und Tenant-Spoofing, `SEC-004` zieht Supplier-Portal-Queries auf tenant-gebundene parametrisierte Statements, `SEC-005` schliesst die generischen Realtime-WebSockets fuer POS/Workflow/Policy, `SEC-006` zieht Accounting-Periods auf kontextgebundene Tenant-Isolation, `SEC-007` haertet den Creditor-Router gegen Payload-/Query-/ID-basierte Cross-Tenant-Zugriffe, `SEC-008` bis `SEC-013` schliessen Tenant-Isolation/Mass-Assignment im Einkauf, SQL-Identifier-Whitelists fuer Admin Mobile, XML-Injection im VIES-Client, Information Disclosure im Documents-Router, SSRF bei Webhooks und XSS in browserbasierten Print-Pfaden, `SEC-014` verdrahtet HashiCorp Vault als externen Secret-Provider mit Production-Startup-Fail-Fast, `SEC-015` zieht Accruals/Provisions auf kontextgebundene Tenant-Isolation, `SEC-016` zentralisiert die Egress-/SSRF-Policy fuer Webhooks sowie externe Broker-HTTP-Pfade, `SEC-017` verankert die behobenen Security-Pfade als feste CI-Regression-Lane, `SEC-018` inventarisiert die verbleibenden Frontend-HTML-Sinks mit einem festen Guard-Test, `SEC-019` bis `SEC-021` binden AP-Approval-Workflow, Nebenbuch-Abstimmung und Tax-Keys an den Kontext-Tenant, `SEC-022` bis `SEC-024` schliessen dieselbe Tenant-Luecke fuer VAT-Return, Sales Credit Notes/Returns und Sales Reports, `SEC-025` bis `SEC-027` haerten Sales Delivery Notes, Articles API sowie Warehouse Transfers gegen freie Query-/Payload-/ID-basierte Cross-Tenant-Zugriffe, `SEC-028` surfact blockierte Outbound-Targets sowie denied Cross-Tenant-Zugriffe zentral ueber Security-Monitoring-Endpoints, `SEC-029` zieht Agrar Contracts auf kontextgebundene Tenant-Isolation, `SEC-030` bindet die Security-Surface an Admin-Dashboard und Alerting-Konfiguration an, `SEC-031` und `SEC-032` schliessen die verbleibenden freien Tenant-Pfade in Sales Orders und Sales Offers, und `SEC-034` macht Security-Events append-only restart-stabil. Offen bleiben vor allem weitere routerweise P1-SAST-Funde ausserhalb des bisherigen Sales-/Finance-Clusters sowie laengerfristig DB-/Audit-Bridge und externes Alerting fuer Security-Events. Roadmap und Folge-Slices: `docs/roadmap/status/2026-04-03-security-hardening-phase-2.md`
- NATS-Consumer + Core-Handler: DLQ, Idempotenz, zusaetzlich Flow-Spine-Handler und Event-Observability (`flow_spine_handlers.py`, `observability.py`) sind umgesetzt; produktives Surfacing im Betrieb/Monitoring steht ueber `neuro_event_monitoring.py` bereit, die gleichen Zaehler werden zusaetzlich als Prometheus-Counters auf `GET /metrics` exportiert (`valeo_event_bus_*`). Offen bleibt vor allem die Anbindung der Scrapes an externe Dashboards/Alerting (Grafana/Prometheus-Stack)
- Der zentrale Neuro Tool Broker ist umgesetzt (NC-A6/NC-A7 inkl. interner OpenAPI-Execution); NC-A14/NC-A16 ziehen Tenant-Override-Propagation, externe HTTP-Execution und contract-gesteuerte Request-Payloads nach. Offen bleiben primaer weitere produktive Tool-Adapter und breitere UI-/Runtime-Nutzung
- Verification und Policy Engine sind in Wave 2 (NC-A8) gekoppelt; Wave 3 ist mit NC-A9 (LLM-Fallback) und NC-D5 (Hash-Chain-Tests) umgesetzt; Wave 4 ist mit NC-A10 (dynamische Plan-Generierung), NC-A11 (Cross-Entity-Integrity), NC-A12 (Risk-Scoring) und NC-A13 (Tenant-Overrides) abgeschlossen. Offen bleiben nun vor allem tiefere Broker-/UI-Folgepfade und produktive Monitoring-/RAG-Ausbaustufen. Details in `docs/project-context/neuro-stack-gap-matrix-2026-03-29.md`
- ChromaDB fuer produktive RAG-Nutzung muss mit Prozesswissen befuellt werden
- Voice-Kanal setzt Web Speech API voraus (Chrome/Edge); Firefox und Safari nicht unterstuetzt
- Agentenarchitektur-Diagramm zeigt weiterhin Restluecken bei produktiver Vault-Anbindung, Memory-Governance, Process-Kernel-Contracts und tieferer Observability (siehe `docs/project-context/agent-architecture-gaps-2026-03-28.md`)
- Neuro-Stack-Status und P1-Luecken sind als Matrix dokumentiert (siehe `docs/project-context/neuro-stack-gap-matrix-2026-03-29.md`)
- Knowledge Store (`knowledge_store.py`, `/neuro/knowledge`) ist umgesetzt; offen bleiben breitere produktive Nutzung in RAG-/Resolver-Pfaden und ggf. dedizierte Migrationen je nach Deploy-Strategie
- Multi-Channel: WhatsApp, E-Mail, Voice, Live-Chat (Backend-REST), Channel-Ingress; offen bleiben outbound Routing und vollstaendige Live-Chat-WebSocket-Anbindung im Produkt-UI
- Superglue Self-Host ist mit `INT-SG-035` bis `INT-SG-066` auf den aktuellen Upstream-Runtime-/REST-Vertrag gezogen; CRM-/Masterdata, Artifact-/Idempotenz-/Retry-Pfade, Admin-/Monitoring-/CI-Surfaces sowie Procurement-, Finance-, Logistics-, Agribusiness-, Service- und Analytics-Rollouts liegen jetzt als thin-wrapper Connector-Familien im VALEO-Pfad vor. `INT-SG-061` bis `INT-SG-066` schliessen auch die letzten implementierbaren Ops-Pfade: Live-Readiness, Tenant-Onboarding-Pack, CLI-/Shell-Exports, ENV-/Vault-Templates, CI-Validierung und Admin-Downloads. **Operativ offen bleiben** damit nur noch die echte Befuellung je Tenant/Environment: Live-Credentials, produktive Zielsystem-URLs und Ops-seitige Alerting-/Retention-Werte ausserhalb des Repos. **Kernel/Finance:** `PostAPInvoice` fuehrt Journal+OP+Outbox im Kernel-Pfad aus (`app/services/ap_invoice_kernel_posting.py`); Execute-Request braucht `human_confirmation: true`. Einkauf: optionale Tenant-Praefixe `TENANT_PO_PREFIX_<SANITIZED_TENANT>`; Duplikat-Bereinigung+Unique per Migration `einkauf_bestellungen_dedupe_unique_20260407`. Finance-Export: zweiter Upload-Weg S3/MinIO (`FINANCE_EXPORT_S3_*`, `finance_export_upload.py`).
- Erstinstallation und Migration aus bestehendem `service-erp`/L3 sind repo-seitig jetzt soweit geschlossen, wie es ohne Live-Betriebsdaten moeglich ist: `scripts/prepare_first_install.py` erzeugt ein Bundle fuer jungfraeuliche Installationen; `scripts/bootstrap_db.py` haertet Force-/Backup-/Superglue-Onboarding-Pfade; `scripts/import_l3.py` validiert Legacy-Exporte, fuehrt Dry-Runs aus und laedt Rohdaten nachvollziehbar nach `l3_staging` mit Run-Tracking in `app_control.l3_import_runs`. **Extern offen bleiben** dafuer nur noch die echten Quelldumps, produktiven Secrets/Zielsysteme sowie fachlich freigegebene FIBU-/Konten-/Steuer-Mappings fuer den finalen Cutover.

## Zuletzt geschlossene Punkte (Wave 104, 2026-03-27)

- ~~Copilot-/Voice-Pfade sind nicht ueberall gleich tief produktiv~~ -> Voice-Kanal Admin-Seite (`pages/admin/voice-channel.tsx`) im Nav verankert (GAP-104-I)
- ~~RAG-/Knowledge-Tiefe ist nicht in jedem Agentenpfad vollstaendig verdrahtet~~ -> `POST /agent-action` mit ChromaDB-RAG produktiv (graceful degradation, GAP-104-H)
- ~~Flow Spine Outbox-Events nicht verdrahtet~~ -> `FlowSpineInstanceCreated` / `FlowSpineTransitionOccurred` via Outbox (GAP-104-G)

## Zuletzt geschlossene Punkte (2026-03-31)

- ~~SVC-001-P4 Field-Service: `fetch()` statt apiClient~~ — `field-service-tasks.tsx` nutzt `apiClient` + TanStack Query; Backend-Endpunkte unter `/api/v1/agribusiness/field-service-tasks` in `app/api/v1/endpoints/compat.py` (CRM-Mapping, Demo-Fallback).
- ~~Kurz-IDs aus `uuid7()[:8]` bei schnellen Mehrfach-Inserts~~ — Praefix-IDs verwenden `uuid7_short_suffix()` / `default_prefixed_id()` / `prefixed_id()` in `app/core/uuid7.py` (Zeit-Praefix der v7-String-Darstellung war in derselben Millisekunde nicht eindeutig).

## Zuletzt geschlossene Punkte (2026-04-06)

- ~~Test-Suite scheitert ohne laufende DB/Keycloak an fehlender `API_DEV_TOKEN`-Konfiguration und ungefangenen DB-Verbindungsfehlern~~ — zentrales `tests/conftest.py` setzt `API_DEV_TOKEN` fuer alle Tests via autouse-Fixture; `require_db`-Fixture und `skip_if_db_unavailable()` sorgen fuer sauberes Skippen bei fehlender PostgreSQL-Verbindung. 10 Testdateien gefixt, 49 vorherige Failures/Errors auf 0 reduziert.
- ~~FastAPI Deprecation-Warnung: `regex=` in `Query()`~~ — `app/routers/translations_router.py` nutzt jetzt `pattern=` statt `regex=`.
- Mock-Seiten-Inventur: 10 Frontend-Seiten mit Hardcoded-Daten statt API-Anbindung identifiziert (Futter, Rezepte, Produktion, Kasse, Etiketten, Strecke — zur Mock-API-Migration vorgemerkt).
- ~~Superglue-Restblock ab CRM-/Masterdata bis breitem Domain-Rollout war noch offen~~ — INT-SG-049 bis INT-SG-060 liefern CRM-/Masterdata-Read, Artifact-/Idempotenz-/Retry-Pfade, Admin-/Monitoring-/CI-Surfaces sowie Procurement-, Finance-, Logistics-, Agribusiness-, Service- und Analytics-Rollouts ueber denselben upstream-first Connector-Standard.
- ~~Superglue-Live-Betriebsfreigabe war nur als Restluecke dokumentiert~~ — `INT-SG-061` surfact fehlende Tenant-Credentials, Platzhalter-Zielsysteme sowie Alerting-/Retention-Policies jetzt als `GET /providers/superglue/live-readiness` und in der Admin-Seite `Agenten-Integration`.
- ~~Superglue-Ops mussten fehlende Secret-Keys und Zielsystem-Felder weiter manuell aus mehreren Stellen zusammensuchen~~ — `INT-SG-062` liefert `GET /providers/superglue/onboarding-pack` plus Admin-Surface `Superglue Onboarding Pack` mit den konkreten Secret-Key-Kandidaten und Policy-Werten pro Tenant.
- ~~Superglue-Onboarding-Artefakte mussten nach dem Pack noch manuell in Dateien/Downloads ueberfuehrt werden~~ — `INT-SG-063` bis `INT-SG-066` liefern CLI-/Shell-Exports, ENV-/Vault-Templates, CI-Validierung und direkte Admin-Downloads.

## Zuletzt geschlossene Punkte (2026-04-07)

- ~~Jungfraeuliche Erstinstallation hatte kein konsolidiertes repo-seitiges Ops-Bundle~~ -> `scripts/prepare_first_install.py` erzeugt jetzt unter `runtime/first-install/bundle` Installationskontext, Kommandopfad sowie Superglue-Onboarding-Templates fuer Tenant und Environment.
- ~~`bootstrap_db.py` war fuer produktionsnaehere Reset-/Neuaufsetzpfade zu grob~~ -> der Bootstrap erkennt jetzt Environments, fordert exakte `DELETE-<ENV>`-Tokens, kann vor Force-Reset automatisch `pg_dump` ziehen und exportiert optional direkt repo-lokale Superglue-Onboarding-Artefakte.
- ~~L3-/service-erp-Migration endete an einem unvollstaendigen ETL-Skript~~ -> `scripts/import_l3.py` validiert jetzt den Legacy-Vertrag strikt, laedt roh nach `l3_staging`, protokolliert Execute-Laeufe in `app_control.l3_import_runs`, unterstuetzt Reports, Logging, inkrementelle Vorbereitung via `--since` und Backup vor Execute.
- ~~Mock-Frontendseiten fuer Futter, Etiketten, Schaeden, Strecke, Produktion und Kasse waren noch nicht an echte API-Pfade angebunden~~ -> neue Router unter `app/api/v1/endpoints/{futter_stamm,etiketten,schaeden,strecke,produktion_mischfutter,kasse_tagesabschluss}.py` plus passende Frontend-API-Clients/Pages schliessen diese Parallelpfade.
- ~~Die L3-/Erstinstallationsdoku entsprach nicht mehr dem aktuellen Script-Stand~~ -> `docs/db/l3_import.md` und `docs/db/first-install-and-l3-cutover.md` beschreiben jetzt den realen Bootstrap-, Landing-Zone- und Cutover-Pfad inklusive FIBU-Vorbereitung.
- ~~NeuroASSIST hatte noch keinen gemeinsamen Agent-Ops-Pfad fuer Budgets, Kosten, Heartbeats, Rollen, Tickets und Ziele~~ -> `PCP-001` bis `PCP-006` liefern jetzt `app/agents/agent_ops.py` als gemeinsame Runtime, Budget-Guardrails im `NeuroAssistService`, neue Ops-Endpunkte unter `/api/v1/agents/neuroassist/ops/*` und die Admin-Surface `Agent Ops Budgeting / Cost Ledger / Heartbeats / Roles And Goals` in `packages/frontend-web/src/pages/admin/agenten-integration.tsx`.
- ~~Die restlichen Paperclip-inspirierten Agent-Ops-Folgeslices waren noch offen~~ -> `PCP-007` bis `PCP-012` liefern jetzt Intervention Console, zentrales Dashboard, Template-Export/Import, Skill-Pack-Manifest, Mobile-Ops-Read-Model und einen expliziten Plugin-Boundary-Review ueber `app/agents/agent_ops.py`, `app/api/v1/endpoints/agents.py`, `docs/workflows/pcp-007-012-agent-ops-rollout.md` und `docs/architecture/agent-plugin-boundary-review-2026-04-07.md`.
- ~~Das Agent Ops UI war noch nicht als echtes Control Center mit Ticketfokus, Chain of Command, Revisionssicht und fokussierter Mobile-Ops-Surface ausgezogen~~ -> `PCP-013` bis `PCP-018` liefern jetzt `GET /api/v1/agents/neuroassist/ops/control-center`, Konfigurationsrevisionen fuer Budgets/Heartbeats/Profile/Skill-Packs, ticket-zentrierte stale-/review-faehige Arbeitsobjekte, sichtbare Ownership-/Eskalationsketten und die neue Admin-Surface `Agent Control Center / Ticket-Centered Agent Work / Chain Of Command / Config Versions / Focused Mobile Ops` in `packages/frontend-web/src/pages/admin/agenten-integration.tsx`.

## Zuletzt geschlossene Punkte (2026-04-05)

- ~~CRM-Kunde/Business-Partner-Verknuepfung persistiert implizit gegen den Default-Tenant~~ — `app/api/v1/endpoints/customers.py` validiert und persistiert `business_partner_id` jetzt tenant-gebunden auch im Create-/Update-Pfad; Regressionen liegen in `tests/test_crm_customer_business_partner_link.py`.
- ~~Globaler Frontend-Typecheck ist breit an inkonsistenten `apiClient`-/Axios-Contracts rot~~ — `packages/frontend-web/src/lib/api-client.ts` stellt jetzt einen hybriden `ApiResult<T>` bereit; betroffene Call Sites und Typstubs wurden nachgezogen, `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false` ist wieder gruen.
- ~~Superglue Self-Host lief auf einem veralteten Runtime-Vertrag und scheiterte im echten Compose-Smoke~~ — Compose/K8s/Helm sprechen jetzt den aktuellen Upstream-Port-/Env-/Run-Contract (`/v1/*`, `3001/3002`, `OPENAI_API_KEY`, `POSTGRES_SSL=false`, `MASTER_ENCRYPTION_KEY`); der lokale Upstream-Container liefert wieder `GET /v1/health` und `GET /v1/tools`.
- Process-Kernel: Migration `neuro_step_audit_einkauf_tenant_20260405` legt `domain_shared.neuro_step_audit_trace` an und ergaenzt `einkauf_bestellungen.tenant_id` wo fehlend; Kernel-Actions und Broker schreiben Audit bei gesetzter DB-Session; optionale Mutation `CreatePurchaseOrder` (Einkauf); Finance-Follow-up-Erweiterung Kasse (`/finance/followup/kasse/*`); PCN nutzt `X-Tenant-ID`. Doku: `docs/workflows/kernel-action-execution-mutations.md`.

- ~~Superglue-Katalog blieb im frischen lokalen Stack leer und ein echter Tool-Run war nicht nachgewiesen~~ — `app/integrations/services/superglue_tool_provisioning.py` provisioniert jetzt drei kanonische Pilot-Tools via `POST/PUT /v1/tools`; der lokale Upstream-Container liefert `total=3` auf `GET /v1/tools`, und `POST /v1/tools/sg.document.search/run` endet erfolgreich.

- ~~Lokaler In-App-Smoke ueber `SuperglueClient` blockierte `localhost` vollstaendig~~ — `SUPERGLUE_ALLOW_LOOPBACK_DEV_EGRESS` erlaubt jetzt explizit und default-off nur im Debug-Kontext Loopback fuer Superglue; `.internal`-Hosts und private Netze bleiben weiter geblockt.

## Analysepflicht

Wenn in Code, Tests oder UI ein Widerspruch zwischen:

- Doku
- Implementierung
- Fachlogik
- Benutzerfuehrung

auftaucht, ist das hier oder in der passenden Workflow-Datei zu dokumentieren.

## Verweis

Formale Projekt- und Lieferstaende liegen weiterhin in:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/roadmap/status/*.md`

