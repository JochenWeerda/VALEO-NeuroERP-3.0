# L3 → VALEO-NeuroERP Import: Best Practices Draft

This draft collects recommended conventions for bridging the legacy L3 data model into the VALEO-NeuroERP platform. It complements `docs/db/l3_import.md` with opinionated guidance so the upcoming scripts and migrations can be implemented consistently.

## 1. Canonical Metadata & Mapping Governance
- **Single Source**: Maintain `docs/data/l3/raw_tables.json` as the unmodified truth extracted from the XHTML export. Re-run the extractor whenever L3 delivers an updated schema.
- **Mapping File**: Keep `config/l3_mapping.yaml` versioned in Git. Every entry should include: `target`, `type`, `transform` (if required), and `notes` for tricky cases.
- **Reviews**: Treat mapping edits like code—use pull requests, require at least one domain owner approval, and run lightweight validation (`python scripts/validate_mapping.py`) in CI.
- **Naming Discipline**: Normalize table/column names while writing the mapping (e.g. uppercase legacy identifiers → snake_case target) and capture aliases to avoid ambiguity during ETL transforms.

## 2. Schema Bootstrap Strategy
- **Alembic First**: All schema objects needed for the 181 masks should live in Alembic migrations. Prefer `CREATE SCHEMA IF NOT EXISTS` plus idempotent table creation.
- **Bootstrap Script**: `scripts/bootstrap_db.py` should orchestrate:
  - database emptiness check (`SELECT COUNT(*) FROM information_schema.tables ...`);
  - optional `--force` teardown for dev/CI;
  - optional `--seed` to insert deterministic test fixtures.
- **Config Awareness**: Respect environment variables (e.g. `VALEO_ENV=prod|stage|dev`). Forbid destructive actions unless `VALEO_ENV != prod` or an explicit override flag is provided.

## 3. ETL & Staging Pipeline
- **Raw Landing Zone**: Import L3 dumps into a dedicated `l3_staging` schema (one table per L3 table, identical column names and types as close as possible).
- **Transform Layer**: Build a pure function module (`app/services/l3_transform.py`) that receives staging rows and mapping metadata, emits validated domain objects, and tracks conversion issues.
- **Dry Run Default**: `scripts/import_l3.py` should run in dry-run mode unless `--execute` (or similar) is passed. Dry runs log prospective actions, enabling validation without touching production data.
- **Incremental Imports**: Support both full reloads and incremental batches (e.g. `--since 2024-01-01`). Record import checkpoints in a small control table (`app_control.l3_import_runs`).

## 4. Production Safety Nets
- **Confirmation Workflow**: Destructive commands demand explicit confirmation, e.g. `python scripts/bootstrap_db.py --force --confirm DELETE-PROD`.
- **Backups**: Automatically trigger `pg_dump` (or the current DB backup process) before any operation that rewrites data. Store the dump path in the run logs.
- **Audit Trail**: Centralize logs under `logs/db/import_l3.log`, include timestamps, environment, operator, dry-run/execute mode, row counts, and errors.
- **Role Separation**: Ensure only deployment/DBA accounts can perform executes; developers stay limited to dry runs or sandbox databases.

## 5. Testing & Quality Gates
- **Unit Tests**: Cover parsing, mapping validation, and critical transforms (date conversions, enum mapping). Use synthetic fixtures in `tests/l3_import/`.
- **CI Guardrail**: The GitHub Actions pipeline (`ci.yml`) invokes `python scripts/validate_mapping.py --fail-on-warn` so PRs fail when mappings drift from raw metadata or domain rules.
- **Integration Harness**: Add a CI job (`ci/l3_mock_import.yml`) that spins up Postgres, runs bootstrap with seeds, executes ETL in dry-run, and exercises a representative mask test suite.
- **Data Quality Rules**: Encode mandatory checks (not-null, range, referential integrity) as assertions. On failure, abort and provide actionable diagnostics referencing the offending table/column.
- **Regression Data**: Maintain a curated set of L3 samples under `data/l3_samples/` to reproduce historical issues and prevent regression gaps.

## 6. Operational Workflow
- **Runbook**: Extend `docs/db/import_l3.md` with an operator-centric checklist: backup, dry run, review logs, execute, post-run verification, and rollback procedure.
- **Monitoring**: Emit Prometheus metrics (e.g. import duration, rows processed, failed rows) from the ETL script when running in service mode.
- **Change Management**: Whenever the mapping or schema changes, communicate via release notes and require a mask regression round before promoting to production.

## 7. Open Items to Refine
1. Decide where `scripts/validate_mapping.py` should live and what validations (duplicate targets, missing target columns, unsupported transforms) it enforces.
2. Align domain owners around naming conventions for new schemas/tables created during bootstrap.
3. Specify the exact CI environments (GitHub Actions, GitLab, Azure) and secrets handoff for database credentials.
4. Draft disaster recovery steps (restore from backup, re-run ETL) and incorporate them into the operator runbook.

Feedback is welcome—this draft is meant to be iterated as we implement the bootstrap, migrations, and ETL tooling.

## 8. Domain Owner Review Checklist
- **Finance (domain_finance)**: Confirm fiscal period tables cover all reporting requirements, agree on currency handling, and specify how legacy codes (`CODE1`-`CODE5`) map to modern analytics cubes.
- **CRM/Sales (domain_crm)**: Validate cancellation/absage reasons, contact hierarchies, and lead status enums; mark columns that should become reference-data tables instead of free-text fields.
- **Inventory/Logistics (domain_inventory)**: Review unit-of-measure conversions, stock location granularity, and batch/lot traceability; flag columns requiring historical retention for compliance.
- **HR/Workforce (domain_hr)**: Decide which personal data needs pseudonymisation, map legacy role IDs to IAM roles, and identify sensitive fields requiring masking in non-prod environments.
- **Manufacturing/Production (domain_mfg)**: Check routing/BOM structures, ensure staging captures all timestamped events, and agree on default values for missing telemetry.
- **Cross-Cutting**: For every domain, annotate data quality contracts (nullability, lookup dependencies), regulatory constraints (GDPR, audit), and the owner of acceptance tests for mask validation.
