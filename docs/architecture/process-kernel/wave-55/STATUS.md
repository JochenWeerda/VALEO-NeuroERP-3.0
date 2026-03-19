# Wave 55 - Priority Queue + Rollback Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 139 gruen, 0 Fehler

## Scope

Wave 55 ergaenzt Prioritaetswarteschlangen fuer operative Steuerung und Rollback-Contracts fuer kontrollierte Rueckabwicklung.

## Zielbild

Aufgabenpriorisierung und Ruecksetzlogik sollen als wiederverwendbare Contracts reproduzierbar und API-faehig im Kernel verfuegbar sein.

## Lieferumfang

### `app/core/process_priority_contracts.py`

- `AufgabenPrioritaet`
- `WarteschlangenStatus`
- `PRIORITAET_GEWICHT`
- `PrioritaetsAufgabe`
- `PrioritaetsWarteschlange`
- `get_default_warteschlangen()`

### `app/core/workflow_rollback_contracts.py`

- `RollbackTyp`
- `RollbackStatus`
- `UmkehrbarkeitsGrad`
- `RollbackSchritt`
- `RollbackPlan`
- `get_default_rollback_plaene()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/process/prioritaet/warteschlangen` | Alle Warteschlangen mit Tiefe und naechster Aufgabe |
| POST | `/process/prioritaet/sortiere` | Aufgaben nach Prioritaet sortieren |
| GET | `/process/rollback/plaene` | Alle Rollback-Plaene mit Fortschritt |
| POST | `/process/rollback/pruefe-ausfuehrbarkeit` | Ausfuehrbarkeit eines Plans pruefen |

## Abnahmekriterien

- Warteschlangen koennen Aufgaben nach Prioritaet sortieren und naechste Aufgaben liefern.
- Rollback-Plaene bilden Ausfuehrbarkeit und Fortschritt korrekt ab.
- Default-Warteschlangen und Default-Rollback-Plaene stehen bereit.
- Die vier API-Endpunkte liefern Warteschlangen- und Rollback-Funktionen.

## Tests

- Gesamt: 139
- Priority Queue: 75
- Rollback: 64
- Regressions-Check: bestehende Tests weiterhin gruen

## Status

`abgeschlossen`
Stand: 2026-03-16
