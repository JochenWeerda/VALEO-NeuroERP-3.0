---
title: Session Start Checklist
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Pflichtschritte beim Start einer neuen Agenten-Sitzung — Workboard lesen, Memory laden, Branch pruefen, Governance-Gates.
---

# Session Start Checklist

## Zweck

Diese Checkliste minimiert Kontextverlust bei Neustarts oder Agentenwechseln.

## Reihenfolge

1. [AGENTS.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/AGENTS.md) lesen
2. [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md) lesen
3. passenden Handoff oder Resume-Block lesen
4. betroffene Source-of-Truth-Dateien oeffnen
5. offenen Dateibesitz und Risiken pruefen
6. erst dann in Code oder Tests einsteigen

## Pflichtfragen

- Was ist das aktuelle Ziel?
- Welche Dateien sind bereits in Bearbeitung?
- Welche Risiken oder Blocker bestehen?
- Welche Annahmen wurden bereits getroffen?
- Welche Tests oder Checks sind Pflicht?
- Welche Doku muss nachgezogen werden?

## Vor dem ersten Edit

- **Ist-Stand pruefen:** Code, Tests, Workboard, `open-gaps-and-known-issues.md` und
  betroffene Slice-/Handshake-Doku lesen — nicht erneut implementieren, was bereits
  erledigt oder parallel in Arbeit ist
- eigenen Slice im Workboard aktualisieren
- klaren Dateibesitz oder Themenbesitz festhalten
- bei Ueberschneidung mit anderem Agenten Integrationspunkt dokumentieren

## Nach jeder relevanten Aenderung (Pflicht)

- Workboard-Stand und Slice-YAML (`status`, Ergebnis, offene Risiken)
- betroffene Fach-/Operations-Doku (`open-gaps`, Runbooks, Handshakes)
- README-/Index-Verweise, wenn neue Artefakte oder Gates entstehen
- **nicht** nur Code committen und Doku offen lassen
