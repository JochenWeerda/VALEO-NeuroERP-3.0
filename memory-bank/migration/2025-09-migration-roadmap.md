# Migration Roadmap (September–November 2025)

This roadmap continues the migration journey after completing the CRM spike. Each sprint spans two weeks and follows the validate ? plan ? implement ? reflect ? handover cadence mandated by the project charter. All milestones must adhere to the MSOA fundamentals (Type-Safe First, Zero Context, Domain-Driven Business Logic, Module Federation, Lifecycle Management).

| Sprint | Dates | Primary Focus | Key Deliverables | Definition of Done |
| --- | --- | --- | --- | --- |
| **S4** | 29 Sep – 10 Oct | ERP Finance & Inventory Foundations | • Finance + inventory SQL migrations (`migrations/sql/erp/001_*`)<br>• Postgres repositories wired via shared pool helper<br>• Jest integration suite green (finance/inventory repositories)<br>• `ERP_DATABASE_URL` propagated through compose/env | • Migrations run on Docker Postgres 5433<br>• Integration tests = 85% coverage<br>• Memory bank updated (`erp-finance-sprint-01.md` addendum)<br>• Toolkit enhanced with ERP descriptors (`schema-registry.json`) |
| **S5** | 13 Oct – 24 Oct | ERP Order & Procurement Services | • Order, procurement, supplier entities + services generated via scaffolder<br>• Cross-entity validation (debitor/kreditor/bankkonto) implemented with branded IDs<br>• REST controllers exposed through domain bootstrap<br>• Postman/E2E smoke against compose stack | • End-to-end CRUD flow passes (orders, suppliers)<br>• API docs (OpenAPI) published in docs/architecture/api<br>• Error handling documented in memory bank lessons<br>• CI pipeline runs new suites without regressions |
| **S6** | 27 Oct – 07 Nov | ERP Integrations & Shared Utilities | • Shared utilities package hardened (transaction helpers, error mappers)<br>• Async workflows (service bus bindings) for ERP events<br>• Data seeding scripts for finance/order reference data<br>• `run_sql_migration.ts` supports directory/glob execution | • Service bus integration tested with dockerised RabbitMQ<br>• Seeds rerunnable and documented<br>• Toolkit JSON updated with new scripts<br>• Tech-debt log captures remaining ERP gaps |
| **S7** | 10 Nov – 21 Nov | Analytics Domain Enablement | • Analytics schema migrations (ClickHouse + Postgres analytics)<br>• Data ingestion services scaffolded with generators<br>• Reporting API baseline + integration tests<br>• Monitoring dashboards wired (Grafana) | • ClickHouse health check stable in compose<br>• Analytics tests executed with seeded data<br>• Observability docs in memory bank (`analytics-observability.md`)
|
| **S8** | 24 Nov – 05 Dec | Integration Domain (External Connectors) | • Legacy connector inventory processed via `legacy_inventory.py` filters<br>• New integration services scaffolded (webhooks, sync jobs)
• Security hardening (API keys, rate limiting)
• Comprehensive runbooks for partner onboarding | • Pen-test checklist completed<br>• Integration smoke tests executed against sandbox endpoints
• Memory bank updated with connector migration table |
| **S9** | 08 Dec – 19 Dec | Hardening & Release Prep | • ts-node installed workspace-wide; generators validated via smoke script
• Performance benchmarks for ERP/CRM flows (load test scripts)
• Documentation sweep (memory bank, architecture)
• Release checklist + handover package | • All automation commands reproducible without `npx`
• Performance targets met (P95 < 500?ms)
• Handover docs signed off by stakeholders |

---

## Sprint Backlogs & Dependencies

### Sprint 4 (ERP Finance & Inventory)
- [ ] Import legacy finance/inventory SQL schemas; merge into `migrations/sql/erp/001_*` with branded IDs.
- [ ] Capture entity descriptors in `memory-bank/schema-registry.json` for scaffolder automation.
- [ ] Run `scaffold_domain.ts` (after ts-node loader patch) to generate finance/inventory skeletons.
- [ ] Wire repositories to `packages/utilities/src/postgres.ts`; add Joi/Zod validation.
- [ ] Execute Jest integration suites (`npm run test --workspace=domains/erp`).
- [ ] Update memory bank entry `migration/erp-finance-sprint-01.md` with outcomes and open risks.

**Dependencies:** Docker compose ERP Postgres container exposed on 5433, `ERP_DATABASE_URL` configured, `ts-node` dependency installed.

