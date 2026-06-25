# Governance Rollout Summary

Stand: 2026-03-19

## Zweck

Diese Datei ist eine kompakte `abgeleitete Sicht` auf den aktuellen Rollout-Stand der Markdown-Governance. Sie richtet sich an neue Agenten und Mitwirkende, die schnell verstehen muessen, welche Dokumentklassen bereits verbindlich geprueft werden und wo die operative Wahrheit liegt.

## Operative Wahrheit

Die wichtigsten Source-of-Truth-Dokumente sind:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/architecture/process-kernel/wave-*/STATUS.md`
- [PLAN_GAPS_023_024_043_049.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/PLAN_GAPS_023_024_043_049.md)

Abgeleitete operative Sichten sind insbesondere:

- [DELIVERY-MAP.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/DELIVERY-MAP.md)
- [DEVELOPMENT-MAP.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/DEVELOPMENT-MAP.md)
- `docs/roadmap/status/*.md`

## Bereits gehaertet

Diese Dokumentklassen laufen aktuell unter Repo-Checks:

- globale und wave-spezifische `STATUS.md`
- `PLAN_GAPS_*.md`
- gehaertete `docs/roadmap/status/*.md`
- `wave-*/package-*/STATUS.md`
- zentrale Referenzdokumente:
  - [docs/architecture/index.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/index.md)
  - [docs/AI-VISION.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/AI-VISION.md)
  - [docs/AGENT-INTEGRATION.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/AGENT-INTEGRATION.md)
- ADR-Bestand unter `docs/adr/*.md`

## Bewusst nicht hart geregelt

Diese Bereiche bleiben vorerst locker oder ausgenommen:

- [README.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/README.md) nur teilweise renoviert, aber nicht im harten Governance-Checker
- `docs/archive/**`
- `swarm/**`
- modul- und service-lokale Doku ohne Statusrelevanz
- historische Roadmap-Dateien ausserhalb des bereits gehaerteten Teilbestands

## Was die Checks aktuell pruefen

- H1 in Zeile 1
- Pflichtabschnitte je Dokumentklasse
- Datumsformat `YYYY-MM-DD`
- erlaubte Statuswerte in Steuerungsdokumenten
- Einordnungs- und Referenzhinweise bei abgeleiteten Sichten
- minimale ADR-Metadaten und Kernabschnitte
- Markdown-Hygiene wie fehlende Heading-Spaces, Tabs, Trailing Whitespace und offene Code-Fences

## Relevante Skripte

- [docs-markdown-check.cjs](c:/Users/Jochen/VALEO-NeuroERP-3.0/scripts/docs-markdown-check.cjs)
- [docs-governance-check.cjs](c:/Users/Jochen/VALEO-NeuroERP-3.0/scripts/docs-governance-check.cjs)
- [markdown-governance.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/standards/markdown-governance.md)
- [docs-governance.yml](c:/Users/Jochen/VALEO-NeuroERP-3.0/.github/workflows/docs-governance.yml)

## Neue Analyse-Leitfaeden

Fuer workflow- und UI-zentrierte Prozessanalysen stehen jetzt zusaetzlich bereit:

- [docs/README.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/README.md)
- [AGENTS.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/AGENTS.md)
- [Agent Ops README](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/README.md)
- [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md)
- [System Overview](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/system-overview.md)
- [Domain Landhandel und Agrarhandel](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/domain-landhandel-und-agrarhandel.md)
- [Workflow Analysis Master Prompt](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/workflows/workflow-analysis-master-prompt.md)
- [Card Template](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/cards/card-template.md)
- [Browser-Use Checklists](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/quality-assurance/browser-use-checklists.md)

## Arbeitsregel fuer neue Agenten

- Erst pruefen, ob ein Dokument Source of Truth oder abgeleitete Sicht ist.
- Steuerungsdokumente nicht frei umformulieren; nur innerhalb des vorgegebenen Schemas aendern.
- Historische Dokumente nicht in aktuelle Ist-Aussagen umdeuten.
- Bei neuen statusrelevanten Dokumenttypen zuerst das Governance-Dokument erweitern, dann Inhalte anpassen.
- Vor Workflow-Analyse oder UI-Validierung immer zuerst `docs/README.md` und den relevanten Kontext unter `docs/project-context/` lesen.

## Referenzen

- [Markdown Governance](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/standards/markdown-governance.md)
- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- [ADR Index](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/adr/README.md)
