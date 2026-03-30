# NC-A11 - Cross-Entity Integrity

**Lane:** NC-A / NC-B Schnittstelle
**Prioritaet:** P2
**Status:** umgesetzt
**Abhaengigkeit:** NC-B1, NC-A8, NC-A10

## Kontext

Nach NC-A8 und NC-A10 blieb die tiefere Cross-Entity-Integrity offen. Einzelne Transitionen wurden geprueft, aber relationale Inkonsistenzen zwischen Bestellung, Lieferschein, Rechnung, Freigabe oder Gutschrift wurden noch nicht als Snapshot-Vertrag ausgewertet.

## Umsetzung

- `StateGraphService` liefert Snapshot-Pruefung fuer `ERZEUGT`, `REFERENZIERT`, `BLOCKIERT`, `FOLGT_AUF`, `ENTHAELT`
- `check_cross_entity_integrity()` wertet `state_graph_snapshot` in der Verification Engine aus
- `verify_plan()` propagiert Snapshot-Violations auf Plan- und Step-Level
- `latest_confidence()` in `confidence_ledger.py` wurde auf append-only-Ordnung stabilisiert, damit die Lane-B-Suite deterministisch bleibt

## Dateien

- `app/core/neuro_state_graph.py`
- `app/core/confidence_ledger.py`
- `app/services/neuro_verification_engine.py`
- `tests/test_neuro_state_graph.py`
- `tests/test_neuro_verification_engine.py`

## Verifikation

- `pytest tests/test_neuro_state_graph.py tests/test_neuro_verification_engine.py -q --no-cov`
- `python -m py_compile app/core/confidence_ledger.py app/core/neuro_state_graph.py app/services/neuro_verification_engine.py`
