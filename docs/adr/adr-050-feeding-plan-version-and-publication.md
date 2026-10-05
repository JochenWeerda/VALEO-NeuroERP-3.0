---
title: "ADR-050 Unveraenderliche FeedingPlanVersion und atomare Publikation"
type: adr
audience: [architektur, domain, entwickler, qa]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-16
version: 1.0.0
---

# ADR-050 Unveraenderliche FeedingPlanVersion und atomare Publikation

**Status:** Accepted

**Datum:** 2026-07-16

## Kontext

Eine aktive Rationsversion ist eine fachliche Rezeptur je Tier. Fuer Stall,
Mischwagen, Versorgung und spaetere Ist-Erfassung braucht es einen separaten,
zeitlich gueltigen Ausfuehrungssnapshot mit Tierzahl und Dosiertechnik.

## Entscheidung

- `FeedingPlan` ist der Kopf je Fuetterungsgruppe; jede Publikation erzeugt eine
  unveraenderliche `FeedingPlanVersion` aus genau einer `approved` oder `active`
  Rationsversion.
- Tierzahl, Gueltigkeit, Dosierschritt, Rundungsmodus und Auditgrund gehoeren zur
  Planversion. `valid_until` darf nicht vor `valid_from` liegen.
- `MixingInstruction` bewahrt Mischreihenfolge, FM je Tier, ungerundete
  Chargenmenge, dosierbare Zielmenge und Rundungsdelta. Fehlende FM bleibt auf
  allen vier Feldern unbekannt und wird nie als Null interpretiert.
- Rundung arbeitet mit Decimal und den expliziten Modi `nearest`, `up`, `down`.
  Das Delta bleibt sichtbar; Publikation behauptet keine Scheingenauigkeit.
- Ein tenantgebundener Idempotency-Key mit Request-Hash verhindert doppelte oder
  widerspruechliche Publikationen. Transaktionale Advisory Locks serialisieren
  Retries und Versionsvergabe je Gruppe.
- Planversion, Anweisungen und ein `feeding.plan.published`-Outbox-Ereignis in
  Schema-Version 1.0 werden atomar in derselben Transaktion gespeichert.
- Lesen und Publizieren erzwingen Feed-Rolle, Tenant und Business-Grant.

## Konsequenzen

Stallansicht, PDF, Maschinenexport, Bedarf und ActualFeeding koennen stabil auf
eine Planversions-ID referenzieren. FEED-PLAN-027 liefert native ObjectPage,
Browserdruck/PDF und die planversionsgebundene mobile Stallroute; sie berechnen
keine eigenen Chargenmengen. Ein signierter Server-PDF-Job bleibt Teil der
spaeteren Berichtsarchitektur.
