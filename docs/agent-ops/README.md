---
title: Agent Ops — Ueberblick
type: explanation
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Ueberblick ueber den Agent-Ops-Bereich — parallele Agentenarbeit restart-sicher und konfliktarm gestalten; Verzeichnisstruktur und Verantwortlichkeiten.
---

# Agent Ops

## Zweck

Dieser Bereich macht parallele Agentenarbeit restart-sicher, konfliktarm und kontextstabil.

Er ist bewusst klein gehalten und ergaenzt die bestehende Fach- und Statusdokumentation.

## Wann dieser Bereich benutzt wird

- wenn zwei oder mehr Agenten parallel arbeiten
- wenn Arbeit nach Session-Neustart schnell fortgesetzt werden muss
- wenn ein Slice an einen anderen Agenten uebergeben wird
- wenn unklar ist, welche Dateien oder Themen bereits in Bearbeitung sind

## Kernprinzip

Nicht die komplette Doku lesen, sondern zuerst den kleinsten moeglichen verlaesslichen Kontext laden:

1. [AGENTS.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/AGENTS.md)
2. [Session Start Checklist](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/session-start-checklist.md)
3. [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md)
4. passenden Handoff oder Resume-Block
5. erst dann Fach- und Workflow-Doku

## Dateien

- [Session Start Checklist](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/session-start-checklist.md)
- [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md)
- [Parallel Work Protocol](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/parallel-work-protocol.md)
- [Task Slice Template](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/task-slice-template.md)
- [Handoff Template](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/handoff-template.md)
- [Resume Packet Template](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/resume-packet-template.md)

## Beziehung zur restlichen Doku

- Liefer- und Reifegrad: `docs/architecture/process-kernel/STATUS.md`
- Fachlicher Kontext: `docs/project-context/`
- Workflow-Methode und Prompting: `docs/workflows/`
- QA und Browser-Use: `docs/quality-assurance/`

## Regel fuer neue Agenten

Wenn du eine Aufgabe uebernimmst:

- reserviere oder aktualisiere zuerst den Slice im Workboard
- arbeite nur in deinem Dateibesitz oder mit explizit dokumentierter Ueberschneidung
- schreibe vor Abschluss einen Handoff oder Resume-Block

## AI-Harness fuer neue Slices

Neue Agenten-Slices verwenden den erweiterten Harness aus
[Task Slice Template](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/task-slice-template.md).
Damit werden fachlicher Vertrag, Architekturvertrag, Datenvertrag, Testvertrag,
Security-Vertrag, Betriebsvertrag, Dokumentationsvertrag und externe Gates
vor der Umsetzung sichtbar. Die Governance-Scripts pruefen neue oder
geaenderte Slice-YAMLs auf diese Mindestfelder.

## Doku-Governance bei Archivierungen

`scripts/docs-governance-check.cjs` prueft eine kuratierte Default-Liste plus
ADR-, Roadmap- und Package-Statusdateien. Wenn Legacy-Dokumente nach
`docs/_internal/archive/` verschoben werden, duerfen alte Default-Ziele nicht
mehr hart als fehlende Dateien scheitern. Der Check filtert deshalb nicht mehr
existierende Default-Targets vor der Inhaltspruefung; vorhandene Dateien und
explizit uebergebene Ziele bleiben weiterhin strikt geprueft.
