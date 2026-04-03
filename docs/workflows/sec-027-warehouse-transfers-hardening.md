# SEC-027 - Warehouse Transfers Tenant Hardening

## Ziel

Transfer-, Transfer-Line-, Correction- und Bin-Location-Pfade duerfen keine freien Query-Tenants oder tenant-ungebundene ID-Lookups mehr nutzen.

## Umsetzung

- `warehouse_transfers.py` nutzt durchgaengig `Depends(get_tenant_id)`.
- Neue Helper `_get_transfer_or_404`, `_get_transfer_line_or_404`, `_get_correction_or_404` und `_get_correction_line_or_404` scope'n ID-Zugriffe tenant-gebunden.
- Line-, Post-, Delete- und Correction-Pfade validieren zuerst den Parent im Kontext-Tenant.

## Abnahme

- Security-Regressionen pruefen Kontext-Tenant auf Listen-, Line- und Create-Pfaden
- `py_compile` fuer den Router gruen

## Restrisiko

- weitere Lager-/Bewegungsrouter ausserhalb dieses Transfer-Blocks muessen weiter sliceweise gehaertet werden
