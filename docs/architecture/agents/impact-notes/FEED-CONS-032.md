---
title: "Impact Note FEED-CONS-032"
type: reference
audience: [architektur, agrar, beratung, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-16
version: 1.0.0
---

# Impact Note FEED-CONS-032

## Scope und Entscheidungsstufe

Domain Agrar/Tierernaehrung; significant. Additiver Lebenszyklus fuer
Actual-Massnahmen, empfaengersicheres In-App-Read-Model und strukturierte,
versionierte Beratungsentwuerfe. Keine neue Containergrenze, kein externer
Notification-Provider und kein PDF-/DMS-Versprechen.

## Betroffene Artefakte

- [x] Domain-State-Machine und Application Services
- [x] additive, lineare Alembic-Migration mit Backfill der Version 1
- [x] REST-Vertraege und bestehende Consulting-Journey
- [x] `feeding.measure.completed|overdue` auf ADR-054-Outbox
- [x] Domain-, API-, Security- und Component-Tests
- [x] ADR-055, Agrar Domain Pack und Feeding-SSOT
- [ ] C4/Containergrenze — unveraendert
- [ ] PDF/DMS/Zustellung — FEED-REP-039/040

## Sicherheits- und Betriebswirkung

Rolle, Tenant und Business-Grant werden vor Historie, Transition, Falllink und
Entwurf erzwungen. Hinweise sind nur fuer `recipient_subject` lesbar. Der
Scheduler darf den Overdue-Command wiederholen; der stabile Dedupe-Key verhindert
fachliche Dubletten. Append-only-Trigger schuetzen Audit- und Berichtshistorie.

## UI-Wirkung

Die Wirksamkeitskontrolle ersetzt nicht zugaengliche Browser-Prompts durch ein
beschriftetes Domain-Overlay mit expliziter Bewertung, Ergebnis-Guard und
Abbruch. Es ist eine begrenzte Legacy-Integration; keine neue Seiten- oder
Designsystemarchitektur neben Meridian.

## Abnahme

Die TDD-Wellen belegen State-Machine, Optimistic Concurrency, Abschlussguard,
Overdue-Idempotenz, Eventzahl, Rollen-/Grant-/Empfaengerisolation,
Report-Hash/Version und die bedienbare Wirksamkeitskontrolle.
