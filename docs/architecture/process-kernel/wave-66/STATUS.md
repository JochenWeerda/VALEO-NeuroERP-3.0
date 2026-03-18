# Wave 66 — Concurrency + Resource Lock Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-18
**Tests:** 163 grün, 0 Fehler

## Module

### `app/core/process_concurrency_contracts.py`
Concurrent Execution Limits und Mutex-Muster:
- `KonkurrenzModus` (MUTEX, SEMAPHORE, READ_WRITE, SINGLE_WRITER)
- `AusfuehrungsSlotStatus` (FREI, BELEGT, RESERVIERT)
- `KonkurrenzRegel.effektives_limit()` — MUTEX erzwingt Limit 1
- `AusfuehrungsSlot.ist_abgelaufen()` / `ist_verfuegbar()`
- `KonkurrenzWaechter.belegte_slots()` / `kann_ausfuehren()` / `auslastung_pct()`
- Default-Fixtures: KW-001 (MUTEX, 100% ausgelastet), KW-002 (SEMAPHORE max=3, 2/3 belegt)

### `app/core/workflow_resource_lock_contracts.py`
Feingranulares Ressource-Locking mit Deadlock-Erkennung:
- `RessourceLockTyp` (EXKLUSIV, GETEILT, UPGRADE)
- `DeadlockStatus` (KEIN_DEADLOCK, DEADLOCK_ERKANNT, DEADLOCK_AUFGELOEST)
- `RessourceLock.__post_init__()` — ablauf_am = erstellt_am + ttl_sekunden
- `pruefe_lock_kompatibilitaet()` — GETEILT+GETEILT und UPGRADE+GETEILT kompatibel
- `erkenne_deadlock()` — DFS-Zykluserkennung in Warte-Graphen
- Default-Fixtures: RL-001 (EXKLUSIV aktiv), RL-002/003 (GETEILT aktiv), RL-004 (expired)

## FastAPI Endpoints (process_kernel_api.py)

| Method | Path | Beschreibung |
|--------|------|-------------|
| GET | `/process/konkurrenz/waechter` | Alle Konkurrenz-Waechter mit Auslastung |
| POST | `/process/konkurrenz/pruefe-ausfuehrbarkeit` | Prüfe ob Ausführung möglich |
| GET | `/process/resource-lock/locks` | Alle Ressource-Locks mit Aktiv-Status |
| POST | `/process/resource-lock/erkenne-deadlock` | Deadlock-Erkennung via Warte-Relationen |

## Testergebnisse

- 163 Tests, alle grün
- Keine Regressionen (39 vorbestehende Fehler unverändert)
