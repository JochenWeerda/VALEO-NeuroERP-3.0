---
title: Datenmodell & Multi-Tenancy
type: explanation
audience: [entwickler, qa, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Datenmodell & Multi-Tenancy

VALEO NeuroERP ist **multi-mandantenfähig**: jeder HTTP-Request läuft in einem
Mandantenkontext; Datenbankzugriffe müssen diesen Kontext respektieren.

## Mandantenkontext

- Header: `X-Tenant-ID` (UUID)
- Middleware: `app/core/tenant_context.py` setzt den aktiven Mandanten pro Request.
- Dev-Fallback über `DEFAULT_TENANT_ID` in `.env`.

!!! warning "Invariante"
    Keine mandantenübergreifenden Queries ohne explizite, review-pflichtige Ausnahme
    (siehe ADR-034 Tenant-Isolation).

## PostgreSQL-Schemas

Domänen nutzen getrennte Schemas, z. B.:

| Schema | Inhalt (Beispiele) |
|--------|-------------------|
| `domain_shared` | mandantenübergreifende Referenz-/Knowledge-Objekte |
| `domain_inventory` | Lager, Ernteannahme, Wiegescheine |
| `domain_agrar` | Agrar-spezifische Erweiterungen |
| `domain_erp` | FiBu-Kern (Journal, offene Posten, …) |

ORM: SQLAlchemy 2.0, `Base` aus `app.core.database`. Migrationen: Alembic
(`alembic/versions/`).

## Architektur-Schichten

```
API (FastAPI Router)
  → Service (Domänenlogik)
    → Repository / SQLAlchemy Session
      → PostgreSQL (schema-qualified)
```

Entscheidungen: [ADR-003 Canonical Domain Model](../adr/adr-003-canonical-domain-model.md),
[ADR-014 Service-Layer](../adr/adr-014-service-layer-pattern.md).

## Module & Feature-Flags

Installierte Module pro Mandant: `INSTALLED_MODULES` / `TENANT_MODULE_FLAGS`
(`app/core/module_registry.py`). Nicht installierte Module liefern keine Routen/UI.

## Weiterführend

- [Schnittstellen — REST-API](../schnittstellen/rest-api.md)
- [Admin — Mandanten-Administration](../admin/mandanten-administration.md)
- [Process Kernel STATUS](../architecture/process-kernel/STATUS.md)
