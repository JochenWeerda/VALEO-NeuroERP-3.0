---
title: "Impact Note FEED-SUP-028"
type: reference
audience: [architektur, agrar, einkauf, frontend, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-16
version: 1.0.0
---

# Impact Note FEED-SUP-028

## Scope und Grenzen

Der Slice ergaenzt eine Plan-to-Supply-Read-Projektion und einen kontrollierten
Agrar-zu-Einkauf-Handoff. Er fuehrt keinen neuen Container ein und schreibt
keine Einkaufsbestellung. Reservierungen, offene Lieferungen und Chargen-FIFO
sind nicht Teil dieses Inkrements.

## Architekturartefakte

- additive Migration `feed_supply_handoffs_20260716`
- reine Decimal-Regeln fuer Bedarf, Sicherheit, Reichweite und Rundung
- grant-/tenant-sichere Projektion aktueller FeedingPlanVersions
- idempotenter append-only Handoff plus transaktionales Outbox-Ereignis
- REST-API `/feeding/supply` und `/feeding/supply/procurement-handoffs`
- native Meridian-Supply-Worklist mit schmalem Bestaetigungsdialog

## Sicherheit, Betrieb und Datenqualitaet

READ/WRITE-Rollen und Business-Grants gelten serverseitig. Fehlender Scope wird
wie ein nicht vorhandener Plan behandelt. Unbekannter Bestand und unbekannte
Handelseinheit blockieren den Handoff. Advisory Locks und Request-Hashes
verhindern doppelte bzw. widerspruechliche Commands.

## UI-Vertrag

Die Maske laeuft ueber ScreenDefinition, RenderPlan,
`useUniversalMaskRuntime` und `UniversalMaskRenderer`. Der Dialog bestaetigt nur
den konkreten Zeilenbedarf und nennt Unterdeckung, gerundeten Vorschlag sowie
Rundungsaufschlag. Erfolg verweist auf Bestellvorschlaege und erklaert explizit,
dass keine Bestellung erzeugt wurde.
