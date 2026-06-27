---
title: Architecture Agent Protocol
type: explanation
audience: [agent, architect, entwickler]
owner: architecture
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
description: Verbindlicher Before/During/After-Ablauf für strukturelle Änderungen (Architecture OS).
---

# Architecture Agent Protocol

Gilt für **strukturelle** Änderungen: neue Services, Container, Domänen-Grenzen, API-Verträge, DB-Schemas, C4-Elemente, Events.

## Before (Planung)

1. [`config/architecture-index.yaml`](../../../config/architecture-index.yaml) lesen — betroffene `domains.*`
2. Prefix-Regeln prüfen: [`config/architecture-domain-prefixes.yaml`](../../../config/architecture-domain-prefixes.yaml)
2. Domain Pack unter `docs/architecture/domains/<domain>/` konsultieren
3. [`workspace.dsl`](../c4/workspace.dsl) + relevante C4-Views prüfen
4. Process Kernel nur für **Lieferstatus**, nicht für Domänen-Inventar duplizieren
5. Entscheidungsstufe festlegen (siehe unten)

## During (Umsetzung)

| Artefakt | Wann aktualisieren |
|---|---|
| Code | Immer zuerst oder parallel mit Vertrag |
| `workspace.dsl` | Neuer Container / System-Grenze |
| `generate_architecture_index.py` | Neues Prefix-Mapping nötig |
| Domain Pack README/api | Neue Routes, Endpoints, Workflows |
| ADR | Significant / Strategic |
| Tests | Regression für Vertrag |

**Leitprinzip:** Jede strukturelle Codeänderung hinterlässt eine Spur in Index, Structurizr/Views, ADR (falls nötig) und Tests.

## After (Abschluss)

1. Generatoren ausführen:
   ```bash
   pnpm arch:render
   python scripts/generate_architecture_index.py
   ```
2. `pnpm arch:validate` — muss grün sein
3. [Impact Note](impact-note-template.md) ausfüllen (Handoff / PR)
4. Workboard + Open-Gaps bei Liefer-Gaps aktualisieren

## Entscheidungsstufen

| Stufe | Beispiel | Pflicht |
|---|---|---|
| **Minor** | Rename intern, Doc-Fix, Bugfix ohne Vertrag | Index/Views optional |
| **Significant** | Neuer Endpoint-Cluster, Service-Modul, Event-Typ | ADR *Proposed*, Index, Domain Pack |
| **Strategic** | Neuer Bounded Context, Mandantenmodell, Auth-Modell | ADR *Accepted* + **Human Approval** |

## Rollen (Dokumentation)

| Rolle | Datei |
|---|---|
| Cartographer | [roles/cartographer.md](roles/cartographer.md) |
| Domain Architect | [roles/domain-architect.md](roles/domain-architect.md) |
| ADR Keeper | [roles/adr-keeper.md](roles/adr-keeper.md) |
| Drift Agent | [roles/drift-agent.md](roles/drift-agent.md) |
| QA/Workflow | [roles/qa-workflow.md](roles/qa-workflow.md) |

## CLI

```bash
pnpm arch:render    # C4 aus workspace.dsl
pnpm arch:validate  # Generatoren + Drift (non-strict)
pnpm arch:drift     # Domänen-Drift (strict für CI)
```

## Rollout für Agenten

Copy-Paste-Prompt und Kurzanleitung: [architecture-os-rollout-prompt.md](architecture-os-rollout-prompt.md)

## Referenzen

- [ADR-037](../../adr/adr-037-structurizr-c4-source-of-truth.md)
- [quality-gates/architecture-drift-checks.md](../quality-gates/architecture-drift-checks.md)
- [AGENTS.md](../../../AGENTS.md)
