---
title: Skripte & Generatoren
type: reference
audience: [entwickler, betrieb, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Skripte & Generatoren

Übersicht häufig genutzter Repo-Skripte. Vollständige Befehle siehe `CLAUDE.md`.

## Dokumentation

| Skript | Zweck |
|--------|-------|
| `scripts/generate_openapi.py` | OpenAPI-Spec → `docs/schnittstellen/openapi.json` |
| `scripts/generate_mcp_tool_reference.py` | MCP-Tool-Referenz aus `config/mcp_erp_tools.yaml` |
| `scripts/generate_agent_handbuch.py` | Agent-Handbuch (Prozessketten, Masken-API, Automatisierung) → `docs/agent-handbuch/` |
| `scripts/maybe_regenerate_agent_handbuch.py` | Pre-Commit: Agent-Handbuch bei Aenderung an Flow Spine / SDs / MCP |
| `scripts/generate_adr_nav.py` | MkDocs ADR-Navigation patchen |
| `scripts/generate_code_inventories.py` | Endpoint-/Service-/Migrations-Inventare |
| `scripts/generate_container_inventory.py` | Docker-Compose-Container-Inventar → C4-Drift-Check |
| `scripts/doc_drift_report.py` | Code↔Doku-Drift-Report → `artifacts/` |
| `scripts/docs-legacy-migrate.py` | Alt-Doku inventarisieren/archivieren |
| `scripts/docs-staleness-check.cjs` | `last_reviewed`-Gate (Node) |

## Datenbank & Migration

| Skript / Befehl | Zweck |
|-----------------|-------|
| `alembic upgrade head` | Migrationen anwenden |
| `pnpm migrate:erp-finanz` | ERP-Finanz-SQL-Migrationen (`tools/migration/`) |

## Qualität & Governance

| Skript | Zweck |
|--------|-------|
| `pytest` | Backend-Tests |
| `scripts/check_sql_fstrings.py` | SQL-f-string CI-Gate |
| `scripts/check_critical_backend_coverage.py` | Coverage-Ratchet |
| `scripts/check_toolchain_pins.py` | Toolchain-Pins |
| `scripts/valeo_slice.py` | Slice claim/verify/close (Agent-Ops) |

## Frontend

| Befehl | Zweck |
|--------|-------|
| `npm run dev` / `build` / `test` | Dev-Server, Produktionsbuild, Vitest |
| `npx playwright test` | E2E |

## Agenten & Metriken

| Skript | Zweck |
|--------|-------|
| `scripts/generate_metrics_page.py` | AI Engineering Metrics Markdown |
| `scripts/cards-inventory-audit.py` | Workflow-Cards inventarisieren |

!!! note "Drift & Staleness"
    Drift-Report ist informativ (wöchentliche CI); Staleness blockiert PRs bei
    veralteten kuratierten MkDocs-Seiten. Siehe [Doku-Governance](../dokumentation/governance.md).
