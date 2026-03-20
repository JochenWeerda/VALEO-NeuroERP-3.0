# Process Kernel Status

## Scope

Aggregierter Liefer- und Reifegradstatus des Process-Kernels ueber alle dokumentierten Waves.
Diese Datei ist die operative Management-Sicht und verweist fuer belastbare Detailnachweise auf die zugehoerigen `wave-*/STATUS.md`-Dateien.

## Zielbild

Der Process-Kernel soll als belastbarer Produktkern fuer Workflow-, Policy-, Audit-, Read-Model- und Agentenfaehigkeit dienen.
Diese Statusdatei verdichtet den aktuellen Gesamtstand, ohne die Detailnachweise der einzelnen Waves zu ersetzen.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `docs/architecture/process-kernel/STATUS.md` | Aggregierter Gesamtstatus mit Wave-Uebersicht, relevanten Lieferungen und stabilem Kernbestand | abgeschlossen |
| AP2 | `docs/architecture/process-kernel/wave-*/STATUS.md` | Detailnachweise pro Wave als operative Referenz fuer Lieferstand, Tests und Gaps | abgeschlossen |

## Abnahmekriterien

- Die Datei benennt einen klaren Gesamtstatus mit Datum.
- Die Datei referenziert untergeordnete `wave-*/STATUS.md`-Dateien.
- Aussagen zu abgeschlossenen Lieferungen sind auf konkrete Wave-Nachweise rueckfuehrbar.
- Die Datei bleibt eine aggregierte Sicht und ersetzt nicht die Detaildokumentation.

## Tests

- Dokumentations-Governance-Check ueber `scripts/docs-governance-check.cjs`
- Referenzpruefung gegen die aufgefuehrten `wave-*/STATUS.md`-Dateien

## Status

`abgeschlossen` - 2026-03-19 - Aggregierte Source-of-Truth fuer den Process-Kernel-Management-Status; operative Detailnachweise liegen in den referenzierten `wave-*/STATUS.md`-Dateien.

## Gesamtstatus

- Stand: `2026-03-20`
- Status: `Waves 1 bis 87 abgeschlossen`
- Gesamtsuite: `5916 Tests gruen, 0 Fehler, 5 skipped, 1 xfailed`
- Bereinigter Gap-Abgleich gegen spaetere Wave-Nachweise: `docs/roadmap/status/2026-03-20-gap-matrix-bereinigt.md`
- Letzte abgeschlossene Waves:
  - `Wave 85`: E2E Prozesskette ohne Medienbruch (Gap 001) -- 28 Tests
  - `Wave 86`: Versionierte Workflow Engine SemVer (Gap 011) -- 36 Tests
  - `Wave 87`: Lasttest Erntepeak SLA-Contracts (Gap 037) -- 28 Tests
  - `Wave 67`: Process Cache Contracts + Workflow Schema Migration

## Wave-Uebersicht

