# Lieferschein-Erfassung - Auth-Debugging

**Datum:** 2025-01-16  
**Problem:** Login-Seite erscheint immer noch nach Öffnen des Debitor-Auswahlfensters

## Debugging-Schritte

### 1. Prüfen, ob Dev-Token gesetzt wird

**Browser-Konsole öffnen (F12) und eingeben:**

```javascript
// Prüfen, ob Token gesetzt ist
localStorage.getItem('access_token')

// Sollte "dev-token" zurückgeben, wenn OIDC nicht konfiguriert ist
```

### 2. Prüfen, ob OIDC konfiguriert ist

**Browser-Konsole:**

```javascript
// Prüfen, ob OIDC-Discovery-URL gesetzt ist
import.meta.env.VITE_OIDC_DISCOVERY_URL

// Sollte undefined oder leer sein für Dev-Mode
```

### 3. Prüfen, ob Token an API gesendet wird

**Browser-Konsole → Network-Tab:**
1. Debitor-Auswahl öffnen (Strg+F1)
2. Network-Tab öffnen
3. Request zu `/api/v1/crm/customers` prüfen
4. **Headers** → **Authorization** sollte `Bearer dev-token` enthalten

### 4. Prüfen, ob Backend den Token akzeptiert

**Backend-Logs prüfen:**
- Sollte `API_DEV_TOKEN = "dev-token"` in Config haben
- Sollte Token akzeptieren, wenn er `"dev-token"` ist

### 5. Mögliche Probleme

#### Problem 1: Token wird nicht gesetzt
**Lösung:** AuthService-Constructor wird nicht ausgeführt
- Prüfen, ob `auth` Singleton korrekt initialisiert wird
- Prüfen, ob `localStorage` verfügbar ist

#### Problem 2: Token wird nicht gesendet
**Lösung:** Axios-Interceptor funktioniert nicht
- Prüfen, ob `getAccessToken()` korrekt funktioniert
- Prüfen, ob Token in Request-Header gesetzt wird

#### Problem 3: Backend akzeptiert Token nicht
**Lösung:** Backend-Config prüfen
- `API_DEV_TOKEN` muss `"dev-token"` sein
- Backend muss Token validieren

#### Problem 4: Timing-Problem
**Lösung:** Token wird zu spät gesetzt
- AuthService wird beim ersten Import initialisiert
- Sollte sofort verfügbar sein

## Aktuelle Fixes

### Fix 1: Dev-Token wird nicht als JWT decodiert

**Datei:** `packages/frontend-web/src/lib/auth.ts`

```typescript
if (this.accessToken === 'dev-token' || this.accessToken === import.meta.env.VITE_API_DEV_TOKEN) {
  // Dev token - use mock user, don't try to decode as JWT
  if (!this.user) {
    const mockUser: User = { ... }
    this.user = mockUser
  }
  return
}
```

### Fix 2: Fallback auf Dev-Token in Axios-Interceptor

**Datei:** `packages/frontend-web/src/lib/axios.ts`

```typescript
const token = getAccessToken()
// Always send token if available, or use dev-token as fallback in dev mode
const oidcConfigured = (import.meta.env.VITE_OIDC_DISCOVERY_URL ?? '').length > 0
const finalToken = token || (!oidcConfigured ? (import.meta.env.VITE_API_DEV_TOKEN || 'dev-token') : null)
if (finalToken !== null && readHeader(headers, "Authorization") === undefined) {
  writeHeader(headers, "Authorization", `Bearer ${finalToken}`)
}
```

## Nächste Schritte

1. **Browser-Cache leeren:**
   - Strg+Shift+Delete
   - "Cached images and files" auswählen
   - "Clear data"

2. **localStorage leeren:**
   ```javascript
   localStorage.clear()
   ```

3. **Seite neu laden:**
   - F5 drücken
   - Dev-Token sollte automatisch gesetzt werden

4. **Network-Tab prüfen:**
   - Request zu `/api/v1/crm/customers` sollte `Authorization: Bearer dev-token` haben

5. **Backend-Logs prüfen:**
   - Sollte Token akzeptieren
   - Sollte keine 401 zurückgeben

## Falls Problem weiterhin besteht

1. **Backend-Config prüfen:**
   ```python
   # app/core/config.py
   API_DEV_TOKEN: Optional[str] = "dev-token"
   ```

2. **Backend-Logs prüfen:**
   - Welcher Status-Code wird zurückgegeben?
   - Welche Fehlermeldung?

3. **Frontend-Logs prüfen:**
   - Browser-Konsole → Fehler?
   - Network-Tab → Request-Details?

