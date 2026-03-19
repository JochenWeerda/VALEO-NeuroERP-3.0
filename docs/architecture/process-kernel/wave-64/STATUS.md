# Wave 64 - Data Lineage + Process Simulation Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-18
**Tests:** 173 gruen, 0 Fehler

## Scope

Wave 64 fuehrt Data-Lineage-Contracts fuer Datenflussbeziehungen und Simulations-Contracts fuer Prozessszenarien ein.

## Zielbild

Datenherkunft und Prozesssimulation sollen als standardisierte, API-faehige Kernel-Bausteine verfuegbar sein.

## Lieferumfang

### `app/core/process_lineage_contracts.py`

- `LineageKnotenTyp`
- `LineageOperationTyp`
- `LineageKnoten`
- `LineageKante`
- `LineageGraph`
- `get_default_lineage_graph()`

### `app/core/workflow_simulation_contracts_wave64.py`

- `SimulationsTyp`
- `SimulationsStatus`
- `SimulationsParameter`
- `SimulationsErgebnis`
- `SimulationsLauf`
- `get_default_simulations_laeufe()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/process/lineage/w64/graph` | Lineage-Graph-Uebersicht |
| POST | `/process/lineage/w64/upstream` | Upstream-Knoten fuer gegebene Knoten-ID |
| GET | `/process/simulation/w64/laeufe` | Liste aller Simulationslaeufe |
| POST | `/process/simulation/w64/ergebnis` | Simulations-Ergebnis fuer Lauf-ID |

## Abnahmekriterien

- Lineage-Graphen liefern Quelle, Ziel, Upstream, Downstream und Datenmenge korrekt.
- Simulationslaeufe bilden Status, Laufzeit und Ergebnisabweichungen korrekt ab.
- Ein Default-Lineage-Graph und drei Default-Simulationslaeufe stehen bereit.
- Die vier API-Endpunkte liefern Lineage- und Simulationsfunktionen.

## Tests

**Anzahl:** 173

## Status

`abgeschlossen`
Stand: 2026-03-18
