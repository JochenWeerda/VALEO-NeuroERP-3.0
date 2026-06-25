---
title: Deployment
type: how-to
audience: [betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Deployment

VALEO NeuroERP wird containerisiert über Docker Compose betrieben.

## Stacks

| Stack | Zweck |
|---|---|
| `docker compose up -d` | Vollständiger Stack (Postgres, Redis, NATS, Keycloak, Services). |
| `docker compose -f docker-compose.dev.yml up` | Leichter Dev-Stack (Postgres + Backend). |

## Wichtige Umgebungsvariablen

Konfiguration über Umgebungsvariablen (siehe `.env.example`):

| Variable | Bedeutung |
|---|---|
| `DATABASE_URL` | PostgreSQL-Verbindung. |
| `REDIS_URL` | Redis-Verbindung (Cache/Rate-Limit). |
| `API_DEV_TOKEN` | OIDC-Bypass **nur** für Entwicklung. |
| `OIDC_CLIENT_ID`, `OIDC_ISSUER_URL`, `OIDC_JWKS_URL` | OIDC-Provider. |
| `DEFAULT_TENANT_ID` | Fallback-Mandant. |

!!! danger "Secrets"
    Niemals echte Secrets ins Repository committen. `API_DEV_TOKEN` ausschließlich
    in Entwicklungsumgebungen verwenden, niemals in Produktion.

## Ablauf (Erstinstallation)

1. `.env` aus `.env.example` ableiten und befüllen.
2. `docker compose up -d` starten.
3. Datenbankmigrationen anwenden → siehe
   [Datenbank-Migrationen](datenbank-migrationen.md).
4. Health-Checks prüfen (`/healthz`).
5. OIDC-Login testen.

## Frontend

Das Web-Frontend (`packages/frontend-web`) wird separat gebaut
(`npm run build`) und über den Reverse-Proxy ausgeliefert; `/api/v1` proxyt zum
Backend.
