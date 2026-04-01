# SEC-024

## Titel

Tenant-Isolation fuer Sales Reports

## Problem

Sales-Reporting und Pipeline-KPIs akzeptierten freie `tenant_id`-Query-Parameter.

## Loesung

- Umstellung aller Report-Endpunkte auf kontextgebundenen Tenant
- Regressionstests fuer Summary-, Top-Customer- und Pipeline-Pfad
