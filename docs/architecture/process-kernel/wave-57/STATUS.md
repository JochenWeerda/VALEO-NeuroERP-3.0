# Wave 57 - Process Observability + Workflow Versioning Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 151 gruen, 0 Fehler, 0 skipped

## Scope

Wave 57 liefert Observability-Contracts fuer Traces und Health Checks sowie Versionierungs-Contracts fuer Workflow-Schemata und Migrationspruefungen.

## Zielbild

Observability und Versionsverwaltung sollen als belastbare Kernel-Contracts fuer Monitoring, Health und Schema-Migrationen verfuegbar sein.

## Lieferumfang

### `app/core/process_observability_contracts.py`

- `SpanStatus`
- `HealthStatus`
- `MetrikEinheit`
- `ObservabilitySpan`
- `Trace`
- `HealthCheck`
- `SystemHealthReport`
- `get_default_traces()`
- `get_default_health_report()`

### `app/core/workflow_versioning_contracts_wave57.py`

- `VersionsStatus`
- `MigrationsTyp`
- `KompatibilitaetsTyp`
- `WorkflowSchemaVersion`
- `MigrationsSchritt`
- `MigrationsGuard`
- `get_default_migrations_guards()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process-kernel/observability/traces` | Alle Default-Traces mit Metriken |
| GET | `/api/v1/process-kernel/observability/health` | System-Health-Report |
| GET | `/api/v1/process-kernel/versioning/guards` | Alle Migrations-Guards |
| POST | `/api/v1/process-kernel/versioning/pruefe-brechend` | Breaking-Change-Check |

## Abnahmekriterien

- Traces liefern Root-Spans, Fehlerquoten und Gesamtdauer korrekt.
- Health-Checks aggregieren zu einem reproduzierbaren Gesamtstatus.
- Migrations-Guards erkennen aktive, neueste und brechende Versionen.
- Die vier API-Endpunkte stellen Observability- und Versionierungsdaten bereit.

## Tests

**Datei:** `tests/test_process_kernel_wave57_observability_versioning.py`
**Anzahl:** 151

## Status

`abgeschlossen`
Stand: 2026-03-16
