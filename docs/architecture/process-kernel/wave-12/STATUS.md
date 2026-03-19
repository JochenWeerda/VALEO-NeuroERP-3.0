# Wave 12 - SLA-Eskalation, Settlement-Commands und Dunning-Level-Modell

**Status:** abgeschlossen
**Datum:** 2026-03-13

## Scope

Wave 12 fuehrt SLA-Scanner, Eskalationsereignisse, Settlement-Command-Payloads und ein Dunning-Level-Modell als gemeinsame Core-Vertraege ein.

## Zielbild

SLA-Scans, Eskalationen, Settlement-Dispatch und Mahnstufen sollen auf expliziten, testbaren Kernmodellen beruhen.

## Lieferumfang

| AP | Inhalt | Modul oder Endpunkt | Status |
|----|--------|---------------------|--------|
| AP1 | SLA Batch-Scanner | `POST /api/v1/process/sla/scan` | abgeschlossen |
| AP2 | Eskalationsereignis erzeugen und quittieren | `POST /api/v1/process/sla/escalate` | abgeschlossen |
| AP3 | Settlement-Command-Payload und Dispatch-Result | `app/core/settlement_commands.py` | abgeschlossen |
| AP4 | Command-Dispatch-Log mit Prozessreferenzkette | `app/core/settlement_commands.py` | abgeschlossen |
| AP5 | Dunning-Level-Berechnung | `app/core/dunning_model.py` | abgeschlossen |
| AP6 | Dunning-Level-Counts fuer MahnwesenPreview | `app/core/dunning_model.py` | abgeschlossen |

## Abnahmekriterien

- SLA-Scans und Eskalationsereignisse sind als Core-Contracts verfuegbar.
- Settlement-Command-Payloads und Dispatch-Logs sind definiert.
- Mahnstufen koennen deterministisch berechnet und aggregiert werden.

## Tests

- `pytest tests/test_process_kernel_wave12_sla_commands_dunning.py -q --no-cov`
- Ergebnis: 22 passed

## Status

`abgeschlossen`
Stand: 2026-03-13
