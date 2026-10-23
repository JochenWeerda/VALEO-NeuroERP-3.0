# VALEO NeuroERP 3.0 threat model

## What the project does and where untrusted input enters

VALEO NeuroERP 3.0 is a multi-tenant ERP for agricultural trading and
cooperatives. It processes financial records, contracts, inventory movements,
weighing data, customer and supplier records, regulatory documents and agentic
commands.

Treat all external input as untrusted, especially:

- HTTP path, query, header, cookie and JSON/form payloads under `app/api/` and
  the service-specific APIs under `services/`;
- OIDC/JWT claims and tenant context derived in `app/core/` and
  `app/middleware/`;
- MCP and mask actions, proposals, voice/omnibox commands and deep links;
- CSV, XML, JSON, spreadsheet, PDF and document imports, including CAMT,
  MT940, XRechnung/ZUGFeRD, XBRL/eBilanz, EUDR and DMS content;
- email, webhook, portal, mobile, NATS/event-bus and integration-adapter data;
- browser-rendered business data and user-controlled URLs in the React client.

## Components that matter most

Highest priority:

- authentication, authorization, role checks and tenant isolation in
  `app/core/`, `app/middleware/`, `app/api/` and shared auth packages;
- finance, payment, bank import/reconciliation, journal, POS/fiscalization,
  audit, outbox and document-retention code;
- inventory and warehouse movements, weighing, contracts and regulatory
  imports where a write can change stock, money or compliance evidence;
- MCP/action execution and proposal approval paths, especially any route that
  can turn model output into a business mutation;
- parsers, upload handlers, archive/document extraction, outbound HTTP,
  webhook and email integrations;
- frontend HTML/URL rendering, OIDC token handling, open redirects and stored
  cross-site scripting reachable through persisted business data.

Lower priority, but still in scope, includes analytics, dashboards and
read-only projections. Generated documentation, screenshots, archived code in
`docs/_internal/archive/`, test fixtures and purely local demo data are not
production attack surfaces. Third-party dependency vulnerabilities are useful
only when VALEO usage makes them reachable or changes their impact.

## Security invariants

- The authenticated token decides the tenant. A request payload, query or
  freely chosen header must never override that identity.
- Reads, writes, joins, caches, audit records, outbox events, files and agent
  proposals must remain tenant-scoped. Cross-tenant existence should not leak.
- Non-idempotent finance, inventory and agent actions must be atomic and must
  not report success after a rollback or partial failure.
- Payment and posting approvals require the documented roles and separation of
  duties. Agent execution must not bypass human approval gates.
- Journal, fiscal and inventory evidence must remain complete and tamper
  evident; failure of stamping, audit or outbox work must fail closed.
- Parsers and imports must reject ambiguous, oversized, recursive or malformed
  input before writes. XML external entities and unsafe object construction are
  prohibited.
- Outbound requests must not enable SSRF to loopback, private networks, cloud
  metadata endpoints or attacker-controlled redirect targets.
- Errors and logs must not expose tokens, credentials, personal data, SQL or
  cross-tenant identifiers.

## How to exercise the checkout

The scanner image contains Python dependencies in `/opt/venv`, all pnpm
workspace dependencies, compiled Python bytecode and built TypeScript
workspaces. Useful offline commands from `/src` include:

```bash
python -m pytest -q --no-cov tests/test_auth_middleware.py \
  tests/test_tenant_enforcement.py tests/test_mcp_oidc_verification.py
python -m pytest -q --no-cov tests/test_mcp_tenant_isolation_all.py
python -m pytest -q --no-cov tests/test_journal_amount_integrity.py \
  tests/test_journal_stamp_integrity.py tests/test_bank_statement_import_integrity.py
pnpm --filter @valero-neuroerp/frontend-web exec vitest run \
  src/__tests__/lib/omnibox/command-safety.test.ts
```

Tests marked as requiring PostgreSQL need the repository's CI-provided
database and are not expected to create a database or Docker container inside
the scanner environment. Static review and non-database tests remain valid
offline.

## Severity guidance

- **Critical:** unauthenticated remote-code execution; authentication bypass;
  arbitrary cross-tenant reads or writes; extraction of deployment secrets;
  or an agent/API path that can execute arbitrary business mutations without
  the required approval.
- **High:** SQL injection; stored XSS in a privileged workflow; tenant escape
  requiring an authenticated low-privilege user; SSRF reaching credentials or
  internal control planes; path traversal; unsafe deserialization; bypass of
  payment separation-of-duties; or manipulation/removal of GoBD/fiscal audit
  evidence.
- **Medium:** reflected XSS, meaningful information disclosure, tenant
  enumeration, CSRF on a state-changing path, or resource exhaustion requiring
  sustained traffic.
- **Low:** defense-in-depth gaps with no demonstrated confidentiality,
  integrity or availability impact.

Increase severity when a finding affects money, stock, tax/fiscal evidence,
personal data, administrator sessions or multiple tenants. Reports should
include a minimal reproducer, affected tenant/role assumptions, transaction
effects and a focused patch with regression tests where possible.

## Anything to leave alone

- Do not report placeholder credentials or email addresses that occur only in
  documentation, examples or tests unless they are accepted by runtime code.
- Do not treat explicit fail-closed `409`, `422`, `501` or readiness responses
  as vulnerabilities unless they can be bypassed or leak sensitive data.
- Do not propose weakening tenant, audit, idempotency, approval, migration or
  evidence checks merely to make a test pass.
- Do not edit generated OpenAPI, inventory or handbook output without also
  changing its source generator.
- Do not use real personal, customer or production data in a reproducer.
