# VALEO NeuroERP 3.0 – Engineering Tooling

The `tools/` workspace hosts the scripts that automated the CRM migration and will be reused for upcoming domains. Combine this README with the curated manifest in [`tools/migration/CRM_TOOLKIT.md`](migration/CRM_TOOLKIT.md) for a quick start.

## Prerequisites

- **Node.js = 18** with npm workspaces enabled.
- **ts-node** included in workspace devDependencies; run tooling with `ts-node …`.
- **Python = 3.10** for the legacy inventory helper.
- **PostgreSQL client connectivity** (Docker compose spins up local instances; environment variables such as `CRM_DATABASE_URL`, `ERP_DATABASE_URL` must be exported before running repositories/tests).

## Tool Catalog

### Code Generation (`tools/codegen`)

| Script | Description | Typical Usage |
| --- | --- | --- |
| `domain_bootstrap_generator.ts` | Emits domain bootstrap skeleton (service locator wiring, env var mapping). | `ts-node tools/codegen/domain_bootstrap_generator.ts crm`
| `entity_generator.ts` | Creates entities with branded types and base validation helpers. Accepts inline fields or references JSON descriptors. | `ts-node tools/codegen/entity_generator.ts crm Customer name:string email?:string`
| `repository_generator.ts` | Produces repository interface + Postgres implementation scaffold that uses `packages/utilities/src/postgres`. | `ts-node tools/codegen/repository_generator.ts crm Customer`
| `test_generator.ts` | Generates Jest test baselines (unit + integration). Extend them with business rules after generation. | `ts-node tools/codegen/test_generator.ts crm repository CustomerRepository`

**Generator hints**
- Store reusable field definitions in `memory-bank/schema-registry.json` and feed them into the generators in upcoming sprints.
- Generated imports follow conventional filenames; adjust when the target directory deviates.

### Migration (`tools/migration`)

| Script | Description | Typical Usage |
| --- | --- | --- |
| `legacy_inventory.py` | Catalogues the legacy (2.0) codebase; outputs CSV/JSON with file sizes and domain hints for migration planning. | `python tools/migration/legacy_inventory.py ..\VALEO-NeuroERP-2.0 --include crm`
| `run_sql_migration.ts` | Streams a SQL file to Postgres using the shared connection pool helper. Keeps pooled connections for reuse until `disposePools()` is called. | `ts-node tools/migration/run_sql_migration.ts $env:CRM_DATABASE_URL migrations/sql/crm/001_crm_schema.sql`

**Migration hints**
- Wrap destructive SQL in `BEGIN; … COMMIT;` inside the file because the runner does not add implicit transactions.
- Prefix filenames with an ordinal (`001_`, `002_`) to preserve execution order.
- The CRM Docker compose file already sets `CRM_DATABASE_URL`; replicate the pattern for other domains before running migrations inside containers.

### Testing (`tools/testing`)

Existing helpers (coverage reporter, watch scripts) rely on Jest. Update runners when adopting Vitest or other frameworks. Review each file before reuse; most expect a `--domains <name>` argument.

## CRM Toolkit Snapshot

The CRM migration relied on a stable subset of scripts. The definitive manifest, usage notes, and lessons learned live in [`tools/migration/CRM_TOOLKIT.md`](migration/CRM_TOOLKIT.md). Treat that file as the authoritative checklist when starting another domain.

## Adding New Tools

1. Place new helpers under an appropriate subdirectory (`codegen`, `migration`, `testing`, `ci`).
2. Document the script at the top of the file and add a short entry to the tables above.
3. Update the memory bank (see `memory-bank/migration`) with scenarios and pitfalls discovered during use.

## Known Limitations & Follow-up

- `run_sql_migration.ts` currently processes a single file. Wrap it in a shell loop or extend it to walk a directory when batch execution is required.
- The code generators do not yet consume the planned `schema-registry.json`. Capture descriptors during ERP analysis and patch the generators to ingest them in the next sprint.
- Some generated paths point to placeholders (e.g. `@packages/utilities/service-locator`). Ensure those packages exist before committing the output.
- If TypeScript path aliases diverge from defaults, pass the `TS_NODE_PROJECT` environment variable so `ts-node` resolves the correct `tsconfig.json`.

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| `ts-node: command not found` | Install `ts-node` globally (`npm install -g ts-node`) or call scripts via `ts-node …` |
| `Error: connection refused` when running migrations | Confirm the Postgres Docker container is up and that the relevant `*_DATABASE_URL` env var is exported. |
| UnicodeDecodeError in `legacy_inventory.py` | The script opens files with `errors="ignore"`; rerun with `--include` filters to skip binary assets if the error persists. |
| Generated repositories fail tests due to missing pool | Import and invoke `getPostgresPool({ connectionString, name })` before executing queries, and dispose pools (`disposePools()`) in `afterAll`. |

Keep this README concise and factual; detailed run-books belong in the memory bank.
