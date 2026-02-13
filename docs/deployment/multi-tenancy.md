# Multi-Tenancy Aktivierung

## Technischer Status
- Tenant wird pro Request aus `X-Tenant-ID` oder Token-Claim (`tenant_id`/`tid`) ermittelt.
- Tenant-Context ist request-scoped verfügbar (ContextVar).
- Frontend sendet Tenant Header automatisch in jedem API-Request.
- Compat-/Dokumenten-Endpunkte filtern tenant-basiert.

## Relevante Dateien
- `main.py` (Tenant-Resolution Middleware)
- `app/core/tenant_context.py`
- `app/core/tenant.py`
- `app/auth/deps.py`
- `app/documents/repository.py`
- `app/documents/router_helpers.py`
- `app/api/v1/endpoints/compat.py`
- `packages/frontend-web/src/lib/api-client.ts`

## Betrieb
- Tenant Header setzen: `X-Tenant-ID: <tenant-id>`
- Fallback ohne Header: `DEFAULT_TENANT_ID`

## Beispiel
```bash
curl -H "Authorization: Bearer <token>" -H "X-Tenant-ID: tenant-a" https://api.example.com/api/v1/purchase-orders
```
