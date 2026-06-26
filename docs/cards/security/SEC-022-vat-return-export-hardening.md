# SEC-022

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_vat_return_export.py

## Titel

Tenant-Isolation fuer VAT Return Export

## Problem

Der VAT-Return-Router akzeptierte freie `tenant_id`-Querys und im Calculate-Pfad sogar einen Body-Tenant.

## Loesung

- Umstellung auf kontextgebundenen Tenant
- Body-Tenant-Mismatch im Calculate-Pfad fuehrt zu `403`
- direkte Regressionstests fuer Get/List und Payload-Spoofing
