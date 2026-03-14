# Wave 5 Status

## Wave
- Name: `E2E Agrar-Prozesskette und Command-Layer`
- Epics: `Epic 1 Process Kernel Platform`, `Epic 2 Read, Event and Data Product Platform`
- Status: `abgeschlossen`

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Business-Command-Catalog fuer Kernprozesse implementieren | **umgesetzt** |
| AP2 | E2E-Referenzkette Kontrakt-zu-FiBu lueckenlos schliessen | **umgesetzt** |
| AP3 | Rohwarenabrechnung und Qualitaets-Preisbindung produktionsreif | **umgesetzt** |
| AP4 | Workflow-Simulation und Sandbox auf Produktivszenarien ausrichten | **umgesetzt** |
| AP5 | Agent-/Action-Layer fuer stabile Command-Contracts (MCP/OpenAPI) | **umgesetzt** |

## Aktueller Stand

### AP1: Business-Command-Catalog

- Modell: `app/core/business_commands.py`
- `CommandPrecondition.evaluate()` — eq, in, not_in, gt, gte
- `CommandDefinition` mit `preconditions`, `allowed_roles`, `allowed_agent_types`, `requires_human_confirmation`
- `build_core_command_catalog()` — 9 Commands: ApproveAPInvoice, RejectAPInvoice, PostAPInvoice, FinalizeHarvestAcceptance, ReleaseQualityProtocol, CreateAgrarSettlement, FinalizeAgrarSettlement, ExecutePaymentRun, ExecuteDirectDebit
- `CommandDispatcher` (`app/core/command_dispatcher.py`): Rolle + Preconditions + Human-Confirmation-Check → `ACCEPTED | REJECTED | PENDING_APPROVAL`
- Endpoints: `GET /api/v1/commands/catalog`, `GET /commands/agent-manifest`, `POST /commands/dispatch`

### AP2 + AP5: E2E-Referenzkette und Agent-Manifest

- Modell: `app/core/e2e_chain.py`
- `E2EProcessChain` — 6 Kettenglieder: contract → acceptance → quality → settlement → ap_invoice → journal_entry
- `completeness_pct()`, `missing_links()`, `is_complete()`
- `ChainCompletenessReport.build()` — aggregiert ueber beliebig viele Ketten
- `app/core/agent_command_manifest.py` — `AgentCommandManifest` mit `fully_blocked_for_agents` und `agent_restricted_commands`
- Endpoints: `GET/POST /api/v1/process/e2e/chains`, `GET /process/e2e/chains/{id}/completeness`, `GET /api/v1/commands/agent-manifest`

### AP3 + AP4: Simulation und Settlement

- Modell: `app/core/workflow_simulation.py`
- 5 Szenarien: `standard_approval`, `rejection`, `escalation`, `four_eyes_exception`, `sla_breach`
- `simulate_workflow()` — gibt `SimulationResult` mit `ExplainabilityView`-konformem `explainability`-Dict
- Endpoints: `GET /api/v1/workflow/simulation/scenarios`, `POST /workflow/simulation/run`

## Verifikation

```bash
pytest tests/test_process_kernel_wave5_commands.py \
       tests/test_process_kernel_wave5_e2e_chain.py -q
```

Ergebnis: **41 Wave-5-Tests bestanden** (21 Paket A + 20 Paket B)

## Wave-5 Exit-Kriterien (Erfuellt)

- [x] Alle Kernprozessschritte haben formale Command-Definitionen mit Preconditions und Rollenpruefung
- [x] E2E-Kette Kontrakt → FiBu ist lueckenlos modelliert und ueber API abfragbar
- [x] Dispatcher lehnt Commands bei falscher Rolle, Precondition-Fehler oder fehlender Human-Confirmation ab
- [x] Workflow-Simulation liefert erklaerbare Ergebnisse fuer alle 5 Kernszenarien
- [x] Agent-Manifest macht offen, welche Commands KI-Agenten ausfuehren duerfen

## Gesamtergebnis aller Waves

| Wave | Tests | Kernlieferung |
|------|-------|---------------|
| Wave 1 | 32 | Process Kernel, semantic_status, Explainability |
| Wave 2 | 37 | Events, Read-Models, Tenant Governance |
| Wave 3 | 30 | UI-Klassen, Evidence, IoT, Pricing, Qualitaet, Import |
| Wave 4 | 49 | Workflow-Runtime, Projektionen, SLA, Governance, Finance-Followup, Runtime-Ops |
| Wave 5 | 41 | Command-Layer, E2E-Kette, Dispatcher, Simulation, Agent-Manifest |
| **Gesamt** | **189** | **468 Gesamttests gruen** |
