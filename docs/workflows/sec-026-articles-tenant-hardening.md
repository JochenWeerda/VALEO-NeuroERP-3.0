# SEC-026 - Articles API Tenant Hardening

## Ziel

Die Artikel-API darf weder Payload-Tenants vertrauen noch tenant-fremde Nebenpfade fuer Dokumente, Preise, Supplier, Stock oder Image-Enrichment erlauben.

## Umsetzung

- `articles.py` validiert Payload-Tenants explizit ueber `_resolve_article_tenant`.
- Alle Haupt- und Nebenpfade laufen ueber `Depends(get_tenant_id)`.
- Artikel-Nebenpfade validieren zuerst den Parent-Artikel tenant-gebunden und filtern Folgeabfragen ebenfalls auf denselben Tenant.

## Abnahme

- Security-Regressionen pruefen Payload-Mismatch und tenant-gebundene Dokumentpfade
- `py_compile` fuer den Router gruen

## Restrisiko

- weitere Inventory-/Masterdata-Endpunkte ausserhalb `articles.py` bleiben separat zu inventarisieren
