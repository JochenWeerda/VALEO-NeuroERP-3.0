# SEC-020

## Titel

Tenant-Isolation fuer Nebenbuch-Abstimmung

## Problem

Die Reconciliation-Router nahmen freie `tenant_id`-Query-Parameter an und waren damit fuer Cross-Tenant-Abfragen offen.

## Loesung

- Umstellung aller Endpunkte auf kontextgebundenen Tenant
- Regressionstests fuer AR- und Detailpfade
