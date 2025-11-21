# FiBu-Gateway

Anti-Corruption-Layer zwischen Frontend/anderen Domains und den FiBu-Microservices.

## Ziele

- Einheitliche REST-/GraphQL-API für das Frontend
- Weiterleitung von Requests an spezialisierte FiBu-Services (`fibu-core`, `fibu-master-data`, `fibu-op`, …)
- Mandanten- / Rollen-Kontext einspeisen (Header `X-Tenant-ID`)
- Optionale Event-Publishing- und Workflow-Hooks

## Features (Stand Scaffold)

- FastAPI-Anwendung mit Health/Ready-Endpoints
- Konfigurierbare Ziel-Services via Environment (`FIBU_CORE_URL`, `FIBU_MASTER_DATA_URL`, …)
- HTTP-Client-Wrappers (`FibuCoreClient`, `FibuMasterDataClient`, `FibuOpClient`)
- Erste REST-Routen
  - `GET /api/v1/chart-of-accounts`
  - `GET /api/v1/journal-entries`
  - `POST /api/v1/journal-entries`
  - `GET /api/v1/open-items`
- Tenant-Middleware + Dependency Injection
- Tests (pytest + httpx AsyncClient)

## Getting Started

```bash
cd services/finance/fibu-gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8600
```

Environment Variables (Auszug):

| Variable | Default | Beschreibung |
| --- | --- | --- |
| `FIBUGW_HOST` | `0.0.0.0` | Bind-Adresse |
| `FIBUGW_PORT` | `8600` | Port |
| `FIBUGW_FIBU_CORE_URL` | `http://finance-service:8003` | Ziel-Service für Journale |
| `FIBUGW_FIBU_MASTER_DATA_URL` | `http://finance-service:8003` | Kontenstammdaten |
| `FIBUGW_FIBU_OP_URL` | `http://finance-service:8003` | OP-Verwaltung |
| `FIBUGW_DEFAULT_TENANT` | `default` | Fallback-Tenant |

## Open Tasks

- AuthN/RBAC Integration
- Event-Bus & Workflow-Hooks
- GraphQL-Schema / Federation
- Error-Mapping & Circuit-Breaker pro Downstream-Service


