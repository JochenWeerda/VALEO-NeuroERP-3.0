# SEC-020 - Nebenbuch-Abstimmung Hardening

## Ziel

Alle Reconciliation-, Detail-, Export- und Summary-Pfade sollen den Tenant nur noch aus dem Request-Kontext beziehen.

## Scope

- `app/api/v1/endpoints/subsidiary_ledger_reconciliation.py`
- `tests/test_security_subsidiary_ledger_reconciliation.py`

## Umsetzung

- `AR/AP/BANK`, Drilldown, CSV-Export und Summary nutzen `Depends(get_tenant_id)`
- freie Query-Tenants sind entfernt
- direkte Regressionstests pruefen die tenant-gebundenen SQL-Parameter

## Verifikation

- `pytest tests/test_security_subsidiary_ledger_reconciliation.py -q --no-cov`
- `python -m py_compile app/api/v1/endpoints/subsidiary_ledger_reconciliation.py tests/test_security_subsidiary_ledger_reconciliation.py`
