# CRM Migration Toolkit (Working Scripts Reference)

This collection lists the scripts that proved reliable during the CRM domain migration. Use the same commands as blueprints when migrating additional domains.

| Tool | Location | Purpose | Key Dependencies | Sample Command |
| --- | --- | --- | --- | --- |
| Legacy Inventory | `tools/migration/legacy_inventory.py` | Scans VALEO-NeuroERP-2.0 and produces CSV/JSON inventory for prioritising migration targets. | Python 3.10+, standard library | `python tools/migration/legacy_inventory.py ../VALEO-NeuroERP-2.0 --include crm` |
| SQL Migration Runner | `tools/migration/run_sql_migration.ts` | Executes raw SQL migrations/seeds against a Postgres database using shared pool helper. | Node 18+, `ts-node` (local or via `npx`), `pg` workspace dependency | `ts-node tools/migration/run_sql_migration.ts $env:CRM_DATABASE_URL migrations/sql/crm/001_crm_schema.sql` |
| Domain Bootstrap Generator | `tools/codegen/domain_bootstrap_generator.ts` | Generates MSOA-compliant bootstrap scaffolding per domain (service locator wiring, env vars). | Node 18+, `ts-node`, write access to `domains/<domain>/src` | `ts-node tools/codegen/domain_bootstrap_generator.ts crm` |
| Entity Generator | `tools/codegen/entity_generator.ts` | Generates branded types, entity interfaces, and mapping helpers based on legacy metadata. | Node 18+, `ts-node`, JSON descriptors | `ts-node tools/codegen/entity_generator.ts crm Customer name:string email?:string` |
| Repository Generator | `tools/codegen/repository_generator.ts` | Produces repository interface + Postgres implementation skeletons aligned with shared pool helper. | Node 18+, `ts-node`, existing entity definitions | `ts-node tools/codegen/repository_generator.ts crm Customer` |
| Test Generator | `tools/codegen/test_generator.ts` | Emits baseline unit/integration tests for entities, services, repositories, controllers. | Node 18+, `ts-node`, Jest configured in workspace | `ts-node tools/codegen/test_generator.ts crm repository CustomerRepository` |

## Usage Notes

- **ts-node availability:** Already installed in the workspace; invoke scripts with `ts-node ...` as shown above.
- **Shared Postgres helper:** All generated repositories rely on `packages/utilities/src/postgres.ts`. Ensure pools are disposed using `disposePools()` in tests.
- **SQL ordering:** Prefix migration filenames with increasing numbers (e.g. `001_`, `002_`) so the runner applies them predictably.
- **Idempotent seeds:** Structure seed SQL with `ON CONFLICT DO NOTHING` to make repeated runs safe.
- **CRM env vars:** Export `CRM_DATABASE_URL` before running repositories or integration tests. Compose already injects this value when using the provided docker setup.

## Suggested Automation Flow

1. Run `legacy_inventory.py` targeting the legacy module to collect the candidate files and dependencies.
2. Use the CSV/JSON output to populate the migration tracking table in the memory bank.
3. Generate entities, repositories, and tests with the `codegen` scripts using the descriptors from legacy models.
4. Adapt generated code manually to include business rules, cross-entity validation, and branded IDs.
5. Apply the SQL migrations via `run_sql_migration.ts` and seed reference data.
6. Execute the generated Jest integration suites to verify connectivity against the Postgres containers.

## Known Limitations

- Generators currently rely on inline parameter lists; large schemas benefit from JSON descriptors (capture in `schema-registry.json` before invoking).
- `domain_bootstrap_generator.ts` assumes controller filenames follow `{domain}-api-controller.ts`; adjust generated path imports when domains differ.
- The SQL runner streams a file in one command; it does not manage transactional batches or schema version tables yet. Wrap critical migrations in explicit `BEGIN/COMMIT` blocks inside the SQL file if needed.
- `legacy_inventory.py` filters by substring; for complex include/exclude logic feed it a pre-built file list via Python piping.

Update this file whenever a script gains new flags or when additional helpers graduate from experimental to production-ready.
