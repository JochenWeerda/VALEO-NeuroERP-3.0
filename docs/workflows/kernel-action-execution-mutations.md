# Kernel Action Execution — DB-Mutationen und Audit

## Zweck

Nach Wave 17/18 validiert der `CommandDispatcher` Business-Commands und liefert `ACCEPTED`, ohne selbst zu persistieren. Persistente Nebenwirkungen laufen über:

1. **Audit-Zeile** in `domain_shared.neuro_step_audit_trace` (Neuro-Plan-Schritte und Kernel-`POST /process/actions/execute`).
2. **Optionale Domain-Mutationen** pro `command_name` über `register_domain_mutation` in `app/services/action_execution_mutations.py`.

## Datenbank

| Objekt | Zweck |
|--------|--------|
| `domain_shared.neuro_step_audit_trace` | Append-only Trace; Migration `neuro_step_audit_einkauf_tenant_20260405` |
| `public.einkauf_bestellungen.tenant_id` | Mandantenbindung für Einkauf; dieselbe Migration bzw. `scripts/init-all-tables.sql` |

Greenfield: `alembic upgrade head` oder `scripts/init-all-tables.sql` (enthält `CREATE TABLE` + `tenant_id`-Alter).

## API

- `POST /api/v1/process/actions/execute` — `Depends(get_db)`; `ActionExecutionService.execute(..., db=db)`.
- Idempotenz wird **nur** in `ActionExecutionService.execute` persistiert (kein zweites `remember` im Router).

## Registrierte Domain-Mutationen

| Command | Handler-Modul | Persistenz |
|---------|-----------------|------------|
| `CreatePurchaseOrder` | `app/services/command_handlers_procurement.py` | `INSERT` in `einkauf_bestellungen` bei gesetztem `lieferant_id`; Bestellnummer aus Nummernkreis oder optional `TENANT_PO_PREFIX_<TENANT>` + Nummernkreis |
| `ApproveAPInvoice` | `app/services/command_handlers_finance.py` | `UPDATE` `documents` (`ap_invoice`) Freigabe |
| `PostAPInvoice` | `app/services/ap_invoice_kernel_posting.py` | Journal (`domain_erp.journal_entries` / Lines), `offene_posten`, `documents`, `outbox_events` — **Execute-Body:** `human_confirmation: true` (Katalog verlangt menschliche Bestaetigung) |

Weitere Commands: `register_domain_mutation("CommandName", callable)` — Signatur `(db, request, result) -> None`.

## Neuro Tool Broker

`execute_plan(..., db=session)` reicht die Session bis `ActionExecutionService.execute(..., db=db)` durch (Command-Binding).

## Finance Follow-up — Kasse

- `GET /api/v1/finance/followup/kasse/preview` — POS/TSE-Compliance-Zähler (`domain_docflow.pos_receipt_compliance`).
- `POST /api/v1/finance/followup/kasse/export` — Export-Metadaten (202).
- Uploads: zuerst DMS (`DMS_DOCUMENT_TYPE_ID`), sonst S3 (`FINANCE_EXPORT_S3_BUCKET`, optional `AWS_ENDPOINT_URL_S3` fuer MinIO).

## Compliance — PCN

- `POST/GET /api/v1/compliance/pcn-meldungen` — Mandant über `X-Tenant-ID` (`get_tenant_id`), Liste liefert `items` und `meldungen`.

## Nächste logische Schritte (Stand 2026-04)

Erledigt in diesem Slice:

1. **Domain-Handler `ApproveAPInvoice`** — Status/Freigabe in `documents` (AP); Registrierung in `command_handlers_finance.py`.
2. **Finance Follow-up** — `GET .../download` für Mahnwesen, Lastschrift, Kasse (CSV); optional DMS-Spiegel via `DMS_TOKEN` + `DMS_DOCUMENT_TYPE_ID`; Stub-Tabelle `domain_shared.finance_followup_exports`.
3. **Neuro Broker** — Integrationstest `tests/test_neuro_tool_broker_db_integration.py` (mark `integration`, echte Session).
4. **Einkauf** — Nummernkreis; optional `TENANT_PO_PREFIX_<SANITIZED_TENANT>`; Duplikat-Bereinigung + Unique per Migration `einkauf_bestellungen_dedupe_unique_20260407`.
5. **Monitoring** — Prometheus `neuro_kernel_audit_inserts_total`; API `GET /api/v1/neuro/kernel-step-audit/summary?days=7`.
6. **Deployment** — `docs/operations/kernel-deployment-smoke.md`, `scripts/smoke_kernel_action_execute.ps1`.
7. **PostAPInvoice (Kernel)** — `app/services/ap_invoice_kernel_posting.py`: Journal + OP + Outbox + `documents`-Update (ein DB-Commit mit Kernel-Audit); Execute mit `human_confirmation: true`.
8. **Finance-Export** — `finance_export_upload.py`: DMS, fallback S3/MinIO (`boto3`).

Offen / Feinschliff:

- **Grafana-Dashboards** auf Basis von `neuro_kernel_audit_inserts_total` und der Summary-API.
- **Superglue** — produktiver CI-Smoke (optional Nightly / `workflow_dispatch`).
