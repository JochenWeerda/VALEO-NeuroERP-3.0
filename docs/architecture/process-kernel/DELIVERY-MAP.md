# Process Kernel — Delivery Map

Stand: 2026-05-16 | Waves 1–67 + 94–104 abgeschlossen + Service-Layer-Refaktorierung + Gap-Closure | 8564 Tests gruen

## Wave → Gap Mapping

| Wave | Abgeschlossen | Gaps geschlossen | Tests | Schwerpunkt |
|------|---------------|-----------------|-------|-------------|
| 1 | 2026-03 | – | 35 | semantic_status AP-Invoices, WorkflowInstanceReference |
| 2 | 2026-03 | – | 37 | Event-Namenskonvention, Read-Models, Tenant-Governance |
| 3 | 2026-03 | – | 30 | MaskRegistry, AuditEvidence, IoT, PricingGovernance |
| 4 | 2026-03 | – | 49 | WorkflowRuntime, ProjectionConsumer, ProcessSLA |
| 5 | 2026-03 | – | 41 | BusinessCommands, CommandDispatcher, E2E-Kette |
| 6 | 2026-03 | – | 44 | Agrar-P0 (FLIK, DüV, PSM), SupplierPortal |
| 7 | 2026-03 | – | 56 | ReadModelPersistence, Reklamation, PriceHedge |
| 8 | 2026-03 | – | 69 | ReportingLayer, TenantIsolationGuard, GoBD-Retention |
| 9 | 2026-03 | – | 50 | EDI-Integration, ApiGateway, Zertifikate, ErnteKampagne |
| 10 | 2026-03 | – | 11 | ProcessMining, Observability-Signale |
| 11 | 2026-03 | – | 30 | ProcessCommands, ExceptionCatalog, Explainability |
| 12 | 2026-03 | – | 22 | ProcessSLA-Erweiterung, Commands-Policy |
| 13 | 2026-03 | – | 27 | Settlement-Dunning-Compliance |
| 14 | 2026-03 | – | 31 | CommandDispatcher, AgentCommandManifest |
| 15 | 2026-03 | – | 34 | ApprovalStatus, WorkflowSimulation, SiloQuality |
| 16 | 2026-03 | – | 31 | AggregateRegistry (8 Aggregate) |
| 17 | 2026-03 | – | 17 | ActionExecutionService, ActionIdempotencyStore |
| 18 | 2026-03 | – | 55 | CanonicalProcessDefinitions, WorkflowVersioning |
| 19 | 2026-03 | Gap 004 (teilw.), Gap 033 | 62 | Settlement Approval, Finance Read-Models, Human-Gate |
| 20 | 2026-03 | Gap 010, Gap 035, Gap 041 | 43 | Audit-Hash-Kette, GoBD-Check, Optimistic Locking |
| 21 | 2026-03 | Gap 006, Gap 001 (teilw.) | 37 | Preisformel-Engine, Journal-Bridge, E2E-Referenz |
| 22 | 2026-03 | Gap 022 | 8 | Command Palette, Action-Dispatch |
| 23 | 2026-03 | Gap 007, Gap 042 | 46 | Nebenkosten-Automatik, Intrastat-Meldungsmodell |
| 24 | 2026-03 | Gap 005, Gap 009 | 41 | Kampagnenvorlagen, Tenant-Prozessvarianten |
| 25 | 2026-03 | Gap 025 | 10 | Kontextsensitive Quick Actions |
| 26 | 2026-03 | Gap 003, Gap 011 | 37 | Trocknungsabrechnung Audit-Contract, Migrations-Guard |
| 27 | 2026-03 | Gap 027 | 6 | Role Density Contract (Frontend) |
| 28 | 2026-03 | Gap 013, Gap 039 | 11 | SLA-Eskalations-Engine, OpenTelemetry Span-Contracts |
| 29 | 2026-03 | Gap 014, Gap 031 | 10 | Policy-as-Code Engine, Query-Vertrags-Registry |
| 30 | 2026-03 | Gap 015, Gap 050 | 10 | Human-in-the-loop AI-Freigaben, SLO/SLI-Definitionen |
| 31 | 2026-03 | Gap 017, Gap 040 | 105 | MCP/OpenAPI Tool Contracts, Datenqualitaetsregeln |
| 32 | 2026-03 | Gap 032, Gap 033 (vertieft) | 47 | Dashboard Read-Model Snapshots, Query-Fallback-Contracts |
| 33 | 2026-03 | Gap 034, Gap 036 | 59 | API-Bulk-Operationen, Queue-basierte Hintergrundjobs |
| 34 | 2026-03 | Gap 038, Gap 049 | 55 | Tenant-isolierte Caches/Rate-Limits, Security-Hardening |
| 35 | 2026-03 | Gap 026, Gap 028 | 54 | Inline-Validierung mit Erklaerungen, Error-UX-Leitsystem |
| 36 | 2026-03 | Gap 043, Gap 044 | 60 | EDI/API-Hub, Lieferketten-Tracking |
| 37 | 2026-03 | Gap 045, Gap 048 | 60 | DMS+OCR+Extraktion, Agenten-Integrationsklassen |
| 38 | 2026-03 | Gap 046, Gap 047 | 60 | Nachhaltigkeit/CO2-Reporting, Branchenbenchmarking |
| 39 | 2026-03 | – | 60 | Command-Surfacing-Contracts, Prozess-Benachrichtigung |
| 40 | 2026-03 | PKP-02, PKP-03 | 60 | Workflow-Versionierung, Canonical Audit Trail (SHA256) |
| 41 | 2026-03 | – | 82 | Process Capacity Contracts, Event Replay Contracts |
| 42 | 2026-03 | – | 60 | Domain Event Schema Registry, Process Compensation |
| 43 | 2026-03 | – | 73 | Workflow Checkpoint Contracts, Cross-Domain Projection |
| 44 | 2026-03 | – | 60 | Process Routing Contracts, Data Lineage Contracts |
| 45 | 2026-03 | – | 78 | Feature Flag Contracts, Process Cost Contracts |
| 46 | 2026-03 | – | 68 | Process Quarantine Contracts, Workflow ACL Contracts |
| 47 | 2026-03 | – | 128 | Process State Machine Contracts, Workflow Delegation |
| 48 | 2026-03 | – | 147 | Process Timeout Contracts, Workflow Batch Processing |
| 49 | 2026-03 | – | 115 | Process Notification Contracts (W49), Workflow Lock |
| 50 | 2026-03 | – | 129 | Process Archive Contracts, Workflow Metrics Contracts |
| 51 | 2026-03 | – | 135 | Process Capacity Contracts, Saga Compensation Contracts |
| 52 | 2026-03 | – | 135 | Circuit Breaker Contracts, Event Sourcing Contracts |
| 53 | 2026-03 | – | 146 | Rate Limit Contracts, Workflow Idempotency Contracts |
| 54 | 2026-03 | – | 150 | Process Retry Contracts, Workflow Checkpoint Contracts |
| 55 | 2026-03 | – | 139 | Process Priority Queue, Workflow Rollback Plans |
| 56 | 2026-03 | – | 153 | Process Dependency DAG, Workflow Signal Contracts |
| 57 | 2026-03 | – | 151 | Process Observability Contracts, Workflow Versioning |
| 58 | 2026-03 | – | 155 | Process Cost Allocation, Workflow Audit Trail (SHA-256) |
| 59 | 2026-03 | – | 142 | GDPR Consent Contracts, Workflow Trigger Conditions |
| 60 | 2026-03 | – | 157 | Process Forecasting, Workflow Handover Contracts |
| 61 | 2026-03 | – | 166 | Process Quota Management, Workflow Pause/Resume |
| 62 | 2026-03 | – | 132 | Process Template Contracts, Workflow Deadline Escalation |
| 63 | 2026-03 | – | 150 | Process Validation Engine, Workflow Collaboration Voting |
| 64 | 2026-03 | – | 173 | Process Data Lineage DAG, Workflow Simulation Contracts |
| 65 | 2026-03 | – | 155 | Exception Pattern Classification, Remediation Playbooks |
| 66 | 2026-03 | – | 163 | Process Concurrency/Mutex, Resource Lock + Deadlock Detection |
| 67 | 2026-03 | – | 192 | Process Cache Contracts, Workflow Schema Migration |
| 102 | 2026-03-24 | Gap 049 | – | Security-Hardening Runtime-Wiring (AuditMiddleware, SecurityHeaders, Startup-Guards) |
| 103 | 2026-03-24 | Gap 023, Gap 024 | – | Touch-optimierte Feldworkflows (WCAG), Keyboard-first Kernmasken (~85% Abdeckung) |
| 104 | 2026-03-27 | Gap 104-A–I | 15 | Flow Spine DB+Tenant+Paginierung, PCN DB, Outbox-Events (NATS), Agent-Action+RAG, Voice-Kanal, Repo-Hygiene |

