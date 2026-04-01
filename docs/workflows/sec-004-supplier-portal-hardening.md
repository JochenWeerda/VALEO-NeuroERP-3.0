# SEC-004 - Supplier-Portal SQL- und Tenant-Hardening

## Ziel

Das Supplier Portal soll keine zusammengesetzten SQL-Fragmente mehr verwenden und alle lesenden Endpunkte sauber an den Tenant-Kontext binden.

## Umsetzung

- `app/api/v1/endpoints/supplier_portal.py`
  - `lieferungen`, `kontrakte` und `preisauskunft` nutzen jetzt explizit `tenant_id = Depends(get_tenant_id)`
  - alle Queries filtern auf `tenant_id`
  - die bisherigen dynamischen WHERE-/JOIN-Fragmente wurden in parametrisierte Statements ueberfuehrt
  - die Silo-Abfrage bindet jetzt sowohl `silos` als auch `silo_lots` an denselben Tenant und laesst den Lieferantenfilter nur noch als Bound Parameter zu
- `tests/test_process_kernel_wave6_supplier.py`
  - enthaelt neue Query-Vertrags-Tests fuer Tenant-Bindung und parametrisierte Lieferantenfilter
  - setzt im Testlauf explizit den Dev-Token, damit die globale Auth-Middleware nicht in OIDC-Fallback kippt

## Ergebnis

- Supplier-Portal-Endpunkte lesen keine tenant-fremden Daten mehr ueber implizite Defaults
- die fraglichen Query-Pfade bauen keine ad-hoc-SQL-Fragmente mehr aus Request-Daten zusammen
- die Haertung ist mit API- und Unit-Tests abgesichert

## Restpunkte

- weitere SAST-Funde zu Auth-/Tenant-Isolation in anderen Routern bleiben offen
- das Supplier Portal hat weiterhin nur lesende Minimal-Views; weitergehende Rollen-/Ownership-Pruefungen sind ein separater Slice
