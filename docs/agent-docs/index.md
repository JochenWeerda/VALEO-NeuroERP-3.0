---
title: Agent-Dokumentation
type: explanation
audience: [ki-agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Agent-Dokumentation

Maschinenlesbare Schicht für KI-Agents (Hermes, Operator-, Coding-Agents). Agents
sind Leser **und** Autoren der Doku.

## Bestandteile

- **AGENTS.md** (Repo-Root) — Einstieg, Pflichtreihenfolge, Parallel-Protokoll.
- [**Capability-Katalog**](capability-catalog.md) — Fähigkeiten je Agent-Rolle.
- [**Tool-Katalog**](tool-catalog.md) — MCP-Tools (Schema, Scope, Idempotenz, Risiko).
- [**Guardrails**](guardrails.md) — Human-Approval bei HIGH-Risk, fail-closed, RBAC.
- [**Contracts**](contracts.md) — `ai_harness`-Verträge je Slice (7 Pflichtverträge).

## Zwei Rollen

- **Agent als Leser:** strukturierte Verträge (`ai_harness`, MCP-JSON-Schema,
  OpenAPI, generierte Inventare).
- **Agent als Autor:** jeder Slice erzeugt Pflichtdoku; Doku-Update = Definition
  of Done; Drift wird wöchentlich gemessen (siehe [Doku-Governance](../dokumentation/governance.md)).

## Verwandte Metriken

- [AI Engineering Metrics](../entwickler/engineering-metrics.md) — Slice-Cycle-Time,
  Rework-Rate (generiert, MkDocs-Nav).
