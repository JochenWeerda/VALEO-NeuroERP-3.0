# SEC-032 - Sales Offers Tenant Hardening

## Ziel

Der Sales-Offers-Router darf Tenant-Kontext nicht mehr ueber freie Query- oder Payload-Felder beziehen.

## Umsetzung

- `sales_offers.py` nutzt fuer List-, Get-, Create-, Update-, Delete- und Convert-Pfade jetzt `Depends(get_tenant_id)`.
- Payload-Tenant-Spoofing bei `create_sales_offer` wird mit `403` abgewiesen.
- Item-Reset, Total-Update, Soft-Delete, Convert-Status-Update und Re-Reads sind tenant-gescoped.

## Abnahme

- Security-Regressionen pruefen Payload-Mismatch, tenant-gescopten Item-Reset/Total-Update und tenant-gescopte Convert-Mutation.

## Restrisiko

- weitere Sales-/CRM-Router mit historischen Query-Tenant-Mustern muessen weiterhin routerweise geschnitten werden.
