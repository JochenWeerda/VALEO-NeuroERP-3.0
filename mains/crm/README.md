# CRM Domain (VALEO NeuroERP 3.0)

The CRM domain exposes a production-ready customer management service layer wired against the legacy FastAPI backend. Key components:

- `src/infrastructure/repositories/rest-customer-repository.ts` – talks to the 2.0 CRM service via authenticated HTTP calls (`CRM_SERVICE_URL`, `CRM_SERVICE_TOKEN`).
- `src/bootstrap.ts` – registers the REST repository by default; the in-memory adapter is available only for unit/integration tests.
- `tests/` – Node test suites executed through `npm run test:crm` (compiles with `tsc` and runs `node --test`).

## Environment

| Variable | Description | Default |
| --- | --- | --- |
| `CRM_DATABASE_URL` | Postgres connection string for CRM domain. | _required_ |
| `CRM_SERVICE_URL` | Base URL of the legacy CRM API (`/api/crm`). | `http://localhost:8000/api/crm` |
| `CRM_SERVICE_TOKEN` | Bearer token used for authenticated requests. | _none (requests sent without auth)_ |

The repository mirrors the response models returned by the FastAPI service and maps them to the new branded domain types, making the migration path deterministic.
