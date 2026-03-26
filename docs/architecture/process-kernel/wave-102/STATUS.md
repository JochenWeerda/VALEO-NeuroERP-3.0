# Wave 102 — Gap 049: Security-Hardening Runtime-Wiring

## Scope
Gap 049 — Security-Hardening: OIDC-Guards, Secrets, Audit-Middleware, Demo-Endpoint-Absicherung.

## Zielbild
Alle Security-Schichten aus Wave 75 in der Runtime verdrahtet; keine hardcodierten Secrets; Mutations automatisch auditiert.

## Lieferumfang

### A) SecurityHeadersMiddleware in main.py eingebunden
- `app.add_middleware(SecurityHeadersMiddleware)` — alle Security-Header (CSP, HSTS, X-Frame-Options etc.) werden jetzt in der Runtime erzwungen
- Wave 75 hatte die Middleware implementiert aber nicht eingebunden

### B) Produktions-Startup-Guard (SC-AUTH-002)
- Wenn `APP_ENV == "production"` und `API_DEV_TOKEN is not None` → `RuntimeError` beim Start
- Dev-Modus: `API_DEV_TOKEN` auf `"dev-token"` gesetzt falls nicht konfiguriert (Rückwärtskompatibilität für Tests)

### C) Secret-Key-Startup-Guard (SC-SECRETS-001)
- `SECRET_KEY` und `ENCRYPTION_KEY`: kein hardcoded Default mehr (`None` statt `secrets.token_urlsafe(32)`)
- Produktion: `RuntimeError` wenn nicht per Env gesetzt
- Dev-Modus: ephemere Keys werden mit Warnung generiert

### D) Demo-Auth-Endpoints gesichert
- `POST /auth/demo-login` und `POST /auth/demo-multi-role` geben HTTP 403 zurück wenn `APP_ENV == "production"`
- Rate Limiting: `@limiter.limit("10/minute")` auf beiden Demo-Endpoints

### E) AuditMiddleware — automatische Mutation-Erfassung (SC-AUDIT-001)
- Neue Middleware `app/middleware/audit_middleware.py`
- Alle POST/PUT/PATCH/DELETE auf `/api/v1/*` werden als strukturiertes Audit-Event geloggt
- Felder: `action`, `entity_type`, `user_id`, `tenant_id`, `status_code`, `duration_ms`, `correlation_id`, `ip_address`
- Kein DB-Write in der Middleware (vermeidet Session-Konflikte); Audit-API `/api/v1/audit/log` für explizite Einträge

### F) knowledge_api.py — 204-Response-Fix
- `DELETE /{knowledge_id}`: `response_class=Response` + explizites `return Response(status_code=204)` (FastAPI-Constraint)

## Sicherheitslücken geschlossen

| OWASP | Lücke | Maßnahme |
|-------|-------|----------|
| A05 | Security Headers nicht aktiv | SecurityHeadersMiddleware eingebunden |
| A07 | API_DEV_TOKEN hardcoded in Produktion möglich | Startup-Guard + 403 auf Demo-Endpoints |
| A02 | SECRET_KEY regeneriert bei Restart | Kein Default, Prod-Guard, Dev-Warnung |
| A09 | Mutationen nicht automatisch geloggt | AuditMiddleware für alle /api/v1 Mutations |

## Tests
Wave 75 Security-Tests: 49 passed (unverändert)
GoBD Compliance-Tests: 60 passed, 3 wurden durch API_DEV_TOKEN=None gebrochen und sind repariert

## Abnahmekriterien
- SecurityHeadersMiddleware aktiv in main.py
- `APP_ENV=production` + `API_DEV_TOKEN` → RuntimeError beim Start
- `SECRET_KEY` / `ENCRYPTION_KEY` ohne Prod-Default
- AuditMiddleware loggt alle POST/PUT/PATCH/DELETE auf /api/v1/*

## Status
`abgeschlossen` — 2026-03-24
