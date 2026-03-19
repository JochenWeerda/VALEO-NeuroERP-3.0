# Wave-33 Status

## Scope
API-Bulk-Operationen (Gap 034) + Queue-basierte Hintergrundjobs (Gap 036)

## Zielbild

Wave 33 schliesst zwei P1-Luecken:
Gap 034 (API-Bulk-Operationen fuer Massenvorgaenge — 3x Throughput bei Batch-Import)
und Gap 036 (Queue-basierte Hintergrundjobs fuer schwere Prozesse — p95 UI-Response <300ms unter Last).

Die Bulk-Operations-Contracts definieren typisierte Batch-Anfragen mit Domain-spezifischen
Limits, Validierung und strukturierten Ergebnissen.
Die Background-Job-Queue modelliert Job-Typen, Prioritaeten, Routing und Status-Tracking
ohne echten Job-Runner im Core-Layer — die Contracts sind produktiv einsetzbar sobald
ein Worker (Celery, NATS, ARQ) angebunden wird.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/bulk_operations.py` | `BulkOperationTyp`, `BulkItem`, `BulkRequest`, `BulkResult`; `validate_bulk_request()`; Domain-Limits | abgeschlossen |
| AP2 | `app/core/bulk_operations.py` | `get_default_bulk_limits()` — Limits fuer Finance, Agrar, Compliance, Workflow | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/bulk-limits[?domain=]` + `POST /process/bulk-operations/validate` | abgeschlossen |
| AP4 | `app/core/background_jobs.py` | `JobTyp`, `JobStatus`, `BackgroundJob`, `JobPrioritaet`, `JobQueueEntry`, `JobQueue` | abgeschlossen |
| AP5 | `app/core/background_jobs.py` | `evaluate_job_routing()`, `get_default_job_types()` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/jobs[?typ=][?status=]` + `POST /process/jobs/enqueue` + `GET /process/jobs/heartbeat` + `GET /process/jobs/heartbeat/recovery` | abgeschlossen |

## Abnahmekriterien

- `validate_bulk_request()` prueft Batch-Groesse, Item-Limits und Domain-Regeln
- Domain-Limits sind konfigurierbar und geben strukturierte Fehler statt 500
- `BackgroundJob` traegt Typ, Status, Zeitstempel und Ergebnis-Summary
- `JobQueue.enqueue()` / `dequeue()` arbeiten prioritaetsbasiert (KRITISCH > HOCH > MITTEL > NIEDRIG)
- `evaluate_job_routing()` weist Jobs deterministisch Worker-Klassen zu
- `GET /process/jobs/heartbeat` liefert eine explizite Scheduler-/Worker-Liveness-Sicht mit Lease-/Stale-Status
- `GET /process/jobs/heartbeat/recovery` liefert einen standardisierten Recovery-/Eskalationsplan fuer `ACTIVE`, `DEGRADED` und `STALE`
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave33_bulk_jobs.py` — 59 Tests, alle gruen

```bash
pytest tests/test_process_kernel_wave33_bulk_jobs.py -q --no-cov
# Ergebnis: 59 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
