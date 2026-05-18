# Top-50 Gap Backlog 2026-03-06 (Landhandel, Genossenschaft, Agrarkonzerne)

**Strategischer Kontext:** [2026-03-06-valeo-spitzenposition-konsolidiert.md](2026-03-06-valeo-spitzenposition-konsolidiert.md) – Kurzfazit, Wettbewerbsvergleich, 90-Tage-Priorisierung

**Arbeitsaufteilung:** [2026-03-06-arbeitsaufteilung-codex-hauptstrang.md](2026-03-06-arbeitsaufteilung-codex-hauptstrang.md) – 30 % Codex (Parallel Chat), 70 % Hauptstrang, einheitliche Statuskontrolle

**Zielbild:** [target-state-landhandel-erp.md](../../architecture/target-state-landhandel-erp.md) – verbindliche Leitplanke für Produktkern, Architektur und Priorisierung.

## Ziel
Dieses Backlog priorisiert die fehlenden Faehigkeiten, um VALEO NeuroERP auf Spitzenniveau gegenueber etablierten Agrar-ERP-Plattformen, Agrar-Spezialsoftware sowie weiteren etablierten ERP-Suiten zu bringen. Fokus: End-to-End Prozessabdeckung, AI-first Workflows, Agent-Interoperabilitaet, UUIX, Performance, Parallelverarbeitung.

## Statusabgleich 2026-03-20

Abgleich gegen den operativen Lieferstand in `docs/architecture/process-kernel/STATUS.md`
und den zugehoerigen `wave-*/STATUS.md`-Dateien:

| Gap-ID | Status | Beleg |
|---|---|---|
| 003 | abgeschlossen | `docs/architecture/process-kernel/wave-26/STATUS.md` |
| 006 | abgeschlossen | `docs/architecture/process-kernel/wave-21/STATUS.md` |
| 011 | abgeschlossen | `docs/architecture/process-kernel/wave-26/STATUS.md` |
| 017 | abgeschlossen | `docs/architecture/process-kernel/wave-31/STATUS.md` |
| 026 | abgeschlossen | `docs/architecture/process-kernel/wave-35/STATUS.md` |
| 028 | abgeschlossen | `docs/architecture/process-kernel/wave-35/STATUS.md` |
| 032 | abgeschlossen | `docs/architecture/process-kernel/wave-32/STATUS.md` |
| 033 | abgeschlossen | `docs/architecture/process-kernel/wave-32/STATUS.md` |
| 034 | abgeschlossen | `docs/architecture/process-kernel/wave-33/STATUS.md` |
| 036 | abgeschlossen | `docs/architecture/process-kernel/wave-33/STATUS.md` |
| 038 | abgeschlossen | `docs/architecture/process-kernel/wave-34/STATUS.md` |
| 040 | abgeschlossen | `docs/architecture/process-kernel/wave-31/STATUS.md` |
| 043 | abgeschlossen | `docs/architecture/process-kernel/wave-36/STATUS.md` |
| 044 | abgeschlossen | `docs/architecture/process-kernel/wave-36/STATUS.md` |
| 045 | abgeschlossen | `docs/architecture/process-kernel/wave-37/STATUS.md` |
| 046 | abgeschlossen | `docs/architecture/process-kernel/wave-38/STATUS.md` |
| 047 | abgeschlossen | `docs/architecture/process-kernel/wave-38/STATUS.md` |
| 048 | abgeschlossen | `docs/architecture/process-kernel/wave-37/STATUS.md` |
| 049 | abgeschlossen | `docs/architecture/process-kernel/wave-34/STATUS.md` |
| 010 | abgeschlossen | `docs/architecture/process-kernel/wave-20/STATUS.md` |
| 022 | abgeschlossen | `docs/architecture/process-kernel/wave-22/STATUS.md` |
| 035 | abgeschlossen | `docs/architecture/process-kernel/wave-20/STATUS.md` |
| 041 | abgeschlossen | `docs/architecture/process-kernel/wave-20/STATUS.md` |
| 001 | abgeschlossen | `docs/architecture/process-kernel/wave-85/STATUS.md` |
| 002 | abgeschlossen | `docs/architecture/process-kernel/wave-91/STATUS.md`, `docs/architecture/process-kernel/wave-92/STATUS.md` |
| 005 | abgeschlossen | `docs/architecture/process-kernel/wave-24/STATUS.md` |
| 007 | abgeschlossen | `docs/architecture/process-kernel/wave-23/STATUS.md` |
| 008 | abgeschlossen | `tests/test_process_kernel_wave8_complaint_e2e.py`, `app/api/v1/endpoints/reklamation_api.py` |
| 009 | abgeschlossen | `docs/architecture/process-kernel/wave-24/STATUS.md` |
| 025 | abgeschlossen | `docs/architecture/process-kernel/wave-25/STATUS.md` |
| 027 | abgeschlossen | `docs/architecture/process-kernel/wave-27/STATUS.md` |
| 042 | abgeschlossen | `docs/architecture/process-kernel/wave-23/STATUS.md` |
| 012 | abgeschlossen | `tests/test_process_kernel_wave86_workflow_sandbox.py`, `app/api/v1/endpoints/workflow_simulation.py` |
| 016 | abgeschlossen | `app/api/v1/endpoints/idempotency_monitoring.py`, `packages/frontend-web/src/components/agent/IdempotencyMonitoringPanel.tsx` |
| 018 | abgeschlossen | `tests/test_process_kernel_wave87_process_mining_observation.py`, `app/api/v1/endpoints/process_mining_observation.py` |
| 019 | abgeschlossen | `docs/architecture/process-kernel/wave-81/STATUS.md` |
| 020 | abgeschlossen | `docs/architecture/process-kernel/wave-90/STATUS.md` |
| 021 | abgeschlossen | `docs/architecture/process-kernel/wave-84/STATUS.md`, `docs/architecture/process-kernel/wave-91/STATUS.md` |
| 023 | abgeschlossen | `docs/architecture/process-kernel/wave-77/STATUS.md`, `docs/architecture/process-kernel/wave-91/STATUS.md`, `docs/architecture/process-kernel/wave-94/STATUS.md` |
| 024 | abgeschlossen | `docs/architecture/process-kernel/wave-76/STATUS.md`, `docs/architecture/process-kernel/wave-91/STATUS.md`, `docs/architecture/process-kernel/wave-92/STATUS.md` |
| 029 | abgeschlossen | `docs/architecture/process-kernel/wave-93/STATUS.md`, `docs/architecture/process-kernel/wave-98/STATUS.md` |
| 030 | abgeschlossen | `docs/architecture/process-kernel/wave-89/STATUS.md` |
| 037 | abgeschlossen | `docs/architecture/process-kernel/wave-87/STATUS.md` |
| 004 | abgeschlossen | `docs/architecture/process-kernel/wave-19/STATUS.md`, `docs/architecture/process-kernel/wave-100/STATUS.md` |

