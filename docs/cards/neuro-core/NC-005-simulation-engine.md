# NC-005 — Neuro Simulation Engine (Dry-Run)

**Lane:** Neuro-Core
**Prioritaet:** P1 (Architektur-kritisch)
**Status:** umgesetzt

## Kontext
Neue Regeln und Policies muessen vor dem Rollout getestet werden koennen, ohne reale Seiteneffekte auszuloesen. Ohne Simulation fehlt die Moeglichkeit, Edge Cases und What-If-Szenarien sicher zu validieren.

## Loesung
Eine Simulation Engine erstellt Sandbox-Kopien, fuehrt den Planner und die Verification Engine im Dry-Run-Modus aus und liefert Ergebnisberichte ohne Seiteneffekte — inklusive What-If-Vergleich und Stress-Tests.

## Dateien
- `app/services/simulation_engine.py` — Kern-Service
- `app/api/v1/endpoints/neuro_simulate.py` — REST-API
- `docs/workflows/nc-005-simulation-engine.md` — Workflow-Doku
