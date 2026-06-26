# SEC-021

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_tax_keys.py

## Titel

Tenant-Isolation fuer Tax Keys

## Problem

Tax-Key-Endpunkte nahmen freie `tenant_id`-Query-Parameter an und konnten damit tenantfremde Stammdaten lesen oder veraendern.

## Loesung

- Umstellung auf kontextgebundenen Tenant fuer CRUD und Code-Lookup
- direkte Regressionstests fuer die tenant-gebundenen SQL-Pfade