Hinweise:
- Dieses Dokument bleibt die strategische Priorisierung und kein feingranulares Delivery-Log.
- Der aktuelle Wahrheitsstand fuer Process-Kernel-Lieferungen liegt in `docs/architecture/process-kernel/STATUS.md`.
- Weitere Gaps werden hier nur dann als abgeschlossen eingeordnet, wenn der Abschluss entweder explizit in einer Wave-STATUS-Datei oder ueber stabile Code-/Test-Artefakte belastbar belegt ist.
- Fuer den bereinigten Zwischenstand nach spaeteren Lieferungen siehe zusaetzlich `docs/roadmap/status/2026-03-20-gap-matrix-bereinigt.md`.
- Nach dem aktuellen Abgleich verbleiben keine produktfachlich offenen Top-50-Restgaps.
- Fuer den final bereinigten Stand siehe `docs/roadmap/status/2026-03-20-gap-matrix-bereinigt.md`.

## Bewertungslogik
- Prioritaet: P0 (kritisch), P1 (hoch), P2 (mittel)
- Aufwand: S (1-2 Wochen), M (2-4 Wochen), L (4-8 Wochen), XL (8+ Wochen)
- Horizon: H1 (0-90 Tage), H2 (3-6 Monate), H3 (6-12 Monate)
- KPI-Typen: Produktivitaet, Qualitaet, Performance, Adoption, Compliance

