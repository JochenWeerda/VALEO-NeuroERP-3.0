# NC-E — Fast Track + Compensation

**Lane:** Neuro-Core (Lane E)
**Prioritaet:** P2
**Status:** umgesetzt (E1-E2, E3-E5 via NC-006)

## Kontext
Standard-CRUD-Operationen (Artikel lesen, Kunden listen) brauchen keinen AI-Overhead.
Ein deterministischer Bypass beschleunigt diese Requests erheblich.

## Loesung
FastTrackClassifier mit konfigurierbarer Whitelist und Pattern-Matching.
GET auf Stammdaten immer Fast Track. Neuro-Pfade und Finance-Closing nie.
Compensation Engine (NC-006) fuer Fehlerbehandlung bei beiden Pfaden.

## Dateien
- `app/services/fast_track.py` — Classifier + Router
- `app/api/v1/endpoints/neuro_fast_track.py` — REST-API
- `docs/workflows/nc-e-fast-track-compensation.md` — Workflow-Doku
