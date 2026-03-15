# Process Kernel — Delivery Map

Stand: 2026-03-15 | Waves 1–27 abgeschlossen | 1235 Tests gruen

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
| Gap 022 | Command Palette (Ctrl+K) Power User | 22 | 8 |
| Gap 025 | Kontextsensitive Quick Actions | 25 | 10 |
| Gap 027 | Konsistente Informationsdichte je Rolle | 27 | 6 |
| Gap 033 | Read-Models für Dashboards | 19 | 62 |
| Gap 035 | Optimistic Locking | 20 | 43 |
| Gap 041 | GoBD Belegkette | 20 | 43 |
| Gap 042 | Intrastat/Zoll produktiv | 23 | 46 |

## Offene P0-Gaps (Stand 2026-03-15)

| Gap-ID | Beschreibung | Priorität | Horizon |
|--------|-------------|-----------|---------|
| Gap 002 | Vollständige Waage/Annahme-Masken | P0 | H1 |
| Gap 013 | SLA/Timeout/Eskalationsknoten | P0 | H1 |
| Gap 014 | Policy-as-Code mit Tenant Overrides | P0 | H1 |
| Gap 015 | Human-in-the-loop Freigaben für AI | P0 | H1 |
| Gap 031 | Query-Verträge (keine undefined) | P0 | H1 |
| Gap 032 | 500er bei controlling/kpis eliminieren | P0 | H1 |
| Gap 037 | Lasttests Erntepeak | P0 | H2 |
| Gap 049 | Security-Hardening | P0 | H1 |
| Gap 050 | SLO/SLI Runbooks | P0 | H1 |

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
