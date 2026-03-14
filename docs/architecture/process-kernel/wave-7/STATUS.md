# Wave 7 Status

## Wave
- Name: `Read-Model-Persistenz, Reklamation und Preisabsicherung`
- Epics: `Epic 2 Read, Event and Data Product Platform`, `Epic 1 Process Kernel Platform`
- Status: `abgeschlossen`
- Startbedingung: Wave 6 abgeschlossen (Agrar-P0, Supplier Portal, Silo Ops)

## Ziel

Wave-2-Read-Models erhalten echte Snapshot-Persistenz und NATS-Consumer-Wiring.
Reklamations-, Ausnahme-, Preisabsicherungs- und Silo-Protokollpfade werden
als formale Kernbausteine in den Process Kernel ueberfuehrt.

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Read-Model-Persistenz: Snapshots fuer Wave-2-Projektionen | umgesetzt |
| AP2 | Event-Consumer-Wiring: NATS-Subjects an ProjectionConsumer koppeln | umgesetzt |
| AP3 | Reklamations-Aggregat mit Zustandsmaschine | umgesetzt |
| AP4 | Ausnahmepfade als Workflow-Extension (Exception Rules) | umgesetzt |
| AP5 | Preisabsicherung: HedgeReference fuer MATIF-Futures-Bindung | umgesetzt |
| AP6 | Silo-Reinigungsprotokoll und Trocknungsprotokoll (GoBD) | umgesetzt |

## Scope

### AP1: Read-Model-Persistenz

Neue Dateien:
- `app/core/read_model_persistence.py`
- `app/infrastructure/models/read_model_snapshots.py`

Geliefert:
- `ReadModelSnapshot` mit Hash-basierter Integritaetspruefung
- `SnapshotCursor` fuer stabile Paginierung
- `ReadModelSnapshotStore` mit SQLAlchemy-gestuetzter DB-Persistenz
- In-Memory-Fallback fuer isolierte Contract-Tests
- API-Endpunkte in `app/api/v1/endpoints/read_model_snapshots.py`

### AP2: Event-Consumer-Wiring

Neue Datei: `app/core/event_consumer_wiring.py`

Geliefert:
- `NatsSubjectMapping`
- `ConsumerWiringRegistry`
- `build_default_wiring()` fuer Wave-1 bis Wave-6-Subjects
- `WiringHealthReport`

### AP3 bis AP6: Domain-Bausteine

Geliefert:
- `app/core/reklamation.py`
- `app/core/exception_workflow_extension.py`
- `app/core/price_hedge.py`
- `app/core/silo_protokolle.py`

## Pakete

### Paket A: Read-Model Persistenz und Event-Wiring
- Artefakt: `package-a/STATUS.md`
- Tests: `tests/test_process_kernel_wave7_read_models.py`

### Paket B: Reklamation, Ausnahmen, Preisabsicherung, Silo
- Artefakt: `package-b/STATUS.md`
- Tests: `tests/test_process_kernel_wave7_domain.py`

## Exit-Kriterien

- [x] `ReadModelSnapshot` kann erzeugt, gespeichert und per Cursor paginiert werden
- [x] `ConsumerWiringRegistry` kennt die relevanten Wave-1 bis Wave-6-Event-Subjects
- [x] `Reklamation` durchlaeuft eine gueltige Zustandsmaschine
- [x] `AusnahmeAntrag` wird ueber den Dispatcher korrekt ausgeloest
- [x] `HedgeReference` berechnet Absicherungsquote korrekt
- [x] `SiloReinigungsprotokoll` und `TrocknungsProtokoll` sind GoBD-vollstaendig pruefbar
- [x] Wave-7-Tests sind gruen

## Verifikation

```bash
pytest tests/test_process_kernel_wave7_read_models.py \
       tests/test_process_kernel_wave7_domain.py -q --no-cov
# Ergebnis: 56 passed
```

## Startpunkte fuer Folgearbeit

- `app/core/read_model_persistence.py` ist jetzt DB-faehige Basis fuer Wave-8-Datenprodukte
- `app/core/event_consumer_wiring.py` bleibt die zentrale Subject-zu-Consumer-Registry
- `app/core/command_dispatcher.py` und `app/core/agent_command_manifest.py` sind Ankerpunkte fuer Wave 8
