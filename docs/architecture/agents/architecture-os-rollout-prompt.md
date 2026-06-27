---
title: Architecture OS — Rollout-Prompt für Agenten
type: how-to
audience: [agent, architect, entwickler]
owner: architecture
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
description: Copy-Paste-Prompt und Kurzanleitung, damit Agenten Architecture OS im Alltag anwenden.
---

# Architecture OS — Rollout-Prompt für Agenten

Architecture OS ist die agentensteuerbare Architektur-Schicht des Repos: Structurizr DSL, Architecture Index, Domain Packs, Drift-Checks und ein verbindliches Before/During/After-Protokoll. Dieses Dokument bringt die Infrastruktur in den operativen Agenten-Alltag.

## Kurzanleitung für Menschen

1. **Neue Agent-Session starten** — den Copy-Paste-Prompt unten als erste Nachricht oder System-Kontext einfügen (zusätzlich zu `AGENTS.md`).
2. **Strukturelle Tasks** (neue Services, Routes, Endpoints, Container, Events, Domänen-Grenzen) immer über [architecture-protocol.md](architecture-protocol.md) führen — nicht nur Code ändern.
3. **Prefix-Regeln pflegen** — neue Route-Segmente, Service- und Endpoint-Stems in [`config/architecture-domain-prefixes.yaml`](../../../config/architecture-domain-prefixes.yaml) eintragen, dann Index neu generieren.
4. **Vor Abschluss** — `pnpm arch:validate` und bei strukturellen Änderungen `pnpm arch:drift` ausführen; Impact Note ausfüllen.
5. **Parallelbetrieb** — Slice auf dem [Active Workboard](../../agent-ops/active-workboard.md) claimen, bevor mit ARCH-OS-bezogener Arbeit begonnen wird.

**Wann ist ein Task strukturell?** Neue API-Verträge, neue Frontend-Routen unter einer Domäne, neuer Microservice/Container, neues Event-Schema, neue DB-Schemas über Domänengrenzen, neue Bounded Contexts.

**Wann reicht Minor?** Interne Renames ohne Vertragsänderung, reine Bugfixes, reine Doc-Korrekturen ohne Modelländerung.

---

## Copy-Paste Prompt

Den folgenden Block vollständig in die Agent-Session kopieren:

