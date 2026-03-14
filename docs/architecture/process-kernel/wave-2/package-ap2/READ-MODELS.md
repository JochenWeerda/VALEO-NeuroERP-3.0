# Wave 2 AP2: Read-Models fuer Cockpits, KPI- und Prozessbeobachtung

## Ziel

Server-seitige, voraggregierte Read-Models mit stabilen Query-Contracts als Alternative
zu n client-seitigen API-Aufrufen mit In-Browser-Aggregation.

## Architekturprinzip

- Read-Models sind **schreibgeschuetzt** — sie werden durch Events/Outbox aktualisiert
- Jedes Read-Model traegt `schema_version: int` fuer Migrations-Stabilitaet
- Query-Contracts sind durch Contract-Tests abgesichert

## Implementierte Endpunkte

```
GET /api/v1/finance/read-models/ap-invoice-cockpit
GET /api/v1/finance/read-models/payment-run-cockpit
GET /api/v1/finance/read-models/process-observation
```

## AP-Invoice Cockpit Read-Model

```json
{
  "tenant_id": "tenant1",
  "buckets": [
    {"status": "ENTWURF", "count": 5, "total_amount": 12500.0},
    {"status": "ZUR_FREIGABE", "count": 3, "total_amount": 8200.0},
    {"status": "FREIGEGEBEN", "count": 2, "total_amount": 4100.0}
  ],
  "total_count": 10,
  "pending_approval_count": 3,
  "ready_to_post_count": 2,
  "overdue_count": 1,
  "schema_version": 1
}
```

Felder:
- `buckets`: Zaehler je `semantic_status` (ENTWURF/ZUR_FREIGABE/TEILWEISE_FREIGEGEBEN/FREIGEGEBEN/ABGELEHNT/VERBUCHT)
- `pending_approval_count`: Summe aus ZUR_FREIGABE + TEILWEISE_FREIGEGEBEN
- `ready_to_post_count`: Rechnungen mit `approval_can_post == true`
- `overdue_count`: ENTWURF-Rechnungen aelter als 30 Tage

## Payment Run Cockpit Read-Model

```json
{
  "tenant_id": "tenant1",
  "draft_count": 2,
  "approved_count": 1,
  "executed_count": 5,
  "total_pending_amount": 45000.0,
  "schema_version": 1
}
```

## Process Observation Read-Model

Fachliche Beobachtung laufender Workflow-Instanzen:

```json
{
  "tenant_id": "tenant1",
  "workflow_instances": [
    {"process_key": "ap_approval", "running_count": 3, "waiting_count": 2, "completed_today": 1, "failed_count": 0},
    {"process_key": "harvest_acceptance", "running_count": 1, "waiting_count": 0, "completed_today": 4, "failed_count": 0}
  ],
  "total_running": 4,
  "total_waiting": 2,
  "schema_version": 1
}
```

## Naechste Schritte

- Read-Models durch Event-Consumer (Outbox-Subscriber) asynchron aktualisieren
- Redis-Cache fuer sub-100ms Dashboard-Ladezeit
- Inkrementelle Updates statt Full-Recompute

## Verifikation

```
pytest tests/test_process_kernel_wave2_read_models.py -q
python -m py_compile app/api/v1/endpoints/finance_read_models.py
```
