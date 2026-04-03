# SEC-025 - Sales Delivery Notes Tenant Hardening

## Ziel

Sales-Delivery-Note-Endpunkte duerfen Tenant-Kontext nicht mehr aus freien Query-Parametern beziehen.

## Umsetzung

- `sales_delivery_notes.py` nutzt fuer Create, Read, Update, Delete, Post, Print, List, Last und `create-invoice` jetzt `Depends(get_tenant_id)`.
- Alle ID-basierten Lookup-Pfade laufen ueber `_get_delivery_note_or_404(..., tenant_id)`.
- Die finale Statusmutation in `create_invoice_from_delivery` scoped das `UPDATE` jetzt ebenfalls mit `tenant_id`.

## Abnahme

- direkte Security-Regressionen decken Listen- und Invoice-Pfad ab
- `py_compile` fuer den Router gruen

## Restrisiko

- weitere Sales-Router ausserhalb Delivery Notes muessen weiterhin sliceweise geprueft werden
