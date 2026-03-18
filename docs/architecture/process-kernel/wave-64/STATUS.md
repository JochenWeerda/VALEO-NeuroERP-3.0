# Wave 64 — Data Lineage + Process Simulation Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-18
**Tests:** 173 grün, 0 Fehler

## Module

### `app/core/process_lineage_contracts.py`
- `LineageKnotenTyp` (QUELLE, TRANSFORMATION, ZIEL, ZWISCHENSPEICHER)
- `LineageOperationTyp` (LESEN, SCHREIBEN, TRANSFORMIEREN, KOPIEREN, LOESCHEN)
- `LineageKnoten`, `LineageKante`, `LineageGraph`
- `LineageGraph.quell_knoten()`, `ziel_knoten()`, `upstream_knoten()`, `downstream_knoten()`, `gesamt_datenmenge_bytes()`
- `get_default_lineage_graph()` — 6 Knoten, 5 Kanten, 6144 Bytes

### `app/core/workflow_simulation_contracts_wave64.py`
- `SimulationsTyp` (LAST_TEST, PFAD_ANALYSE, ENGPASS_ANALYSE, WHAT_IF)
- `SimulationsStatus` (AUSSTEHEND, LAUFEND, ABGESCHLOSSEN, FEHLGESCHLAGEN)
- `SimulationsParameter` mit `abweichung_pct` Property
- `SimulationsErgebnis` mit `groesste_abweichung` Property
- `SimulationsLauf` mit `laufzeit_sekunden()` Methode
- `get_default_simulations_laeufe()` — 3 Läufe (SL-001 ABGESCHLOSSEN, SL-002 LAUFEND, SL-003 AUSSTEHEND)

## Endpoints (append to `process_kernel_api.py`, Prefix `/process`)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/process/lineage/w64/graph` | Lineage-Graph Übersicht |
| POST | `/process/lineage/w64/upstream` | Upstream-Knoten für gegebene Knoten-ID |
| GET | `/process/simulation/w64/laeufe` | Liste aller Simulations-Läufe |
| POST | `/process/simulation/w64/ergebnis` | Simulations-Ergebnis für Lauf-ID |

Note: Pfade mit `/w64/` Infix um Konflikte mit Wave 44 (`/lineage/graph`) zu vermeiden.

## Testabdeckung

- Enum-Tests: 16
- LineageKnoten/Kante: 10
- LineageGraph leer: 9
- LineageGraph Logik: 16
- Default-Graph: 30
- SimulationsParameter: 9
- SimulationsErgebnis: 7
- SimulationsLauf: 8
- Default-Läufe: 33
- Endpoint-Tests: 25 (11 Lineage + 14 Simulation)
- **Gesamt: 173 Tests**