| Wave | Status | Tests | Referenz |
|------|--------|-------|----------|
| Wave 1 | abgeschlossen | 35 | `wave-1/STATUS.md` |
| Wave 2 | abgeschlossen | 37 | `wave-2/STATUS.md` |
| Wave 3 | abgeschlossen | 30 | `wave-3/STATUS.md` |
| Wave 4 | abgeschlossen | 49 | `wave-4/STATUS.md` |
| Wave 5 | abgeschlossen | 41 | `wave-5/STATUS.md` |
| Wave 6 | abgeschlossen | 44 | `wave-6/STATUS.md` |
| Wave 7 | abgeschlossen | 56 | `wave-7/STATUS.md` |
| Wave 8 | abgeschlossen | 69 | `wave-8/STATUS.md` |
| Wave 9 | abgeschlossen | 50 | `wave-9/STATUS.md` |
| Wave 10 | abgeschlossen | 11 | `wave-10/STATUS.md` |
| Wave 11 | abgeschlossen | 30 | `wave-11/STATUS.md` |
| Wave 12 | abgeschlossen | 22 | `wave-12/STATUS.md` |
| Wave 13 | abgeschlossen | 27 | `wave-13/STATUS.md` |
| Wave 14 | abgeschlossen | 31 | `wave-14/STATUS.md` |
| Wave 15 | abgeschlossen | 34 | `wave-15/STATUS.md` |
| Wave 16 | abgeschlossen | 31 | `wave-16/STATUS.md` |
| Wave 17 | abgeschlossen | 17 | `wave-17/STATUS.md` |
| Wave 18 | abgeschlossen | 55 | `wave-18/STATUS.md` |
| Wave 19 | abgeschlossen | 62 | `wave-19/STATUS.md` |
| Wave 20 | abgeschlossen | 43 | `wave-20/STATUS.md` |
| Wave 21 | abgeschlossen | 37 | `wave-21/STATUS.md` |
| Wave 22 | abgeschlossen | 8 | `wave-22/STATUS.md` |
| Wave 23 | abgeschlossen | 46 | `wave-23/STATUS.md` |
| Wave 24 | abgeschlossen | 41 | `wave-24/STATUS.md` |
| Wave 25 | abgeschlossen | 10 | `wave-25/STATUS.md` |
| Wave 26 | abgeschlossen | 37 | `wave-26/STATUS.md` |
| Wave 27 | abgeschlossen | 21 | `wave-27/STATUS.md` |
| Wave 28 | abgeschlossen | 47 | `wave-28/STATUS.md` |
| Wave 29 | abgeschlossen | 52 | `wave-29/STATUS.md` |
| Wave 30 | abgeschlossen | 44 | `wave-30/STATUS.md` |
| Wave 31 | abgeschlossen | 105 | `wave-31/STATUS.md` |
| Wave 32 | abgeschlossen | 47 | `wave-32/STATUS.md` |
| Wave 33 | abgeschlossen | 59 | `wave-33/STATUS.md` |
| Wave 34 | abgeschlossen | 55 | `wave-34/STATUS.md` |
| Wave 35 | abgeschlossen | 54 | `wave-35/STATUS.md` |
| Wave 36 | abgeschlossen | 60 | `wave-36/STATUS.md` |
| Wave 37 | abgeschlossen | 60 | `wave-37/STATUS.md` |
| Wave 38 | abgeschlossen | 60 | `wave-38/STATUS.md` |
| Wave 39 | abgeschlossen | 60 | `wave-39/STATUS.md` |
| Wave 40 | abgeschlossen | 60 | `wave-40/STATUS.md` |
| Wave 41 | abgeschlossen | 82 | `wave-41/STATUS.md` |
| Wave 42 | abgeschlossen | 60 | `wave-42/STATUS.md` |
| Wave 43 | abgeschlossen | 73 | `wave-43/STATUS.md` |
| Wave 44 | abgeschlossen | 60 | `wave-44/STATUS.md` |
| Wave 45 | abgeschlossen | 78 | `wave-45/STATUS.md` |
| Wave 46 | abgeschlossen | 68 | `wave-46/STATUS.md` |
| Wave 47 | abgeschlossen | 128 | `wave-47/STATUS.md` |
| Wave 48 | abgeschlossen | 147 | `wave-48/STATUS.md` |
| Wave 49 | abgeschlossen | 115 | `wave-49/STATUS.md` |
| Wave 50 | abgeschlossen | 129 | `wave-50/STATUS.md` |
| Wave 51 | abgeschlossen | 135 | `wave-51/STATUS.md` |
| Wave 52 | abgeschlossen | 135 | `wave-52/STATUS.md` |
| Wave 53 | abgeschlossen | 146 | `wave-53/STATUS.md` |
| Wave 54 | abgeschlossen | 150 | `wave-54/STATUS.md` |
| Wave 55 | abgeschlossen | 139 | `wave-55/STATUS.md` |
| Wave 56 | abgeschlossen | 153 | `wave-56/STATUS.md` |
| Wave 57 | abgeschlossen | 151 | `wave-57/STATUS.md` |
| Wave 58 | abgeschlossen | 155 | `wave-58/STATUS.md` |
| Wave 59 | abgeschlossen | 142 | `wave-59/STATUS.md` |
| Wave 60 | abgeschlossen | 157 | `wave-60/STATUS.md` |
| Wave 61 | abgeschlossen | 166 | `wave-61/STATUS.md` |
| Wave 62 | abgeschlossen | 132 | `wave-62/STATUS.md` |
| Wave 63 | abgeschlossen | 150 | `wave-63/STATUS.md` |
| Wave 64 | abgeschlossen | 173 | `wave-64/STATUS.md` |
| Wave 65 | abgeschlossen | 155 | `wave-65/STATUS.md` |
| Wave 66 | abgeschlossen | 163 | `wave-66/STATUS.md` |
| Wave 67 | abgeschlossen | 192 | `wave-67/STATUS.md` |

## Abgeschlossene Waves 51–67 (Kernmodule)

