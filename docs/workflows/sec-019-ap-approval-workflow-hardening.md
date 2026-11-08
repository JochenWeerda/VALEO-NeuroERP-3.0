# SEC-019 - AP Approval Workflow Hardening

## Ziel

Der AP-Freigabeworkflow soll keine freien Query-Tenants mehr akzeptieren und keine tenantfremden Rechnungen aus dem Document-Store verarbeiten.

## Scope

- `app/api/v1/endpoints/ap_approval_workflow.py`
- `tests/test_security_ap_approval_workflow.py`

## Umsetzung

- `list/create/request/approve/status` ziehen `tenant_id` jetzt ueber `Depends(get_tenant_id)`
- geladene AP-Invoices werden vor der Workflow-Verarbeitung gegen `tenantId` bzw. `tenant_id` geprueft
- tenantfremde Rechnungen werden mit `404` abgelehnt

## Verifikation

- `pytest tests/test_security_ap_approval_workflow.py -q --no-cov`
- `python -m py_compile app/api/v1/endpoints/ap_approval_workflow.py tests/test_security_ap_approval_workflow.py`

## Erweiterung 2026-10-20

Inhaltsgebundene Antragsreferenz, gepruefte Urheber, Funktionstrennung und gemeinsame
Buchungstransaktion auch fuer Kernel-Kommandos: [Abnahme](../quality-assurance/ap-workflow-security-20261020.md).
