# Kernel / Neuro — Deployment und Smoke

## Migration

Auf Staging und Produktion vor dem Rollout:

```bash
alembic upgrade head
```

Relevante Revisionen u. a.:

- `neuro_step_audit_einkauf_tenant_20260405` — `neuro_step_audit_trace`, `einkauf_bestellungen.tenant_id`
- `finance_followup_exports_einkauf_uq_20260406` — `finance_followup_exports`, optional Unique `(tenant_id, bestellnummer)` auf `einkauf_bestellungen`

## Smoke-Tests

### PowerShell (lokal)

```powershell
.\scripts\smoke_kernel_action_execute.ps1 -BaseUrl "http://127.0.0.1:8000"
```

Erwartung: HTTP 200 und `status` `accepted` (sofern Command-Dispatch und DB-Schreibpfad passen).

### Finance Follow-up

Nach `POST` mit `record_count > 0` sollte `GET` auf die in `download_url` angegebene Route einen CSV-Download liefern; optional DMS-Spiegel, wenn `DMS_TOKEN` und `DMS_DOCUMENT_TYPE_ID` gesetzt sind.

### Monitoring

- Prometheus: `neuro_kernel_audit_inserts_total`
- API: `GET /api/v1/neuro/kernel-step-audit/summary?days=7` (Header `X-Tenant-ID`)
