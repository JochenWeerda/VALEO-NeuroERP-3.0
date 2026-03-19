# Wave 51 - Process Capacity + Workflow Compensation Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 135 gruen, 0 Fehler

## Scope

Wave 51 liefert zwei neue Core-Module und vier FastAPI-Endpunkte fuer Kapazitaetsplanung und Workflow-Kompensation im Saga-Pattern.

## Zielbild

Der Process-Kernel bildet Kapazitaetszustaende und Saga-Kompensation als wiederverwendbare Domain-Contracts mit klaren API-Zugriffspunkten ab.

## Lieferumfang

| Datei | Inhalt |
|-------|--------|
| `app/core/process_capacity_contracts_wave51.py` | `KapazitaetsTyp`, `KapazitaetsStatus`, `SkalierungsStrategie`, `KapazitaetsRegel.berechne_status()`, `KapazitaetsMessung`, `KapazitaetsPlan`, `get_default_kapazitaets_regeln()` |
| `app/core/workflow_compensation_contracts.py` | `KompensationsTyp`, `KompensationsStatus`, `SagaStatus`, `KompensationsSchritt.ist_abgeschlossen()`, `SagaInstanz`, `erstelle_kompensations_plan()`, `get_default_saga_instanzen()` |

### API-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process-kernel/kapazitaet/regeln` | Fuenf Standard-Kapazitaetsregeln |
| POST | `/api/v1/process-kernel/kapazitaet/pruefe-auslastung` | Berechnet `KapazitaetsStatus` fuer gegebene Auslastung |
| GET | `/api/v1/process-kernel/kompensation/sagas` | Vier Standard-Saga-Instanzen |
| POST | `/api/v1/process-kernel/kompensation/erstelle-plan` | Erstellt `SagaInstanz` aus Schrittdefinitionen |

## Abnahmekriterien

- Fuenf Standard-Kapazitaetsregeln sind verfuegbar.
- Kapazitaetsstatus wird fuer gegebene Auslastung reproduzierbar berechnet.
- Vier Standard-Saga-Instanzen sind ueber die API abrufbar.
- Ein Kompensationsplan kann aus Schrittdefinitionen erzeugt werden.

## Tests

**Datei:** `tests/test_process_kernel_wave51_capacity_compensation.py`
**Anzahl:** 135

### Testklassen

- `TestKapazitaetsTypEnum` (6)
- `TestKapazitaetsStatusEnum` (5)
- `TestSkalierungsStrategieEnum` (4)
- `TestBerechneStatus` (18)
- `TestKapazitaetsRegelAttributes` (3)
- `TestKapazitaetsMessung` (2)
- `TestKapazitaetsPlan` (9)
- `TestGetDefaultKapazitaetsRegeln` (14)
- `TestKompensationsTypEnum` (6)
- `TestKompensationsStatusEnum` (6)
- `TestSagaStatusEnum` (5)
- `TestKompensationsSchrittIstAbgeschlossen` (8)
- `TestSagaInstanzOffeneKompensationen` (3)
- `TestBerecheSagaStatus` (9)
- `TestErstelle_KompensationsPlan` (11)
- `TestGetDefaultSagaInstanzen` (25)

## Status

`abgeschlossen`
Stand: 2026-03-16
