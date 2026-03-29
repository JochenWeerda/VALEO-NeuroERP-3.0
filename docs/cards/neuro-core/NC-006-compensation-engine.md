# NC-006 — Compensation Engine

**Lane:** Neuro-Core
**Prioritaet:** P1 (Architektur-kritisch)
**Status:** umgesetzt

## Kontext
Bei Tool-Fehlern oder API-Ausfaellen waehrend der Ausfuehrung koennen inkonsistente Business-Zustaende entstehen. Ohne Compensation-Mechanismus bleiben fehlgeschlagene Aktionen in einem undefinierten Zustand.

## Loesung
Eine Compensation Engine mit konfigurierbaren Strategien (Retry mit linearem/exponentiellem Backoff, Rollback-Ketten, alternative Pfade, Eskalation) behandelt Fehler systematisch und stellt konsistente Zustaende wieder her.

## Dateien
- `app/services/compensation_engine.py` — Kern-Service
- `app/api/v1/endpoints/neuro_compensate.py` — REST-API
- `docs/workflows/nc-006-compensation-engine.md` — Workflow-Doku
