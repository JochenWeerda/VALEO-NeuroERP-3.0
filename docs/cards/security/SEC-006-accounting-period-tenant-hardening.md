# SEC-006 - Accounting Periods haerten

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_accounting_periods.py

## Ziel

Tenant-Isolation im Perioden-Router durchziehen, ohne den kompletten Finance-Stack anzufassen.

## Scope

- `app/api/v1/endpoints/accounting_periods.py`
- `tests/test_security_accounting_periods.py`
- `docs/workflows/sec-006-accounting-period-tenant-hardening.md`

## Abnahme

- Create/List/Get/Update nutzen den aktuellen Tenant-Kontext statt frei uebersteuerbarer Tenant-Parameter
- der Kompatibilitaetspfad `/check/{tenant_id}/{period}` akzeptiert keine fremden Tenants mehr
- Regressionstests sind gruen

## Risiken

- andere Finance-Router koennen aehnliche freie Tenant-Parameter weiterhin haben
- Payload-Feld `tenant_id` in `PeriodCreate` bleibt aus Kompatibilitaetsgruenden noch sichtbar und wird nur serverseitig validiert
