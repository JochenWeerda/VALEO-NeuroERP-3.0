# Lieferschein-Erfassung - Auth-Fix für Debitor-Auswahl

**Datum:** 2025-01-16  
**Problem:** Nach Öffnen des Debitor-Auswahlfensters erscheint Login-Seite

## Problem

Beim Öffnen des Debitor-Auswahlfensters (Strg+F1) erscheint die Login-Seite, obwohl kein OIDC konfiguriert ist.

## Ursache

1. **Frontend:** Kein Access-Token wird gesendet, wenn OIDC nicht konfiguriert ist
2. **Backend:** API-Endpunkt `/api/v1/crm/customers` gibt 401 zurück
3. **Interceptor:** `handleUnauthorized()` leitet zur Login-Seite um, auch wenn OIDC nicht konfiguriert ist

## Lösung

### 1. Frontend: Dev-Token verwenden

Das Backend unterstützt `API_DEV_TOKEN = "dev-token"` für Development. Das Frontend verwendet jetzt diesen Token, wenn OIDC nicht konfiguriert ist.

**Datei:** `packages/frontend-web/src/lib/auth.ts`

```typescript
// Development mode: Create mock user if no OIDC config and no token
const oidcConfigured = config.oidc.discoveryUrl.length > 0
if (!oidcConfigured && this.accessToken == null) {
  // Create a mock user for development
  const mockUser: User = {
    sub: 'dev-user',
    email: 'dev@valeo-neuro-erp.local',
    name: 'Development User',
    scopes: ['admin:all', 'sales:read', 'sales:write', 'crm:read', 'crm:write'],
    roles: ['admin', 'user'],
    exp: Math.floor(Date.now() / 1000) + 86400,
  }
  this.user = mockUser
  // Use API_DEV_TOKEN if available, otherwise use default "dev-token" that matches backend
  const devToken = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  this.accessToken = devToken
  localStorage.setItem('access_token', devToken)
  return
}
```

### 2. Frontend: Keine Umleitung bei 401 ohne OIDC

**Datei:** `packages/frontend-web/src/lib/auth.ts`

```typescript
export function handleUnauthorized(): void {
  const oidcConfigured = config.oidc.discoveryUrl.length > 0
  // Only redirect to login if OIDC is configured
  if (oidcConfigured) {
    auth.logout()
    if (typeof window !== 'undefined') {
      window.location.assign('/login')
    }
  } else {
    // In dev mode without OIDC, just clear session but don't redirect
    auth.logout()
  }
}
```

### 3. Frontend: Warnung statt Umleitung bei 401

**Datei:** `packages/frontend-web/src/lib/axios.ts`

```typescript
if (status === HTTP_STATUS_UNAUTHORIZED) {
  // In development mode without OIDC, don't redirect to login
  const oidcConfigured = (import.meta.env.VITE_OIDC_DISCOVERY_URL ?? '').length > 0
  if (oidcConfigured) {
    handleUnauthorized()
  }
  // In dev mode, log the error but don't redirect
  console.warn('API request returned 401 Unauthorized. In dev mode without OIDC, this might be expected.')
  throw error
}
```

## Backend-Konfiguration

Das Backend akzeptiert den Dev-Token in `app/core/security.py`:

```python
API_DEV_TOKEN: Optional[str] = "dev-token"
```

Der Token wird in `require_bearer_token()` validiert:

```python
token = credentials.credentials.strip()
expected = settings.API_DEV_TOKEN

if expected and token == expected:
    request.state.token_claims = {"token_type": "dev"}
    return token
```

## Test

1. **Seite neu laden:** `http://localhost:3000/verkauf/lieferschein-erfassung`
2. **Debitor-Auswahl öffnen:** Strg+F1 oder Klick auf "..." bei Debitor-Kto.
3. **Erwartung:** Dialog "AUSWAHL KUNDEN" öffnet sich, keine Login-Seite

## Optional: Environment Variable

Falls ein anderer Dev-Token verwendet werden soll, kann `VITE_API_DEV_TOKEN` in der `.env` gesetzt werden:

```env
VITE_API_DEV_TOKEN=mein-dev-token
```

Der Standardwert ist `"dev-token"`, der mit dem Backend übereinstimmt.

