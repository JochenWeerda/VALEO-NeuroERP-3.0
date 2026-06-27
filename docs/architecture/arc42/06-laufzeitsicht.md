---
title: arc42 — 6. Laufzeitsicht
type: explanation
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# 6. Laufzeitsicht

## Geschäftsprozesse (BPMN-äquivalent)

Mermaid-Flowcharts — **kein BPMN-XML** ([ADR-035](../../adr/adr-035-kein-workflow-designer.md)):

- [ERP Prozesskarte](../process-map.md) — O2C, P2P, FiBu/DATEV, Agrar, POS/TSE, QS
- [Workflow-Spine](../../workflows/) — detaillierte E2E-Analysen

## UML-Sequenzdiagramme (technische Interaktion)

| Ablauf | Seite |
|---|---|
| Order-to-Cash → DATEV | [seq-o2c-fibu.md](../views/sequences/seq-o2c-fibu.md) |
| Annahme → Settlement → Journal | [seq-agrar-settlement.md](../views/sequences/seq-agrar-settlement.md) |
| Auth & Tenant | [seq-auth-tenant.md](../views/sequences/seq-auth-tenant.md) |
| DMS-Archivierung | [dms-paperless-integration.md](../dms-paperless-integration.md) |

## UML Klassendiagramm

Canonical Core (Aggregate + Operationen): [uml-canonical-domain-class.md](../views/uml-canonical-domain-class.md)

## Events

NATS/Outbox-Standard: [ADR-008](../../adr/adr-008-eventing-outbox-standard.md), [Event-Katalog](../../schnittstellen/events.md)

[← Kapitel 5](05-bausteinsicht.md) | [Kapitel 7 →](07-verteilungssicht.md)
