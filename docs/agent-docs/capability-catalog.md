---
title: Capability-Katalog
type: reference
audience: [ki-agent, entwickler, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Capability-Katalog

Überblick über die Agent-Rollen, ihre Fähigkeiten und ihre Grenzen.

## Agent-Rollen

| Rolle | Zweck | Schreibrechte | Freigabe |
|---|---|---|---|
| **Coding-Agent** | Entwicklung in Slices (Code + Doku) | Repo (eigener Slice) | Slice-Governance, CI |
| **Operator-Agent (Hermes)** | Fachliche ERP-Aktionen über MCP-Tools | nur via MCP-Tools/Scopes | Human-Approval bei HIGH-risk |
| **Explorer/Readonly-Agent** | Recherche, Analyse, Reporting | keine | n/a |

## Fähigkeiten (Operator-Agent)

Der Operator-Agent handelt ausschließlich über den
[MCP-Tool-Katalog](tool-catalog.md). Beispiele:

- **Lesen:** Kundensuche, 360-Sicht, Auftragsstatus, offene Posten,
  Lot-Verfolgung, Silozellen-Status, Dokumentsuche, Gate-Status.
- **Schreiben (kontrolliert):** Kontaktprotokoll erfassen, Rechnungsvorschlag
  (HIGH-risk → Human-Approval).

## Grenzen

- Kein direkter DB-Zugriff; nur definierte Tools/Endpoints.
- Mandantenbindung ist nicht umgehbar.
- Schreib-/Risiko-Tools unterliegen [Guardrails](guardrails.md).
- Jede Aktion ist auditierbar.

## Rollen als Leser und Autor

- **Leser:** maschinenlesbare Verträge ([Contracts](contracts.md)),
  MCP-JSON-Schema, OpenAPI.
- **Autor:** Coding-Agents erzeugen je Slice Pflichtdoku (Workboard, Slice-YAML,
  Workflow-Doc); Doku-Update ist Definition of Done.
