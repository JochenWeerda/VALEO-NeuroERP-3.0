---
title: "Impact Note FEED-PLAN-026"
type: reference
audience: [architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-16
version: 1.0.0
---

# Impact Note FEED-PLAN-026

## Scope und Grenzen

Neues Plan-Aggregat im bestehenden Agrar-/Rations-Optimization-Container.
Publikation konsumiert nur persistierte Rationsversionen und verwendet die
bestehende `public.outbox_events`-Infrastruktur. Keine neue Systemgrenze und kein
Maschinenadapter in diesem Slice.

## Betroffene Architekturartefakte

- [x] lineare additive Migration `feed_plan_versions_20260716`
- [x] reine Decimal-Skalierungs- und Rundungsregeln
- [x] transaktionaler Application Service mit Idempotenz und Outbox
- [x] typisierte Publish/List/Get-API
- [x] Tenant-/Grant-/Rollen-, Lifecycle-, Immutable- und Eventtests
- [ ] Meridian-ObjectPage, PDF und Mobilroute - FEED-PLAN-027

## Sicherheit und Betrieb

Planlisten filtern auch ohne Gruppenparameter nach Ersteller oder aktivem
Business-Grant. Einzelzugriff verschleiert fehlenden Scope mit 404. Advisory
Locks verhindern parallele Doppelerzeugung; DB-Trigger schuetzen publizierte
Planversionen und Mischanweisungen.

## Rollback

Downgrade entfernt nur Plan-/Anweisungstabellen und Trigger. Outbox-Ereignisse
koennen bereits konsumiert sein; produktiv ist deshalb ein Forward-Fix und kein
Downgrade nach Eventpublikation vorgesehen.
