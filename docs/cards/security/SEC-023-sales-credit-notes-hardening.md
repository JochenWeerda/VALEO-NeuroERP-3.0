# SEC-023

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_sales_credit_notes.py, docs/roadmap/status/2026-04-01-security-hardening-phase-1.md

## Titel

Tenant-Isolation fuer Sales Credit Notes / Returns

## Problem

Der Router vertraute freien Query-Tenants, Payload-Tenant-Overrides und ungescopten ID-Pfaden bei Buchung und Retourenstatus.

## Loesung

- Kontext-Tenant statt Query-/Payload-Tenant
- `403` bei Payload-Tenant-Spoofing
- tenant-gescopte ID-Updates fuer Post und Return-Status
