# Wave 13 — Settlement-Contracts, Steuermodell, Compliance-Exports und Dunning-Execution

## Status
- Stand: `2026-03-13`
- Status: `abgeschlossen`
- Tests: `27 gruen` (`tests/test_process_kernel_wave13_settlement_dunning_compliance.py`)

## Arbeitspakete

| AP | Inhalt | Modul | Status |
|----|--------|-------|--------|
| AP1 | `DeductionInput` Validierungskontrakte | `app/core/agrar_settlement_models.py` | abgeschlossen |
| AP2 | `compute_contract_status` Zustandsübergänge | `app/core/agrar_contract_status.py` | abgeschlossen |
| AP3 | `TaxKeyCreate` Validatoren (code, reverse_charge, Datum) | `app/core/tax_key_models.py` | abgeschlossen |
| AP4 | `extract_hazard_export_rows` + `compute_nutrient_stream` | `app/core/compliance_exports.py` | abgeschlossen |
| AP5 | `DunningRun` Execution Model | `app/core/dunning_run.py` | abgeschlossen |
| AP6 | Mahnlauf Eskalation + Gebühren | `app/core/dunning_run.py` | abgeschlossen |

## Neues Core-Modul

- `app/core/dunning_run.py` — `DunningRunItem`, `DunningRunResult`, `execute_dunning_run()`

## Abnahme-Verifikation

```bash
pytest tests/test_process_kernel_wave13_settlement_dunning_compliance.py -q --no-cov
# Ergebnis: 27 passed
```
