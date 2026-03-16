# Wave 51 — Process Capacity + Workflow Compensation Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-16
**Tests:** 135 grün, 0 Fehler

## Scope

Wave 51 liefert zwei neue Core-Module und 4 FastAPI-Endpunkte für Kapazitätsplanung und Workflow-Kompensation (Saga-Pattern).

## Module

| Datei | Inhalt |
|-------|--------|
| `app/core/process_capacity_contracts_wave51.py` | KapazitaetsTyp, KapazitaetsStatus, SkalierungsStrategie, KapazitaetsRegel (berechne_status), KapazitaetsMessung, KapazitaetsPlan (kritische_messungen, auslastungs_zusammenfassung), get_default_kapazitaets_regeln (5 Regeln) |
| `app/core/workflow_compensation_contracts.py` | KompensationsTyp, KompensationsStatus, SagaStatus, KompensationsSchritt (ist_abgeschlossen), SagaInstanz (offene_kompensationen, berechne_saga_status), erstelle_kompensations_plan, get_default_saga_instanzen (4 Instanzen) |

## API-Endpunkte (appended to process_kernel_api.py)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process-kernel/kapazitaet/regeln` | 5 Standard-Kapazitätsregeln |
| POST | `/api/v1/process-kernel/kapazitaet/pruefe-auslastung` | Berechnet KapazitaetsStatus für gegebene Auslastung |
| GET | `/api/v1/process-kernel/kompensation/sagas` | 4 Standard-Saga-Instanzen |
| POST | `/api/v1/process-kernel/kompensation/erstelle-plan` | Erstellt SagaInstanz aus Schritt-Definitionen |

## Tests

**Datei:** `tests/test_process_kernel_wave51_capacity_compensation.py`
**Anzahl:** 135

### Testklassen
- `TestKapazitaetsTypEnum` (6)
- `TestKapazitaetsStatusEnum` (5)
- `TestSkalierungsStrategieEnum` (4)
- `TestBerechneStatus` (18) — alle Schwellwerte inkl. 69.9/70.0/89.9/90.0/99.9/100.0, max=0, negativ, custom-Schwellen
- `TestKapazitaetsRegelAttributes` (3)
- `TestKapazitaetsMessung` (2)
- `TestKapazitaetsPlan` (9) — kritische_messungen, auslastungs_zusammenfassung, Nullwerte
- `TestGetDefaultKapazitaetsRegeln` (14) — 5 Regeln, korrekte IDs/Typen/Strategien
- `TestKompensationsTypEnum` (6)
- `TestKompensationsStatusEnum` (6)
- `TestSagaStatusEnum` (5)
- `TestKompensationsSchrittIstAbgeschlossen` (8)
- `TestSagaInstanzOffeneKompensationen` (3)
- `TestBerecheSagaStatus` (9) — alle Zweige inkl. Prioritätsreihenfolge
- `TestErstelle_KompensationsPlan` (11)
- `TestGetDefaultSagaInstanzen` (25) — alle 4 Instanzen, Statuse, Schritt-Details

## Gesamtstand nach Wave 51

- Waves 1–51: **3135 Tests grün**, 5 skipped, 1 xfailed
