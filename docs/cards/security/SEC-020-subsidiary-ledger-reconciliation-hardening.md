# SEC-020

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_subsidiary_ledger_reconciliation.py

## Titel

Tenant-Isolation fuer Nebenbuch-Abstimmung

## Problem

Die Reconciliation-Router nahmen freie `tenant_id`-Query-Parameter an und waren damit fuer Cross-Tenant-Abfragen offen.

## Loesung

- Umstellung aller Endpunkte auf kontextgebundenen Tenant
- Regressionstests fuer AR- und Detailpfade
