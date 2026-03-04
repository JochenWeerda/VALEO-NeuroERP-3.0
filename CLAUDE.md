# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VALEO NeuroERP 3.0 is a multi-tenant enterprise ERP system for agricultural cooperatives and trading companies. The system is German-language-focused (UI labels, docs, domain terms are in German). It covers 12+ business domains: Agrar (harvest acceptance, contracts, drying rules), Sales, Procurement, Inventory, Finance, CRM, Logistics, Compliance, and more.

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI, SQLAlchemy 2.0 (PostgreSQL 15+), Alembic migrations, Pydantic 2.x
- **Frontend:** React 18 / TypeScript 5.5 / Vite 5.4, Tailwind CSS, Radix UI, Zustand, TanStack React Query
- **Auth:** OIDC (Keycloak/Azure AD/Auth0) with bearer token enforcement and tenant isolation
- **Infrastructure:** Docker Compose, Redis 7, NATS JetStream (event bus), Paperless-ngx (DMS)

## Common Commands

### Backend
```bash
# Start backend with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
pytest

# Run tests by marker
pytest -m unit
pytest -m integration

# Run a single test file
pytest tests/test_drying_rule_engine.py

# Run with coverage
pytest --cov=app --cov-report=term

# Database migrations
alembic upgrade head          # Apply all migrations (bei Neuinstallation/Clone ausführen → alle Tabellen)
alembic revision --autogenerate -m "description"  # Create migration
```

### Frontend
```bash
cd packages/frontend-web

npm install          # Install dependencies
npm run dev          # Dev server (port 3001, proxies /api/v1 → backend:8000)
npm run build        # Production build
npm run lint         # ESLint
npm run test         # Vitest unit tests
npm run storybook    # Storybook (port 6006)
npx playwright test  # E2E tests
```

### Docker
```bash
docker compose up -d                          # Full stack (postgres, redis, nats, keycloak, all services)
docker compose -f docker-compose.dev.yml up   # Lightweight dev stack (postgres + backend only)
```

## Architecture

### Backend Structure

```
app/
├── main.py                  # FastAPI app, middleware stack, lifespan
├── core/                    # Framework: config, database, security, RBAC, SSE, tenant context
├── api/v1/
│   ├── api.py               # Master router — includes 70+ sub-routers
│   └── endpoints/           # Route handlers grouped by domain
├── infrastructure/models/   # SQLAlchemy models (multi-schema: domain_shared, domain_*)
└── einkauf/                 # Procurement domain (router + schemas)

modules/
└── agrar/                   # Agrar vertical module
    ├── services/            # Domain services (harvest calc, drying rules, pricing, self-billing)
    ├── repositories/        # Data access layer
    └── config/              # Module configuration
```

**Key patterns:**
- Multi-tenancy via `X-Tenant-ID` header, enforced in middleware (`app/core/tenant_context.py`)
- Module registry (`app/core/module_registry.py`) controls per-tenant feature flags via `INSTALLED_MODULES` / `TENANT_MODULE_FLAGS`
- Dependency injection container in `app/core/container_config.py`
- Event-driven outbox pattern with NATS JetStream for reliable async events
- PostgreSQL schemas: `domain_shared` for cross-tenant data, domain-specific schemas per module
- Middleware stack order: Prometheus → Correlation ID → Bearer token → Request logging → Exception handling

### Frontend Structure

```
packages/frontend-web/src/
├── app/navigation/          # manifest.tsx (nav tree), route-aliases.json
├── components/
│   ├── mask-builder/        # Reusable ERP mask framework (ObjectPage, ListReport, Wizard, Worklist, OverviewPage)
│   ├── patterns/            # Shared UI patterns (ListReport, Wizard)
│   └── ui/                  # Radix-based primitives (data-table, etc.)
├── features/                # Feature modules (forms/FormBuilder, prospecting)
├── lib/api/                 # API client functions (admin.ts, meldewesen.ts)
├── pages/                   # File-based route pages grouped by domain
│   ├── agrar/               # Harvest, contracts, varieties, soil samples
│   ├── verkauf/             # Sales (delivery notes, orders)
│   ├── einkauf/             # Procurement
│   ├── lager/               # Inventory
│   └── ...                  # 30+ domain folders
└── components/navigation/   # AppShell with sidebar navigation
```

**Key patterns:**
- **Mask Builder Framework** (`components/mask-builder/`): Config-driven ERP screens. Use `ObjectPage` for detail views with tabs, `ListReport` for filterable lists, `Wizard` for multi-step forms. Screens are defined declaratively via config objects, not custom JSX.
- Path alias: `@/*` → `src/*`
- Vite proxy: `/api/v1` → backend (port 8000), `/api/mcp` → BFF (port 4001), `/api/events` → SSE (port 5174)
- State: Zustand for client state, TanStack React Query for server state
- Auth: `oidc-client-ts` with OIDC flow; dev mode uses `API_DEV_TOKEN`
- i18n: `i18next` / `react-i18next`

### Document Consistency Principle (Gewohnheits-Prinzip)

Documents in a document chain (e.g., Sales Order → Delivery Note → Invoice) must share the same layout structure: header area (doc number, branch, date), customer/supplier area with tabs, positions grid, position details, totals, and bottom toolbar. See `docs/MASKEN.md` for the full standard.

## Environment Variables

Key variables (see `.env.example`):
- `DATABASE_URL` — PostgreSQL connection (default: `postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp`)
- `REDIS_URL` — Redis connection
- `API_DEV_TOKEN` — Bypass OIDC in development
- `OIDC_CLIENT_ID`, `OIDC_ISSUER_URL`, `OIDC_JWKS_URL` — OIDC provider config

## Database

- PostgreSQL 15+ with multi-schema design
- ORM: SQLAlchemy 2.0 with `declarative_base()` from `app.core.database`
- Migrations: Alembic (`alembic/versions/`)
- Default dev DB: `valeo_neuro_erp` on localhost:5432
- All models import `Base` from `app.core.database`

## Testing

- **pytest** with markers: `unit`, `integration`, `e2e`, `slow`
- Config in `pytest.ini`, tests in `tests/` directory
- Frontend unit tests: Vitest
- Frontend E2E: Playwright
- Coverage reports: terminal + HTML + XML