## Gap → Wave Mapping (nur abgeschlossene Gaps)

| Gap-ID | Beschreibung (Kurzform) | Wave | Tests (Wave) |
|--------|------------------------|------|-------------|
| Gap 001 | E2E Kontrakt→Settlement (teilweise) | 21 | 37 |
| Gap 003 | Trocknungsregeln versioniert + reproduzierbar | 26 | 37 |
| Gap 004 | Settlement Freigabe-Flow (teilweise) | 19 | 62 |
| Gap 005 | Saisonale Kampagnenvorlagen | 24 | 41 |
| Gap 006 | Kontrakt-Preislogik Fix/Formel/Terminmarkt | 21 | 37 |
| Gap 007 | Nebenkosten/Fracht/Lagergeld automatisch | 23 | 46 |
| Gap 009 | Rollenbasierte Prozessvarianten | 24 | 41 |
| Gap 010 | Betriebsprüfungsfeste Prozessjournalisierung | 20 | 43 |
| Gap 011 | Versionierte Workflow Engine, Migrations-Guard | 26 | 37 |
| Gap 013 | SLA/Timeout/Eskalationsknoten | 28 | 11 |
| Gap 014 | Policy-as-Code mit Tenant Overrides | 29 | 10 |
| Gap 015 | Human-in-the-loop Freigaben für AI | 30 | 10 |
| Gap 017 | MCP/OpenAPI Tool Contracts | 31 | 105 |
| Gap 022 | Command Palette (Ctrl+K) Power User | 22 | 8 |
| Gap 025 | Kontextsensitive Quick Actions | 25 | 10 |
| Gap 026 | Inline-Validierung mit Erklärungen | 35 | 54 |
| Gap 027 | Konsistente Informationsdichte je Rolle | 27 | 6 |
| Gap 028 | Leitsystem für Ausnahmefälle / Error UX | 35 | 54 |
| Gap 031 | Query-Verträge (keine undefined) | 29 | 10 |
| Gap 032 | 500er bei controlling/kpis eliminieren | 32 | 47 |
| Gap 033 | Read-Models für Dashboards | 32 | 47 |
| Gap 034 | API-Bulk-Operationen | 33 | 59 |
| Gap 035 | Optimistic Locking | 20 | 43 |
| Gap 036 | Queue-basierte Hintergrundjobs | 33 | 59 |
| Gap 038 | Tenant-isolierte Caches/Rate Limits | 34 | 55 |
| Gap 039 | End-to-End Tracing UI→API→DB | 28 | 11 |
| Gap 040 | Datenqualitätsregeln Schreibpfade | 31 | 105 |
| Gap 041 | GoBD Belegkette | 20 | 43 |
| Gap 042 | Intrastat/Zoll produktiv | 23 | 46 |
| Gap 043 | EDI/API-Hub | 36 | 60 |
| Gap 044 | Lieferketten-Tracking | 36 | 60 |
| Gap 045 | DMS + OCR + strukturierte Extraktion | 37 | 60 |
| Gap 046 | Nachhaltigkeit/CO2-Reporting | 38 | 60 |
| Gap 047 | Branchenbenchmarking-Cockpit | 38 | 60 |
| Gap 048 | Offene Integrationsfähigkeit Agenten | 37 | 60 |
| Gap 049 | Security-Hardening OIDC/RBAC/Audit | 34 | 55 |
| Gap 050 | SLO/SLI Runbooks | 30 | 10 |