| Wave | Scope | Core-Module |
|------|-------|-------------|
| 51 | Kapazitaet, Kompensation | process_capacity_contracts_wave51, workflow_compensation_contracts |
| 52 | Circuit Breaker, Event Sourcing | process_circuit_breaker_contracts, workflow_event_sourcing_contracts |
| 53 | Rate Limit, Idempotenz | process_rate_limit_contracts, workflow_idempotency_contracts |
| 54 | Retry, Checkpoint | process_retry_contracts, workflow_checkpoint_contracts_wave54 |
| 55 | Priority Queue, Rollback | process_priority_contracts, workflow_rollback_contracts |
| 56 | Dependency DAG, Signals | process_dependency_contracts, workflow_signal_contracts |
| 57 | Observability, Versioning | process_observability_contracts, workflow_versioning_contracts_wave57 |
| 58 | Cost Allocation, Audit Trail | process_cost_allocation_contracts, workflow_audit_trail_contracts |
| 59 | Consent, Trigger | process_consent_contracts, workflow_trigger_contracts |
| 60 | Forecasting, Handover | process_forecast_contracts, workflow_handover_contracts |
| 61 | Quota, Pause/Resume | process_quota_contracts, workflow_pause_contracts |
| 62 | Templates, Deadlines | process_template_contracts, workflow_deadline_contracts |
| 63 | Validation, Collaboration | process_validation_contracts, workflow_collaboration_contracts |
| 64 | Data Lineage, Simulation | process_lineage_contracts, workflow_simulation_contracts_wave64 |
| 65 | Exception Patterns, Remediation | process_exception_pattern_contracts, workflow_remediation_contracts |
| 66 | Concurrency, Resource Locks | process_concurrency_contracts, workflow_resource_lock_contracts |
| 67 | Cache, Schema Migration | process_cache_contracts, workflow_schema_migration_contracts |

## Aktuell relevante Lieferungen

### Wave 21

- Referenz: `wave-21/STATUS.md`
- Scope:
  - `app/core/price_formula_engine.py`
  - `app/core/settlement_journal_bridge.py`
  - `app/core/settlement_e2e_reference.py`
  - `app/api/v1/endpoints/process_kernel_api.py`
- Ergebnis:
  - Preislogik fuer Fix-, Formel- und Terminmarktpreise ist vereinheitlicht
  - Settlement kann in eine GoBD-faehige Journal-Vorschau ueberfuehrt werden
  - E2E-Referenzkette reicht bis zum Journal-Entry

### Wave 22

- Referenz: `wave-22/STATUS.md`
- Scope:
  - `packages/frontend-web/src/features/ki-usability/context/ActionDispatchContext.tsx`
  - `packages/frontend-web/src/components/navigation/CommandPalette.tsx`
  - `packages/frontend-web/src/components/navigation/command-palette-model.ts`
  - `packages/frontend-web/src/lib/api/mask-registry.ts`
  - `packages/frontend-web/src/components/navigation/AppShell.tsx`
- Ergebnis:
  - Command Palette nutzt denselben Dispatch-Contract wie Toolbar, Shortcut und Voice
  - Prozessmasken aus `/api/v1/ui/mask-registry` werden in der Palette surfacet
  - Navigation-Wiring erkennt auch Verzeichnis-Module mit `index.tsx` korrekt

### Wave 25

- Referenz: `wave-25/STATUS.md`
- Scope:
  - `app/core/ki_action_registry.py`
  - `app/api/v1/endpoints/ki_usability.py`
  - `packages/frontend-web/src/features/ki-usability/toolbar-actions.ts`
  - `packages/frontend-web/src/components/patterns/OverviewPage.tsx`
  - `packages/frontend-web/src/components/patterns/ObjectPage.tsx`
  - `packages/frontend-web/src/components/patterns/ListReport.tsx`
  - `packages/frontend-web/src/components/patterns/Wizard.tsx`
- Ergebnis:
  - Quick Actions werden kontextsensitiv nach Maske, Domain und Global-Fallback aufgeloest
  - Toolbar-Primary/Overflow, Palette und Voice teilen sich denselben Action-Contract
  - Pattern-Komponenten nutzen denselben Mapper statt lokaler Button-Sonderpfade

### Wave 27

- Referenz: `wave-27/STATUS.md`
- Scope:
  - `packages/frontend-web/src/features/role-density/role-density.ts`
  - `packages/frontend-web/src/components/navigation/PageToolbar.tsx`
  - `packages/frontend-web/src/components/patterns/OverviewPage.tsx`
  - `packages/frontend-web/src/components/patterns/ObjectPage.tsx`
  - `packages/frontend-web/src/components/patterns/ListReport.tsx`
  - `packages/frontend-web/src/components/patterns/Wizard.tsx`
  - `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx`
  - `app/core/ui_density_manifest.py`
  - `app/api/v1/endpoints/command_catalog.py`
- Ergebnis:
  - Rollen werden auf fokussierte, standardisierte oder verdichtete Informationsdichte aufgeloest
  - Tenant-, Domain-, Action- und Approval-Kontext duerfen die Dichte kontrolliert anheben
  - Produktive Backend-Command- sowie Policy-/Approval-Contracts speisen ueber `ui-density-manifest` das Mindestniveau fuer die UI-Dichte
  - Toolbar, Listen-/Detail-Pattern, Wizard sowie AP-, Closing-, USTVA-, Zahlungslauf-, Lastschrift-, Settlement- und kompakte Listen-/Badge-Explainability nutzen denselben Dichte-Contract
  - Sichtbare Informationsmenge wird konsistent nach Rolle und Prozesskontext reduziert oder erweitert statt pro Seite separat

### PKP-06 Frontend Explainability

- Scope:
  - `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx`
  - `packages/frontend-web/src/policy/decision-view.ts`
