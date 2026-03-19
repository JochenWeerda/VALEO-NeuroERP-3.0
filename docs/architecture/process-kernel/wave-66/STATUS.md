# Wave 66 - Concurrency + Resource Lock Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-18
**Tests:** 163 gruen, 0 Fehler

## Scope

Wave 66 fuehrt Konkurrenzsteuerung fuer parallele Ausfuehrung und Ressource-Locks mit Deadlock-Erkennung ein.

## Zielbild

Ausfuehrungslimits und Locking sollen als standardisierte Kernel-Contracts fuer sichere Parallelverarbeitung bereitstehen.

## Lieferumfang

### `app/core/process_concurrency_contracts.py`

- `KonkurrenzModus`
- `AusfuehrungsSlotStatus`
- `KonkurrenzRegel.effektives_limit()`
- `AusfuehrungsSlot.ist_abgelaufen()`
- `AusfuehrungsSlot.ist_verfuegbar()`
- `KonkurrenzWaechter`

### `app/core/workflow_resource_lock_contracts.py`

- `RessourceLockTyp`
- `DeadlockStatus`
- `RessourceLock.__post_init__()`
- `pruefe_lock_kompatibilitaet()`
- `erkenne_deadlock()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/process/konkurrenz/waechter` | Alle Konkurrenz-Waechter mit Auslastung |
| POST | `/process/konkurrenz/pruefe-ausfuehrbarkeit` | Prueft, ob Ausfuehrung moeglich ist |
| GET | `/process/resource-lock/locks` | Alle Ressource-Locks mit Aktiv-Status |
| POST | `/process/resource-lock/erkenne-deadlock` | Deadlock-Erkennung via Warte-Relationen |

## Abnahmekriterien

- Konkurrenzregeln berechnen effektive Limits und Auslastung reproduzierbar.
- Ressource-Locks pruefen Kompatibilitaet und erkennen Deadlocks ueber Wartegraphen.
- Default-Waechter und Default-Locks stehen bereit.
- Die vier API-Endpunkte liefern Konkurrenz- und Lock-Funktionen.

## Tests

**Anzahl:** 163

## Status

`abgeschlossen`
Stand: 2026-03-18