## Block 001-010: Prozessabdeckung Kern Landhandel (P0)

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 001 | E2E Kontrakt->Annahme->Qualitaet->Settlement ohne Medienbruch | >=95% Vorgaenge ohne manuelle Nebenliste | L | Workflow Core, Stammdaten | P0 | H1 | **GESCHLOSSEN Wave 85** - `e2e_process_chain_contracts.py`, `docs/architecture/process-kernel/wave-85/STATUS.md` |
| 002 | Vollstaendige Waage/Annahme-Masken fuer alle Warenfluesse | 100% Annahmearten ueber produktive Maske | M | Waage APIs, Rollenmodell | P0 | H1 | **GESCHLOSSEN Waves 91/92** - Annahme-/Waage-/Rohware-/Verladungs-Kernflow mit Touch/Keyboard-Haertung, `docs/architecture/process-kernel/wave-91/STATUS.md`, `docs/architecture/process-kernel/wave-92/STATUS.md` |
| 003 | Trocknungs- und Abzugsregeln als versionierte Engine | 100% Abrechnungen regelbasiert reproduzierbar | M | Rule Engine, Audit | P0 | H1 | **GESCHLOSSEN Wave 26** - `trocknungs_abrechnung.py`, `docs/architecture/process-kernel/wave-26/STATUS.md` |
| 004 | Settlement inkl. Gutschrift/Belastung mit Freigabe-Flow | <2% manuelle Korrekturbuchungen | L | Finance, Approval Workflow | P0 | H1 | **GESCHLOSSEN Wave 100** - Settlement-Abschlussvertrag ueber Gutschrift, Belastung und Korrektur, `docs/architecture/process-kernel/wave-100/STATUS.md` |
| 005 | Saisonale Kampagnenprozesse (Erntefenster) als Vorlagen | Setup-Zeit neue Kampagne <30 min | S | Workflow Templates | P1 | H1 |
| 006 | Kontrakt-Preislogik (Fix, Formel, Terminmarkt) einheitlich | 0 ungeklaerte Preisabweichungen >24h | L | Pricing Service, Marktdaten | P0 | H2 |
| 007 | Nebenkosten/Fracht/Lagergeld automatisch im Prozess | >=90% automatische Kostenzuordnung | M | Logistik, Finance | P1 | H1 |
| 008 | Landhandel-spezifische Reklamationsprozesse E2E | SLA-Erfuellung Reklamationen >=95% | M | CRM Service, DMS | P1 | H2 | **GESCHLOSSEN** - `reklamation.py`, `reklamation_api.py`, `tests/test_process_kernel_wave8_complaint_e2e.py` |
| 009 | Rollenbasierte Prozessvarianten je Genossenschaft | 0 globale Hardcoded Prozessschritte | M | Tenant Config | P0 | H1 |
| 010 | Betriebspruefungsfeste Prozessjournalisierung | 100% kritische Schritte mit Audit Hash | M | Audit Domain | P0 | H1 |

## Block 011-020: Workflow, Policy, Agent-Ready Platform

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 011 | Versionierte Workflow Engine mit Migrationen | 0 ungeplante Workflow-Brueche bei Releases | L | Workflow Service | P0 | H1 | **GESCHLOSSEN Wave 26** - `workflow_migrations_guard.py`, `docs/architecture/process-kernel/wave-26/STATUS.md` |
| 012 | Simulation/Sandbox fuer neue Workflows | 80% weniger Fehler nach Go-Live | M | Testdaten, Rule Engine | P1 | H1 | **GESCHLOSSEN** - `workflow_simulation.py`, `tests/test_process_kernel_wave86_workflow_sandbox.py` |
| 013 | SLA/Timeout/Eskalationsknoten standardisiert | >=95% SLA-Einhaltung Kernprozesse | M | Notification, RBAC | P0 | H1 | **GESCHLOSSEN Wave 28** — `sla_eskalation_engine.py`: evaluate_sla_breach(), validate_sla_policy(), 6 Default-Policies; API GET /process/sla/eskalationen |
| 014 | Policy-as-Code mit Tenant Overrides | 100% Ausnahmen regelbasiert dokumentiert | M | Policy Store | P0 | H1 | **GESCHLOSSEN Wave 29** — `policy_code_engine.py`: evaluate_policy_set(), apply_tenant_overrides() (Pflichtregeln geschuetzt), Default-PolicySets; API GET+POST /process/policy-rules |
| 015 | Human-in-the-loop Freigaben fuer AI Aktionen | 100% AI-Aktionen mit Approval-Trail | M | Agent Layer, Audit | P0 | H1 | **GESCHLOSSEN Wave 30** — `human_approval_gate.py`: evaluate_approval_requirement() (NIEDRIG/MITTEL/HOCH/KRITISCH), record_approval_decision() (frozen + SHA-256 Audit-Trail), 8 Default-Regeln; API GET/POST /process/agent/approval-* |
| 016 | Idempotente Business-Commands statt UI-CRUD fuer Agenten | >=99.9% sichere Retries ohne Duplikate | L | API Refactor | P0 | H2 | **GESCHLOSSEN** - `action_idempotency.py`, `idempotency_monitoring.py`, `IdempotencyMonitoringPanel.tsx` |
| 017 | MCP/OpenAPI Tool Contracts fuer externe Agenten | 20 produktive Agent-Tools freigeschaltet | M | API Governance | P1 | H2 | **GESCHLOSSEN Wave 31** - `mcp_tool_contracts.py`, `docs/architecture/process-kernel/wave-31/STATUS.md` |
| 018 | Ereignisbasierte Prozessbeobachtung (Process Mining Lite) | Durchlaufzeit-Drilldown fuer Top-10 Prozesse | L | Event Bus, Data Mart | P1 | H2 | **GESCHLOSSEN** - `process_mining_observation.py`, `tests/test_process_kernel_wave87_process_mining_observation.py` |
| 019 | Policy Explainability im UI (Warum freigegeben/blockiert) | 50% weniger Support-Rueckfragen | S | Frontend Components | P1 | H1 | **GESCHLOSSEN Wave 81** - `policy_explainability_contracts.py`, `docs/architecture/process-kernel/wave-81/STATUS.md` |
| 020 | Workflow-Template Marketplace intern | Neue Prozessvariante in <1 Tag | M | Template Registry | P2 | H3 | **GESCHLOSSEN Wave 90** - `workflow_template_marketplace.py`, `docs/architecture/process-kernel/wave-90/STATUS.md` |

