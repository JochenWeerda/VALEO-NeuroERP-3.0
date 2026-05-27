# ADR-015: Auth-Enforcement-Strategie (Router-Level Dependency)

**Status:** Accepted
**Datum:** 2026-05-27
**Kontext:** Wave A2 / Wave E — Security & Developer Experience

---

## Kontext

FastAPI unterstützt zwei Ansätze für auth-Enforcement:
1. **Global Middleware** — prüft alle Requests, aber kann keine Dependency-Injection nutzen
2. **Router-Level Dependency** — explizit pro Router, ermöglicht Fine-Grained-Control

Die Codebasis hatte 304 von 311 Endpoint-Dateien ohne explizite Auth-Dependency, weil die Dependency per-Route vergessen wurde.

## Entscheidung

Auth-Enforcement erfolgt **einmalig auf Router-Ebene in `api.py`** beim `include_router`-Aufruf:

```python
# app/api/v1/api.py
api_router.include_router(
    agrar_contracts.router,
    prefix="/agrar/contracts",
    tags=["Agrar — Kontrakte"],
    dependencies=[Depends(require_bearer_token)],  # ← einmalig hier
)
```

### Regeln

1. **Alle Business-Router** in `api.py` erhalten `dependencies=[Depends(require_bearer_token)]`
2. **Public-Endpoints** (Health, OpenAPI, Auth-Callback) werden explizit **außerhalb** des api_router eingebunden oder mit `include_in_schema=False` und eigenem Router ohne Auth-Dependency
3. **Admin-Endpoints** erhalten zusätzlich `Depends(require_admin_role)`
4. **Interne Service-zu-Service-Calls** nutzen Service-Tokens (nicht User-Tokens)

### Monitoring

- `scripts/check_tenant_isolation.py` — CI-Gate prüft Tenant-Filter-Konsistenz
- `scripts/check_sql_fstrings.py` — CI-Gate prüft SQL-Injection-Risiken

## Konsequenzen

**Positiv:**
- Keine Möglichkeit, Auth-Dependency versehentlich zu vergessen
- Einheitlicher Security-Perimeter
- Klare Ausnahmeliste für Public-Endpoints

**Negativ:**
- Einige Endpoints (z.B. Webhooks mit eigener Signatur-Validierung) benötigen Override
- Test-Code muss `API_DEV_TOKEN` setzen

## Referenz

- `app/api/v1/api.py` — Master-Router mit dependencies
- `app/core/security.py` — `require_bearer_token` Dependency
- `.github/workflows/quality-gate.yml` — CI-Gate für Tenant-Isolation
