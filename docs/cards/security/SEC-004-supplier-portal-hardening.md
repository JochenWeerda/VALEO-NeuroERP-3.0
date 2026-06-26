# SEC-004 - Supplier Portal haerten

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_process_kernel_wave6_supplier.py

## Ziel

SQL-/Tenant-Risiken im Supplier Portal mit kleinem Backend-Slice schliessen.

## Scope

- `app/api/v1/endpoints/supplier_portal.py`
- `tests/test_process_kernel_wave6_supplier.py`
- `docs/workflows/sec-004-supplier-portal-hardening.md`

## Abnahme

- alle Supplier-Portal-Endpunkte sind tenant-gebunden
- Lieferanten- und Datumsfilter laufen nur noch ueber Bound Parameters
- Query-Vertrags-Tests decken die Haertung ab

## Risiken

- andere fachliche Read-Model-Router koennen aehnliche Query-Muster behalten
- feinere Rollen-/Ownership-Pruefungen fuer Lieferantenzugriffe sind noch nicht Teil dieses Slices
