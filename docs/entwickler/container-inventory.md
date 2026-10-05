---
title: Container-Inventar
type: reference
audience: [entwickler, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-16
version: 3.1.0
description: Docker-Compose-Services (Dev + Production) — Basis fuer C4 Container Drift-Check.
---

# Container-Inventar

> Automatisch generiert via `python scripts/generate_container_inventory.py`. **Nicht manuell bearbeiten.**

Architektur-Sicht: [C4 Container](../architecture/views/c4-02-containers.md).

**Stand:** 2026-07-16 — **38** Services (alle Compose-Dateien)

## Development (`docker-compose.yml`)

**27** Services

### Presentation

| Service | In C4 dokumentiert |
|---|---|
| `frontend-web` | ja |

### Edge / BFF

| Service | In C4 dokumentiert |
|---|---|
| `bff-web` | ja |
| `dev-sse` | ja |

### Core API

| Service | In C4 dokumentiert |
|---|---|
| `backend` | ja |

### Domain — CRM

| Service | In C4 dokumentiert |
|---|---|
| `crm-ai` | ja |
| `crm-analytics` | ja |
| `crm-communication` | ja |
| `crm-core` | ja |
| `crm-multichannel` | ja |
| `crm-sales` | ja |
| `crm-security` | ja |
| `crm-service` | ja |
| `crm-workflow` | ja |

### Domain — Sonstige

| Service | In C4 dokumentiert |
|---|---|
| `ai` | ja |
| `inventory-service` | ja |
| `ki-usability` | ja |
| `rations-optimization` | ja |

### Integration / DMS

| Service | In C4 dokumentiert |
|---|---|
| `dms-adapter` | ja |
| `paperless` | ja |
| `paperless-db` | ja |
| `paperless-redis` | ja |

### Data / Event

| Service | In C4 dokumentiert |
|---|---|
| `nats` | ja |
| `postgres` | ja |
| `redis` | ja |

### Identity

| Service | In C4 dokumentiert |
|---|---|
| `keycloak` | ja |

### Dev Tools

| Service | In C4 dokumentiert |
|---|---|
| `pgadmin` | ja |
| `redis-commander` | ja |

## Production (`docker-compose.production.yml`)

**11** Services

### Presentation

| Service | In C4 dokumentiert |
|---|---|
| `frontend` | ja |

### Core API

| Service | In C4 dokumentiert |
|---|---|
| `valeo-app` | ja |

### Domain — Lager

| Service | In C4 dokumentiert |
|---|---|
| `inventory-service` | ja |

### Data / Event

| Service | In C4 dokumentiert |
|---|---|
| `nats` | ja |
| `postgres` | ja |
| `redis` | ja |

### Identity

| Service | In C4 dokumentiert |
|---|---|
| `keycloak` | ja |
| `postgres-keycloak` | ja |

### Observability

| Service | In C4 dokumentiert |
|---|---|
| `grafana` | ja |
| `loki` | ja |
| `prometheus` | ja |

## Regenerieren

```bash
python scripts/generate_container_inventory.py
python scripts/generate_container_inventory.py --check
```

CI: `.github/workflows/docs.yml` und `scripts/check_all_doc_generators.sh --check`.
