---
title: Tool-Katalog (Agent-Sicht)
type: reference
audience: [ki-agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Tool-Katalog (Agent-Sicht)

Agents nutzen ERP-Funktionen ausschließlich über den **MCP-Tool-Katalog**. Die
vollständige, generierte Referenz (inkl. Eingabe-/Ausgabe-Schema je Tool) liegt
im Schnittstellenbereich:

➡️ **[MCP-Tool-Referenz](../schnittstellen/mcp-tools.md)**

Diese wird deterministisch aus `config/mcp_erp_tools.yaml` generiert
(`python scripts/generate_mcp_tool_reference.py`) — **keine Doppelpflege**.

## Lesehilfe für Agents

Pro Tool sind diese Metadaten verbindlich:

| Feld | Bedeutung für den Agent |
|---|---|
| `scope` | Benötigte Berechtigung (RBAC). Ohne Scope kein Aufruf. |
| `idempotent` | `true` → gefahrlos wiederholbar. `false` → Duplikate vermeiden. |
| `risk_class` | `low`/`medium`/`high`. `high` → Human-Approval (siehe Guardrails). |
| `human_approval_required` | Wenn `true`: Ausführung erst nach Freigabe. |
| `audit` | `read`/`write` — jede Nutzung wird protokolliert. |
| `input_schema` / `output_schema` | Vertrag für Argumente und Rückgabe. |

## Auswahllogik (empfohlen)

1. Aufgabe → passenden `scope` und `domain` bestimmen.
2. Bevorzugt **idempotente Lese-Tools** für Kontext.
3. Schreib-/HIGH-risk-Tools nur mit klarer Absicht und Freigabe.
4. Ergebnis gegen `output_schema` prüfen.
