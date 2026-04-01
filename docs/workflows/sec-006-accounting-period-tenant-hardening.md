# SEC-006 - Accounting-Periods Tenant-Hardening

## Ziel

Die Periodensteuerung soll keine fremden Tenants mehr ueber Payload, Query, Pfadparameter oder ID-basierte Zugriffe lesen oder veraendern koennen.

## Umsetzung

- `app/api/v1/endpoints/accounting_periods.py`
  - `create_period` verlangt jetzt, dass `payload.tenant_id` dem aktuellen Tenant-Kontext entspricht
  - `list_periods` ignoriert keine freien Tenant-Query-Overrides mehr, sondern filtert immer auf `Depends(get_tenant_id)`
  - `get_period` und `update_period` scopen `period_id`-Zugriffe jetzt mit `tenant_id`
  - der alte Kompatibilitaetspfad `GET /check/{tenant_id}/{period}` bleibt vorhanden, lehnt aber tenant-fremde Zugriffe mit `403` ab
  - `GET /check/{period}` bleibt der sichere Kontextpfad
- `tests/test_security_accounting_periods.py`
  - deckt Tenant-Mismatch bei Create und Check ab
  - prueft tenant-gebundene Query-/ID-Statements fuer List/Get/Update

## Ergebnis

- Cross-Tenant-Lesen und -Aendern ueber `period_id` ist fuer diesen Router geschlossen
- freie Tenant-Overrides in Listen- und Check-Pfaden sind nicht mehr moeglich
- die Aenderung bleibt API-kompatibel genug, weil der alte Check-Pfad nicht entfernt, sondern nur abgesichert wurde

## Restpunkte

- andere Finance-Router mit eigener Tenant-Query-Logik muessen separat geprueft und ggf. gleich nachgezogen werden
- mittelfristig sollten tenant-sensitive Payload-Felder breiter aus REST-Schemas entfernt oder serverseitig ignoriert werden
