# Wave 5 Paket A Status

## Paket
- Name: `Command-Layer und Agent-Contracts`
- Zugeordnete Aufgaben: `AP1`, `AP5`
- Status: `in Arbeit`

## Ziel
Alle Kernprozessaenderungen laufen ueber formale Business Commands.
Das Agent-Command-Manifest macht ausfuehrbare Commands oeffentlich verfuegbar.

## Gelieferte Artefakte

| Datei | Inhalt | Status |
|-------|--------|--------|
| `app/core/business_commands.py` | `BusinessCommand`, `CommandResult`, `CommandError`, `CommandPrecondition`, `CommandDefinition`, `build_core_command_catalog()` | in Arbeit |
| `app/core/command_dispatcher.py` | `CommandDispatcher.dispatch()` — Rolle + Preconditions + Human-Confirmation | in Arbeit |
| `app/core/agent_command_manifest.py` | `AgentCommandManifest`, `build_agent_command_manifest()` | in Arbeit |
| `app/api/v1/endpoints/command_catalog.py` | `GET /commands/catalog`, `GET /commands/agent-manifest`, `POST /commands/dispatch` | in Arbeit |
| `tests/test_process_kernel_wave5_commands.py` | ≥ 18 Tests | in Arbeit |

## Command-Katalog (Zielstand)

| Command | Aggregat | requires_human_confirmation | allowed_agents |
|---------|---------|----------------------------|----------------|
| `ApproveAPInvoice` | ap_invoice | nein | audit_agent |
| `RejectAPInvoice` | ap_invoice | nein | — |
| `PostAPInvoice` | ap_invoice | **ja** | — |
| `FinalizeHarvestAcceptance` | harvest_acceptance | nein | acceptance_agent |
| `ReleaseQualityProtocol` | quality_protocol | nein | quality_agent |
| `CreateAgrarSettlement` | agrar_settlement | nein | settlement_agent |
| `FinalizeAgrarSettlement` | agrar_settlement | **ja** | — |
| `ExecutePaymentRun` | payment_run | **ja** | — |
| `ExecuteDirectDebit` | direct_debit_run | **ja** | — |

## Abnahmekriterien
- `CommandDispatcher.dispatch()` gibt `ACCEPTED` fuer valide Commands zurueck
- `CommandDispatcher.dispatch()` gibt `REJECTED` bei falscher Rolle oder Precondition-Fehler
- `ExecutePaymentRun` und `PostAPInvoice` geben `PENDING_APPROVAL` ohne explizite `requires_human_confirmation=True`
- `AgentCommandManifest.fully_blocked_for_agents` enthaelt alle Commands ohne `allowed_agent_types`
- `POST /commands/dispatch` gibt `CommandResult` mit `schema_version=1` zurueck

## Abhaengigkeiten
- `app/core/process_commands.py` (Wave 1) — Inventur-Basis, wird NICHT veraendert
- `app/core/audit_evidence.py` (Wave 3 AP2) — Dispatcher-Audit-Hook
- `app/core/tenant_governance.py` (Wave 2 AP5) — `AgentManifest`-Referenz
