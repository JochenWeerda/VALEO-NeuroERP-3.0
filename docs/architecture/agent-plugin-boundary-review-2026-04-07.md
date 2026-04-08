# Agent Plugin Boundary Review (2026-04-07)

## Zweck

Diese Notiz konkretisiert `PCP-012` fuer Paperclip-inspirierte Erweiterungen im VALEO-Kern.

## Erlaubte Muster

- Budget-, Kosten- und Heartbeat-Steuerung um bestehende NeuroASSIST-Runs
- UI-Surfaces als duenne Wrapper ueber bestehende Agent-Ops-Endpoints
- Export/Import von Templates ohne Secret-Material
- Skill-Pack-Manifeste, die auf bestehende Capability-, Prompt- und Handoff-Vertraege zeigen

## Verbotene Muster

- zweiter Orchestrator neben NeuroASSIST
- zweite Tool-Registry neben Command-Manifest und Superglue
- Plugins, die Approval-, Policy- oder Audit-Senken umgehen
- Einbettung einer externen "company control plane" als produktiver ERP-Kern

## Begruendung

- VALEO behaelt genau einen internen Agent-Orchestrierungspfad.
- Governance, Secrets, Audit und Policy bleiben VALEO-eigene Kernverantwortung.
- Externe Systeme duerfen Funktionalitaeten ergaenzen, aber nicht die Steuerhoheit uebernehmen.
