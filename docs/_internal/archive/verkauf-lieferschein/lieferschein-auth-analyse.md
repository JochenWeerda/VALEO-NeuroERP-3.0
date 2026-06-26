# Lieferschein-Erfassung - Auth-Analyse: Funktioniert Anmeldung?

**Datum:** 2025-01-16  
**Frage:** Würde es funktionieren, wenn ich mich anmelde?

## Aktuelle Situation

### 1. Login-Seite erscheint
- Nach Öffnen des Debitor-Auswahlfensters wird zur Login-Seite umgeleitet
- Login-Seite zeigt: "Mit SSO anmelden"

### 2. OIDC-Konfiguration

**Prüfung:** Ist `VITE_OIDC_DISCOVERY_URL` gesetzt?

- **Wenn JA:** OIDC ist konfiguriert → Anmeldung würde funktionieren
- **Wenn NEIN:** OIDC ist nicht konfiguriert → Anmeldung würde **NICHT** funktionieren

### 3. Login-Funktion

**Code:** `packages/frontend-web/src/lib/auth.ts` Zeile 111-114

```typescript
async login(): Promise<void> {
  if (config.oidc.discoveryUrl.length === 0) {
    throw new Error('OIDC not configured. Set VITE_OIDC_DISCOVERY_URL')
  }
  // ... OIDC Flow
}
```

**Ergebnis:**
- **Wenn OIDC konfiguriert:** Login funktioniert → Weiterleitung zu OIDC-Provider
- **Wenn OIDC NICHT konfiguriert:** Login wirft Fehler → "OIDC not configured"

## Lösung: Dev-Mode ohne Anmeldung

### Aktuelle Implementierung

Das Frontend sollte automatisch den Dev-Token verwenden, wenn OIDC nicht konfiguriert ist:

```typescript
// Development mode: Create mock user if no OIDC config and no token
const oidcConfigured = config.oidc.discoveryUrl.length > 0
if (!oidcConfigured && this.accessToken == null) {
  // Create a mock user for development
  const mockUser: User = { ... }
  this.user = mockUser
  // Use API_DEV_TOKEN if available, otherwise use default "dev-token"
  const devToken = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  this.accessToken = devToken
  localStorage.setItem('access_token', devToken)
  return
}
```

### Problem

Die Umleitung zur Login-Seite passiert **bevor** der Dev-Token gesetzt wird, weil:
1. API-Call zu `/api/v1/crm/customers` gibt 401 zurück
2. `handleUnauthorized()` wird aufgerufen
3. Umleitung zu `/login` erfolgt

### Lösung

Die Umleitung sollte **nur** erfolgen, wenn OIDC konfiguriert ist:

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

## Antwort auf die Frage

### Würde es funktionieren, wenn Sie sich anmelden?

**Antwort:** **NUR wenn OIDC konfiguriert ist**

1. **Wenn `VITE_OIDC_DISCOVERY_URL` gesetzt ist:**
   - ✅ Anmeldung würde funktionieren
   - ✅ Weiterleitung zu OIDC-Provider (Keycloak, Azure AD, etc.)
   - ✅ Nach erfolgreicher Anmeldung: Token wird gespeichert
   - ✅ API-Calls funktionieren mit dem echten Token

2. **Wenn `VITE_OIDC_DISCOVERY_URL` NICHT gesetzt ist:**
   - ❌ Anmeldung würde **NICHT** funktionieren
   - ❌ Fehler: "OIDC not configured. Set VITE_OIDC_DISCOVERY_URL"
   - ✅ Aber: Dev-Token sollte automatisch verwendet werden
   - ✅ API-Calls sollten mit Dev-Token funktionieren

## Empfehlung

### Option 1: Dev-Mode ohne Anmeldung (Empfohlen für Entwicklung)

1. **Prüfen:** Ist `VITE_OIDC_DISCOVERY_URL` gesetzt?
   ```bash
   # In .env oder env.example
   VITE_OIDC_DISCOVERY_URL=  # Leer lassen für Dev-Mode
   ```

2. **Seite neu laden:** F5 drücken
3. **Dev-Token wird automatisch verwendet**
4. **Keine Anmeldung nötig**

### Option 2: Mit OIDC-Anmeldung (Für Production/Testing)

1. **OIDC konfigurieren:**
   ```env
   VITE_OIDC_DISCOVERY_URL=https://keycloak.example.com/realms/valeo/.well-known/openid-configuration
   VITE_OIDC_CLIENT_ID=valeo-erp
   ```

2. **Seite neu laden:** F5 drücken
3. **Auf "Mit SSO anmelden" klicken**
4. **Bei OIDC-Provider anmelden**
5. **Token wird gespeichert**

## Nächste Schritte

1. **Prüfen:** Ist OIDC konfiguriert?
   - Browser-Konsole öffnen (F12)
   - `localStorage.getItem('access_token')` prüfen
   - Environment-Variablen prüfen

2. **Testen:**
   - Seite neu laden (F5)
   - Debitor-Auswahl öffnen (Strg+F1)
   - Sollte funktionieren ohne Anmeldung (wenn OIDC nicht konfiguriert)

3. **Falls immer noch Login-Seite erscheint:**
   - Browser-Cache leeren
   - `localStorage.clear()` in Konsole
   - Seite neu laden

