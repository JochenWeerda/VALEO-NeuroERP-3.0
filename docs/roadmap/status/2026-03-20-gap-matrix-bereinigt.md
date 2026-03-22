# Bereinigte Gap-Matrix 2026-03-20

**Zweck:** Finaler Abgleich zwischen strategischem Gap-Backlog, belastbaren `wave-*/STATUS.md`-Nachweisen, vorhandenen Tests und dem aktuellen Code-Stand.

## Ziel

Diese Datei beschreibt die operative Zwischenwahrheit nach den Waves `81`, `84`, `85`, `89`, `90` sowie `91` bis `98`.
Sie ersetzt weder die historischen Priorisierungen noch die Detailnachweise pro Wave, sondern verdichtet den tatsaechlichen Lieferstand.

## Statusabgleich

- Strategische Quelle: `docs/roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md`
- Liefernachweise: `docs/architecture/process-kernel/wave-*/STATUS.md`
- Aggregierte Delivery-Sicht: `docs/architecture/process-kernel/STATUS.md`
- Direkter Vergleich zum Backlog: [Top-50 Gap Backlog 2026-03-06](2026-03-06-top-50-gap-backlog-landhandel.md)
- Wichtige Feststellung:
  - Der fruehere Restgap-Stand war durch spaetere Waves und nachgezogene Tests ueberholt.
  - Fuer `008`, `012`, `016`, `018` liegt der Abschluss aktuell ueber belastbare Code-/API-/Test-Artefakte vor, auch wenn die historische Backlog-Sicht diese Gaps noch nicht sauber nachgezogen hatte.
  - Mit Wave `100` liegt jetzt auch fuer `004` ein expliziter Abschlussvertrag ueber Gutschrift, Belastung und Korrektur vor.

## Bewertungslogik

- `geschlossen`: belastbarer Wave- oder Test-/Code-Nachweis vorhanden
- `teilweise`: technisch weit geliefert, aber formale Endabnahme ueber Varianten oder KPI-Nachweis noch offen
- `offen`: aktuell keine belastbare Abschlusslage

## Gap-Matrix

