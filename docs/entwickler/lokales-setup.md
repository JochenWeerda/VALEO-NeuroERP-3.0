---
title: Lokales Setup
type: how-to
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Lokales Setup

Kurzanleitung für Backend, Frontend und Datenbank auf dem Entwicklerrechner.

## Voraussetzungen

- Python 3.11+
- Node.js 20+ und npm
- PostgreSQL 15+ (lokal oder via Docker)
- Optional: Docker Compose für den Gesamtstack

## Schnellstart (leichtgewichtig)

1. `.env` aus `.env.example` anlegen und `DATABASE_URL` setzen.
2. Postgres starten (z. B. `docker compose -f docker-compose.dev.yml up -d`).
3. Migrationen: `alembic upgrade head`
4. Backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Frontend:

```bash
cd packages/frontend-web
npm install
npm run dev
```

Dev-Server: Port **3001**, Proxy `/api/v1` → Backend **8000**.

## Authentifizierung (Entwicklung)

- OIDC ist produktiv verbindlich; lokal kann `API_DEV_TOKEN` aus `.env` den Login umgehen.
- Mandant: Header `X-Tenant-ID` (Default in `.env.example`).
- **Niemals** Produktions-Tokens oder Secrets committen.

## Vollstack (Docker)

Für Integrationstests mit Keycloak, NATS, Redis:

```bash
docker compose up -d
```

Details: [Deployment](../admin/deployment.md), [Datenbank-Migrationen](../admin/datenbank-migrationen.md).

## Nützliche Befehle

| Bereich | Befehl |
|---------|--------|
| Backend-Tests | `pytest` / `pytest -m unit` |
| Frontend-Build | `cd packages/frontend-web && npm run build` |
| MkDocs lokal | `pip install -r requirements-docs.txt && python -m mkdocs serve` |
| OpenAPI | `python scripts/generate_openapi.py` |

Repo-Konventionen: `CLAUDE.md`, `AGENTS.md` (Root).
