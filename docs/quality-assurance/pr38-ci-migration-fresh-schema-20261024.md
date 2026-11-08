---
title: PR38 CI migration and fresh-schema follow-up
type: reference
owner: Codex
status: review
last_reviewed: 2026-10-24
---

# PR38 CI migration and fresh-schema follow-up

The failed PR38 strict and six smoke jobs at `7bc7e37fa` stopped in
`scripts/init_db.py` before running tests. Alembic could not resolve
`loading_tenant_20261023`'s predecessor `dms_inbox_tenant_20261022` and raised
`KeyError: 'dms_inbox_tenant_20261022'`. The predecessor was present in the
separately verified PR39 source and is now included unchanged in the PR38
repair source. Its SHA-256 is
`08b4a1a16cf67e167679f78e7736f27f77d4bbdfb39c43444a2c0607a872d32e`.
The generated migration inventory includes the revision. `python -m alembic
heads` now resolves the single head `loading_stop_fk_20261023`; the history
shows `portal_interessenten_preise_20261020` → `dms_inbox_tenant_20261022` →
`loading_tenant_20261023` → `loading_stop_fk_20261023`.

For the physical table catalog, the PR38 and PR39 source trees contain exactly
437 Alembic migration files with the same names and zero content differences
after CRLF/LF normalization. `scripts/init_db.py`, `alembic/env.py`,
`app/core/database.py`, the catalog generator, table ownership classifier, and
all model files explicitly imported by `create_tables()` have identical
normalized content. The PR38 Outbox difference changes delivery methods only,
not its mapped table. The PR38 lineage collector additionally loads the Stamm
screen registry; this affects consumer links, not the physical schema.

The available CI39 fresh PostgreSQL artifact at `93161e503` reports **31
schemas, 688 tables, 9096 columns**. The prior PR38 catalog reported 681 tables
and 9011 columns; it is stale. Its table set omitted nine tables present in the
fresh artifact and retained two `studio_abnahme_20261021` tables absent there.
The repaired PR38 catalog uses the CI39 artifact's physical tables, columns,
keys, ownership and placement unchanged, then recomputes read/write/screen
lineage from the clean published PR38 source at
`artifacts/workspace-closure-head-source`. The repair view has 22 pending
API/ScreenDefinition edits, so it is not used as catalog source. Comparing the
two lineages identified ten table entries influenced by those pending edits;
the published-HEAD derivation excludes them. The physical portion compares
exactly equal to the CI39 artifact; all 688 tables are present and the native
entity-table lineage check reports zero missing references.

The post-fix PR38 run `40095003871` confirms `Alembic head OK:
loading_stop_fk_20261023`; its backend job then fails at the documentation
drift gate with 272 `page_no_route_or_nav` findings. It stops before a fresh
catalog artifact is uploaded. In run `40095003898`, Agrar, Finance, and Sales
smoke jobs each print `Database schema migrated to head.` before browser
assertions fail. Therefore the original migration graph blocker is closed,
while direct PR38 fresh-catalog comparison is still outstanding.

Local schema-free regression checks (`test_alembic_single_head.py`,
`test_generate_table_catalog.py`, `test_generate_code_inventories.py`) finished
with 14 passed and one live-database case skipped. The four composite-FK
database tests were not rerun in this follow-up.

The smoke failure artifacts identify UI behavior separately from schema:

- Agrar: three pages show `Workspace konnte nicht geladen werden.`; the
  Sortenregister renders a generic list without the expected `Suche Sorten`
  input.
- Finance: Zahlungseingang renders a generic list headed `Zahlungseingang`,
  while the smoke test expects `Zahlungseingang / Auszifferung`.
- Sales: the three O2C pages render generic headings that differ from the
  expected business headings. The Angebote list renders `Angebot erstellen`
  without the list/table/card/empty-state markers expected by its smoke test.

The three Agrar workspace failures are confirmed HTTP 404 responses in the
Playwright network traces for the ScreenDefinition URLs ending in
`agrar__duenger__bedarfsrechner`, `agrar__psm__liste`, and `agrar__psm__stamm`.
The frontend pages request those exact IDs. The registry instead contains
`agrar/psm-liste` and `agrar/psm`; it contains no Bedarfsrechner definition.
`agrar/duenger-rechner` exists but is a statistics-list definition, not the
former calculator. Before the Studio conversion, the Bedarfsrechner page was a
wizard with area/crop/soil inputs, LWK grassland and cereal/rape tables, NPK
calculation, export, and a handoff to planning. Redirecting it to the statistics
list would not restore that function. The PSM list reads BVL (`?source=bvl`),
while the existing PSM detail definition defaults to a local-only GET; simply
renaming the screen ID would leave row-to-detail data-source parity unresolved.

Narrow repair ownership is `packages/frontend-web/src/pages/agrar/psm/liste.tsx`
and `stamm.tsx` for canonical screen IDs and object routing;
`app/core/screen_definitions_stamm.py` for PSM detail field/source parity; and
`packages/frontend-web/src/pages/agrar/duenger/bedarfsrechner.tsx` plus a real
calculation-capable ScreenDefinition/command contract for the Bedarfsrechner.
This section is diagnosis only; no production code was changed here.

This is a source-equivalence and transferred fresh-schema proof, not a new
PR38 database catalog harvest. No database, container, migration, reset, or
cleanup was performed during this follow-up.