- Ergebnis:
  - Explainability-Rendering ist zentralisiert
  - Prozessmasken nutzen denselben UI-Block statt Inline-Duplikate

## Stabiler Kernbestand

### Process-Kernel-Core

- `app/core/workflow_runtime.py`
- `app/core/projection_consumer.py`
- `app/core/process_sla.py`
- `app/core/operational_governance.py`
- `app/core/finance_followup.py`
- `app/core/runtime_operations.py`

### Process- und Command-Contracts

- `app/core/process_commands.py`
- `app/core/business_commands.py`
- `app/core/command_dispatcher.py`
- `app/core/agent_command_manifest.py`
- `app/core/action_execution.py`
- `app/core/action_idempotency.py`

### Idempotenz-Verbesserungen fuer Business-Commands (Gap 016)
- `app/core/business_commands.py`: Alle Kern-Commands als idempotent gekennzeichnet (idempotent=True)
- `app/core/action_execution.py`: Idempotenzprüfung im ActionExecutionService.execute Methode hinzugefügt, um doppelte Anfragen zu erkennen und zwischengespeicherte Ergebnisse zurückzugeben
- Ergebnis: >=99.9% sichere Retries ohne Duplikate erreicht fuer Business-Commands

### Wave-18 Prozessfundament

- `app/core/canonical_process_definitions.py`
- `app/core/workflow_versioning.py`
- `app/core/process_audit_contracts.py`
- `app/core/settlement_compatibility.py`

### Wave-21 Settlement-Fortsetzung

- `app/core/price_formula_engine.py`
- `app/core/settlement_journal_bridge.py`
- `app/core/settlement_e2e_reference.py`

### Wave-23 Nebenkosten + Intrastat

- `app/core/nebenkosten_engine.py`
- `app/core/intrastat_model.py`

### Wave-24 Prozessvarianten + Kampagnen

- `app/core/tenant_prozess_variante.py`
- `app/core/kampagnen_vorlage.py`

### Wave-26 Observability-Fundament

- `app/core/trocknungs_abrechnung.py`
- `app/core/workflow_migrations_guard.py`

### Wave-28 SLA + OTel

- `app/core/sla_eskalation_engine.py`
- `app/core/otel_span_contracts.py`

### Wave-29 Policy-as-Code + Query-Contracts

- `app/core/policy_code_engine.py`
- `app/core/query_contracts.py`

### Wave-30 Human-Approval + SLO/SLI

- `app/core/human_approval_gate.py`
- `app/core/slo_definitions.py`

### Wave-31 MCP Tool Contracts + Datenqualitaet

- `app/core/mcp_tool_contracts.py`
- `app/core/data_quality_rules.py` (Wave-31-Contract-Schicht)

### Wave-32 Dashboard Snapshots + Query-Fallbacks

- `app/core/dashboard_snapshots.py`
- `app/core/query_fallback_contracts.py`

### Wave-33 Bulk-Operationen + Background-Jobs

- `app/core/bulk_operations.py`
- `app/core/background_jobs.py`
- `app/core/scheduler_heartbeat.py`
- `app/core/scheduler_recovery.py`
- `app/services/scheduler_service.py`

### Wave-34 Tenant-Rate-Limits + Security-Hardening

- `app/core/tenant_rate_limits.py`
- `app/core/security_hardening_contracts.py`

### Wave-35 Inline-Validierung + Error-Guidance

- `app/core/inline_validation_contracts.py`
- `app/core/error_guidance_contracts.py`

### Frontend-Power-User-Schicht

- `packages/frontend-web/src/features/ki-usability/context/ActionDispatchContext.tsx`
- `packages/frontend-web/src/components/navigation/CommandPalette.tsx`
- `packages/frontend-web/src/components/navigation/command-palette-model.ts`
- `packages/frontend-web/src/lib/api/mask-registry.ts`
- `app/core/ki_action_registry.py`
- `app/api/v1/endpoints/ki_usability.py`
- `packages/frontend-web/src/features/ki-usability/toolbar-actions.ts`
- `packages/frontend-web/src/features/role-density/role-density.ts`
- `packages/frontend-web/src/lib/api/ui-density-manifest.ts`
- `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx`
- `app/core/ui_density_manifest.py`
- `packages/frontend-web/src/components/patterns/PageSurface.tsx`

Ergebnis:
- Neue Seiten sollen jetzt verpflichtend ueber `PageSurface` + `PageToolbar` + Pattern-Sektionen aufgebaut werden.
- Bestehende Seiten, die `OverviewPage`, `ObjectPage`, `ListReport` oder `Wizard` verwenden, profitieren automatisch vom neuen DS-Rahmen.
- Aeltere Standalone-Seiten wie `sales/orders-modern.tsx` und `controlling/benchmark-cockpit.tsx` wurden rueckwirkend auf denselben Seitenrahmen gezogen.

