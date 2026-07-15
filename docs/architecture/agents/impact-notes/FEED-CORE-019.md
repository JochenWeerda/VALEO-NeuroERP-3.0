---
title: "Impact Note FEED-CORE-019"
type: reference
audience: [architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
---

# Impact Note FEED-CORE-019

## Scope und Grenzen

Additiver Ausbau von `domain_shared.grundfutter_analysen` im bestehenden
Agrar-/Rations-Optimization-Container. Kein neuer Container, kein paralleler
Laborstamm und keine eigene Dateispeicherung ausserhalb des DMS.

## Betroffene Architekturartefakte

- [x] neuer typisierter Endpoint-Cluster unter dem vorhandenen Rations-Prefix
- [x] additive lineare Alembic-Migration
- [x] Application Service und Domainregeln
- [x] Agrar-Domain-Pack, ADR und Vertragstests
- [x] zwei native ScreenDefinitions und zentrale Meridian-Runtime
- [ ] neuer Container oder neue Systemgrenze — nicht betroffen
- [ ] Structurizr-Beziehung — nicht betroffen

## Sicherheits- und Datenvertrag

Alle kanonischen Endpunkte erzwingen Tenant und Feed-Rollen; Release braucht
`APPROVE_ROLES`. Optimistische Revisionen, append-only Snapshots, scope-spezifische
Unique-Constraint und Zeilensperren sichern parallele Freigaben. Importierte
Dateien bleiben ohne DMS-ID/SHA-256 blockiert.

## Migration und Rollback

`feed_core_feed_analyses_20260715` folgt linear auf FEED-CORE-018. Bestehende
Analyse-IDs und Legacy-Spalten bleiben erhalten; verifizierte Bestandsdaten
werden als `validated` gekennzeichnet. Downgrade entfernt nur additive
Kindtabellen, Constraints und Kopfattribute.

## Nachweise

Die konkreten Test-, Migrations-, UI-, Doku- und Architektur-Gates werden beim
Slice-Abschluss in `docs/agent-ops/slices/FEED-CORE-019.yaml` festgehalten.
