# Paket A Status

## Paket
- Name: `Command und Workflow-Grundlagen`
- Zugeordnete Aufgaben: `A1`, `A2`, `A3`, `A4`

## Ziel
- bestehende Kernprozesspfade in einen belastbaren Command- und Workflow-Rahmen überführen

## Aktueller Stand
- `A1`: umgesetzt, reproduzierbare Command-Inventur vorhanden
- `A2`: umgesetzt, zentrales Workflow-Definitionsmodell in `app/core/workflow_definitions.py`
- `A3`: umgesetzt, Ziel-Command-Katalog dokumentiert
- `A4`: umgesetzt, `WorkflowInstanceReference` in AP-Approval-Audit-Pfad eingebunden

## Verprobte Produktivpfade
- `ap_approval_workflow.py`: jeder Audit-Eintrag traegt `workflow_instance_ref` mit `process_key`, `definition_version`, `definition_origin`, `status` und `business_reference`
- `workflow-sandbox`: Preview-Contract erzwingt versionierte Workflow-Metadaten

## Verifikation
- `pytest tests/test_process_kernel_wave1_contracts.py tests/test_app_bootstrap_imports.py -q`
- `python -m py_compile app/api/v1/endpoints/ap_approval_workflow.py app/core/workflow_definitions.py`

## Artefakte
- `PKP-01-command-inventory.md`
- `PKP-02-workflow-definition-schema.md`
- `PKP-01-target-command-catalog.md`
- `PKP-02-instance-and-migration-model.md`

## Naechster Schritt
- Wave-2: Workflow-Instanzen in eigene DB-Tabelle persistieren (Outbox/Event-Basis aus Wave-2-Epic-2)
