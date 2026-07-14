---
title: Agent-Handbuch
type: explanation
audience: [ki-agent, entwickler, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-14
version: 3.0.0
description: Maschinenlesbare Bedienungsanleitung für KI-Agenten — Prozessketten, Masken-APIs, Automatisierung.
---

# Agent-Handbuch

> **Automatisch generiert** via `python scripts/generate_agent_handbuch.py`. **Nicht manuell bearbeiten.**

Ergänzt das [Endnutzer-Benutzerhandbuch](../benutzerhandbuch/index.md) um die **Agent-Sicht**: Welche API wann, in welcher Prozesskette, mit welchem Risiko.

## Schnellnavigation

| Dokument | Inhalt |
|---|---|
| [Prozessketten](prozessketten.md) | 9 Flow-Spine E2E-Ketten mit Knoten, Deep-Links, Instanz-API |
| [Masken-API-Katalog](masken-api-katalog.md) | 36 ScreenDefinitions mit AgentContract, Endpoints, Actions |
| [Automatisierung](automatisierung.md) | 18 MCP-Tools, 66 Domain-Events, ActionRuntime-Modi |
| [agent-process-manifest.json](agent-process-manifest.json) | JSON-Manifest für SDK/Agent-Router |

## Entscheidungsbaum für Agenten

```text
Aufgabe erhalten
  ├─ Fachlicher Prozess / Belegkette? → Prozessketten.md + Flow-Spine Instanz
  ├─ Einzelmaske / Stammdaten?       → Masken-API-Katalog + GET .../agent-contract
  ├─ Idempotente Lesefrage?          → MCP-Tool (scope:read) bevorzugen
  └─ Schreiben / Folgebeleg?         → dryRun → propose → Human-Approval → execute
```

## Authentifizierung (alle APIs)

| Header | Wert |
|---|---|
| `Authorization` | `Bearer <token>` |
| `X-Tenant-ID` | Mandanten-UUID |
| `X-Correlation-ID` | optional, für Tracing |

## ActionRuntime-Modi (Mask-Actions)

| Modus | Body | Wirkung |
|---|---|---|
| `validate` | `_mode: "validate"` | Nur Validierung |
| `dryRun` | `_mode: "dryRun"` | Simulation ohne Persistenz |
| `propose` | `_mode: "propose"` | Vorschlag für Freigabe |
| `execute` | (default) | Persistenz + Audit |

Zusatzfelder: `_auditReason`, `_idempotencyKey`

## Flow-Spine-Übersicht

| process_key | Route | Domäne |
|---|---|---|
| `order-to-cash` | `/workflow/flow-spine-order-to-cash` | sales |
| `procure-to-pay` | `/workflow/flow-spine-procure-to-pay` | procurement |
| `inventory-to-settlement` | `/workflow/flow-spine-inventory-to-settlement` | inventory |
| `harvest-to-settlement` | `/workflow/flow-spine-harvest-to-settlement` | agrar |
| `contract-to-settlement` | `/workflow/flow-spine-contract-to-settlement` | agrar |
| `complaint-to-resolution` | `/workflow/flow-spine-complaint-to-resolution` | quality |
| `service-to-customer` | `/workflow/flow-spine-service-to-customer` | service |
| `finance-to-close` | `/workflow/flow-spine-finance-to-close` | finance |
| `compliance-to-report` | `/workflow/flow-spine-compliance-to-report` | compliance |

## Verwandte Dokumentation

- [Agent-Dokumentation (Governance)](../agent-docs/index.md)
- [Guardrails](../agent-docs/guardrails.md)
- [MCP-Tool-Referenz](../schnittstellen/mcp-tools.md)
- [REST-API / OpenAPI](../schnittstellen/rest-api.md)
- [Mask Runtime API](../entwickler/mask-runtime-api.md)
- [Mask Runtime Agent-Runbook](../agent-docs/runbooks/mask-runtime-agent-modus.md)
