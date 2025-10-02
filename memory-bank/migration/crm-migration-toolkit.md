# CRM Migration Toolkit & Playbook

This playbook records the *working* approach we used to move the CRM domain from VALEO-NeuroERP-2.0 into the new MSOA architecture. Treat it as the baseline for the ERP, Analytics, and Integration migrations. The corresponding script manifest lives in [`tools/migration/CRM_TOOLKIT.md`](../../tools/migration/CRM_TOOLKIT.md) and [`crm-toolkit.json`](../../tools/migration/crm-toolkit.json).

---

## 1. End-to-End How-To (Repeatable Workflow)

1. **Inventory the legacy code**
   - `python tools/migration/legacy_inventory.py ..\VALEO-NeuroERP-2.0 --include crm`
   - Archive the CSV/JSON outputs in `memory-bank/inventories/` for traceability.
2. **Model the target schema**
   - Copy the relevant `.sql` files from the legacy repo.
   - Apply branding/tenant ID updates.
   - Place the result under `migrations/sql/<domain>/<ordinal>_<name>.sql`.
3. **Generate scaffolding**
   - Entities: `ts-node tools/codegen/entity_generator.ts crm Customer name:string email?:string status:string`
   - Repository: `ts-node tools/codegen/repository_generator.ts crm Customer`
   - Tests: `ts-node tools/codegen/test_generator.ts crm repository CustomerRepository`
4. **Run the migrations**
   - `ts-node tools/migration/run_sql_migration.ts $env:CRM_DATABASE_URL migrations/sql/crm/001_crm_schema.sql`
   - Re-run with seed files as needed.
5. **Wire services**
   - Use the generated repository skeleton, replace TODOs with real SQL, and import the shared pool helper from `packages/utilities/src/postgres.ts`.
   - Bootstrap the domain via `domain_bootstrap_generator.ts` or amend the existing `bootstrap.ts` manually.
6. **Validate**
   - Run Jest integration tests in `domains/crm/tests` once they point to a seeded database.
   - Smoke-test HTTP controllers against the Docker stack if available.
7. **Document results**
   - Update the migration table in the memory bank.
   - Record blockers/open tasks under “Lessons Learned & Follow-up”.

---

## 2. Script Catalogue (Confirmed Working)

| Script | Role in CRM Migration | Notes |
| --- | --- | --- |
| `tools/migration/legacy_inventory.py` | Produced the initial file/domain inventory. | Handles encoding edge cases via `errors="ignore"`; pass `--include` filters to keep runtime low. |
| `tools/migration/run_sql_migration.ts` | Applied CRM schema + seed scripts to Dockerised Postgres. | Requires `ts-node`; wrap multiple files with a shell loop. |
| `tools/codegen/domain_bootstrap_generator.ts` | Generated base `bootstrap.ts`, later customised for environment wiring. | Adjust import paths if the target service locator package differs. |
| `tools/codegen/entity_generator.ts` | Created branded `Customer` model skeleton. | Supplement with domain-specific validation (e.g. VAT format). |
| `tools/codegen/repository_generator.ts` | Produced repository interface + Postgres skeleton; we replaced SQL stubs with actual queries. | Ensures compatibility with shared Postgres helper. |
| `tools/codegen/test_generator.ts` | Scaffolded Jest specs for repositories/services/controllers. | Extend with scenario-specific assertions (e.g. uniqueness checks). |

Supporting utilities:
- `packages/utilities/src/postgres.ts` (connection pooling + query helper).
- Docker compose services (`.infrastructure/docker-compose/docker-compose.yml`) for CRM Postgres.

---

## 3. Lessons Learned (Use for Future Domains)

### 3.1 SQL & Data
- **String quoting:** When porting legacy SQL, convert double quotes in text columns to single quotes. Use `E''` escaping for backslashes.
- **Idempotent seeds:** Always append `ON CONFLICT DO NOTHING` or perform existence checks; this allowed multiple test runs without dropping databases.
- **Branded IDs:** Legacy integer IDs were replaced with UUID-based branded types. Update primary/foreign keys accordingly before importing data.

### 3.2 TypeScript & Tooling
- **ts-node constraints:** Provide `TS_NODE_PROJECT=tsconfig.json` when running generators from different working directories; otherwise path aliases fail.
- **Pool disposal:** Integration tests must import `disposePools()` in `afterAll` to avoid open handle warnings.
- **Path aliases:** Align generator output with the actual `tsconfig` paths; rewired imports to relative paths when alias resolution lagged behind.

### 3.3 Docker & Environment
- `CRM_DATABASE_URL` is injected via compose; replicate that pattern for ERP (`ERP_DATABASE_URL`) before enabling those repositories.
- ClickHouse health checks require extra startup time; wait for `docker ps` to report `healthy` before running analytics migrations.
- Keep Postgres containers warm during migration sprints—cold starts add 10–15 seconds to integration pipelines.

### 3.4 Process Optimisations
- Use the inventory CSV to drive the migration table manually—attempts to auto-import into spreadsheets cost more time than manual curation.
- Start with the simplest generator parameters; progressively add fields/relations after verifying baseline output.
- Version every script change in Git before regenerating code to keep diffs reviewable.

---

## 4. Open Items & Follow-up

| Topic | Status | Next Action |
| --- | --- | --- |
| Schema descriptors (`memory-bank/schema-registry.json`) | Draft | Capture JSON descriptors for ERP entities before running generators. |
| Multi-file SQL runner | Backlog | Extend `run_sql_migration.ts` to accept directories or glob patterns. |
| Generator output validation | Backlog | Add automated smoke tests ensuring generated code compiles against workspace `tsconfig`. |
| ERP Postgres automation | In progress | Mirror CRM wiring: expose container port, export `ERP_DATABASE_URL`, seed via migrations. |

---

## 5. Checklists

### Before Starting a New Domain
- [ ] Legacy inventory updated and reviewed.
- [ ] Migration table entries created with priority/complexity ratings.
- [ ] SQL schemas ported and annotated with branded IDs.
- [ ] Environment variables registered (.env, compose, CI secrets).

### After Completing Migration Tasks
- [ ] Generators customised, manual code review performed.
- [ ] Tests executed locally (unit + integration); coverage captured.
- [ ] Memory bank updated with outcomes and blockers.
- [ ] Tool manifest (`crm-toolkit.json`) updated if scripts/flags changed.

---

## 6. References
- Toolkit manifest: [`tools/migration/CRM_TOOLKIT.md`](../../tools/migration/CRM_TOOLKIT.md)
- Script metadata JSON: [`tools/migration/crm-toolkit.json`](../../tools/migration/crm-toolkit.json)
- Database migrations: [`migrations/sql/crm`](../../migrations/sql/crm)
- Utility helpers: [`packages/utilities/src/postgres.ts`](../../packages/utilities/src/postgres.ts)
- Docker compose: [`.infrastructure/docker-compose/docker-compose.yml`](../../.infrastructure/docker-compose/docker-compose.yml)

Keep enriching this document after each sprint. Add concrete command snippets, schema notes, and time-saving shortcuts as we process further domains.
