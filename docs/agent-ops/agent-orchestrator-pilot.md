---
title: Agent Orchestrator Pilot
type: explanation
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Pilotentwurf fuer einen Agent-Orchestrator — Aufgabenverteilung, Tool-Routing und Koordinationsmuster fuer mehrere parallele Agenten (Stand 2026-05-05).
---

# Agent Orchestrator Pilot

Stand: `2026-05-05`

## Zweck

Dieser Pilot nutzt Symphony als Blaupause, bleibt aber bewusst kleiner:
Das Workboard bleibt die Steuerzentrale, und der Supervisor arbeitet zunaechst read-only.

Ziel ist nicht, Agents automatisch zu starten oder Git-Operationen zu uebernehmen.
Ziel ist, offene Slices schneller, einheitlicher und restart-sicherer vorzubereiten.

## Scope AGENT-ORCH-001

Der erste Pilot liefert:

- Workboard-Slice-Erkennung aus `docs/agent-ops/active-workboard.md`
- Statusklassifikation: `open`, `reserved`, `in_progress`, `done`, `unknown`
- Claim-Vorschlag fuer offene Slices
- Check-Kommando-Ausgabe je Slice
- optionales Ausfuehren dokumentierter Checks per explizitem `--run`
- Handoff-Template je Slice

Der Pilot macht nicht:

- keine automatische Workboard-Aenderung
- kein automatischer Commit
- kein Push oder PR
- kein Starten paralleler Agenten
- keine Uebernahme reservierter oder laufender Slices

## Kommandos

Offene Slices anzeigen:

```bash
python scripts/agent_workboard_supervisor.py list --status open
```

Alle Slices als JSON anzeigen:

```bash
python scripts/agent_workboard_supervisor.py list --json
```

Claim-Vorschlag erzeugen:

```bash
python scripts/agent_workboard_supervisor.py claim-proposal DOM-FIN-002 --owner Codex
```

Checks fuer einen Slice anzeigen:

```bash
python scripts/agent_workboard_supervisor.py checks COV-FIN-003
```

Checks bewusst ausfuehren:

```bash
python scripts/agent_workboard_supervisor.py checks COV-FIN-003 --run
```

Handoff-Template erzeugen:

```bash
python scripts/agent_workboard_supervisor.py handoff-template AGENT-ORCH-001 --owner Codex
```

## Sicherheitsregeln

- Der Supervisor ist read-only, bis ein spaeterer Slice anderes explizit freigibt.
- Ein Claim bleibt ein manueller Workboard-Edit plus separater Claim-Commit.
- Ein Slice mit `reserviert` oder `in arbeit` erzeugt keinen Claim-Vorschlag.
- Unklare Statuswerte werden als `unknown` klassifiziert.
- Dokumentierte Checks werden nur mit `--run` ausgefuehrt.

## Naechste Ausbaustufen

1. Maschinenlesbare Slice-Dateien unter `docs/agent-ops/slices/` einfuehren.
2. Workboard-Parser als Validierungs-Gate fuer Claim-Pflicht nutzen.
3. Check-Ergebnisse in einen Resume-/Handoff-Block schreiben.
4. Optional einen lokalen Agent-Launcher anbinden, der nur bereits reservierte Slices verarbeitet.
