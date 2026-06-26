# ADR: Auth- und Tenant-Kontext (API-Vertrag)

**Status:** akzeptiert
**Datum:** 2026-04-24
**Meilenstein:** M-01
**Bezug:** [TODO-SPRINT-001](../agent-ops/slices/TODO-SPRINT-001.yaml), `packages/erp-domain/src/types/express.d.ts`

## Kontext

Backend-Services und das `erp-domain`-Paket müssen denselben technischen Vertrag für **Tenant-Isolation** und **handlungsfähige Subjekte** (Benutzer, Service-Accounts) nutzen, damit Auditing, CRM-Dienste und Tests konsistent bleiben.

## Entscheidung

| Thema | Vertrag |
|--------|---------|
| **Tenant** | Primär HTTP-Header `x-tenant-id` (trim, nicht leer). Sekundär `req.user.tenantId`, sofern gesetzt. Fehlt beides in produktionsnahen Schreibpfaden → **400** `Missing tenant` oder **401** je nach Gateway. |
| **User / Subject** | `req.user.id` nach erfolgreicher Authentifizierung (JWT/Session — Außerhalb dieses ADR). Typen: `packages/erp-domain/src/types/express.d.ts`. |
| **Service-Accounts** | Nur mit explizitem Flag/Role (z. B. `req.user.roles` enthält `service`) und **immer** im Audit mit Kennzeichnung; kein stiller Fallback. |
| **Schreibende APIs** | `created_by` / `updated_by` / Audit `actorId` aus Request-Kontext, nicht aus fachlichen Body-Feldern (außer bewusst und dokumentiert). |
| **Fehlerbilder** | **401** nicht authentifiziert; **403** authentifiziert aber nicht berechtigt; **400** fehlender Tenant. |
| **Abweichung Entwicklung** | Wenn `NODE_ENV=development` **oder** `ERP_ALLOW_SYSTEM_ACTOR=1`, darf `resolveActorId` auf `'system'` fallen — **nicht** in standardisierten Produktions-Builds. |
| **Abweichung Tenant (nur Dev/Test)** | `NODE_ENV=development` \| `test` oder `ERP_ALLOW_MISSING_TENANT=1`: fehlender Header/JWT-Tenant → Fallback `ERP_DEV_TENANT_ID` oder `dev-tenant` (Implementierung: `resolveTenantId` in `request-context.ts`). |
| **Testbarkeit** | E2E (Playwright) und interne Tests setzen dieselben Header/Token wie das Produkt (siehe `tests/e2e` Hilfen). |

## Konsequenzen

- **erp-domain:** zentrale Hilfsfunktionen unter `packages/erp-domain/src/presentation/utils/request-context.ts` (`resolveTenantId`, `resolveActorId`, `respondControllerError`, `respondDomainMutationError`).
- **Finanz-Stammdaten & Purchase Orders** im erp-domain: Mandantenfilter persistiert (`finanz.*.tenant_id`, `purchase_orders.tenant_id`); Operationalisierung und Migrationsreihenfolge: [ERP: Finanz & Mandant](../erp-finanz-multitenancy.md).
- **FastAPI CRM:** analoge `Depends`-Funktionen (Header/JWT) pro Service; gleiche Semantik.
- Änderungen am Vertrag erfordern **Revision dieser ADR** und Anpassung der Tests.

## Status-Umsetzung

Implementierung in Code-Meilensteinen M-04 (erp-domain) und M-06 (CRM); E2E in M-05.
