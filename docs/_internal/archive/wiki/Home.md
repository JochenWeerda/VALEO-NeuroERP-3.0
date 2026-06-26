# VALEO NeuroERP 3.0 - Developer Wiki

> Multi-Tenant ERP-System fuer Agrargenossenschaften und Handelsunternehmen

## Inhaltsverzeichnis

1. **[Architektur-Ueberblick](Architecture-Overview.md)** - Tech-Stack, Schemas, Multi-Tenancy
2. **[Datenmodell-Referenz](Data-Model-Reference.md)** - Alle SQLAlchemy-Modelle, 7 Domain-Schemas, 100+ Tabellen
3. **[REST-API-Referenz](REST-API-Reference.md)** - Alle Endpunkte, Request/Response-Formate, Auth-Header
4. **[Entwickler-Leitfaden](Developer-Guidelines.md)** - Lessons Learned, Best Practices fuer DB-Erweiterungen, Masken, Seed-Skripte
5. **[Seed-Skript-Leitfaden](Seed-Script-Guide.md)** - Korrekte Testdaten-Erstellung, Validierungsregeln

## Quick Links

- **Backend-Start:** `docker compose up -d`
- **Health-Check:** `curl http://localhost:8000/health`
- **API-Basis-URL:** `http://localhost:8000/api/v1/`
- **Auth-Header:** `Authorization: Bearer dev-token` + `X-Tenant-ID: <uuid>`
- **Default-Tenant:** `00000000-0000-0000-0000-000000000001`

## Aktueller Stand (Februar 2026)

- 129 Tabellen ueber 9 Domain-Schemas erstellt
- 100+ SQLAlchemy-Modelle
- 110+ API-Endpoint-Dateien mit 70+ Router-Prefixes
- UUID v7 als Standard-Primaerschluessel
- Docker Full-Stack: PostgreSQL 15, Redis 7, NATS 2.10, Keycloak 22
