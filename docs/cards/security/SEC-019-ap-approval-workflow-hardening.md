# SEC-019

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_ap_approval_workflow.py

## Titel

Tenant-Isolation fuer AP Approval Workflow

## Problem

Der Router akzeptierte freie `tenant_id`-Query-Parameter und konnte tenantfremde AP-Invoices aus dem Document-Store verarbeiten.

## Loesung

- Umstellung auf kontextgebundenen Tenant
- Tenant-Pruefung auf geladene Rechnungen
- Regressionstests fuer Rule-/Create- und Cross-Tenant-Request-Pfad
