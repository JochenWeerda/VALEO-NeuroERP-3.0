# SEC-007 - Creditors Tenant Hardening

## Ziel

Den Kreditoren-Router auf denselben Tenant-Isolationsstandard ziehen wie die bereits gehaerteten Finance-Slices.

## Umfang

- `POST /creditors`: Kontext-Tenant erzwingen, Payload-Tenant nicht vertrauen
- `GET /creditors`: keine freie Tenant-Query mehr
- `GET /creditors/{id}`: Lookup tenant-gescoped
- `PUT /creditors/{id}`: bestehende Daten, Update und Readback tenant-gescoped
- `GET /creditors/{id}/balance`: Balance nur fuer tenant-eigenen Kreditor
- `DELETE /creditors/{id}`: Soft-Delete nur tenant-gescoped

## Umsetzung

- `get_tenant_id` wird in allen relevanten Endpunkten als Pflichtkontext verwendet.
- `create_creditor()` lehnt Tenant-Mismatch mit `403 Tenant mismatch` ab.
- Query-, Update- und Lookup-SQL schliesst `tenant_id` jetzt in die ID-basierten Zugriffe ein.
- Die Balance-Pruefung verlaesst sich nicht mehr auf globale Kreditor-IDs.

## Tests

- `tests/test_security_creditors.py`
- direkte Async-Regressionen fuer Create/List/Get/Update/Balance/Delete

## Restpunkte

- weitere P1-SAST-Funde ausserhalb des `creditors.py`-Dateibesitzes bleiben separat
