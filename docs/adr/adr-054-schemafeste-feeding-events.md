---
title: "ADR-054 Schemafeste Feeding-Events auf der Transactional Outbox"
type: adr
audience: [architektur, agrar, integration, entwickler, qa]
owner: domain/agrar
status: proposed
last_reviewed: 2026-07-16
version: 1.0.0
---

# ADR-054 Schemafeste Feeding-Events auf der Transactional Outbox

**Status:** Proposed

**Datum:** 2026-07-16

## Kontext

Feeding-Services bauten Outbox-Payloads teilweise inline. Dadurch konnten
Eventname, Huelle, Zeitstempel und fachliche Referenzen auseinanderlaufen.
Zudem fehlten Ereignisse fuer Aktivierung, Analysefreigabe und Quarantaene.

## Entscheidung

- `app/agrar/rations/events.py` ist die Code-SSOT fuer Feeding-Eventtypen und
  die Huelle `schema_version`, `event_id`, `event_type`, `aggregate_id`,
  `timestamp`, `payload`.
- Schema `1.0` bleibt im Envelope; der Eventname erhaelt keinen parallelen
  `.v1`-Suffix.
- Der Builder akzeptiert nur die geschlossene Typliste. Neue Typen erfordern
  Vertrags-, Dokumentations- und Regressionserweiterung im selben Slice.
- Der Emitter schreibt nur in die vorhandene Outbox und fuehrt keinen Commit
  aus. Der aufrufende Application Service committed oder rollt Fachaggregat
  und Event gemeinsam zurueck.
- Publisher bleiben at-least-once. Konsumenten deduplizieren die stabile
  `event_id`; fachliche Commands verhindern doppelte Erzeugung bei Retry.
- Eventpayloads enthalten Referenzen und Entscheidungskontext, aber keine
  breit verteilten Tiergesundheits- oder Provider-Rohdaten.

## Kanonische Namen

`feeding.analysis.released`, `feeding.ration.version.activated`,
`feeding.plan.published`, `feeding.actual.recorded`,
`feeding.deviation.exceeded`, `feeding.measure.created|completed|overdue`,
`feeding.import.quarantined` und
`feeding.supply.procurement_handoff.created`.

## Konsequenzen

Event- und Aggregatpersistenz sind atomar testbar. Bestehende Namen bleiben
kompatibel; die zuvor nur dokumentierten Plural-/`.v1`-Varianten werden nicht
als zweite Topics eingefuehrt. Reale DDW-/MLP-Livepfade bleiben ausserhalb
dieser Entscheidung bis zum Partnervertrag blockiert.
