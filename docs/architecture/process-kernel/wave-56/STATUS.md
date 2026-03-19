# Wave 56 - Process Dependencies + Workflow Signals

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 153 gruen, 0 Fehler, 0 skipped

## Scope

Wave 56 fuehrt Abhaengigkeitsgraphen fuer Prozesse und Signalkontrakte fuer ereignisgesteuerte Workflow-Steuerung ein.

## Zielbild

Der Kernel soll bereite Prozessschritte aus Abhaengigkeiten ableiten und Signale regelbasiert verarbeiten koennen.

## Lieferumfang

### `app/core/process_dependency_contracts.py`

- `AbhaengigkeitsTyp`
- `SchrittStatus`
- `AbhaengigkeitsKante`
- `ProzessSchritt`
- `ProzessGraph`
- `get_default_prozess_graphen()`

### `app/core/workflow_signal_contracts.py`

- `SignalTyp`
- `SignalStatus`
- `TriggerAktion`
- `WorkflowSignal`
- `verarbeite_signal()`
- `get_default_signal_regeln()`
- `get_default_signale()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/abhaengigkeit/graphen` | Alle Default-Prozessgraphen mit bereiten Schritten |
| POST | `/abhaengigkeit/bereite-schritte` | Dynamische Berechnung bereiter Schritte |
| GET | `/signal/signale` | Alle Default-Signale mit aktuellem Status |
| POST | `/signal/verarbeite` | Signal gegen Regelkatalog verarbeiten |

## Abnahmekriterien

- Bereite Schritte und topologische Reihenfolgen werden fuer DAGs korrekt berechnet.
- Signale koennen auf Ablauf, Status und Regelabgleich bewertet werden.
- Zwei Default-Prozessgraphen, fuenf Signalregeln und vier Signale sind verfuegbar.
- Die vier API-Endpunkte exposeieren Graph- und Signalverarbeitung.

## Tests

- Enums: 15
- Prozessgraphen und Bereitschaftslogik: 66
- Signale und Signalregeln: 50
- Integration und Edge Cases: 22
- Gesamt: 153

## Status

`abgeschlossen`
Stand: 2026-03-16
