---
title: "Impact Note FEED-EDITOR-025"
type: reference
audience: [architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-16
version: 1.0.0
---

# Impact Note FEED-EDITOR-025

## Scope und Grenzen

Additive Tabelle, Command-Service und Betriebsaktenprojektion im bestehenden
Agrar-/Rations-Optimization-Container. Keine neue Domaenengrenze, kein zweiter
Rationseditor und keine Provider-Livecalls.

## Betroffene Architekturartefakte

- [x] lineare Migration `feed_editor_templates_20260716`
- [x] Lifecycle-Provenienz innerhalb derselben Gruppe
- [x] typisierte Create/List/Apply-API und Read-Endpunkte
- [x] native ScreenDefinition `agrar/feeding-business`
- [x] TDD-Vertraege fuer Domain, API, RBAC, Migration und UI
- [ ] neuer Container oder Structurizr-Beziehung - nicht betroffen

## Sicherheit, Migration und Rollback

Tenantfilter, Feed-Rollen und Business-Grants gelten vor Command und Projektion.
Quellversionen und Vorlagen sind unveraenderlich; Apply verlangt Zielrevision und
Auditgrund. Downgrade entfernt nur Vorlagenartefakte. Bereits erzeugte
Rationsversionen bleiben gueltige append-only Versionen.
