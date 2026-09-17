---
title: Datenmodell & Multi-Tenancy
type: explanation
audience: [entwickler, qa, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-17
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

## Modell-Schichten und Lebenszyklus

Drei Schichten, die nicht in eins fallen (Plan:
[todo-datenmodell-katalog.md](../agent-ops/todo-datenmodell-katalog.md)):

| Schicht | Wahrheit | Aendert sich wenn |
|---|---|---|
| Canonical Model | ADR-003, [ERD](../architecture/views/erd-canonical-domain.md), [UML](../architecture/views/uml-canonical-domain-class.md) | neues Fachaggregat |
| Physisches Schema | Alembic + `information_schema` | Migration |
| Vertrag / Sicht | OpenAPI, ScreenDefinition, Studio-Katalog | Maske oder Endpunkt |

**Maske loeschen oder aendern droppt keine Spalte.** Eine ScreenDefinition ist
eine Sicht. Spalten leben, bis eine eigene Migration sie streicht — mit
Verbraucher-Suche und GoBD-/Belegketten-Pruefung. Umgekehrt erzeugt eine neue
Maske keine Tabelle; fehlende Persistenz ist eine Migration, kein
`CREATE TABLE` in der UI.

**Neue Spalte nur per Alembic.** Kopffelder der Maske folgen den JSON-Schluesseln
des Endpunkts (ADR-003 Regel 3: keine parallele fachliche Wahrheit in der UI).

**Besitz** ist das PostgreSQL-Schema (`domain_crm`, `domain_agrar`, …).
`scripts/table_ownership.py` mappt 29 Schemas auf Architecture-Domains;
`scripts/check_domain_table_ownership.py` bewertet jede `domain_*`-Tabelle
(only-up: unbekanntes Schema oder Praefix-Konflikt ohne Legacy-Zeile faellt).
Der physische Katalog nennt `owner_domain` und `placement`
([table-catalog.md](../admin/table-catalog.md),
`python scripts/generate_table_catalog.py`). Fachliche Domäne steht im
Architecture Index (`database_schemas`). Zwei Modelle duerfen nicht denselben
Tabellennamen in einem Schema teilen.

**Verbraucher** stehen im Katalog (`read_by`, `written_by`, `screens`), geerntet
aus SQL/ORM unter `app/` (`scripts/table_lineage.py`). Native ScreenDefinitions
duerfen `dataSources.entity.table` setzen — der Wert muss im Katalog vorkommen.
Vor dem Loeschen einer Maske die Verbraucher-Suche, nicht `DROP COLUMN`.

## Module & Feature-Flags

Installierte Module pro Mandant: `INSTALLED_MODULES` / `TENANT_MODULE_FLAGS`
(`app/core/module_registry.py`). Nicht installierte Module liefern keine Routen/UI.

## Weiterführend

- [Schnittstellen — REST-API](../schnittstellen/rest-api.md)
- [Admin — Mandanten-Administration](../admin/mandanten-administration.md)
- [Process Kernel STATUS](../architecture/process-kernel/STATUS.md)
