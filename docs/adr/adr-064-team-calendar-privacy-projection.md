---
title: ADR-064 Teamkalender als datenschutzbewusste Projektion
type: adr
audience: [architektur, entwickler, product, qa]
owner: platform
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-064 Teamkalender als datenschutzbewusste Projektion

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

Der native Planungskalender aggregierte Fristen und Prozesse, belegte aber
weder Teamzugehoerigkeit noch Frei/Belegt oder Datenschutz fuer fremde Termine.

## Entscheidung

- Die bestehende `calendar_items`-Projektion erhaelt Owner, Team,
  Sichtbarkeit und Antwortstatus; ein zweiter Kalender wird nicht eingefuehrt.
- Teamfilter werden gegen aktive tenantgebundene Mitgliedschaften geprueft.
- Private und `free_busy`-Fremdtermine werden immer auf `Belegt` reduziert;
  Objektbezug, Route und Payload werden entfernt. Teamdetails brauchen eine
  eigene Berechtigung.
- Abgelehnte Termine bleiben gespeichert und werden nur bei ausdruecklichem
  `include_declined` angezeigt.

## Konsequenzen

`L3-GAP-TEAMCAL-009` ist repo-seitig geschlossen. Produktive IAM-Team-
Synchronisation und Datenschutz-UAT bleiben externe Rollout-Gates.
