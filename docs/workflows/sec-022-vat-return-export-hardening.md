# SEC-022 - VAT Return Export Hardening

## Ziel

Der VAT-Return-Router soll keine freien Query- oder Body-Tenants mehr akzeptieren.

## Scope

- `app/api/v1/endpoints/vat_return_export.py`
- `tests/test_security_vat_return_export.py`

## Umsetzung

- alle VAT-Return-Endpunkte nutzen `Depends(get_tenant_id)`
- der Calculate-Pfad lehnt tenantfremde Body-Tenants mit `403` ab
- Get/List/Validate/Approve/Submit/Export sind tenant-gebunden

## Verifikation

- `pytest tests/test_security_vat_return_export.py -q --no-cov`
- `python -m py_compile app/api/v1/endpoints/vat_return_export.py tests/test_security_vat_return_export.py`