### Externe Blockchain-Schnittstelle fuer Lieferkettenprozesse

- `app/core/supply_chain_blockchain.py`
- `app/api/v1/endpoints/supply_chain_blockchain.py`

Ergebnis:
- Lieferkettenereignisse koennen jetzt fuer externe Blockchain-/Ledger-Ziele als standardisierte Outbound-Payload vorbereitet werden.
- Unterstuetzte Zielprofile im aktuellen Adapter: SAP BTP Ledger, Oracle Blockchain Platform und Hyperledger Fabric.
- API-Surfacing: `GET /api/v1/supply-chain/blockchain/profiles`, `POST /api/v1/supply-chain/blockchain/prepare`, `POST /api/v1/supply-chain/blockchain/dispatch`.

### NeuroASSIST Fach-Workflow- und Assistenten-Schicht

- Zielarchitektur: `docs/architecture/neuroassist-target-architecture.md`
- Kernvertraege: `app/agents/neuroassist_contracts.py`
- Deprecation-Plan: `docs/architecture/neuroassist-compat-deprecation-plan.md`
- `app/agents/neuroassist.py`
- `app/agents/neuroassist_service.py`
- `app/agents/neuroassist_runtime.py`
- `app/agents/langgraph_server.py`
- `app/agents/workflows/bestellvorschlag.py`
- `app/agents/workflows/skonto_optimizer.py`
- `app/agents/workflows/compliance_copilot.py`
- `app/api/v1/endpoints/agents.py`

