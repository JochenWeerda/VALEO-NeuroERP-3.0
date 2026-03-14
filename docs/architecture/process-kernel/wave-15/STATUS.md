# Wave-15 Status

## Scope
AP-Approval-Status, Workflow-Simulation, Silo-Quality, E2E-Chain

## Lieferumfang

| AP | Modul | Beschreibung |
|----|-------|--------------|
| AP1 | `app/core/ap_approval_status.py` | `build_approval_status_response()`, Status-Mapping-Dicts, can_post/can_pay, Override-Resolution |
| AP2 | `app/core/ap_approval_events.py` | `build_ap_approval_outbox_event()` — alle 4 Pfade (requested, approve-full, approve-partial, reject, none) |
| AP3 | `app/core/workflow_simulation.py` | `simulate_workflow()` — 5 Szenarien: standard, rejection, escalation, four_eyes, sla_breach |
| AP4 | `app/core/silo_quality.py` | `weighted_quality_snapshot()` — gewichtete Durchschnitte, Leerfall, inactive-Filter |
| AP5 | `app/core/e2e_chain.py` | `E2EProcessChain.links()`, `completeness_pct()`, `missing_links()`, `is_complete()` |
| AP6 | `app/core/e2e_chain.py` | `ChainCompletenessReport.build()` — Vollständigkeitsbericht mit Gaps |

## Tests
- Datei: `tests/test_process_kernel_wave15_approval_simulation_chain.py`
- Ergebnis: **34 Tests gruen**
- Gesamtsuite: **855 passed, 5 skipped, 1 xfailed**

## Status
`abgeschlossen`
