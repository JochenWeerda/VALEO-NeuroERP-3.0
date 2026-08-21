---
title: ADR-066 Tankanlagen-Eingang und Lieferschein-Outbox
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/agrar
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-066 Tankanlagen-Eingang und Lieferschein-Outbox

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

Zapfungen und Tankbestand waren vorhanden; rohe Anlagenmeldungen hatten jedoch
keinen idempotenten Eingang, Fehlerkorb oder regelbasierten Lieferscheinpfad.

## Entscheidung

- Tenant, Adapter und externe ID bilden den Idempotenzschluessel; ein SHA-256
  bindet den kanonischen Payload. Eine Wiederverwendung mit anderem Payload
  wird abgewiesen.
- Validierung und Fehlerkorb sind vom Processing getrennt. Retry ersetzt den
  Payload nur begruendet und erhoeht einen Zaehler.
- Processing erzeugt genau eine kanonische `ops_zapfungen`-Zeile.
- Fakturierbarer Kundenverbrauch erzeugt genau einen idempotenten
  `tank.delivery-note.requested`-Outbox-Handover; interner Verbrauch nicht.
- `tankstelle/adapter-inbox` ist eine native Meridian-Worklist.

## Konsequenzen

`L3-GAP-TANK-011` ist repo-seitig geschlossen. Reale Anlagenprotokolle und der
produktive Sales-Outbox-Consumer bleiben externe Gates.
