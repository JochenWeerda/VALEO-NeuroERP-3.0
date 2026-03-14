# PKP-02 Workflow-Definitionsschema

## Zweck
- zentrales Modell für versionierte Prozessdefinitionen
- gemeinsame Basis für Tenant-Overrides, Sandbox und spätere Migrationen

## Status
- erster technischer Kern im Backend angelegt
- Code-Artefakt: `app/core/workflow_definitions.py`

## Aktuelle Felder
- `process_key`
- `version`
- `origin`
- `tenant_id`
- `status`
- `steps`
- `required_roles`
- `step_sla.timeout_hours`
- `step_sla.escalation_roles`
- `description`

## Erste Designentscheidung
- Prozessvarianten werden nicht länger nur als lose `dict[str, Any]` behandelt
- Admin-API und Workflow-Sandbox validieren auf `WorkflowDefinition`

## Nächster Schritt
- `A4` Instanzreferenz und Migrationsmodell an dieses Schema anhängen
