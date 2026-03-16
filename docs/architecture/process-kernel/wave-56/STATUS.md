# Wave 56: Process Dependencies + Workflow Signals

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-16
**Tests:** 153 gruen, 0 Fehler, 0 skipped

## Gelieferte Module

### app/core/process_dependency_contracts.py
- `AbhaengigkeitsTyp` (SEQUENZIELL, PARALLEL, OPTIONAL, BLOCKIEREND)
- `SchrittStatus` (AUSSTEHEND, BEREIT, LAUFEND, ABGESCHLOSSEN, FEHLGESCHLAGEN, UEBERSPRUNGEN)
- `AbhaengigkeitsKante`, `ProzessSchritt`, `ProzessGraph`
- `ProzessGraph.bereite_schritte()` — DAG-basierte Bereitschaftsberechnung
- `ProzessGraph.topologische_reihenfolge()` — Kahn-Algorithmus mit Zykluserkennung
- `get_default_prozess_graphen()` — PG-001 (linear) und PG-002 (fork-join)

### app/core/workflow_signal_contracts.py
- `SignalTyp` (EXTERN, INTERN, ZEITPLAN, BENUTZER, SYSTEM)
- `SignalStatus` (AUSSTEHEND, ZUGESTELLT, VERARBEITET, ABGELAUFEN, ABGEWIESEN)
- `TriggerAktion` (FORTSETZEN, ABBRECHEN, ESKALIEREN, BENACHRICHTIGEN)
- `WorkflowSignal` mit `ist_abgelaufen()` und `aktueller_status()`
- `verarbeite_signal()` — Regelabgleich mit Ablaufpruefung
- `get_default_signal_regeln()` — 5 Regeln SR-001..SR-005
- `get_default_signale()` — 4 Signale SIG-001..SIG-004

## FastAPI Endpoints (process_kernel_api.py)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | /abhaengigkeit/graphen | Alle Default-Prozessgraphen mit bereiten Schritten |
| POST | /abhaengigkeit/bereite-schritte | Dynamische Berechnung bereiter Schritte |
| GET | /signal/signale | Alle Default-Signale mit aktuellem Status |
| POST | /signal/verarbeite | Signal gegen Regelkatalog verarbeiten |

## Testabdeckung

- Enums: 15 Tests
- AbhaengigkeitsKante/ProzessSchritt: 7 Tests
- bereite_schritte (kein Edge, SEQ, BLOCKIEREND, PARALLEL, OPTIONAL, fork-join): 29 Tests
- topologische_reihenfolge (linear, cycle, fork-join, disconnected): 14 Tests
- get_default_prozess_graphen: 16 Tests
- WorkflowSignal (ist_abgelaufen, aktueller_status): 12 Tests
- verarbeite_signal: 14 Tests
- get_default_signal_regeln: 7 Tests
- get_default_signale: 17 Tests
- Integration + Edge Cases: 13 Tests
- Sonstige Dataclass-Tests: 9 Tests

**Gesamt: 153 Tests**
