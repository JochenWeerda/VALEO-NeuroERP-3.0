# Wave 10 Status

## Wave
- Name: `Process Mining, Observability und Analytics-Verknuepfung`
- Epics: `Epic 2 Read, Event and Data Product Platform`, `Epic 3 Tenant, Security and Integration Governance`
- Status: `gestartet`
- Startbedingung: Wave 9 abgeschlossen

## Ziel

Die in Wave 4 bis 9 aufgebauten Runtime-, Cursor-, Replay- und Snapshot-Pfade
werden in eine explizite Process-Mining-Sicht ueberfuehrt. Damit entsteht ein
analytisch nutzbarer Einstiegspunkt fuer Bottlenecks, Drift und Replay-Lag.

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Process-Mining-Report aus Projektion-, Cursor- und Runtime-Zustand | umgesetzt |
| AP2 | Observability-Verknuepfung fuer Telemetrie und Runtime-Komponenten | umgesetzt |
| AP3 | Analytics-Anschluss fuer Benchmark- und Reporting-Produkte | umgesetzt |

## Scope

### AP1: Process-Mining-Report

Neue Dateien:
- `app/core/process_mining.py`
- `app/core/process_mining_application.py`
- `app/api/v1/endpoints/process_mining_api.py`
- `tests/test_process_kernel_wave10_process_mining.py`

Geliefert:
- `ProcessMiningTrace`, `ProcessMiningBottleneck`, `ProcessMiningReport`
- `build_process_mining_report()` auf Basis von `ProjectionStatusReadModel` und `RuntimeHealthReport`
- `build_process_mining_report_for_tenant()` als gemeinsame Core-Orchestrierung fuer API, Reporting und Benchmark
- `GET /api/v1/process-mining/finance/report`
- `GET /api/v1/process-mining/finance/bottlenecks`

### AP2: Observability-Verknuepfung

Geliefert:
- `ProcessObservabilitySignal` fuer tenantbezogene Device-/Telemetry-Signale
- Anbindung an `iot_telemetry`-Device- und Reading-Stores
- Bottleneck-Ableitung fuer `offline`, `error`, `calibrating` und schlechte Reading-Qualitaet

### AP3: Analytics-Anschluss

Geliefert:
- `POST /api/v1/reporting/process-mining/report` als Reporting-Vertrag fuer Mining-Daten
- `GET /api/v1/benchmark/process-mining/{verbund_id}` fuer tenantuebergreifende Mining-Kennzahlen
- Ableitung von Benchmark-Kennzahlen fuer `process_ready_count`, `process_lagging_count` und `process_critical_signal_count`

## Pakete

### Paket A: Process Mining + Observability + Analytics-Anschluss
- Enthaelt: AP1, AP2, AP3
- Tests: `tests/test_process_kernel_wave10_process_mining.py`

## Exit-Kriterien

- [x] Projection-Cursor-Zustaende werden in explizite Mining-Traces ueberfuehrt
- [x] Replay-Lag wird als Bottleneck sichtbar
- [x] degradierte Runtime-Komponenten werden als Bottleneck gespiegelt
- [x] Telemetrie- und Device-Status werden als Observability-Signale gespiegelt
- [x] API liefert Report- und Bottleneck-Contract
- [x] Reporting- und Benchmark-Pfade nutzen dieselbe Mining-Sicht

## Verifikation

```bash
pytest tests/test_process_kernel_wave10_process_mining.py -q --no-cov
```

## Startpunkte

- `app/api/v1/endpoints/finance_read_models.py` - Cursor- und Snapshot-Metadaten
- `app/api/v1/endpoints/runtime_operations.py` - Runtime-Komponenten und Health-Metriken
- `app/core/reporting_layer.py` - spaeterer Analytics-Anschluss
