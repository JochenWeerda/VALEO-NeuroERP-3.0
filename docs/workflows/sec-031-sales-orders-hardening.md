# SEC-031 - Sales Orders Tenant Hardening

## Ziel

Der Sales-Orders-Router darf Tenant-Kontext nicht mehr ueber freie Query- oder Payload-Felder beziehen.

## Umsetzung

- `sales_orders.py` nutzt fuer List-, Get-, Create-, Update-, Delete- und Delivery-Note-Pfade jetzt `Depends(get_tenant_id)`.
- Payload-Tenant-Spoofing bei `create_sales_order` wird mit `403` abgewiesen.
- Item-Deletes, Re-Reads und die finale Delivery-Mutation sind tenant-gescoped.

## Abnahme

- Security-Regressionen pruefen Payload-Mismatch, tenant-gescopen Delete und tenant-gescopte Delivery-Mutation.
- bestehende Numbering-Tests bleiben gruen.

## Restrisiko

- weitere Sales-nahe Router ausserhalb Orders/Offers muessen weiterhin einzeln gegen die SAST-Liste abgeglichen werden.
