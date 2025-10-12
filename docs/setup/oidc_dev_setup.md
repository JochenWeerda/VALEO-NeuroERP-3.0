# OIDC Development Setup

Dieser Leitfaden beschreibt, wie VALEO-NeuroERP lokal oder in Testumgebungen mit einem OpenID-Connect-Provider betrieben wird. Für produktive Szenarien gelten strengere Sicherheitsrichtlinien (siehe Security-Handbuch).

## 1. Token-Konfiguration für lokale Entwicklung

| Variable | Beschreibung | Default |
|----------|--------------|---------|
| `API_DEV_TOKEN` | Backend-Bearer-Token, das Requests ohne externen IdP erlaubt. | `dev-token` |
| `VITE_API_DEV_TOKEN` | Entsprechendes Token für das Frontend (z. B. POS/Storybook). | `dev-token` |
| `OIDC_CLIENT_ID` | Optional eigenes Client-ID-Mapping, falls vom Backend abweichend. | `KEYCLOAK_CLIENT_ID` |
| `OIDC_ISSUER_URL` | Überschreibt den automatisch abgeleiteten Issuer (z. B. bei Auth0). | – |
| `OIDC_JWKS_URL` | Fixe JWKS-URL; sonst wird sie aus Keycloak-URL/Realm berechnet. | – |

- Setze beide Werte in `.env` bzw. `packages/frontend-web/.env` oder nutze die Einträge aus `.env.example` / `packages/frontend-web/env.example`.
- In CI werden die Tokens ebenfalls gesetzt; für private Forks empfiehlt sich ein projektspezifisches Secret.

> Sobald ein echter OIDC-Provider angebunden ist, sollte der Dev-Token deaktiviert werden (entfernen der Variablen).

## 2. Einen Test-IdP bereitstellen

### 2.1 Keycloak (lokal per Docker)
```bash
docker run -d --name keycloak -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:23.0.7 start-dev
```
1. Realm `valeo-neuro-erp` anlegen.
2. Client `valeo-neuro-erp-frontend` (Public) mit Redirect-URI `http://localhost:3000/callback`.
3. Client `valeo-neuro-erp-backend` (Confidential) mit `client_secret`.

In `.env`:
```
VITE_OIDC_DISCOVERY_URL=http://localhost:8080/realms/valeo-neuro-erp/.well-known/openid-configuration
VITE_OIDC_CLIENT_ID=valeo-neuro-erp-frontend
OIDC_CLIENT_SECRET=<secret>  # optional für Server-Side-Flows
```

### 2.2 Azure AD / Auth0 / Okta
- Registriere eine App, aktiviere `Authorization Code` + PKCE.
- Setze Redirect-URL auf `http://localhost:3000/callback` (Frontend) bzw. `http://localhost:8000/auth/callback` (Backend, falls genutzt).
- Notiere `client_id`, `client_secret` (falls erforderlich) und die Discovery-URL.

## 3. Backend-Konfiguration

Die FastAPI-Anwendung nutzt Pydantic Settings (`app/core/config.py`). Folgende Variablen sollten gesetzt werden:
```
OIDC_ISSUER_URL=<Discovery-URL oder Issuer>
OIDC_CLIENT_ID=<Backend-Client-ID>
OIDC_CLIENT_SECRET=<Backend-Client-Secret>
API_DEV_TOKEN=<optional, nur für lokale Tests>
```
> Aktuell erzwingt die Middleware mindestens einen Bearer-Token. Sobald ein IdP aktiv ist, muss der Token validiert und optional gegen Rollen (`roles`-Claim) geprüft werden.

## 4. Frontend-Konfiguration

`packages/frontend-web/env.example` enthält die wichtigsten Parameter:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_OIDC_DISCOVERY_URL=<Discovery-URL>
VITE_OIDC_CLIENT_ID=<Frontend-Client-ID>
VITE_OIDC_REDIRECT_URI=http://localhost:3000/callback
VITE_API_DEV_TOKEN=<Fallback, optional>
```
Trigger den Login über `auth.login()` im Frontend; die Bibliothek nutzt PKCE und speichert Tokens in `localStorage`.

## 5. Test-Strategie
- **Lokale Entwicklung:** Dev-Token aktiv lassen, während IdP eingerichtet wird. Endpoints, die Auth erfordern, sollten mit `Authorization: Bearer <token>` angesprochen werden.
- **CI/CD:** Tokens als Secrets setzen (z. B. `API_DEV_TOKEN`, `VITE_API_DEV_TOKEN`) oder Test-IdP per Docker im Workflow starten.
- **Playwright:** Übergib `API_URL` und `API_DEV_TOKEN`, damit die API-Tests authentifiziert laufen.

## 6. Nächste Schritte
1. Bearer-Middleware um JWT-Validierung erweitern (je nach Provider).
2. Rollen-/Scope-Mapping im Backend implementieren (RBAC/ABAC).
3. Dev-Token in Staging/Production deaktivieren.
