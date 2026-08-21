---
title: ADR-063 Sicheres Anwender-Abfrage-Center
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/finance
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-063 Sicheres Anwender-Abfrage-Center

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

L3 bietet Anwenderabfragen; VALEO hatte feste Reports und Read Models, aber
keinen sicheren, speicherbaren Designer. Ein SQL-Editor waere fuer Isolation,
Berechtigung, Performance und Wartbarkeit nicht vertretbar.

## Entscheidung

- Anwender waehlen nur Datenprodukte, Felder, Gleichheitsfilter und
  Aggregationen aus einer serverseitigen Allowlist.
- Vorschauen verwenden tenantgebundene Read-Model-Snapshots und sind hart auf
  200 Zeilen begrenzt.
- Gespeicherte Abfragen/Favoriten sind tenant- und benutzergebunden; Save,
  Export und Import werden auditiert.
- Austauschpakete tragen eine HMAC-SHA256-Signatur. Beim Import werden Signatur
  und Allowlist erneut geprueft.
- `auswertungen/abfrage-center` ist eine native Meridian-Worklist.

## Konsequenzen

`L3-GAP-QUERY-008` ist repo-seitig geschlossen. Weitere Read Models werden nur
nach fachlicher und datenschutzrechtlicher Freigabe in die Allowlist aufgenommen.
