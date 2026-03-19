# Wave 63 - Process Validation + Workflow Collaboration Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-18
**Tests:** 150 passed, 0 failed

## Scope

Wave 63 erweitert den Kernel um Validierungs-Contracts fuer Geschaeftsregeln und Kollaborations-Contracts fuer gemeinsame Entscheidungen.

## Zielbild

Datenvalidierung und teamuebergreifende Entscheidungslogik sollen als standardisierte Kernel-Contracts verfuegbar sein.

## Lieferumfang

### `app/core/process_validation_contracts.py`

- `ValidierungsSchwere`
- `RegelTyp`
- `ValidierungsStatus`
- `ValidierungsRegel.pruefe()`
- `validiere_daten()`
- fuenf Default-Regeln

### `app/core/workflow_collaboration_contracts.py`

- `AbstimmungsTyp`
- `StimmeTyp`
- `KollaborationsEntscheidung.berechne_ergebnis()`
- `KollaborationsEntscheidung.ausstehende_stimmer()`
- `KollaborationsEntscheidung.beteiligung_pct()`
- drei Default-Entscheidungen

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process/validierung/regeln` | Alle Validierungsregeln |
| POST | `/api/v1/process/validierung/pruefe` | Datensatz gegen Regeln pruefen |
| GET | `/api/v1/process/kollaboration/entscheidungen` | Alle Kollaborationsentscheidungen |
| POST | `/api/v1/process/kollaboration/pruefe-ergebnis` | Einzelentscheidung berechnen |

## Abnahmekriterien

- Validierungsregeln koennen Pflichtfeld-, Wertebereich-, Format-, Querverweis- und Geschaeftsregeln auswerten.
- Kollaborationsentscheidungen berechnen Ergebnisse fuer Mehrheit, Einstimmigkeit und Veto korrekt.
- Default-Regeln und Default-Entscheidungen stehen bereit.
- Die vier API-Endpunkte liefern Validierungs- und Kollaborationsfunktionen.

## Tests

**Anzahl:** 150

## Status

`abgeschlossen`
Stand: 2026-03-18