### Sprint 5 (ERP Order & Procurement)
- [ ] Generate order, procurement, supplier entities/services/controllers using descriptors.
- [ ] Implement cross-entity rules (credit limit checks, supplier compliance) with branded IDs.
- [ ] Add transactional support via utility package (begin/commit/rollback wrappers).
- [ ] Extend API router bootstrap to expose new endpoints; ensure auth/permission middleware reused.
- [ ] Produce OpenAPI spec and publish under `docs/api/erp-ordering.yaml`.
- [ ] Expand integration tests to cover service bus events and HTTP flows.

**Dependencies:** Sprint 4 repositories available, service bus docker container healthy, run_sql_migration enhancements scheduled Sprint 6.

### Sprint 6 (ERP Integrations & Shared Utilities)
- [ ] Enhance `run_sql_migration.ts` to accept glob/directory; add CLI tests under `tools/testing`.
- [ ] Build data seeding scripts leveraging new runner (e.g. `migrations/sql/erp/seeds/`).
- [ ] Wire service bus events for finance/order domain (RabbitMQ exchanges, queue bindings).
- [ ] Document async workflows in memory bank (`migration/erp-async-patterns.md`).
- [ ] Prepare tech debt list for remaining ERP gaps.

**Dependencies:** Order & procurement services merged, RabbitMQ container accessible, shared utilities package ready for extension.

### Sprint 7 (Analytics Domain)
- [ ] Port analytics SQL schemas (ClickHouse, Postgres) using enhanced migration runner.
- [ ] Scaffold ingestion pipelines via code generators (domain + dataflow services).
- [ ] Configure `ClickHouse_DATABASE_URL` env and health-check wait scripts.
- [ ] Implement integration tests that hit ClickHouse using seeded datasets.
- [ ] Publish Grafana dashboards under `monitoring/grafana/` and document setup.

**Dependencies:** Sprint 6 service bus events emitting ERP data; Docker ClickHouse healthy; monitoring stack operational.

### Sprint 8 (Integration Domain)
- [ ] Run `legacy_inventory.py --include integration` to scope remaining connectors.
- [ ] Create migration table mapping legacy connectors to new modules.
- [ ] Generate webhooks/sync job scaffolding; implement secure secrets handling.
- [ ] Define partner onboarding checklist and rate limiting policies.
- [ ] Add integration smoke tests leveraging sandbox credentials.

**Dependencies:** Auth service updated with API key management; security review availability; ERP events published (for downstream syncs).

### Sprint 9 (Hardening & Release)
- [x] Install `ts-node` at repo root (`npm install --save-dev ts-node`) and update documentation eliminating `npx` fallback (completed 26 Sep 2025).
- [ ] Develop generator smoke test script to ensure outputs compile (CI job).
- [ ] Run performance benchmark suite; capture results in memory bank (`lessons-learned/performance-benchmarking.md`).
- [ ] Update all ADRs and handover documents (operations, support).
- [ ] Execute release readiness review and sign-offs.

**Dependencies:** All domain migrations complete; CI pipeline stable; Ops team available for handover.

---

## Risk Register & Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| ClickHouse startup delays block analytics migrations | Medium | Add compose health-check retry script Sprint 7; document manual start procedure. |
| Generator drift vs. actual directory structure | High | Introduce schema descriptors + CI smoke test (Sprint 9) to catch path mismatches early. |
| Service bus throughput under load | Medium | Schedule load testing in Sprint 6; adjust RabbitMQ configuration and document tuning knobs. |
| ts-node dependency missing in CI | Low | Mitigated 26 Sep 2025 by installing ts-node; add CI verification script to prevent regressions. |
| External connector credentials availability | Medium | Coordinate with Integration stakeholders during Sprint 8 planning; use sandbox tokens for development. |

---

## Communication & Reporting Cadence
- **Weekly checkpoint:** 30-minute stand-up review of sprint burndown, blockers, and toolkit updates.
- **Sprint demo:** End-of-sprint walkthrough showing migrated flows (data + API + tests).
- **Memory bank updates:** Mandatory before sprint closure (toolkit, lessons, open items).
- **Stakeholder report:** Summarise deliverables, risks, and next sprint focus every two weeks.

---

Maintain this roadmap by appending outcomes and adjusting dates as sprints conclude. Each sprint lead must ensure alignment with architecture principles and update the memory bank accordingly.