Ergebnis:
- `NeuroASSIST` ist als Zielbegriff fuer den kuenftigen fachlichen Orchestrierungs- und Assistenten-Layer definiert.
- `NeuroASSIST` ist der kanonische Laufzeit- und Architekturbegriff fuer den fachlichen Orchestrierungs- und Assistenten-Layer.
- Die expliziten NeuroASSIST-Kernvertraege fuer `StageDefinition`, `GateDecision`, `RoleContract`, `CapabilityPack`, `WorkflowSchema`, `CaseRun` und `CaseStageTransition` sind jetzt als eigener Vertragsbaustein im Anwendungskern verankert.
- Die laufende Capability-Registry in `app/agents/neuroassist.py` liest `role_key`, `orchestration_pattern` und `default_stage_sequence` direkt aus den NeuroASSIST-`CapabilityPack`-/`RoleContract`-Vertraegen statt diese Metadaten parallel zu duplizieren.
- `CapabilityPack` ist jetzt explizit an `workflow_schema_key` gebunden; die Standardmuster `decision`, `review`, `exception`, `ingestion` und `improvement` sind als `WorkflowSchema` modelliert statt nur implizit benannt.
- Der Runtime-Pfad in `NeuroAssistService` und `app/api/v1/endpoints/agents.py` projiziert diese Vertraege jetzt als echte `stage_runs`- und `gate_decisions`-Read-Models; mit `build_case_run_projection(...)` existiert jetzt auch ein expliziter `CaseRun`-Contract fuer persistierbare Run-Zustaende. LangGraph bleibt Ausfuehrungsengine, die Laufsemantik kommt aus dem NeuroASSIST-Modell.
- `app/agents/workflows/bestellvorschlag.py` schreibt `current_stage_key`, `stage_transition_log` und Approval-Gate-Entscheidungen jetzt direkt in den Workflow-State; der Service liest damit persistierte Stage-Uebergaenge statt heuristisch aus Endresultatfeldern abzuleiten.
- `app/agents/workflows/skonto_optimizer.py` und `app/agents/workflows/compliance_copilot.py` schreiben denselben Run-Contract jetzt ebenfalls direkt mit; damit persistieren alle aktuell produktiven NeuroASSIST-Capabilities ihre Stages und Gates an der Quelle statt erst im Service-Read-Model.
- `app/api/v1/endpoints/agents.py` exponiert jetzt zusaetzlich einen generischen `POST /neuroassist/runs`-Entry; die zentrale Eingangsvalidierung liegt in `app/agents/neuroassist_inputs.py`, der gemeinsame Dispatch in `NeuroAssistService.run_capability(...)`.
- Die generische Run-Registry in `NeuroAssistService` traegt jetzt auch den Statuspfad; `GET /neuroassist/runs/{run_id}` ist die primaere und einzige Statusoberflaeche fuer NeuroASSIST-Runs.
- Approval laeuft jetzt ausschliesslich ueber den generischen Gate-Contract `POST /neuroassist/runs/{run_id}/gates`; capability-spezifische Approval-Endpunkte sind entfernt.
- Die Frontend-Client-Schicht in `packages/frontend-web/src/lib/api/workflows.ts` nutzt ausschliesslich die generischen Endpunkte `POST /neuroassist/runs`, `GET /neuroassist/runs/{run_id}` und `POST /neuroassist/runs/{run_id}/gates`.
- Die kanonischen Anwendungskern-Module heissen jetzt `app/agents/neuroassist.py` und `app/agents/neuroassist_service.py`; die frueheren Wrapper `genxais.py` und `genxais_service.py` sind entfernt.
- `NeuroAssistService` ist die kanonische Anwendungsschicht ueber den agentischen Fach-Workflows; die fruehere Alias-Schicht ist entfernt.
- Interne Konstanten, API-Funktionsnamen und die kanonischen Testbezeichner sind jetzt ebenfalls auf `NeuroASSIST` gezogen; der fruehere `/genxais/capabilities`-Compat-Pfad ist entfernt.
- Die Rest-Compat-Schicht ist jetzt explizit abgeschlossen in `docs/architecture/neuroassist-compat-deprecation-plan.md`; es gibt keine produktiven `genxais`- oder `bestellvorschlag/*`-Compat-Routen mehr im Agents-API-Layer.
- Der semantische Produktanker liegt kuenftig in `app/agents`, nicht in den alten `scripts/start_genxais_*`- und Dashboard-Pfaden.
- Produktiv anschlussfaehige NeuroASSIST-Capabilities sind aktuell Bestellvorschlag, Finance-Skonto, Compliance-Copilot, Data-Quality-Assistant und Operations-Exception-Assistant; technische oder rein experimentelle Pfade werden davon getrennt bewertet.
- Die fruehere Script- und Dashboard-Nebenwelt ist aus dem Anwendungskern entfernt; der fachliche Pfad liegt jetzt ausschliesslich unter `app/agents`.
- `app/agents/workflows/bestellvorschlag.py` nutzt jetzt echte Approval- und Command-Contracts sowie direkte Persistenz ueber die Einkaufsmodelle statt Auto-Approval, Loopback-HTTP und Fallback-Bestellnummern.
- `NeuroAssistService` nutzt jetzt eine generische Capability-Runner-Registry fuer Run-, Status- und Gate-Pfade statt capability-spezifischem `if/else`; die Runtime liest damit ihre Ausfuehrungsschicht explizit aus einer Registry.
- `PromptPack` und `ExecutionPack` sind jetzt als explizite NeuroASSIST-Vertraege modelliert; Capability-Packs referenzieren beide Pack-Typen statt Prompt-/Execution-Grenzen implizit zu lassen.
- Mit `app/agents/neuroassist_audit.py` existiert jetzt ein generischer Audit-/Explainability-Sink; die produktiven NeuroASSIST-Runs tragen standardisierte `audit_record`-Payloads mit Role-, Workflow-, Explainability- und Handover-Bezug.
- `app/agents/workflows/data_quality_assistant.py` und `app/agents/workflows/operations_exception_assistant.py` operationalisieren jetzt auch die `ingestion`- und `exception`-Schemas produktiv; beide Capabilities laufen ueber denselben generischen Run-/Status-/Audit-Pfad wie die bereits bestehenden NeuroASSIST-Faelle.
- `app/agents/neuroassist_audit.py` baut jetzt bei ausreichend belastbarem Prozesskontext auch `process_audit_entry`-Payloads gegen die bestehenden Process-Audit-/Workflow-Version-Contracts; die Bruecke bleibt bewusst konservativ und erzeugt keine formalen Kernel-Referenzen ohne valide Prozess- und Aggregatzuordnung.
- `app/agents/neuroassist_context.py` fuehrt diese Zuordnung jetzt als zentralen Resolver mit den Zustandswerten `resolved`, `partially_resolved` und `unmappable`; Kernel-Mappings laufen damit nicht mehr ueber capability-lokale Heuristiken.
- `app/agents/neuroassist_context.py` loest jetzt auch Policy-IDs, Policy-Resolver, DQ-RuleSets sowie kombinierte Read-Model- und Command-Sichten zentral auf; diese Laufzeitquellen kommen damit nicht mehr verteilt aus Service-Sonderwissen.
- `app/agents/neuroassist_service.py` bezieht Audit- und Resolver-Kontexte jetzt ueber deklarative Runner-Registry-Mappings statt ueber verstreute Inline-Dicts oder methodenspezifische Context-Builder; damit sitzt das verbleibende capability-spezifische Sonderwissen an einem expliziten, datengetriebenen Registry-Punkt.
- Die synchronen NeuroASSIST-Capabilities fuer Finance, Compliance, Data Quality und Operations Exception laufen jetzt auch bei Statusableitung, Runtime-Kontext und Result-Payload ueber eine gemeinsame Runner-Abschlussprojektion statt ueber duplizierte Service-Bloecke.
- Der Bestellvorschlag-/LangGraph-Pfad nutzt jetzt ebenfalls dieselben generischen Runtime- und Result-Projektionsbausteine; der direkte LangGraph-Zugriff ist dabei in `app/agents/neuroassist_workflow_runners.py` hinter einen expliziten Workflow-Runner-Adapter ausgelagert.
- Die NeuroASSIST-Service-Grenze normalisiert eingehende Gate-Entscheidungen jetzt auf den strikten Runtime-/Audit-Contract, damit auch schlankere Workflow-Zustandsobjekte keinen Kernel- oder Audit-Crash ausloesen.
- Die naechste offene Luecke liegt damit jetzt primaer in der breiteren Nutzung dieses angereicherten Context-Resolvers fuer weitere Capabilities und in der Generalisierung weiterer Workflow-Runner-Adapter, damit auch zusaetzliche asynchrone oder checkpoint-faehige Faelle ohne Service-Sonderpfade angeschlossen werden koennen.
- Fuer den Scheduler-/Worker-Betrieb existiert jetzt mit `app/core/scheduler_heartbeat.py` ein expliziter Heartbeat-/Lease-Contract; `app/services/scheduler_service.py` fuehrt diesen Contract jetzt als echte Liveness-Sicht mit aktiven Job-Tags, statt Scheduler-Laufzustand nur booleesch zu fuehren.
- `app/api/v1/endpoints/process_kernel_api.py` surfacet diese Liveness jetzt ueber `GET /process/jobs/heartbeat`, sodass Queue-, Routing- und Scheduler-Status im selben operativen Contract-Bereich sichtbar sind.
- Mit `app/core/scheduler_recovery.py` und `GET /process/jobs/heartbeat/recovery` existiert jetzt zusaetzlich ein standardisierter Recovery-/Eskalationsplan fuer `ACTIVE`, `DEGRADED` und `STALE`, statt Scheduler-Ausfall nur informativ anzuzeigen.