## Block 021-030: UUIX, Designsystem, Bedienlogik

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 021 | Einheitliches Designsystem mit verbindlichen Prozesspatterns | 100% neue Seiten nutzen DS-Komponenten | M | Frontend Platform | P0 | H1 | **GESCHLOSSEN Wave 84** - `design_system_contracts.py`, `docs/architecture/process-kernel/wave-84/STATUS.md` |
| 022 | Command Palette (Ctrl/Cmd+K) fuer Power User | 30% schnellere Task Completion | S | Frontend Shell | P1 | H1 |
| 023 | Keyboard-first fuer alle Kernmasken | >=90% Kernflows ohne Maus bedienbar | M | Accessibility Audit | P1 | H2 | **GESCHLOSSEN Waves 77/91-98** - Keyboard-Shortcuts und Shortcut-Bar in Kernmasken und P1/P2-Seiten ausgerollt |
| 024 | Touch-optimierte Feldworkflows (Tablet/Lager/Waage) | Fehlbedienungen auf Touch -40% | M | Responsive Layouts | P1 | H1 | **GESCHLOSSEN Waves 76/91/92** - Touch-Library und Feldworkflows fuer Annahme, Rohware und Verladung produktiv |
| 025 | Kontextsensitive Quick Actions pro Maske | 25% weniger Klicks pro Vorgang | S | Action Registry | P1 | H1 |
| 026 | Inline-Validierung mit domain-spezifischen Erklaerungen | 35% weniger Eingabefehler | S | Validation Layer | P1 | H1 | **GESCHLOSSEN Wave 35** - `inline_validation_contracts.py`, `docs/architecture/process-kernel/wave-35/STATUS.md` |
| 027 | Konsistente Informationsdichte je Rolle | Nutzerzufriedenheit >=8/10 | M | UX Research | P2 | H2 |
| 028 | Leitsystem fuer Ausnahmefaelle (Error UX) | 50% weniger Abbruchquote bei Fehlern | S | Error Boundaries | P1 | H1 | **GESCHLOSSEN Wave 35** - `error_guidance_contracts.py`, `docs/architecture/process-kernel/wave-35/STATUS.md` |
| 029 | Agent UX Panel (Confidence, Quellen, Aktion) | AI-Adoption in Kernteams >=60% | M | Copilot UI | P1 | H2 | **GESCHLOSSEN Waves 93/98** - `AgentProcessPanel.tsx`, `AgentSuggestionBadge.tsx`, Supervisor- und Capability-Seiten |
| 030 | Multilingual + Fachsprache Landhandel konsistent | 0 kritische Begriffsinkonsistenzen | M | i18n Catalog | P2 | H2 | **GESCHLOSSEN Wave 89** - `terminology_registry.py`, `docs/architecture/process-kernel/wave-89/STATUS.md` |

