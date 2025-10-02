# Schema Descriptor Registry

The `memory-bank/migration/schemas` directory now captures machine-friendly descriptions for every legacy module. These JSON files are generated directly from the frozen 2.0 SQL scripts via `tools/migration/sql_to_schema_json.py` and indexed in `schema-registry.json`.

## Directory Layout

- `schema-registry.json` – central index with `{ baseDir, domains, count }`. Use this for quick lookups or programmatic tooling.
- `schemas/*.json` – one file per legacy table. Filenames follow `<domain>_<schema>_<table>.json` (e.g. `erp_finanz_buchungen.json`).

Each descriptor contains:

```json
{
  "schema": "finanz",
  "name": "buchungen",
  "primaryKey": "id",
  "fields": [
    {
      "name": "id",
      "type": "UUID",
      "nullable": false,
      "default": "gen_random_uuid()",
      "constraints": ["primary-key"]
    }
  ],
  "rawSource": "CREATE TABLE ..."
}
```

The `rawSource` block keeps the exact `CREATE TABLE` snippet so we can audit constraints beyond the generated metadata.

## Regeneration Workflow

1. Ensure the legacy repository is mounted (default path `../VALEO-NeuroERP-2.0`).
2. Run the extractor with the SQL path and an optional filename prefix:
   ```powershell
   python tools/migration/sql_to_schema_json.py `
     --sql ..\VALEO-NeuroERP-2.0\database\finance_schema.sql `
     --prefix finance
   ```
3. Refresh the registry index for tooling:
   ```powershell
   python tools/migration/update_schema_registry.py
   ```

Repeat for any additional SQL bundles you uncover. Regeneration is idempotent—the script overwrites existing JSON files.

## Using Descriptors With the Generators

- **Entities**: pass the descriptor to `entity_generator.ts` to scaffold domain models.
- **Repositories**: the same JSON powers `repository_generator.ts`. Foreign-key hints appear in `constraints`.
- **Services/Controllers/Bootstraps**: after generating the repository, reuse the existing chain (`service_generator.ts`, `controller_generator.ts`, `domain_bootstrap_generator.ts`).

Example for the ERP finance ledger:
```powershell
npx ts-node --transpile-only tools/codegen/entity_generator.ts `
  --domain erp --entity finanz_buchung `
  --schema memory-bank/migration/schemas/finance_finanz_buchungen.json
```

## Next Steps

- Map descriptor groups to migration sprints (e.g. CRM batch ? Sprint 1, Finance ? Sprint 2).
- Add validation to flag missing primary keys or nullable fields that violate new architecture rules.
- Extend the extractor to capture foreign-key targets explicitly (currently noted via `constraints: ["foreign-key"]`).