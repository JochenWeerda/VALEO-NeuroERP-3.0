# SEC-015 - Accruals/Provisions Tenant Hardening

## Ziel

Den Accruals-/Provisions-Router auf denselben Tenant-Isolationsstandard ziehen wie die bereits gehaerteten Finance-Endpunkte.

## Umsetzung

- `tenant_id` wird nicht mehr frei per Query akzeptiert, sondern via `Depends(get_tenant_id)` gezogen
- Listen- und Create-Pfade verwenden den Kontext-Tenant
- der Post-/Journal-Pfad scoped Readback und Status-Update tenant-gebunden

## Tests

- `tests/test_security_accruals_provisions.py`
