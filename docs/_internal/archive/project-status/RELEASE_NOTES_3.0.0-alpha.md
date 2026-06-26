# Release notes – VALEO NeuroERP 3.0.0-alpha

First public alpha. The stack is in place and most domains are wired up; we’re still adding tests and closing gaps before calling it production-ready.

## What’s in this release

- **Stack:** React 18, TypeScript, Vite; FastAPI, PostgreSQL, NATS JetStream; OIDC (Keycloak, Azure AD, Auth0).
- **Domains:** Finance (open items, bookkeeping, bank reconciliation), Agrar (harvest acceptance, contracts), Sales, Inventory, HR, Production, Analytics, Regulatory, Logistics, Quality, Procurement, Weighing.
- **AI & automation:** Event-driven architecture, extensibility for agents and LLM tooling; voice-to-intent and command palette (see docs).
- **Deployment:** Docker Compose, staging deploy via GitHub Actions, health checks and smoke tests.
- **License:** MIT.

## How to run it

See the [README](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0) for quick start (clone, `docker-compose up`, `alembic upgrade head`, frontend in `packages/frontend-web`).

## What’s next

More tests, documentation, and stability work. Contributions and feedback welcome – open an issue or a discussion.
