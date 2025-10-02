# ERP Finance Sprint 01

## Scope
- Generated finance schema descriptors (`memory-bank/migration/schemas/finance_*`).
- Scaffolded ERP finance modules (Konten, Buchungen, Debitoren, Kreditoren, Bankkonten).
- Implemented finance core migration SQL (`migrations/sql/erp/001_finance_core.sql`).

## Implementation Notes
- `FinanzKonto` service enforces kontotyp, kontonummer uniqueness, and steuerschiene bounds.
- `FinanzBuchung` service normalises amount and dates, synthesises fallback booking numbers.
- Repository for `finanz.konten` now performs typed mapping and returns persisted entities.
- Controller generator now supports literal interpolation escaping so subsequent scaffolds work out of the box.

## Outstanding
- Wire `FinanzBuchung` repository with richer joins and account validation once account service is available.
- Add uniqueness helpers for Debitor/Kreditor services; current implementation still uses generated CRUD.
- Execute `tools/migration/run_sql_migration.ts --dir migrations/sql/erp --env ERP_DATABASE_URL` after ensuring the database container exposes a host port (compose currently lacks `ports` mapping).

## Follow-up Tests
- `npm run test --workspace domains/erp` once Jest configuration exists for the domain.
- Manual smoke: call each bootstrap `init*Module` with a live `pg.Pool` and hit the REST routes.