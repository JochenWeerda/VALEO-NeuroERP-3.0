# Architektur-Ueberblick

## Tech-Stack

| Layer | Technologie | Version |
|-------|------------|---------|
| Backend | Python / FastAPI | 3.11+ / 0.100+ |
| ORM | SQLAlchemy | 2.0 (Declarative) |
| Validation | Pydantic | 2.x |
| Database | PostgreSQL | 15+ |
| Cache | Redis | 7 |
| Event Bus | NATS JetStream | 2.10 |
| Auth | Keycloak / OIDC | 22 |
| Frontend | React / TypeScript / Vite | 18 / 5.5 / 5.4 |
| Migrations | Alembic | head-basiert |

## Multi-Schema-Design (PostgreSQL)

```
valeo_neuro_erp (Database)
  |-- domain_shared      -- Tenants, Users, Branches, Audit, System-Properties
  |-- domain_crm         -- Kunden, Leads, Geschaeftspartner (360-Grad)
  |-- domain_inventory   -- Artikel, Lager, Wiegescheine, Silos, Kontrakte
  |-- domain_agrar       -- Saatgut, Duenger, PSM, Sachkunde
  |-- domain_erp         -- Kontenrahmen, Buchungsjournal
  |-- domain_finance     -- Selbstabrechnung, Reklamationen
  |-- domain_portal      -- Kundenportal (Bestellungen, Vertraege)
  |-- domain_ops         -- (reserviert)
  |-- domain_log         -- (reserviert)
```

## Multi-Tenancy

Jede Anfrage traegt einen `X-Tenant-ID` Header. Die Middleware (`app/core/tenant_context.py`) extrahiert und validiert den Tenant. Alle Queries filtern automatisch nach `tenant_id`.

```
Client --> [Bearer Token] --> Middleware-Stack --> Endpoint
                                |
                                +-- Prometheus Metrics
                                +-- Correlation-ID
                                +-- Bearer Token Auth
                                +-- Request Logging
                                +-- Tenant Context
                                +-- Exception Handler
```

## UUID v7 Standard

Alle Primaerschluessel verwenden **UUID v7** (zeitbasiert, sortierbar):

```python
from app.core.uuid7 import uuid7
id = Column(String, primary_key=True, default=uuid7)
```

## Modul-Registry

`app/core/module_registry.py` steuert Feature-Flags pro Tenant ueber `INSTALLED_MODULES` und `TENANT_MODULE_FLAGS`.

## Event-Driven Architecture

- **Outbox-Pattern:** Events werden in `outbox_events`-Tabelle geschrieben und asynchron via NATS JetStream publiziert
- **Publisher:** `app/infrastructure/eventbus/outbox.py` (OutboxPublisher)
- **Polling:** Hintergrund-Task pollt unpublizierte Events alle paar Sekunden

## Backend-Verzeichnisstruktur

```
app/
  main.py                     -- FastAPI App, Middleware, Lifespan
  core/                       -- Framework: Config, DB, Security, RBAC, SSE, Tenant
  api/v1/
    api.py                    -- Master-Router (70+ Sub-Router)
    endpoints/                -- Route-Handler nach Domain
    schemas/                  -- Pydantic-Schemas (base, shared, crm, inventory, finance, agrar, portal)
  infrastructure/
    models/__init__.py        -- Haupt-SQLAlchemy-Modelle
    models/l3c_models.py      -- L3C-spezifische Modelle (Harvest, NaWaRo, Silo, etc.)
    repositories/             -- Data Access Layer
    eventbus/                 -- NATS / Outbox
  domains/shared/             -- Domain-Events
  verkauf/                    -- Verkauf-Domain (Router + Schemas)
modules/
  agrar/                      -- Agrar-Vertikalmodul
    services/                 -- Domain-Services (Harvest, Drying, Pricing, Self-Billing)
    repositories/             -- Data Access
```
