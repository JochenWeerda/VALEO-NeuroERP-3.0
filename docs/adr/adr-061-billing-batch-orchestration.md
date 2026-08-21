---
title: ADR-061 Rechnungstapel als Orchestrierung kanonischer Belege
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/finance
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-061 Rechnungstapel als Orchestrierung kanonischer Belege

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

Faktura, AP/AR, Rohware-Sammelabrechnung und Self-Billing inklusive PDF/GoBD
existieren, aber nicht als gemeinsamer L3-vertrauter Stapelarbeitsplatz.

## Entscheidung

- Stapel referenzieren unveraenderliche kanonische Quellbelege und berechnen
  Rechnungen nicht erneut.
- Vier Typen werden unterstuetzt: Ausgang, Eingang, Selbstabrechner Verkauf und
  Selbstabrechner Kunden-Zukauf.
- Pruefung, Vier-Augen-Freigabe und Ausfuehrung besitzen einen geschlossenen,
  append-only auditierten Lifecycle.
- Zeilen sind ueber Tenant und Idempotenzschluessel eindeutig. Fehler bleiben
  mit Quell-/Nachweisroute sichtbar und koennen nur begruendet wiederholt werden.
- `finance/rechnungstapel` ist eine native Meridian-Worklist.

## Konsequenzen

Alle L3-P1-Funktionsgaps der Vollinventur sind repo-seitig geschlossen.
Providerzustellung, fiskalische Pilotabnahme und Echtdaten-UAT bleiben externe
Rollout-Gates.
