---
title: Schnittstellen
type: reference
audience: [integrator, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Schnittstellen

Verträge für die Integration mit VALEO NeuroERP. Single Source of Truth ist der
Code; OpenAPI/AsyncAPI werden generiert und hier eingebettet.

## Überblick

| Schnittstelle | Format | Quelle |
|---|---|---|
| REST-API | OpenAPI 3.1 | FastAPI `openapi.json` |
| Endpoint-Inventar | Markdown (generiert) | [endpoint-inventory.md](endpoint-inventory.md) |
| Event-Bus | AsyncAPI | NATS/Outbox-Event-Schemas |
| MCP-Tools | JSON-Schema + Scope/Risiko | `config/mcp_erp_tools.yaml` |
| SSE-Streams | Endpoint-Referenz | `sse_router` |
| Webhooks | Payload-Verträge | DMS/GS1-Router |

## Prinzipien

- Generierte Artefakte werden versioniert (`artifacts/`) und in die Site
  eingebettet — keine Handpflege.
- Verknüpfung mit der Release-Compatibility-Matrix.
- Breaking Changes → neue Contract-Version + Deprecation-Frist.

> Generierung & Einbettung folgen in `DOC-INTERFACES-001`.