## Offene Gaps (Stand 2026-03-16)

| Gap-ID | Beschreibung | Priorität | Horizon |
|--------|-------------|-----------|---------|
| Gap 002 | Vollständige Waage/Annahme-Masken | P0 | H1 |
| Gap 008 | Landhandel-spezifische Reklamationsprozesse E2E | P1 | H2 |
| Gap 012 | Silo-Management vollständig | P1 | H2 |
| Gap 016 | Mobile-Erfassung (Fahrer, Waage) | P2 | H2 |
| Gap 018 | Disposition + Logistikplanung | P1 | H2 |
| Gap 019 | Fuhrpark + Kosten-Controlling | P2 | H2 |
| Gap 020 | Lieferantenportal (Self-Service) | P1 | H2 |
| Gap 021 | Kundenportal (Self-Service) | P2 | H3 |
| Gap 023 | Cross-Mandanten-Kontrakte (Verbund) | P1 | H2 |
| Gap 024 | Warenterminmarkt-Integration | P1 | H2 |
| Gap 029 | Dokumenten-OCR vollständig (Rechnungen) | P1 | H2 |
| Gap 030 | Lieferanten-Qualitäts-Scoring | P2 | H3 |
| Gap 037 | Lasttests Erntepeak | P0 | H2 |

## NeuroASSIST Delta zum Zielbild