| Gap | Strategischer Backlog | Technischer Ist-Stand | Beleg | Restluecke / naechster Schritt |
|---|---|---|---|---|
| 001 | offen | geschlossen | `wave-85/STATUS.md` | Backlog-Status nachziehen |
| 002 | offen | geschlossen | `wave-91/STATUS.md`, `wave-92/STATUS.md` | Backlog-Status nachziehen |
| 003 | offen | geschlossen | `wave-26/STATUS.md` | Backlog-Status nachziehen |
| 004 | offen | geschlossen | `wave-19/STATUS.md`, `wave-100/STATUS.md` | Backlog-Status nachziehen |
| 008 | offen | geschlossen | `tests/test_process_kernel_wave8_complaint_e2e.py`, `app/core/reklamation.py`, `app/api/v1/endpoints/reklamation_api.py` | Historische Backlog-/Wave-Referenz bei Gelegenheit angleichen |
| 011 | offen | geschlossen | `wave-26/STATUS.md`, `wave-86/STATUS.md` | Backlog-Status nachziehen |
| 012 | offen | geschlossen | `tests/test_process_kernel_wave86_workflow_sandbox.py`, `app/core/workflow_simulation.py`, `app/api/v1/endpoints/workflow_simulation.py` | Historische Backlog-/Wave-Referenz bei Gelegenheit angleichen |
| 016 | offen | geschlossen | `app/core/action_idempotency.py`, `app/api/v1/endpoints/idempotency_monitoring.py`, `packages/frontend-web/src/components/agent/IdempotencyMonitoringPanel.tsx` | Monitoring-/Audit-Nachweis zentral referenziert, Backlog nachziehen |
| 017 | offen | geschlossen | `wave-31/STATUS.md` | Backlog-Status nachziehen |
| 018 | offen | geschlossen | `tests/test_process_kernel_wave87_process_mining_observation.py`, `app/core/process_mining_observation.py`, `app/api/v1/endpoints/process_mining_observation.py` | Historische Backlog-/Wave-Referenz bei Gelegenheit angleichen |
| 019 | offen | geschlossen | `wave-81/STATUS.md` | Backlog-Status nachziehen |
| 020 | offen | geschlossen | `wave-90/STATUS.md` | Backlog-Status nachziehen |
| 021 | offen | geschlossen | `wave-84/STATUS.md`, `wave-91/STATUS.md` | Backlog-Status nachziehen |
| 023 | offen | geschlossen | `wave-77/STATUS.md`, `wave-91/STATUS.md`, `wave-94/STATUS.md`, `wave-95/STATUS.md`, `wave-96/STATUS.md`, `wave-97/STATUS.md`, `wave-98/STATUS.md` | Backlog-Status nachziehen |
| 024 | offen | geschlossen | `wave-76/STATUS.md`, `wave-91/STATUS.md`, `wave-92/STATUS.md` | Backlog-Status nachziehen |
| 026 | offen | geschlossen | `wave-35/STATUS.md` | Backlog-Status nachziehen |
| 028 | offen | geschlossen | `wave-35/STATUS.md` | Backlog-Status nachziehen |
| 029 | offen | geschlossen | `wave-93/STATUS.md`, `wave-98/STATUS.md`, `packages/frontend-web/src/__tests__/components/agent/AgentUxPanel.test.tsx` | Backlog-Status nachziehen |
| 030 | offen | geschlossen | `wave-89/STATUS.md` | Backlog-Status nachziehen |
| 032 | offen | geschlossen | `wave-32/STATUS.md` | Backlog-Status nachziehen |
| 033 | offen | geschlossen | `wave-32/STATUS.md` | Backlog-Status nachziehen |
| 034 | offen | geschlossen | `wave-33/STATUS.md` | Backlog-Status nachziehen |
| 036 | offen | geschlossen | `wave-33/STATUS.md` | Backlog-Status nachziehen |
| 037 | offen | geschlossen | `wave-87/STATUS.md` | Backlog-Status nachziehen |
| 038 | offen | geschlossen | `wave-34/STATUS.md` | Backlog-Status nachziehen |
| 040 | offen | geschlossen | `wave-31/STATUS.md` | Backlog-Status nachziehen |
| 043 | offen | geschlossen | `wave-36/STATUS.md` | Backlog-Status nachziehen |
| 044 | offen | geschlossen | `wave-36/STATUS.md` | Backlog-Status nachziehen |
| 045 | offen | geschlossen | `wave-37/STATUS.md` | Backlog-Status nachziehen |
| 046 | offen | geschlossen | `wave-38/STATUS.md` | Backlog-Status nachziehen |
| 047 | offen | geschlossen | `wave-38/STATUS.md` | Backlog-Status nachziehen |
| 048 | offen | geschlossen | `wave-37/STATUS.md` | Backlog-Status nachziehen |
| 049 | offen | geschlossen | `wave-34/STATUS.md` | Backlog-Status nachziehen |

## Produktfachlich verbleibende Restgaps

Auf Basis der aktuell belastbaren Repo-Nachweise verbleiben derzeit keine produktfachlich offenen Top-50-Restgaps.

## Gaps mit historischem Doku-Nachzug, aber ohne echte Produktluecke

- `008` Reklamationsprozesse E2E
- `012` Simulation/Sandbox fuer neue Workflows
- `016` Idempotente Business-Commands mit Monitoring/Audit
- `018` Ereignisbasierte Prozessbeobachtung
- `029` Agent UX Panel
- `030` Multilingual + Fachsprache Landhandel

## Folgeaktion

1. Strategischen Top-50-Backlog auf die hier als `geschlossen` markierten Gaps nachziehen.
2. `STATUS.md` auf Waves `89` bis `100` und den final geschlossenen Restgap-Stand angleichen.
3. Rest-Roadmap archivieren oder in einen Abschlussvermerk ueberfuehren.
