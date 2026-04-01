# SEC-021 - Tax Keys Hardening

## Ziel

Tax-Key-CRUD und Code-Lookup sollen keine freien Query-Tenants mehr akzeptieren.

## Scope

- `app/api/v1/endpoints/tax_keys.py`
- `tests/test_security_tax_keys.py`

## Umsetzung

- `list/get/create/update/delete/code-lookup` nutzen `Depends(get_tenant_id)`
- freie Query-Tenants sind entfernt
- Regressionstests decken Listen-, Create- und ID-Lookup-Pfad ab

## Verifikation

- `pytest tests/test_security_tax_keys.py -q --no-cov`
- `python -m py_compile app/api/v1/endpoints/tax_keys.py tests/test_security_tax_keys.py`
