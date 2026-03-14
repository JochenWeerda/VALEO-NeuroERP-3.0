# PKP-02 Instanzreferenz- und Migrationsmodell

## Zweck
- laufende Workflow-Instanzen explizit an eine Definitionsversion binden
- spätere Migrationen strukturiert statt implizit modellieren

## Status
- erstes Backend-Feldmodell angelegt
- Code-Artefakt: `app/core/workflow_definitions.py`

## Kernobjekte
- `WorkflowInstanceReference`
- `WorkflowBusinessReference`
- `WorkflowMigrationPlan`

## Kerngedanke
- laufende Instanzen referenzieren immer `process_key`, `definition_version` und `definition_origin`
- fachlicher Kontext wird über `business_reference` angebunden
- Migrationen werden über eigenes `WorkflowMigrationPlan`-Modell beschrieben

## Aktuelle Migrationsstrategien
- `new-instances-only`
- `in-place`
- `manual-review`
- `replay-required`

## Nächster Schritt
- Persistenz- und Audit-Anbindung für echte Workflow-Instanzen definieren