## Block 031-040: Performance, Daten, Multi-User Parallelbetrieb

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 031 | Query-Vertraege haerten (nie undefined fuer Query Data) | 0 React Query undefined Laufzeitfehler | S | API Client, Schemas | P0 | H1 | **GESCHLOSSEN Wave 29** — `query_contracts.py`: QueryContract + validate_query_result() (strict/non-strict, Enum+Nullable+Typ-Checks), 6 Process-Kernel-Contracts; API GET /process/query-registry |
| 032 | 500er bei controlling/kpis/timeseries eliminieren | Error Rate <0.5% | S | DB Schema, Migrations | P0 | H1 | **GESCHLOSSEN Wave 32** - `query_fallback_contracts.py`, `docs/architecture/process-kernel/wave-32/STATUS.md` |
| 033 | Read-Models fuer Dashboards statt teurer Live-Joins | p95 Dashboard API <250ms | M | Data Pipeline | P0 | H1 | **GESCHLOSSEN Wave 32** - `dashboard_snapshots.py`, `docs/architecture/process-kernel/wave-32/STATUS.md` |
| 034 | API-Bulk-Operationen fuer Massenvorgaenge | 3x Throughput bei Batch-Import | M | API Layer | P1 | H2 | **GESCHLOSSEN Wave 33** - `bulk_operations.py`, `docs/architecture/process-kernel/wave-33/STATUS.md` |
| 035 | Optimistic Locking fuer konkurrierende Bearbeitung | 0 stille Ueberschreibungen | M | DB Models | P0 | H1 |
| 036 | Queue-basierte Hintergrundjobs fuer schwere Prozesse | p95 UI-Response <300ms unter Last | M | Job Runner | P1 | H1 | **GESCHLOSSEN Wave 33** - `background_jobs.py`, `docs/architecture/process-kernel/wave-33/STATUS.md` |
| 037 | Lasttests Erntepeak (mehrere Standorte, parallel) | 500 gleichzeitige User stabil | L | Load Test Harness | P0 | H2 | **GESCHLOSSEN Wave 87** - `load_test_contracts.py`, `docs/architecture/process-kernel/wave-87/STATUS.md` |
| 038 | Tenant-isolierte Caches/Rate Limits | 0 Cross-tenant Performance-Kollisionen | M | API Gateway | P1 | H2 | **GESCHLOSSEN Wave 34** - `tenant_rate_limits.py`, `docs/architecture/process-kernel/wave-34/STATUS.md` |
| 039 | End-to-End Tracing (UI->API->DB->Worker) | MTTR -40% bei Produktionsfehlern | M | OpenTelemetry | P1 | H1 | **GESCHLOSSEN Wave 28** — `otel_span_contracts.py`: 14 SpanContracts (5 Domains), valeo.{domain}.{operation}-Konvention, kein OTel-Import in app/core/; API GET /process/otel/span-registry |
| 040 | Datenqualitaetsregeln (Dublette, Pflichtfeld, Referenz) | Stammdatenfehler -50% | M | MDM Rules | P1 | H2 | **GESCHLOSSEN Wave 31** - `data_quality_rules.py`, `docs/architecture/process-kernel/wave-31/STATUS.md` |

## Block 041-050: Compliance, Integrationen, Markt-Differenzierung

