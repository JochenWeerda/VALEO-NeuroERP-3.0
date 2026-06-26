# Finance Closing Compatibility 2026-06-26

## Zweck

Der Periodenabschluss nutzt primaer den aktuellen `FinanceClosingService` mit
`public.finance_accounting_periods`. Fuer Bestandsinstallationen bleibt ein
enger Legacy-Fallback auf `domain_erp.accounting_periods` aktiv, damit
`calculate`, `lock` und `run` nicht wegen eines noch nicht migrierten
Periodenmodells mit HTTP 500 abbrechen.

## Fachlicher Vertrag

- `POST /finance/closing/calculate` ist ein Read-only-Pruefschritt. Wenn eine
  Periode nicht berechenbar ist, liefert der Endpoint ein leeres Ergebnis mit
  `entry_count = 0` statt einen technischen 500er.
- `POST /finance/closing/lock` sperrt zuerst ueber den modernen
  Periodenservice. Nur bei technischer Inkompatibilitaet wird die alte
  Periodentabelle aktualisiert.
- `POST /finance/closing/run` berechnet, erzeugt wenn moeglich einen
  Abschlussbeleg und sperrt anschliessend die Periode. Der Legacy-Fallback
  dient ausschliesslich der Periodensperre, nicht der Umdeutung fachlicher
  Validierungsfehler.

## Wartungsregel

Der Legacy-Pfad darf entfernt werden, wenn alle unterstuetzten Installationen
die Migration auf `public.finance_accounting_periods` nachweislich ausgefuehrt
haben und ein Upgrade-Test die Entfernung abdeckt.

## Verifikation

- `pytest -q -o addopts= tests/test_finance_actions.py::test_closing_calculate_lock_run_and_approve_paths -vv`
- `pytest -q -o addopts= tests/test_production_readiness_contract.py::test_simulated_assessors_require_repository_evidence_and_keep_external_gates tests/test_production_readiness_contract.py::test_dependency_maintenance_policy_covers_forced_major_updates -vv`