Der Process-Kernel-nahe NeuroASSIST-Vertragsstand ist im Kern hergestellt:

- `StageDefinition`
- `GateDecision`
- `RoleContract`
- `CapabilityPack`
- `WorkflowSchema`
- `CaseRun`
- `CaseStageTransition`

Offen ist damit primaer nicht mehr das Vertrags- oder Dispatch-Modell. Die naechste Ausbaustufe liegt jetzt in der tieferen Audit- und Kontextintegration:

1. `data_quality_assistant` und `operations_exception_assistant` sind jetzt als produktive Runtime-Capabilities angebunden.
2. `exception`- und `ingestion`-Workflows laufen jetzt als echte NeuroASSIST-Run-Familien ueber den generischen Run-/Status-/Audit-Contract.
3. Der generische Audit-Sink ist jetzt konservativ an die vorhandenen Process-Audit-Contracts und Workflow-Versionen angebunden, sobald Prozessdefinition und Aggregatkontext valide aufgeloest werden koennen.
4. Ein zentraler Context-Resolver fuer Prozessdefinition, Aggregatkontext, Workflow-Version, Policy-IDs, DQ-RuleSets und Read-Models ist jetzt als eigener Runtime-Baustein eingefuehrt.
5. Der direkte LangGraph-Zugriff fuer Bestellvorschlag sitzt jetzt hinter `app/agents/neuroassist_workflow_runners.py`, sodass `NeuroAssistService` selbst keine Engine-spezifischen Aufrufe mehr kennen muss.
6. Die Background-Job-Schicht ist jetzt um `scheduler_heartbeat.py` und Heartbeat-/Lease-Sicht im `SchedulerService` ergaenzt; Scheduler-Liveness und Stale-Detection sind damit nicht mehr implizit.
7. Scheduler-Liveness ist jetzt auch operativ eskalierbar: `scheduler_recovery.py` und `GET /process/jobs/heartbeat/recovery` liefern einen standardisierten Recovery-Plan statt blossen Status.

Prioritaet fuer die naechste Liefersequenz:

- weitere produktive Capabilities auf denselben Context-Resolver und Audit-Pfad ziehen
- weitere Workflow-Runner-Adapter fuer checkpoint-faehige oder asynchrone Faelle auf denselben generischen Service- und Audit-Pfad ziehen
- spaeter Vollintegration der Process-Audit-Bruecke ohne capability-spezifische Kontextbeimischung

## Architekturregeln (verbindlich)

1. `schema_version` bestehender Contracts nicht ändern
2. `app/core/` importiert keine `app/api/`-Module
3. Endpoints importieren keine anderen Endpoint-Module direkt
4. `app/api/v1/api.py` nur additiv erweitern
5. Neue Kernlogik in `app/core/`, nicht in Route-Helper
6. Tests der Waves 1–4 sind Abnahme-Contracts — nicht anpassen
7. DB-Tests nutzen Savepoint-Isolation

## Referenzen

- Detaillieferungen: `wave-*/STATUS.md`
- Globaler Status: `STATUS.md`
- Gap-Backlog: `docs/roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md`
- ADR-Index: `docs/architecture/index.md`