```
Du arbeitest im Repository VALEO NeuroERP 3.0. Architecture OS ist aktiv — behandle Architektur-Artefakte als verbindliche Arbeitsgrundlage, nicht als optionale Doku.

## Session-Start (Pflicht bei strukturellen Tasks)

Lies in dieser Reihenfolge:
1. AGENTS.md — Session-Start, Parallelbetrieb, Claim-Pflicht
2. config/architecture-index.yaml — betroffene domains.*, Container, Verweise
3. docs/architecture/domains/<domain>/ — Domain Pack (README, api.md, workflows.md, decisions.md, tests.md)
4. docs/architecture/agents/architecture-protocol.md — Before/During/After
5. docs/architecture/c4/workspace.dsl — bei Container- oder System-Grenz-Änderungen
6. docs/agent-ops/active-workboard.md — offene/reservierte Slices prüfen

Vor jedem Edit: prüfen, ob die Umsetzung bereits im Code, Workboard, Slice-YAML oder docs/project-context/open-gaps-and-known-issues.md existiert — keine Doppelarbeit.

## Strukturelle Änderungen — Before / During / After

### Before (Planung)
- architecture-index.yaml: betroffene Domäne(n) identifizieren
- Domain Pack lesen — bestehende Routes, Endpoints, Workflows, Entscheidungen
- workspace.dsl + relevante C4-Views prüfen
- Entscheidungsstufe festlegen (siehe unten)
- Bei Parallelarbeit: Slice claimen (reserviert + Owner + commit chore(workboard): claim SLICE-ID)

### During (Umsetzung)
Leitprinzip: Jede strukturelle Codeänderung hinterlässt eine Spur in Index, Structurizr/Views (falls nötig), Domain Pack, ADR (falls nötig) und Tests.

| Artefakt | Wann |
|---|---|
| Code | Immer — zuerst oder parallel mit Vertrag |
| config/architecture-domain-prefixes.yaml | Neue route_segments, service_prefixes oder endpoint_prefixes |
| scripts/generate_architecture_index.py | Nach Prefix-Änderung ausführen (Index ist generiert) |
| docs/architecture/c4/workspace.dsl | Neuer Container, System-Grenze, Beziehung |
| docs/architecture/domains/<domain>/ | Neue Routes, Endpoints, Workflows, Tests |
| ADR | Significant oder Strategic |
| Tests | Regression für API-Vertrag / Mapping |

### After (Abschluss)
1. pnpm arch:render
2. python scripts/generate_architecture_index.py (wenn Prefix-Regeln geändert)
3. pnpm arch:validate — muss grün sein
4. pnpm arch:drift — bei strukturellen Änderungen (strict wie CI)
5. Impact Note ausfüllen: docs/architecture/agents/impact-note-template.md
6. Workboard + Open-Gaps bei Liefer-Gaps aktualisieren

## CLI-Befehle

pnpm arch:render    # C4 Context/Container aus workspace.dsl generieren
pnpm arch:validate  # Generatoren + Drift (non-strict) — vor Abschluss grün
pnpm arch:drift     # Domänen-Drift strict — wie CI

## Prefix-Regeln (verbindlich)

Single Source of Truth: config/architecture-domain-prefixes.yaml

Jeder neue Route-Segment (Frontend), Service-Prefix (Backend-Module) oder Endpoint-Stem (API-Router) MUSS dort unter der passenden domains.<name> eingetragen werden, bevor der Task abgeschlossen gilt.

Danach: python scripts/generate_architecture_index.py ausführen und pnpm arch:validate.

Unmapped routes/services führen zu Drift-Warnungen bzw. CI-Failure im strict-Modus.

## Impact Note

Bei jeder strukturellen Änderung Impact Note aus docs/architecture/agents/impact-note-template.md ausfüllen (Handoff, PR-Beschreibung oder docs/agent-ops/handoffs/). Pflichtfelder: Domain(s), Entscheidungsstufe, betroffene Artefakte-Checkboxen, Drift-Check-Ergebnis.

## Entscheidungsstufen

| Stufe | Beispiel | Pflicht |
|---|---|---|
| Minor | Interner Rename, Doc-Fix, Bugfix ohne Vertrag | Index/Views optional |
| Significant | Neuer Endpoint-Cluster, Service-Modul, Event-Typ | ADR Proposed, Index, Domain Pack, Prefix-Mapping |
| Strategic | Neuer Bounded Context, Mandantenmodell, Auth-Modell | ADR Accepted + Human Approval vor Merge |

## First-Run-Checkliste (Architecture OS zum ersten Mal)

- [ ] AGENTS.md und architecture-protocol.md gelesen
- [ ] config/architecture-index.yaml — Domänen-Inventar verstanden
- [ ] config/architecture-domain-prefixes.yaml — Prefix-Schema verstanden
- [ ] pnpm arch:validate lokal ausgeführt und grün
- [ ] pnpm arch:drift ausgeführt — offene Warnungen notiert oder behoben
- [ ] Ein Domain Pack (z. B. docs/architecture/domains/crm/) als Muster gelesen
- [ ] Impact Note Template geöffnet und Format verstanden
- [ ] Active Workboard — ARCH-OS-Slices und offene Arbeit geprüft

## Referenzen

- ADR-037 Structurizr DSL als C4-Quelle: docs/adr/adr-037-structurizr-c4-source-of-truth.md
- ARCH-OS Slices: docs/agent-ops/slices/ARCH-OS-001.yaml … ARCH-OS-006.yaml
- Quality Gates / Drift: docs/architecture/quality-gates/architecture-drift-checks.md
- Architecture Protocol: docs/architecture/agents/architecture-protocol.md
- Workboard ARCH-OS: docs/agent-ops/active-workboard.md (Abschnitt ARCH-OS)

## Nicht verhandelbar

- Process Kernel (docs/architecture/process-kernel/STATUS.md) = Lieferstatus, nicht Domänen-Inventar duplizieren
- workspace.dsl generierte Views (c4-01, c4-02) nicht manuell editieren — nur via render_c4_views.py
- architecture-index.yaml nicht manuell editieren — nur via Generator nach Prefix-Änderung
- Code ohne Doku-Update (Index, Domain Pack, ADR, Tests) gilt bei strukturellen Änderungen nicht als abgeschlossen
```

---

## Weiterführend

- [Architecture Agent Protocol](architecture-protocol.md)
- [Impact Note Template](impact-note-template.md)
- [ADR-037](../../adr/adr-037-structurizr-c4-source-of-truth.md)
- [Architecture Drift Checks](../quality-gates/architecture-drift-checks.md)
- [Active Workboard — ARCH-OS](../../agent-ops/active-workboard.md)