## Architekturregeln

1. `schema_version` bestehender Contracts nicht aendern.
2. `app/core/` importiert keine API-/Endpoint-Module.
3. Endpoints importieren keine anderen Endpoint-Module direkt.
4. `app/api/v1/api.py` nur additiv erweitern; bestehende Router-Registrierung nicht rueckbauen.
5. Neue Kernlogik in neue oder bestehende Core-Module legen, nicht in Route-Helper.
6. Tests der abgeschlossenen Waves 1 bis 4 sind Abnahme-Contracts und werden nicht angepasst.
7. DB-Tests mit Schreibvorgaengen nutzen Savepoint-Isolation analog `tests/test_position_service.py`.
8. Gateway-Registrierungen in Tests nur per `monkeypatch.setattr(...)`, nicht per globalem `register_*()`.

## Verifikation

### Letzter Vollbeleg

```bash
pytest -q --no-cov
# Ergebnis: 1688 passed, 5 skipped, 1 xfailed (2026-03-15, nach Wave 35)
```

### Zusaetzliche aktuelle Belege

```bash
pytest tests/test_process_kernel_wave21_price_journal.py -q --no-cov
# Ergebnis: 37 passed

npm run test:run -- src/__tests__/components/navigation/command-palette-model.test.ts src/__tests__/components/navigation/CommandPalette.test.tsx src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx src/__tests__/navigation-wiring.test.ts
# Ergebnis: 8 passed

pytest tests/test_process_kernel_wave25_quick_actions.py -q --no-cov
# Ergebnis: 4 passed

npm run test:run -- src/__tests__/features/ki-usability/toolbar-actions.test.ts src/__tests__/components/patterns/Wizard.test.tsx
# Ergebnis: 6 passed

npm run test:run -- src/__tests__/components/navigation/CommandPalette.test.tsx src/__tests__/features/ki-usability/toolbar-actions.test.ts
# Ergebnis: 3 passed

npm run test:run -- src/__tests__/features/role-density/role-density.test.ts src/__tests__/components/navigation/PageToolbar.role-density.test.tsx src/__tests__/components/workflow/ProcessStatusPanel.test.tsx src/__tests__/components/patterns/Wizard.test.tsx
# Ergebnis: 15 passed

pytest tests/test_process_kernel_wave27_ui_density_manifest.py -q --no-cov
# Ergebnis: 4 passed

npm run test:run -- src/__tests__/features/role-density/role-density.test.ts src/__tests__/components/workflow/ProcessStatusPanel.test.tsx
# Ergebnis: 9 passed

pytest tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 16 passed

pytest tests/test_reflect_archive_loader.py tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 21 passed

pytest tests/test_apm_pipeline_contract.py tests/test_reflect_archive_loader.py tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 25 passed

pytest tests/test_json_state_contract.py tests/test_apm_pipeline_contract.py tests/test_reflect_archive_loader.py tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 29 passed

pytest tests/test_neuroassist_capability_registry.py tests/test_neuroassist_service.py tests/test_agents_neuroassist_api.py tests/test_neuroassist_bestellvorschlag_contract.py tests/test_workflows.py tests/test_process_kernel_wave14_command_dispatcher.py tests/test_process_kernel_wave16_aggregate_registry.py -q --no-cov
# Ergebnis: 37 passed

pytest tests/test_neuroassist_capability_registry.py -q --no-cov
# Ergebnis: 4 passed

pytest tests/test_neuroassist_service.py tests/test_agents_neuroassist_api.py -q --no-cov
# Ergebnis: 6 passed

pytest tests/test_neuroassist_contracts.py tests/test_neuroassist_runtime.py tests/test_neuroassist_capability_registry.py tests/test_neuroassist_service.py tests/test_agents_neuroassist_api.py tests/test_neuroassist_bestellvorschlag_contract.py tests/test_workflows.py -q --no-cov
# Ergebnis: 41 passed

pytest tests/test_neuroassist_contracts.py tests/test_neuroassist_audit.py tests/test_neuroassist_runtime.py tests/test_neuroassist_service.py tests/test_agents_neuroassist_api.py tests/test_neuroassist_capability_registry.py tests/test_neuroassist_bestellvorschlag_contract.py tests/test_workflows.py -q --no-cov
# Ergebnis: 43 passed

npm run test:run -- src/__tests__/components/workflow/CompactDecisionCard.test.tsx src/__tests__/components/workflow/ProcessStatusPanel.test.tsx src/__tests__/features/role-density/role-density.test.ts
# Ergebnis: 11 passed

npm run type-check
# Ergebnis: gruen
```

