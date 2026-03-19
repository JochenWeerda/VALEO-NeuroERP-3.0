# Wave 13 - Settlement-Contracts, Steuermodell, Compliance-Exports und Dunning-Execution

**Status:** abgeschlossen
**Datum:** 2026-03-13

## Scope

Wave 13 liefert Settlement-Validierung, Steuerschluessel-Modelle, Compliance-Exports und Dunning-Execution als zusammenhaengende Kernvertraege.

## Zielbild

Settlement-, Tax-, Compliance- und Dunning-Pfade sollen ueber gemeinsame Kernmodelle validierbar und ausfuehrbar sein.

## Lieferumfang

| AP | Inhalt | Modul | Status |
|----|--------|-------|--------|
| AP1 | `DeductionInput`-Validierung | `app/core/agrar_settlement_models.py` | abgeschlossen |
| AP2 | `compute_contract_status`-Uebergaenge | `app/core/agrar_contract_status.py` | abgeschlossen |
| AP3 | `TaxKeyCreate`-Validatoren | `app/core/tax_key_models.py` | abgeschlossen |
| AP4 | Compliance-Export-Builder | `app/core/compliance_exports.py` | abgeschlossen |
| AP5 | `DunningRun` Execution Model | `app/core/dunning_run.py` | abgeschlossen |
| AP6 | Mahnlauf-Eskalation und Gebuehren | `app/core/dunning_run.py` | abgeschlossen |

## Abnahmekriterien

- Settlement- und Tax-Validierungen sind reproduzierbar.
- Compliance-Exports liefern strukturierte Zeilen und Naehrstoffstroeme.
- Dunning-Execution und Eskalationen sind als Core-Contracts verfuegbar.

## Tests

- `pytest tests/test_process_kernel_wave13_settlement_dunning_compliance.py -q --no-cov`
- Ergebnis: 27 passed

## Status

`abgeschlossen`
Stand: 2026-03-13
