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
| `CreatePurchaseOrder` | `app/services/command_handlers_procurement.py` | `INSERT` in `einkauf_bestellungen` bei gesetztem `lieferant_id` im Payload |

Weitere Commands: `register_domain_mutation("CommandName", callable)` — Signatur `(db, request, result) -> None`.

## Neuro Tool Broker

`execute_plan(..., db=session)` reicht die Session bis `ActionExecutionService.execute(..., db=db)` durch (Command-Binding).

## Finance Follow-up — Kasse

- `GET /api/v1/finance/followup/kasse/preview` — POS/TSE-Compliance-Zähler (`domain_docflow.pos_receipt_compliance`).
- `POST /api/v1/finance/followup/kasse/export` — Export-Metadaten (202).

## Compliance — PCN

- `POST/GET /api/v1/compliance/pcn-meldungen` — Mandant über `X-Tenant-ID` (`get_tenant_id`), Liste liefert `items` und `meldungen`.

## Nächste logische Schritte

1. **Weitere Domain-Handler** für Kern-Commands (z. B. `ApproveAPInvoice`) mit echten Buchungs-/Status-Updates statt nur Audit.
2. **Download-Endpoints** für `finance_followup` (`.../download`) an DMS/Blob anbinden.
3. **Neuro Broker**: Integrationstests mit echter DB-Session für Command-Steps.
4. **Einkauf**: Unique-Constraint `(tenant_id, bestellnummer)` wenn fachlich gewünscht; Nummernkreis statt freier Strings im Mutation-Handler.
5. **Monitoring**: Dashboard-Widgets für `neuro_step_audit_trace` und Kernel-Action-Volumen pro Tenant.
