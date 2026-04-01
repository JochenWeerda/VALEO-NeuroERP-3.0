# SEC-022

## Titel

Tenant-Isolation fuer VAT Return Export

## Problem

Der VAT-Return-Router akzeptierte freie `tenant_id`-Querys und im Calculate-Pfad sogar einen Body-Tenant.

## Loesung

- Umstellung auf kontextgebundenen Tenant
- Body-Tenant-Mismatch im Calculate-Pfad fuehrt zu `403`
- direkte Regressionstests fuer Get/List und Payload-Spoofing
