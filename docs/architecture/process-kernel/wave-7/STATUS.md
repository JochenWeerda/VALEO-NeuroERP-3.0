# Wave 7 - Read-Model-Persistenz, Reklamation und Preisabsicherung

**Status:** abgeschlossen
**Datum:** 2026-03-19

## Scope

Wave 7 fuehrt Snapshot-Persistenz, Event-Consumer-Wiring sowie Domain-Bausteine fuer Reklamation, Ausnahmefaelle, Preisabsicherung und Silo-Protokolle ein.

## Zielbild

Read-Models sollen dauerhaft speicherbar und Event-getrieben sein, waehrend neue Domain-Contracts Fachpfade auf Kernniveau absichern.

## Lieferumfang

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Read-Model-Persistenz | abgeschlossen |
| AP2 | Event-Consumer-Wiring | abgeschlossen |
| AP3 | Reklamations-Aggregat | abgeschlossen |
| AP4 | Ausnahmepfade als Workflow-Extension | abgeschlossen |
| AP5 | Preisabsicherung | abgeschlossen |
| AP6 | Silo-Reinigungs- und Trocknungsprotokolle | abgeschlossen |

## Abnahmekriterien

- Snapshots sind persistent, integritaetsgeprueft und paginierbar.
- Consumer-Wiring deckt die relevanten Event-Subjects der Waves 1 bis 6 ab.
- Reklamation, Ausnahmeantrag und HedgeReference sind formal modelliert.
- GoBD-relevante Silo-Protokolle sind pruefbar.

## Tests

- `tests/test_process_kernel_wave7_read_models.py`
- `tests/test_process_kernel_wave7_domain.py`

## Status

`abgeschlossen`
Stand: 2026-03-19
