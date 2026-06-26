# SEC-024

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_sales_reports.py

## Titel

Tenant-Isolation fuer Sales Reports

## Problem

Sales-Reporting und Pipeline-KPIs akzeptierten freie `tenant_id`-Query-Parameter.

## Loesung

- Umstellung aller Report-Endpunkte auf kontextgebundenen Tenant
- Regressionstests fuer Summary-, Top-Customer- und Pipeline-Pfad
