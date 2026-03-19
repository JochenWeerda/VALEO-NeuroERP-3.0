# Wave 52 - Circuit Breaker + Event Sourcing Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 135 gruen, 0 Fehler

## Scope

Wave 52 erweitert den Process-Kernel um Ausfallschutz per Circuit Breaker und deterministische Zustandsrekonstruktion per Event Sourcing.

## Zielbild

Kritische Prozessaufrufe sollen robust gegen Fehlerkaskaden abgesichert sein, waehrend Workflow-Zustaende aus Ereignisstroemen reproduzierbar rekonstruiert werden koennen.

## Lieferumfang

### Core Modules

| Datei | Inhalt |
|-------|--------|
| `app/core/process_circuit_breaker_contracts.py` | `CircuitBreakerZustand`, `AufrufErgebnis`, `CircuitBreakerKonfiguration`, `CircuitBreakerZustandsRecord`, fuenf Default-Konfigurationen |
| `app/core/workflow_event_sourcing_contracts.py` | `EreignisTyp`, `ReplayModus`, `WorkflowEreignis`, `EreignisStream`, `rekonstruiere_zustand()`, vier Default-Streams |

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process-kernel/circuit-breaker/konfigurationen` | Listet fuenf Circuit-Breaker-Konfigurationen |
| POST | `/api/v1/process-kernel/circuit-breaker/pruefe-zustand` | Prueft, ob Anfragen durchgelassen werden koennen |
| GET | `/api/v1/process-kernel/event-sourcing/streams` | Listet vier Standard-Ereignisstreams |
| POST | `/api/v1/process-kernel/event-sourcing/rekonstruiere` | Rekonstruiert Workflow-Zustand aus Stream |

## Abnahmekriterien

- Fuenf Circuit-Breaker-Konfigurationen stehen als Default zur Verfuegung.
- Zustandsuebergaenge fuer `GESCHLOSSEN`, `OFFEN` und `HALB_OFFEN` sind getestet.
- Vier Default-Ereignisstreams koennen replayed und rekonstruiert werden.
- Die vier API-Endpunkte liefern die beschriebenen Schutz- und Rekonstruktionsfunktionen.

## Tests

### Circuit Breaker

- Enum-Werte: 7
- Konfiguration: 3
- `kann_anfrage_durchlassen()`: 11
- `verarbeite_ergebnis()`: 21
- Immutabilitaet: 4
- Default-Konfigurationen: 12
- Edge Cases: 8

### Event Sourcing

- Enum-Werte: 10
- `aktuelle_version()`: 4
- `fuege_ereignis_hinzu()`: 6
- `replay()`: 16
- `rekonstruiere_zustand()`: 13
- Default-Streams: 16

## Status

`abgeschlossen`
Stand: 2026-03-16
