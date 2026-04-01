# SEC-024 - Sales Reports Hardening

## Ziel

Sales-Reports und Pipeline-KPIs sollen den Tenant nur noch aus dem Request-Kontext beziehen.

## Scope

- `app/api/v1/endpoints/sales_reports.py`
- `tests/test_security_sales_reports.py`

## Umsetzung

- Summary-, Top-Customer-, Top-Article-, Monthly-Revenue- und Pipeline-Endpunkte nutzen `Depends(get_tenant_id)`
- freie Query-Tenants sind entfernt
- Regressionstests pruefen die tenant-gebundenen Query-Parameter

## Verifikation

- `pytest tests/test_security_sales_reports.py -q --no-cov`
- `python -m py_compile app/api/v1/endpoints/sales_reports.py tests/test_security_sales_reports.py`
