# Next Module Migration Playbook

With schema descriptors and the scaffold orchestrator in place, migrating additional domains (ERP finance/inventory, analytics, HR, etc.) follows a repeatable sequence.

## Preparation Checklist

1. **Select descriptor**: locate the table file in `memory-bank/migration/schemas` (use `schema-registry.json` to filter by domain).
2. **Decide scope**: group tables into migration batches (e.g. finance core = konten, buchungen, debitoren*). Each batch becomes a sprint backlog item.
3. **Confirm infrastructure**: ensure the matching Postgres container is running and migrations for the target domain exist (or plan new SQL files under `migrations/sql/<domain>`).

## Scaffold Workflow (per table/aggregate)

```powershell
npx ts-node --transpile-only tools/codegen/scaffold_domain.ts `
  --domain erp `
  --entity finanz_buchung `
  --schema memory-bank/migration/schemas/finance_finanz_buchungen.json `
  --route /erp/finance/bookings
```

This command generates:
- Core entity (`domains/<domain>/src/core/entities`)
- Postgres repository (`domains/<domain>/src/infrastructure/repositories`)
- Service + controller + bootstrap wiring
- Integration test scaffold (skipped with `--skip-tests` if required)

## Post-Generation Tasks

1. **Adapt business logic**: enrich the generated service with domain rules and data validation.
2. **Wire persistence**: update the domain bootstrap to register the module with the application container, reusing `packages/utilities/src/postgres.ts`.
3. **Run migrations**: execute the SQL bundle for the tables (create new ones if missing).
4. **Execute tests**: run `npm run test --workspace domains/<domain>` or targeted Jest suites.
5. **Document findings**: append lessons to `memory-bank/lessons-learned` and update the migration table.

## Sprint Planning Template

- **Sprint Goal**: Deliver <domain> <subset> running against Postgres with end-to-end API coverage.
- **Milestones**:
  1. Generate scaffolds via `scaffold_domain.ts` for all tables.
  2. Implement repositories/services with business logic.
  3. Connect controllers to platform gateway and verify via integration tests.
  4. Update documentation + memory bank, handover to QA.

## Notes

- Keep migrations deterministic—regenerate schema descriptors if legacy SQL evolves.
- The orchestrator assumes descriptor filenames follow the `<prefix>_<schema>_<table>.json` convention.
- Extend the orchestrator when additional artefacts (e.g. event handlers) become standard for a module.
## Known Limitations
- `tools/codegen/scaffold_domain.ts` currently triggers the nested ts-node loader error (`Expected ',' got '$'`). Continue using the individual generator commands until the orchestrator is hardened.