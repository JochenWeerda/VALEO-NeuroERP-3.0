# Wave-18 Status

## Scope
Canonical Process Definitions + Workflow-Versionierung + SLA/Audit-Contracts + Action-/API-Anbindung

## Zielbild

Wave 18 ist die operative Ableitung aus dem Zielplan
`C:\Users\Jochen\.cursor\plans\valeo_wettbewerbsanalyse_spitzenposition_79027aec.plan.md`.
Der Fokus liegt nicht auf neuer Endpoint-Breite, sondern auf belastbaren
Kernel-Contracts fuer die Landhandel-Kernprozesse:

1. eindeutige Canonical Process Definitions
2. versionsfaehige Workflow-Definitionen
3. SLA-/Audit-Verankerung fuer Prozessinstanzen
4. stabile, agentenfaehige Action-/Command-Anbindung

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/canonical_process_definitions.py` | verbindliches Register fuer Kernprozesse wie `contract_to_intake`, `intake_to_quality`, `quality_to_settlement`, `settlement_to_finance` | abgeschlossen |
| AP2 | `app/core/workflow_versioning.py` | `WorkflowVersion`, `WorkflowDefinitionRef`, Aktivierungs- und Nachfolgerregeln; keine stillen In-Place-Aenderungen an Prozessdefinitionen | abgeschlossen |
| AP3 | `app/core/process_audit_contracts.py` | neutrale Audit-Typen fuer `decision_reason`, `actor_type`, `evidence_refs`, `policy_snapshot`, `workflow_version` | abgeschlossen |
| AP4 | `app/core/process_sla.py` | bestehende SLA-Bausteine auf Canonical Process Definitions abstuetzen; Prozessschritt-/Deadline-Contracts explizit machen | abgeschlossen |
| AP5 | `app/core/action_execution.py` + `app/core/business_commands.py` | Action-/Command-Vertraege um `process_definition_key` und `workflow_version` erweitern, ohne zweite Execute-Logik zu bauen | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | nur lesende/kompositorische Surfacing-Endpoints fuer Prozessdefinitionen bzw. Workflow-Versionen, falls fuer Tests oder Handoff benoetigt | abgeschlossen |

## Modellierungsregeln

1. **Canonical Model zuerst** - Prozessdefinitionen referenzieren bestehende Aggregate und Read-Models, sie erzeugen keine Schattenobjekte
2. **Versionierung statt Mutation** - aenderbare Prozesslogik wird ueber neue Workflow-Versionen modelliert, nicht durch Ueberschreiben aktiver Definitionen
3. **Audit im Kern** - Begruendungen, Freigaben und Evidenzpfade gehoeren in neutrale Core-Contracts, nicht in Endpoint-Helfer
4. **Action-Layer wiederverwenden** - neue Prozessstarts oder Uebergaenge nur ueber `ActionExecutionService` bzw. bestehende Commands anbinden
5. **Keine Schichtverletzungen** - `app/core/` importiert keine API-Module; Router bleiben reine Kompositionsschicht

## Abnahmekriterien

- mindestens ein maschinenlesbares Register fuer Canonical Process Definitions vorhanden
- Workflow-Versionierung verhindert stilles Ueberschreiben bestehender Definitionen
- SLA- und Audit-Daten sind auf Prozessdefinition und Workflow-Version rueckfuehrbar
- Action-/Command-Vertraege koennen Prozessdefinition und Version transportieren
- keine Endpoint-Querimporte, keine zweite Execute-API
- API-Surfacing fuer Prozessdefinitionen und Workflow-Versionen bleibt rein lesend/kompositorisch

## Erreicht per 2026-03-14

- Canonical-Process-Register eingefuehrt und gegen Aggregate-, Command- und SLA-Contracts validiert
- Workflow-Versionierung mit aktiver Version, Draft-Nachfolger und expliziter Aktivierungsplanung eingefuehrt
- neutrale Process-Audit-Contracts mit `process_definition_key` und `WorkflowDefinitionRef` eingefuehrt
- SLA-Policies und SLA-Violations um `process_definition_key`, `workflow_key` und `workflow_version_number` erweitert
- Action-Execution- und Business-Command-Contracts tragen jetzt Wave-18-Prozessmetadaten; aktive Workflow-Version wird bei Bedarf automatisch angereichert
- Process-Kernel-API liefert jetzt lesende Sichten auf Canonical Process Definitions und Workflow-Versionen fuer Handoff, Tests und spaetere Surfacing-Pfade
- Follow-up nach AP1-AP6: Audit-Bruecke von `ActionExecutionRequest`/`ActionExecutionResult` nach `ProcessAuditEntry` ist als reiner Core-Builder vorhanden
- Follow-up nach AP1-AP6: expliziter Kompatibilitaetsvertrag fuer `settlement` (Legacy-Prozess-/Referenzsprache) vs. `agrar_settlement` (Canonical Aggregate) ist eingefuehrt und in E2E-/Referenzpfaden verankert
- Follow-up ausserhalb des direkten Kerns: Process-Commands, Exception-Catalog, Process-Config und Settlement-Command-Contracts tragen jetzt ebenfalls kanonische Settlement-Metadaten

## Nachgezogener Follow-up-Loop

- die freigelegten Wave-1-Altbaustellen in `policies.py`, `admin_core.py`, `ap_approval_workflow.py`, `ap_invoices.py`, `payment_runs.py`, `compat.py`, `closing_checklists.py`, `finance_actions.py` und `vat_return_export.py` wurden kompatibel geschlossen
- Ergebnis: `tests/test_process_kernel_wave1_contracts.py` jetzt vollstaendig gruen (`35 passed`)
- die Wave-18-Kerncontracts bleiben dabei leitend: Explainability-/Override-Modelle, Audit-Referenzen, Approval-Snapshots und kanonische Prozessmetadaten werden jetzt auch von den aelteren Finance-Pfaden wiederverwendet
- zusaetzlicher Hygiene-Loop: erste Pydantic-/SQLAlchemy-Deprecations reduziert (`declarative_base`, `SettingsConfigDict`, mehrere `min_items` -> `min_length`)
- weiterer Hygiene-Loop abgeschlossen:
  - `Field(env=...)` in `app/core/config.py` entfernt
  - `json_encoders` in `app/api/v1/schemas/base.py` entfernt
  - breit importierte API-/Finance-Modelle auf `ConfigDict` umgestellt (`app/api/v1/schemas/*`, `app/api/v1/endpoints/*`, `app/finance/schemas.py`)
  - Ergebnis fuer den breit genutzten Finance-/Wave-1/12/17-Schnitt: `74 passed, 0 warnings`
  - zusaetzliche Härtung: derselbe Schnitt laeuft auch mit `python -W error::DeprecationWarning -m pytest ...` gruen
- naechster Hygiene-Loop abgeschlossen:
  - `app/crm/schemas.py`, `app/einkauf/schemas.py` und `app/verkauf/schemas.py` vollstaendig von class-based `Config` auf `ConfigDict` umgestellt
  - `rg -n "class Config:" app/crm/schemas.py app/einkauf/schemas.py app/verkauf/schemas.py` liefert keine Treffer mehr
  - direkter Modulimport `python -W error::DeprecationWarning -c "import app.crm.schemas, app.einkauf.schemas, app.verkauf.schemas"` laeuft gruen
- abschliessender Hygiene-Loop abgeschlossen:
  - `tests/test_workflows.py` von unnötigem `pytest.mark.asyncio`-Pfad auf `asyncio.run(...)` umgestellt
  - Ursache der drei verbleibenden `pytest_asyncio`-Event-Loop-Warnungen beseitigt, kein Warning-Filter hinzugefuegt
  - `pytest tests/test_workflows.py -q --no-cov -W default` laeuft mit `4 passed, 0 warnings`
  - repo-weites Ergebnis: `pytest -q --no-cov -W default` laeuft mit `1025 passed, 5 skipped, 1 xfailed, 0 warnings`
- weiterer Folge-Loop: Position-Service ursachenorientiert bereinigt
  - DB-Testisolation fuer `tests/test_position_service.py` via Tenant-Cleanup + Nested Transaction stabilisiert
  - Severity-Logik fuer negative Positionen innerhalb Toleranz auf `YELLOW` korrigiert
  - Guard-Logik ohne aktive Regel auf erlaubenden Default zurueckgefuehrt
  - Ergebnis: `tests/test_position_service.py` jetzt vollstaendig gruen (`14 passed`)
- abschliessender Folge-Loop: Vollsuite auf funktional gruen gezogen
  - Wave-6-Supplier-Compat-Routen `/api/v1/contract-pricing/price-matrix` und `/api/v1/contract-pricing/lots` im aktuellen App-Stand verifiziert
  - `tests/test_workflows.py::test_bestellvorschlag_workflow_build` auf aktuellem Build-Contract ebenfalls verifiziert
  - Ergebnis Vollsuite: `963 passed, 5 skipped, 1 xfailed`

## Tests

- `tests/test_process_kernel_wave18_process_definitions.py` - 11 Tests gruen
- `tests/test_process_kernel_wave18_workflow_versioning.py` - 11 Tests gruen
- `tests/test_process_kernel_wave18_process_audit_contracts.py` - 7 Tests gruen
- `tests/test_process_kernel_wave18_process_sla.py` - 5 Tests gruen
- `tests/test_process_kernel_wave18_action_process_contracts.py` - 6 Tests gruen
- `tests/test_process_kernel_wave18_api_surfacing.py` - 6 Tests gruen
- `tests/test_process_kernel_wave18_action_audit_bridge.py` - 4 Tests gruen
- `tests/test_process_kernel_wave18_settlement_compatibility.py` - 5 Tests gruen
- `tests/test_process_kernel_wave18_settlement_contract_propagation.py` - 5 Tests gruen
- Regressionspruefung:
  - `tests/test_process_kernel_wave5_e2e_chain.py` - 20 Tests gruen
  - `tests/test_process_kernel_wave4_ap1_ap2_ap3.py` - 31 Tests gruen
  - `tests/test_process_kernel_wave12_sla_commands_dunning.py` - 22 Tests gruen
  - `tests/test_process_kernel_wave14_command_dispatcher.py` - 31 Tests gruen
  - `tests/test_process_kernel_wave11_commands_policy.py` - 30 Tests gruen
  - `tests/test_process_kernel_wave15_approval_simulation_chain.py` - 34 Tests gruen
  - `tests/test_process_kernel_wave17_action_execution.py` - 17 Tests gruen

## Aktueller externer Blocker

- ehemals blockierende Importfehler wurden beseitigt:
  - `app/api/v1/endpoints/compat.py`: `FutterBulkDeleteOut` vor Router-Nutzung verschoben
  - `app/core/workflow_definitions.py`: Wave-1-kompatible `WorkflowDefinition`-/`merge_workflow_variants()`-Schicht wieder vorhanden
- neuer Ist-Stand nach Freilegung und Bereinigung:
  - `tests/test_process_kernel_wave11_commands_policy.py` laeuft gruen
  - `tests/test_process_kernel_wave12_sla_commands_dunning.py` laeuft gruen
  - `tests/test_process_kernel_wave17_action_execution.py` laeuft gruen
  - `tests/test_process_kernel_wave18_settlement_contract_propagation.py` laeuft gruen
  - `tests/test_process_kernel_wave1_contracts.py` laeuft jetzt ebenfalls vollstaendig gruen
  - globaler Vollregressionslauf ist jetzt funktional gruen: `963 passed, 5 skipped, 1 xfailed`
  - die zuvor blockierenden Pydantic-v2-Deprecation-Warnungen im breit importierten Process-Kernel-/Finance-Schnitt sind beseitigt
  - aktuell sind keine repo-weiten Warning-Cluster mehr offen, die im verifizierten Testlauf sichtbar sind

## Status
`abgeschlossen`
