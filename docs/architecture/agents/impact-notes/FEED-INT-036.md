---
title: "Impact Note FEED-INT-036"
type: reference
audience: [architektur, agrar, integration, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-16
version: 1.0.0
---

# Impact Note FEED-INT-036

## Scope und Entscheidungsstufe

Domain Agrar/Tierernaehrung; significant. Zentraler Eventvertrag und additive
Emissionen auf der bestehenden `public.outbox_events`. Kein neuer Container,
Broker, Endpoint, Consumer oder externer Providerpfad.

## Betroffene Artefakte

- [x] Domain-Code und Application Services
- [x] Event-/AsyncAPI-Katalog
- [x] Agrar Domain Pack
- [x] ADR-054
- [x] Contract-, Atomizitaets- und Emissions-Tests
- [ ] C4/Containergrenze — unveraendert
- [ ] Datenbankmigration — vorhandene Outbox reicht aus

## Sicherheits- und Betriebswirkung

Tenant bleibt eine separate, verpflichtende Outbox-Spalte. Payloads enthalten
nur fachliche Referenzen und keine Provider-Secrets oder breite
Tiergesundheitsdaten. Publisher-Semantik bleibt at-least-once; Consumer muessen
`event_id` deduplizieren.

## Abnahme

Contracttests pruefen geschlossene Typen, Schema 1.0 und Rollback. API-Journeys
belegen genau ein Ereignis bei Aktivierung, Freigabe, Quarantaene und
idempotenten Commands. Architektur- und Dokumentationsgates werden im
Slice-Abschluss protokolliert.
