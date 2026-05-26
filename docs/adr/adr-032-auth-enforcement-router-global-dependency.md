# ADR-032 — Auth-Enforcement über Router-Level Global Dependency

**Status:** Angenommen
**Datum:** 2026-05-26
**Kontext:** Wave A2 Security Hardening

---

## Kontext

304 von 311 Endpoint-Dateien hatten keine explizite Auth-Dependency. Die FastAPI-Dependency
`require_bearer_token` wurde nur in einzelnen Routen deklariert, was dazu führte, dass
neue Endpoints standardmäßig ungeschützt blieben.

## Entscheidung

Authentifizierung wird **einmalig auf `api_router`** in `app/api/v1/api.py` erzwungen:

```python
api_router = APIRouter(dependencies=[Depends(require_bearer_token)])
```

Alle Sub-Router werden über `api_router.include_router(...)` eingebunden und erben
die Auth-Dependency automatisch.

**WebSocket-Ausnahme:** WebSocket-Routen können `Depends(HTTPBearer)` nicht auflösen
(kein HTTP-Request-Objekt). Für sie existiert `ws_router = APIRouter()` ohne globale
Auth-Dependency. WebSocket-Handler implementieren Auth intern via Query-Parameter-Token
und schließen unauthentifizierte Verbindungen mit `WS_1008_POLICY_VIOLATION`.

**Exempt-Pfade** (Health, OpenAPI, Docs) werden in `_is_path_exempt()` in
`app/core/security.py` gepflegt.

## Begründung

- **Sicherheits-Default:** Neue Endpoints sind automatisch geschützt — kein manuelles
  Hinzufügen der Dependency erforderlich.
- **Fail-Secure:** Vergessene Auth-Dependencies sind kein Problem mehr.
- **Zentralisierung:** Auth-Logik an einer Stelle, nicht verstreut über 311 Dateien.

## Alternativen verworfen

- **Middleware-Ansatz:** `@app.middleware("http")` kann keine FastAPI-Dependencies nutzen
  und hat keinen Zugriff auf Dependency-Override-System der Tests.
- **Per-Router-Annotation:** Zu fehleranfällig; neue Router würden vergessen werden.

## Konsequenzen

- Tests: `app.dependency_overrides[require_bearer_token] = lambda: "dev-token"` in
  `conftest.py` reicht für alle HTTP-Tests.
- WebSocket-Tests: Direkte Token-Übergabe als Query-Parameter.
- Exempt-Pfade müssen bei Bedarf in `_is_path_exempt()` gepflegt werden.
