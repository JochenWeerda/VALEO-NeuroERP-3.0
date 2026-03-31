# NC-A12 - Risk Scoring

**Lane:** NC-A / NC-B Schnittstelle
**Prioritaet:** P2
**Status:** umgesetzt
**Abhaengigkeit:** NC-B1, NC-A11

## Kontext

Nach NC-A11 fehlte in Wave 4 noch ein verdichteter Risikoindikator aus dem Confidence Ledger. Vorhanden waren nur Basisstatistiken wie `avg_confidence` und `max_risk`; ein direkt surfacbarer Composite-Score fuer API und UI fehlte.

## Umsetzung

- `ConfidenceLedgerService.risk_score()` berechnet einen konservativen Composite-Score von `0.0` bis `100.0`
- `risk_summary()` wurde um `risk_score`, `latest_confidence`, `latest_risk` und `risk_distribution` erweitert
- Der Summary-Endpoint `/api/v1/neuro/confidence-ledger/summary` surfact die erweiterten Felder ohne Breaking Change
- Tests decken leere Summaries, Verteilungen und Eskalation zwischen Low-/High-Risk-Konstellationen ab

## Dateien

- `app/core/confidence_ledger.py`
- `app/api/v1/endpoints/neuro_state_graph_api.py`
- `tests/test_neuro_state_graph.py`

## Verifikation

- `pytest tests/test_neuro_state_graph.py -q --no-cov`
- `python -m py_compile app/core/confidence_ledger.py app/api/v1/endpoints/neuro_state_graph_api.py`
