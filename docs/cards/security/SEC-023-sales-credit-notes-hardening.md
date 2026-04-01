# SEC-023

## Titel

Tenant-Isolation fuer Sales Credit Notes / Returns

## Problem

Der Router vertraute freien Query-Tenants, Payload-Tenant-Overrides und ungescopten ID-Pfaden bei Buchung und Retourenstatus.

## Loesung

- Kontext-Tenant statt Query-/Payload-Tenant
- `403` bei Payload-Tenant-Spoofing
- tenant-gescopte ID-Updates fuer Post und Return-Status
