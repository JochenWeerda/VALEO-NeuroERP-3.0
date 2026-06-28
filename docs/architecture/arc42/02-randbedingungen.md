---
title: arc42 — 2. Randbedingungen
type: explanation
audience: [entwickler, compliance]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# 2. Randbedingungen

## Regulatorik & Compliance

- **GoBD** — revisionssichere Belege, Hash-Ketten, unveränderliche Belegnummern
- **DSGVO** — Mandantentrennung, Löschkonzepte ([ADR-021](../../adr/adr-021-tenant-weite-datenresidenz-und-exportregeln.md))
- **KassenSichV / TSE** — POS-Fiskalisierung ([pos-fiscalization-providers.md](../pos-fiscalization-providers.md))
- **ELSTER / ERiC** — UStVA, eBilanz (externe Produktiv-Gates)
- **ATLAS / Meldewesen** — Zoll, PCN, VVVO

Quellen: [Compliance-Überblick](../../compliance/index.md), [GoBD-Checkliste](../../compliance/gobd-checklist.md)

## Technische Randbedingungen

- PostgreSQL 15+, Multi-Schema, Alembic Single-Head
- OIDC via Keycloak, `X-Tenant-ID` Pflicht
- NATS JetStream + Outbox ([ADR-008](../../adr/adr-008-eventing-outbox-standard.md))
- Deutsch als UI-Sprache; API/ADR code-nah oft Englisch

## Organisatorisch

- Docs-as-Code, MkDocs, Agent-Betrieb (Hermes)
- Process Kernel als Liefernachweis ([STATUS](../process-kernel/STATUS.md))

[← Kapitel 1](01-einfuehrung.md) | [Kapitel 3 →](03-kontext-scope.md)