| ID | Gap | KPI-Ziel | Aufwand | Abhaengigkeit | Prioritaet | Horizon |
|---|---|---|---|---|---|---|
| 041 | GoBD Belegkette komplett durchgaengig in allen Finanzpfaden | 100% revisionssichere Kette | L | Finance Service | P0 | H1 |
| 042 | Intrastat/Zoll produktiv inkl. Monitoring/Alerting | 0 versaeumte Meldefristen | M | Compliance Services | P0 | H1 |
| 043 | EDI/API Hub fuer Kunden/Lieferanten/Behorden | >=80% Dokumentaustausch digital | L | Integration Platform | P1 | H2 | **GESCHLOSSEN Wave 36** - `edi_hub_contracts.py`, `docs/architecture/process-kernel/wave-36/STATUS.md` |
| 044 | Lieferketten-Tracking inkl. ETA/Abweichungsalarme | OTD +10 Prozentpunkte | M | Event Bus, GPS/Telematik | P1 | H2 | **GESCHLOSSEN Wave 36** - `supply_chain_tracking.py`, `docs/architecture/process-kernel/wave-36/STATUS.md` |
| 045 | DMS + OCR + strukturierte Extraktion in Kernflows | 60% weniger manuelle Belegerfassung | M | DMS, AI OCR | P1 | H2 | **GESCHLOSSEN Wave 37** - `dms_ocr_contracts.py`, `docs/architecture/process-kernel/wave-37/STATUS.md` |
| 046 | Nachhaltigkeit/CO2 Reporting fuer Agrarkonzerne | ESG-Berichte in <1 Tag erzeugbar | M | Sustainability Domain | P2 | H3 | **GESCHLOSSEN Wave 38** - `sustainability_reporting.py`, `docs/architecture/process-kernel/wave-38/STATUS.md` |
| 047 | Branchenbenchmarking Cockpit je Genossenschaft | Monatlicher Benchmarkreport automatisch | M | Analytics Mart | P2 | H3 | **GESCHLOSSEN Wave 38** - `benchmark_cockpit.py`, `docs/architecture/process-kernel/wave-38/STATUS.md` |
| 048 | Offene Integrationsfaehigkeit fuer Agenten (Perplexity etc.) | 10 externe Agent-Use-Cases live | M | Tooling, Security | P1 | H2 | **GESCHLOSSEN Wave 37** - `agent_integration_contracts.py`, `docs/architecture/process-kernel/wave-37/STATUS.md` |
| 049 | Security-Hardening (OIDC, RBAC fein, Secrets, Audit) | 0 kritische Findings in Pentest | L | IAM, DevSecOps | P0 | H1 | **GESCHLOSSEN Wave 34** - `security_hardening_contracts.py`, `docs/architecture/process-kernel/wave-34/STATUS.md` |
| 050 | Produktive Betriebsfuehrung mit SLO/SLI und Runbooks | Verfuegbarkeit >=99.9% | M | Observability, On-call | P0 | H1 | **GESCHLOSSEN Wave 30** — `slo_definitions.py`: SLODefinition+SLIDefinition, check_slo_compliance() (ERFUELLT/TOLERANZBEREICH/VERLETZT/UNBEKANNT), 9 Default-SLOs fuer 5 Dienste; API GET/POST /process/slo/* |

## 90-Tage Ausfuehrungsreihenfolge (empfohlen)
1. Wave A (Wochen 1-4): 001, 002, 003, 009, 010, 011, 013, 014, 031, 032
2. Wave B (Wochen 5-8): 004, 015, 019, 021, 022, 024, 025, 033, 035, 039
3. Wave C (Wochen 9-12): 036, 041, 042, 049, 050 sowie Vorbereitung 016, 037, 043

### Einordnung zum Ist-Stand

- Teile von Wave B sind inzwischen umgesetzt, insbesondere `022` und `035`.
- Teile von Wave C sind inzwischen umgesetzt, insbesondere `041`, `042` (Wave 23).
- Gap `005` (Saisonale Kampagnenvorlagen) ist mit Wave 24 abgeschlossen.
- Gap `007` (Nebenkosten-Automatik) ist mit Wave 23 abgeschlossen.
- Gap `009` (Tenant-Prozessvarianten) ist mit Wave 24 abgeschlossen.
- Gap `025` (Kontextsensitive Quick Actions) ist mit Wave 25 abgeschlossen.
- Gap `027` (Konsistente Informationsdichte je Rolle) ist mit Wave 27 abgeschlossen.
- Gap `042` (Intrastat-Meldungsmodell) ist mit Wave 23 abgeschlossen.
- Gap `050` (Produktive Betriebsfuehrung mit SLO/SLI und Runbooks) ist mit Wave 30 abgeschlossen.
- Die Reihenfolge oben bleibt als historische 90-Tage-Planung erhalten und ist nicht der laufende Ist-Status.

## Governance
- Woechentliches Steering mit drei Pflicht-KPIs:
  - Delivery: % abgeschlossene P0/P1 Items pro Wave
  - Quality: Error Rate, Reopen Rate, SLA-Erfuellung
  - Adoption: aktive Nutzer in Kernprozessen, AI-Aktionsquote mit Approval

## Architekturleitplanken
- [Target State Landhandel ERP](../../architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](../../adr/adr-003-canonical-domain-model.md)
- [ADR-004 Command-/Action-Layer](../../adr/adr-004-command-action-layer.md)
- [ADR-005 Workflow-/Policy-Kern](../../adr/adr-005-workflow-policy-kern.md)

## Referenz auf Ist-Quellen im Repo
- [docs/architecture/current-processes.md](../../architecture/current-processes.md)
- [docs/analysis/valeoneuroerp_soll_ist.md](../../analysis/valeoneuroerp_soll_ist.md)
- [docs/roadmap/a-eins-gap-backlog.md](../a-eins-gap-backlog.md)
