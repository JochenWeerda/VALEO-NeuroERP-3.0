---
title: Sequenz — Auth und Tenant-Kontext
type: explanation
audience: [entwickler, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Sequenzdiagramm — OIDC Auth & Tenant-Kontext

Authentifizierung und Mandantenisolation vom Browser bis zur Datenbank.

```mermaid
sequenceDiagram
  actor User as Nutzer
  participant FE as frontend-web
  participant KC as Keycloak
  participant BE as backend FastAPI
  participant MW as tenant_context middleware
  participant RBAC as RBAC / ADR-032
  participant PG as PostgreSQL

  User->>FE: Login
  FE->>KC: OIDC Authorization Code Flow
  KC-->>FE: Access Token + ID Token
  FE->>FE: Store token (oidc-client-ts)

  User->>FE: API-Aktion (z.B. Auftrag speichern)
  FE->>BE: Request Authorization Bearer + X-Tenant-ID
  BE->>MW: Extract tenant from header
  alt Dev ohne OIDC
    BE->>BE: API_DEV_TOKEN Fallback
  else Produktion
    BE->>KC: JWT validate (JWKS)
    KC-->>BE: Claims ok
  end
  BE->>RBAC: Router global dependency
  RBAC->>RBAC: Permission check
  BE->>MW: Set tenant context
  BE->>PG: Query schema-qualified (tenant filter)
  PG-->>BE: Rows
  BE-->>FE: 200 JSON
```

## Invarianten

- `X-Tenant-ID` Pflicht für mandantenfähige Routen
- Keine mandantenübergreifenden Queries ohne Review ([ADR-034](../../../adr/adr-034-tenant-isolation-klassifizierungssystem.md))
- Auth Enforcement global ([ADR-032](../../../adr/adr-032-auth-enforcement-router-global-dependency.md))

Quellen: [Datenmodell & Tenancy](../../../entwickler/datenmodell-tenancy.md), [Deployment](../../../admin/deployment.md)

→ [C4 Container](../c4-02-containers.md)
