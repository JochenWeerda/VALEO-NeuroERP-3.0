# SEC-029 - Agrar Contracts Tenant Hardening

## Ziel

Der Agrar-Contract-Router darf Tenant-Kontext nicht mehr ueber freie Query-Parameter oder ungescopte ID-Lookups beziehen.

## Umsetzung

- `agrar_contracts.py` nutzt fuer Listen-, Create-, Get-, Update- und Allocation-Pfade jetzt `Depends(get_tenant_id)`.
- neue Helper-Funktion `_get_contract_or_404(..., tenant_id)` scope't Contract-Lookups tenant-gebunden.
- Allocation-Listen sind ebenfalls tenant-gebunden gefiltert.

## Abnahme

- Security-Regressionen pruefen List-, Helper- und Allocation-Filter
- `py_compile` fuer Router und Tests gruen

## Restrisiko

- weitere Agrar-Router mit historischem Query-Tenant-Muster muessen separat geschnitten werden
