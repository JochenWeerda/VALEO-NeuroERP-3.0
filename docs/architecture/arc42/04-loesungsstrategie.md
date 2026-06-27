---
title: arc42 — 4. Lösungsstrategie
type: explanation
audience: [entwickler, architect]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# 4. Lösungsstrategie

## Architekturrichtung

**Modularer Monolith mit klaren Domänengrenzen** — selektive Microservices nur an stabilen Grenzen (CRM-Cluster, Inventory, DMS, KI).

Quelle: [Zielbild Landhandel ERP](../target-state-landhandel-erp.md)

## Kernprinzipien

1. Canonical Domain Model vor API-Wildwuchs ([ADR-003](../../adr/adr-003-canonical-domain-model.md))
2. Business Commands vor UI-CRUD ([ADR-004](../../adr/adr-004-command-action-layer.md))
3. Workflow-Konfiguration vor harter Prozesslogik ([ADR-005](../../adr/adr-005-workflow-policy-kern.md))
4. Read Models für Performance, nicht als zweite Wahrheit ([ADR-006](../../adr/adr-006-read-model-query-contract-prinzip.md))
5. Dokumentations-Stack: ISO 42010 + C4 + arc42 ([ADR-036](../../adr/adr-036-architecture-documentation-stack.md))

## Technologie-Kurzüberblick

| Schicht | Technologie |
|---|---|
| Frontend | React 18, Vite, Tailwind, Mask Builder |
| API | FastAPI, SQLAlchemy 2.0 |
| Events | NATS JetStream, Outbox |
| Auth | OIDC / Keycloak |
| DMS | Paperless-ngx + dms-adapter |

[← Kapitel 3](03-kontext-scope.md) | [Kapitel 5 →](05-bausteinsicht.md)
