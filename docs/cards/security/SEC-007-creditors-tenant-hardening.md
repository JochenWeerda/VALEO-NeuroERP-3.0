# SEC-007 - Creditors Tenant Hardening

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** `tests/test_security_creditors.py`

## Problem

Der Kreditoren-Router vertraute bisher freien Tenant-Eingaben und scopt ID-basierte Zugriffe nicht konsistent auf den aktuellen Tenant.

## Lieferung

- Kontext-Tenant wird in allen sicherheitsrelevanten Creditor-Endpunkten erzwungen
- `Tenant mismatch` fuer abweichende Create-Payloads
- tenant-gescopte Lookups fuer Read, Update, Balance und Delete
- direkte Security-Regressionstests

## Dateien

- `app/api/v1/endpoints/creditors.py`
- `tests/test_security_creditors.py`
- `docs/workflows/sec-007-creditors-tenant-hardening.md`
- `docs/project-context/open-gaps-and-known-issues.md`
- `docs/agent-ops/active-workboard.md`
