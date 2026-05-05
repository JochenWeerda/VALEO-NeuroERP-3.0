# Critical Backend Coverage Plan

Stand: `2026-05-05`

## Aktueller Befund

Das kritische Coverage-Ratchet ist sinnvoll, aber mehrere Altpfade liegen noch unter Schwelle.
Ein kleiner Testlauf erzeugt ausserdem ein unvollstaendiges `coverage.xml`; das Ratchet muss daher mit der passenden Sammelsuite bewertet werden.

Letzter Sammellauf (Stand 2026-05-05):

```bash
pytest tests/test_tenant_enforcement.py tests/test_secrets_vault.py tests/test_event_bus_runtime.py \
  tests/test_process_kernel_wave2_events.py tests/test_integration_bootstrap.py \
  tests/test_finance_actions.py tests/test_finance_followup_api.py tests/test_fibu_connectors_api.py \
  tests/test_dunning_api.py tests/test_finance_payment_runs_api.py tests/test_finance_exchange_rates_api.py \
  tests/test_finance_read_models_api.py tests/test_process_kernel_wave1_contracts.py \
  tests/test_inventory_operations.py tests/test_inventory_counts.py \
  tests/test_waage_api.py tests/test_warehouses_api.py tests/test_warehouse_transfers_api.py \
  tests/test_l3c_smoke.py -q
```

## Fortschritt

| Pfad | Status | Commit |
|---|---|---|
| `payment_runs.py` | ✅ robuste amount-Extraktion | `fix(payment) 2fd4d46` |
| `finance_read_models.py` | ✅ 58 Unit-Tests Projektionfunktionen | `test(finance-read-models) 338e39f` |
| `dunning.py` | ✅ 23 API-Tests Mahnwesen | `test(dunning) f7c75e4` |
| `waage.py` | ✅ Unit-Tests mit Repo-Mocks | `test(cov-inv-002) 6bee78a` |
| `warehouses.py` | ✅ Pagination + Superglue-Unit-Tests | `test(cov-inv-002) 6bee78a` |
| `warehouse_transfers.py` | ✅ Schema + 404-Pfade Unit-Tests | `test(cov-inv-002) 6bee78a` |
| `booking_templates.py` | 🔴 29.8% < 40% | naechster Schritt |
| `chart_of_accounts.py` | 🔴 30.4% < 50% | naechster Schritt |
| `inventory_counts.py` | 🔴 43.6% < 50% | P1 |
| `inventory_operations.py` | 🔴 48.1% < 50% | P1 |
| `exchange_rates.py` | 🔴 33.3% < 50% | P1 |
| `finance_actions.py` | 🔴 36.5% < 90% | P2 |
| `finance_followup.py` | 🔴 14.6% < 70% | P2 |
| `fibu_connectors.py` | 🔴 27.7% < 80% | P2 |
| `secrets_vault.py` | 🔴 28.6% < 49% | P2 |
| `tenant_enforcement.py` | 🔴 0% < 90% | P2 |
| `domains/shared/events.py` | 🔴 40.5% < 65% | P2 |
| `integration_bootstrap.py` | 🔴 nicht in coverage.xml | P3 |

## Naechste Reihenfolge

| Prioritaet | Pfad | Ziel |
|---|---|---|
| P0 | `booking_templates.py` | Setup, Liste, Anwenden, Fehlerpfade auf 40 Prozent |
| P0 | `chart_of_accounts.py` | Konto-CRUD, Saldoabfrage, Suche auf 50 Prozent |
| P1 | `inventory_counts.py` / `inventory_operations.py` | Inventur-Positionen, Buchung, 404s auf Schwelle |
| P1 | `exchange_rates.py` | CRUD + Konvertierung auf 50 Prozent |
| P2 | `finance_actions.py` / `finance_followup.py` / `fibu_connectors.py` | bestehende Tests ausbauen |
| P2 | `secrets_vault.py` | Provider- und Fehlerpfade bis mindestens 49 Prozent |

## Bewertungsregel

Coverage-Gates gelten nur gegen ein Coverage-Artefakt aus der Sammelsuite der kritischen Pfade.
Gezielte Einzeltests bleiben fuer schnelle Regressionen zulaessig, duerfen aber nicht als Gesamt-Ratchet interpretiert werden.
