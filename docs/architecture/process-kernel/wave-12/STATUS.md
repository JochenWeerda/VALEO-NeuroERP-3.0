# Wave 12 — SLA-Eskalation, Settlement-Commands und Dunning-Level-Modell

## Status
- Stand: `2026-03-13`
- Status: `abgeschlossen`
- Tests: `22 gruen` (`tests/test_process_kernel_wave12_sla_commands_dunning.py`)

## Arbeitspakete

| AP | Inhalt | Endpunkt / Modul | Status |
|----|--------|------------------|--------|
| AP1 | SLA Batch-Scanner | `POST /api/v1/process/sla/scan` | abgeschlossen |
| AP2 | Eskalationsereignis erzeugen / quittieren | `POST /api/v1/process/sla/escalate` | abgeschlossen |
| AP3 | Settlement-Command-Payload und Dispatch-Result | `app/core/settlement_commands.py` | abgeschlossen |
| AP4 | Command-Dispatch-Log mit Prozessreferenzkette | `app/core/settlement_commands.py` | abgeschlossen |
| AP5 | Dunning-Level-Berechnung (`compute_dunning_level`) | `app/core/dunning_model.py` | abgeschlossen |
| AP6 | `build_dunning_level_counts` fuer MahnwesenPreview | `app/core/dunning_model.py` | abgeschlossen |

## Neue Core-Module

- `app/core/sla_escalation.py` — Batch-Scanner, Eskalationsereignis, Acknowledgement
- `app/core/settlement_commands.py` — SettlementCommandPayload, DispatchResult, CommandDispatchLog
- `app/core/dunning_model.py` — MahnwesenItem, DunningLevelRule, compute_dunning_level, build_dunning_level_counts

## Abnahme-Verifikation

```bash
pytest tests/test_process_kernel_wave12_sla_commands_dunning.py -q --no-cov
# Ergebnis: 22 passed
```