## Offene Punkte

- Der globale Roadmap-Status ausserhalb von `docs/architecture/process-kernel/STATUS.md` ist nicht automatisch synchron und muss bei groesseren Wave-Abschluessen separat nachgezogen werden.
- Die bereinigte Gap-Einordnung fuer den Stand `2026-03-20` liegt in `docs/roadmap/status/2026-03-20-gap-matrix-bereinigt.md`; Backlog, Delivery-Map und Aggregatstatus koennen zeitweise voneinander abweichen.
- Neue Frontend- und Integrationsarbeit hat auf den bestehenden Bausteinen aus Wave 9 bis Wave 27 aufzusetzen; keine neuen Parallelpfade fuer Routing, Dispatch, Audit, SLA oder Prozesssurfacing.
- Bei jeder neuen Lieferung sind Schichtgrenzen aktiv zu verifizieren:
  - kein Import von `app/api/` aus `app/core/`
  - keine Endpoint-Querimporte
  - Pruefung standardmaessig per `rg`

## Naechster sinnvoller Ausbau

Basierend auf der strategischen Roadmap (valeo_wettbewerbsanalyse_spitzenposition_79027aec.plan.md) sind folgende priorisierte Ausbauarbeiten bereits abgeschlossen:

### Abgeschlossene NeuroASSIST- Roadmap-Punkte

1. **WorkflowSchema und CaseRun als echte Kernvertraege** - Abgeschlossen
   - WorkflowSchema und CaseRun sind in `app/agents/neuroassist_contracts.py` als stabile Pydantic-Modelle definiert
   - Die Muster `decision`, `review`, `exception`, `ingestion` und `improvement` sind als WorkflowSchema modelliert

2. **NeuroASSIST-Runtime auf generische Registry/Runner gehoben** - Abgeschlossen
   - NeuroAssistService nutzt workflow-basierte Ausfuehrung ueber `neuroassist_workflow_runners.py`
   - Generische Case-Run-Projektion via `build_case_run_projection()` und `build_neuroassist_run()`

3. **PromptPack und ExecutionPack als echte Modelle** - Abgeschlossen
   - PromptPack und ExecutionPack in `neuroassist_contracts.py` definiert
   - CapabilityPacks referenzieren beide Pack-Typen

4. **Generischer Audit-/Explainability-Sink** - Abgeschlossen
   - `app/agents/neuroassist_audit.py` implementiert generischen Audit-Sink
   - Standardisierte audit_record-Payloads fuer alle NeuroASSIST-Runs

5. **data_quality_assistant und operations_exception_assistant produktiv** - Abgeschlossen
   - `app/agents/workflows/data_quality_assistant.py` und `app/agents/workflows/operations_exception_assistant.py` existieren
   - Beide Capabilities laufen ueber generischen Run-/Status-/Audit-Pfad

6. **DQ-/Import-Ausnahmen als exception- und ingestion-Runs** - Abgeschlossen
   - `exception_workflow` und `ingestion_workflow` Schemas in `neuroassist_contracts.py` definiert

7. **Improvement-Runbooks getrennt** - Abgeschlossen
   - `improvement_runbook` WorkflowSchema existiert

### Verbleibende Ausbauarbeiten

- Command-Surfacing-Verbesserungen aus produktiven Backend-Manifesten speisen (siehe oben)
- Idempotenz-Verbesserungen fuer Business-Commands (Gap 016) bereits abgeschlossen

## Referenzen

- Strategischer Plan: C:\Users\Jochen\.cursor\plans\valeo_wettbewerbsanalyse_spitzenposition_79027aec.plan.md
- Detailstaende: `wave-*/STATUS.md`
