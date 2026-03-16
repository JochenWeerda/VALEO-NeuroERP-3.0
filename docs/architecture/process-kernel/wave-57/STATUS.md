# Wave 57 — Process Observability + Workflow Versioning Contracts

**Datum:** 2026-03-16
**Status:** ABGESCHLOSSEN
**Tests:** 151 grün, 0 Fehler, 0 skipped

## Scope

### Modul 1: `app/core/process_observability_contracts.py`
Process Observability: Spans, Traces, Health Checks

- `SpanStatus` — LAUFEND / ERFOLGREICH / FEHLER / ABGEBROCHEN
- `HealthStatus` — GESUND / DEGRADIERT / KRANK / UNBEKANNT
- `MetrikEinheit` — MILLISEKUNDEN / ANFRAGEN_PRO_SEKUNDE / PROZENT / BYTES / ANZAHL
- `ObservabilitySpan` — Einzelner Span mit `dauer_ms()`, `ist_root_span()`
- `Trace` — Span-Sammlung mit `root_span()`, `gesamtdauer_ms()`, `fehlerhafte_spans()`, `erfolgsrate_pct()`
- `HealthCheck` — Einzelne Komponentenprüfung
- `SystemHealthReport` — Aggregierter Report mit `gesamtstatus()`, `gesunde_komponenten()`
- `get_default_traces()` — 2 Traces (TRACE-001: 3 Spans alle OK, TRACE-002: 1 Fehler-Span)
- `get_default_health_report()` — 5 Checks (3 GESUND, 1 DEGRADIERT, 1 UNBEKANNT → Gesamtstatus DEGRADIERT)

### Modul 2: `app/core/workflow_versioning_contracts_wave57.py`
Workflow Schema Versioning and Migration Guards

- `VersionsStatus` — ENTWURF / AKTIV / VERALTET / ZURUECKGEZOGEN
- `MigrationsTyp` — VORWAERTS / RUECKWAERTS / DATENMIGRATION
- `KompatibilitaetsTyp` — VOLLSTAENDIG / RUECKWAERTS / BRECHEND
- `WorkflowSchemaVersion` — Versioniertes Schema mit `ist_produktiv()`, `version_tuple()`
- `MigrationsSchritt` — Einzelner Migrationspfad mit Kompatibilitätsflag
- `MigrationsGuard` — Versionsverwaltung mit `aktive_version()`, `neueste_version()`, `hat_brechende_aenderung()`
- `get_default_migrations_guards()` — 2 Guards (MG-001: kontrakt_freigabe 1.0.0→1.1.0→2.0.0, MG-002: ap_rechnung 1.0.0)

### Endpoints (`app/api/v1/endpoints/process_kernel_api.py`)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process-kernel/observability/traces` | Alle Default-Traces mit Metriken |
| GET | `/api/v1/process-kernel/observability/health` | System Health Report |
| GET | `/api/v1/process-kernel/versioning/guards` | Alle Migrations-Guards |
| POST | `/api/v1/process-kernel/versioning/pruefe-brechend` | Breaking-Change-Check |

## Testdatei
`tests/test_process_kernel_wave57_observability_versioning.py` — 151 Tests

## Regressionsstatus
- 4034 passing (alle bisherigen Tests)
- 3 pre-existing failures in `test_process_kernel_wave4_ap4_ap5_ap6.py` (NameError in runtime_operations.py, vor Wave 57 vorhanden)
- 5 skipped, 1 xfailed (unverändert)
