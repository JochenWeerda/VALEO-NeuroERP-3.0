# Wave 55 — Priority Queue + Rollback Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-16
**Tests:** 139 grün, 0 Fehler

## Module

### `app/core/process_priority_contracts.py`
- `AufgabenPrioritaet` (KRITISCH/HOCH/MITTEL/NIEDRIG/HINTERGRUND, P0–P4)
- `WarteschlangenStatus` (WARTEND/VERARBEITUNG/ABGESCHLOSSEN/ABGEBROCHEN)
- `PRIORITAET_GEWICHT` — Gewichtsmapping 0–4
- `PrioritaetsAufgabe` — Aufgabe mit sort_schluessel()
- `PrioritaetsWarteschlange` — naechste_aufgabe(), aufgaben_nach_prioritaet(), warteschlangen_tiefe()
- `get_default_warteschlangen()` — 2 Beispiel-Warteschlangen (WS-001 mit 5 Aufgaben, WS-002 leer)

### `app/core/workflow_rollback_contracts.py`
- `RollbackTyp` (VOLLSTAENDIG/TEILWEISE/SCHRITT)
- `RollbackStatus` (AUSSTEHEND/LAUFEND/ABGESCHLOSSEN/FEHLGESCHLAGEN/NICHT_MOEGLICH)
- `UmkehrbarkeitsGrad` (VOLLSTAENDIG/TEILWEISE/NICHT_UMKEHRBAR)
- `RollbackSchritt` — kann_ausgefuehrt_werden()
- `RollbackPlan` — ausfuehrbare_schritte(), ist_vollstaendig_ausfuehrbar(), rollback_fortschritt_pct()
- `get_default_rollback_plaene()` — 3 Beispiel-Pläne (RP-001 vollständig ausführbar, RP-002 teilweise, RP-003 leer)

## FastAPI Endpoints (in `process_kernel_api.py`)

| Method | Path | Beschreibung |
|--------|------|--------------|
| GET | `/process/prioritaet/warteschlangen` | Alle Warteschlangen mit Tiefe und nächster Aufgabe |
| POST | `/process/prioritaet/sortiere` | Aufgaben nach Priorität sortieren |
| GET | `/process/rollback/plaene` | Alle Rollback-Pläne mit Fortschritt |
| POST | `/process/rollback/pruefe-ausfuehrbarkeit` | Ausführbarkeit eines Plans prüfen |

## Testergebnisse

- Gesamt: 139 Tests
- Priority Queue Tests: 75
- Rollback Tests: 64
- Alle grün, 0 Fehler
- Regressions-Check: 3730 bestehende Tests weiterhin grün (3 Pre-existing Failures in wave4 unverändert)
