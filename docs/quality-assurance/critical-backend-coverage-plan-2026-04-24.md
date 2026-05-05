# Critical Backend Coverage Plan

Stand: `2026-05-05`

## Aktueller Befund

Das kritische Coverage-Ratchet ist nach dem Sammellauf vom 2026-05-05 gruen.
Ein kleiner Testlauf erzeugt nur ein unvollstaendiges `coverage.xml`; das Ratchet muss daher mit der passenden Sammelsuite bewertet werden.

Letzter Sammellauf:

```bash
pytest tests/test_tenant_enforcement.py tests/test_secrets_vault.py tests/test_event_bus_runtime.py \
  tests/test_process_kernel_wave2_events.py tests/test_integration_bootstrap.py \
  tests/test_finance_actions.py tests/test_finance_followup_api.py tests/test_fibu_connectors_api.py \
  tests/test_dunning_api.py tests/test_finance_payment_runs_api.py tests/test_finance_exchange_rates_api.py \
  tests/test_finance_read_models_api.py tests/test_process_kernel_wave1_contracts.py \
  tests/test_inventory_operations.py tests/test_inventory_counts.py \
  tests/test_waage_api.py tests/test_warehouses_api.py tests/test_warehouse_transfers_api.py \
  tests/test_booking_templates_api.py tests/test_chart_of_accounts_api.py \
  tests/test_l3c_smoke.py -q
# Ergebnis: 411 passed

python scripts/check_critical_backend_coverage.py
# Ergebnis: Critical backend coverage OK.
```

## Fortschritt

| Pfad | Status | Nachweis |
|---|---|---|
| `tenant_enforcement.py` | gruen, 100.0% >= 90% | `tests/test_tenant_enforcement.py` |
| `secrets_vault.py` | gruen, 50.4% >= 49% | `tests/test_secrets_vault.py` |
| `domains/shared/events.py` | gruen, 68.4% >= 65% | `tests/test_event_bus_runtime.py`, `tests/test_process_kernel_wave2_events.py` |
| `integration_bootstrap.py` | gruen, 94.6% >= 90% | `tests/test_integration_bootstrap.py` |
| `finance_actions.py` | gruen, 91.0% >= 90% | `tests/test_finance_actions.py` |
| `finance_followup.py` | gruen, 73.4% >= 70% | `tests/test_finance_followup_api.py` |
| `fibu_connectors.py` | gruen, 81.0% >= 80% | `tests/test_fibu_connectors_api.py` |
| `dunning.py` | gruen, 87.5% >= 50% | `tests/test_dunning_api.py` |
| `payment_runs.py` | gruen, 86.7% >= 30% | `tests/test_finance_payment_runs_api.py`, `tests/test_process_kernel_wave1_contracts.py` |
| `exchange_rates.py` | gruen, 79.6% >= 50% | `tests/test_finance_exchange_rates_api.py` |
| `booking_templates.py` | gruen, 63.6% >= 40% | `tests/test_booking_templates_api.py` |
| `chart_of_accounts.py` | gruen, 65.2% >= 50% | `tests/test_chart_of_accounts_api.py` |
| `finance_read_models.py` | gruen, 89.5% >= 60% | `tests/test_finance_read_models_api.py` |
| `waage.py` | gruen, 91.1% >= 75% | `tests/test_waage_api.py` |
| `warehouses.py` | gruen, 97.1% >= 90% | `tests/test_warehouses_api.py` |
| `warehouse_transfers.py` | gruen, 67.8% >= 60% | `tests/test_warehouse_transfers_api.py` |
| `inventory_counts.py` | gruen, 59.9% >= 50% | `tests/test_inventory_counts.py` |
| `inventory_operations.py` | gruen, 55.7% >= 50% | `tests/test_inventory_operations.py` |

## Naechste Reihenfolge

| Prioritaet | Pfad | Ziel |
|---|---|---|
| P0 | Ratchet-Schwellen reviewen | Schwellwerte fuer sehr gut abgedeckte Pfade kontrolliert anheben, ohne Test-Noise zu erzeugen |
| P1 | Weitere produktkritische Pfade aufnehmen | z. B. Security-Observability, Outbound-Gates, DMS-Fehlerpfade |
| P1 | Integrations-Governance vertiefen | `COV-INT-002` mit Superglue-, Secrets-, Bootstrap- und Tenant-Schutz-Fokus fortsetzen |
| P2 | Browser-/CRUD-Abnahme koppeln | Backend-Ratchet mit P0/P1-Flow-Spine-Playwright-Matrix verbinden |

## Bewertungsregel

Coverage-Gates gelten nur gegen ein Coverage-Artefakt aus der Sammelsuite der kritischen Pfade.
Gezielte Einzeltests bleiben fuer schnelle Regressionen zulaessig, duerfen aber nicht als Gesamt-Ratchet interpretiert werden.
