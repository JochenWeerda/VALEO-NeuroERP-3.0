# Wave 15 - AP-Approval-Status, Workflow-Simulation, Silo-Quality, E2E-Chain

**Status:** abgeschlossen
**Datum:** 2026-03-19

## Scope

Wave 15 verbindet Approval-Status, Workflow-Simulation, Silo-Qualitaet und E2E-Kettenanalyse als fachliche Kernvertraege.

## Zielbild

Freigabe-, Simulations-, Qualitaets- und Kettenvollstaendigkeitslogik soll in wiederverwendbaren Core-Modellen verfuegbar sein.

## Lieferumfang

| AP | Modul | Beschreibung |
|----|-------|--------------|
| AP1 | `app/core/ap_approval_status.py` | `build_approval_status_response()`, Status-Mapping, `can_post`, `can_pay` |
| AP2 | `app/core/ap_approval_events.py` | `build_ap_approval_outbox_event()` fuer die relevanten Approval-Pfade |
| AP3 | `app/core/workflow_simulation.py` | `simulate_workflow()` fuer fuenf Kernszenarien |
| AP4 | `app/core/silo_quality.py` | `weighted_quality_snapshot()` fuer gewichtete Qualitaetswerte |
| AP5 | `app/core/e2e_chain.py` | `E2EProcessChain`-Hilfen fuer Links und Vollstaendigkeit |
| AP6 | `app/core/e2e_chain.py` | `ChainCompletenessReport.build()` |

## Abnahmekriterien

- Approval-Status liefert deterministisches Mapping fuer Post- und Pay-Entscheidungen.
- Workflow-Simulation deckt die fuenf Kernszenarien ab.
- Silo-Quality berechnet gewichtete Qualitaetssnapshots korrekt.
- E2E-Kette und Vollstaendigkeitsbericht erkennen fehlende Verknuepfungen.

## Tests

- Datei: `tests/test_process_kernel_wave15_approval_simulation_chain.py`
- Ergebnis: 34 Tests gruen
- Gesamtsuite: 855 passed, 5 skipped, 1 xfailed

## Status

`abgeschlossen`
Stand: 2026-03-19
