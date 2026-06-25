# Lieferschein-Erfassung - Ultimate Auth-Fix

**Datum:** 2025-01-16  
**Status:** 🔧 Finale Lösung

## Problem

Login-Seite erscheint hartnäckig nach Öffnen des Debitor-Auswahlfensters, obwohl OIDC nicht konfiguriert ist.

## Root Cause Analysis

### Problem 1: Dev-Token wird als JWT decodiert
- `jwtDecode()` wirft Fehler bei "dev-token" (kein gültiges JWT)
- Fehler führt zu `logout()`, was Token löscht

### Problem 2: Token wird nicht garantiert gesendet
- Wenn `getAccessToken()` `null` zurückgibt, wird kein Token gesendet
- Backend gibt 401 zurück → Umleitung zur Login-Seite

### Problem 3: Timing-Problem
- AuthService wird beim Import initialisiert
- Aber Token könnte zu spät gesetzt werden

## Ultimate Fix

### Fix 1: Dev-Token wird nicht mehr als JWT decodiert

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

### Fix 2: Immer Dev-Token verwenden, wenn OIDC nicht konfiguriert

**Datei:** `packages/frontend-web/src/lib/auth.ts`

```typescript
// If OIDC not configured, always use dev token (even if token exists in localStorage)
if (!oidcConfigured) {
  // Always use dev token in dev mode (override any existing token)
  const devToken = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  this.accessToken = devToken
  localStorage.setItem('access_token', devToken)
  return
}
```

### Fix 3: Fallback auf Dev-Token in Axios-Interceptor

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

## Test-Plan

### Schritt 1: Browser-Cache leeren
1. Strg+Shift+Delete
2. "Cached images and files" auswählen
3. "Clear data"

### Schritt 2: localStorage leeren
**Browser-Konsole (F12):**
```javascript
localStorage.clear()
```

### Schritt 3: Seite neu laden
1. `http://localhost:3000/verkauf/lieferschein-erfassung`
2. F5 drücken

### Schritt 4: Token prüfen
**Browser-Konsole:**
```javascript
localStorage.getItem('access_token')
// Sollte "dev-token" zurückgeben
```

### Schritt 5: Debitor-Auswahl öffnen
1. Strg+F1 drücken
2. **Network-Tab** öffnen (F12)
3. Request zu `/api/v1/crm/customers` prüfen
4. **Headers** → **Authorization** sollte `Bearer dev-token` enthalten

### Schritt 6: Erwartung
- ✅ Dialog "AUSWAHL KUNDEN" öffnet sich
- ✅ Keine Login-Seite
- ✅ API-Call funktioniert

## Falls Problem weiterhin besteht

### Debugging-Checkliste

1. **Prüfen, ob OIDC konfiguriert ist:**
   ```javascript
   // Browser-Konsole
   import.meta.env.VITE_OIDC_DISCOVERY_URL
   // Sollte undefined oder leer sein
   ```

2. **Prüfen, ob Token gesetzt ist:**
   ```javascript
   localStorage.getItem('access_token')
   // Sollte "dev-token" sein
   ```

3. **Prüfen, ob Token gesendet wird:**
   - Network-Tab → Request zu `/api/v1/crm/customers`
   - Headers → Authorization sollte `Bearer dev-token` enthalten

4. **Prüfen, ob Backend Token akzeptiert:**
   - Backend-Logs prüfen
   - Sollte `API_DEV_TOKEN = "dev-token"` in Config haben

5. **Prüfen, ob Backend 401 zurückgibt:**
   - Network-Tab → Response → Status
   - Sollte 200 sein, nicht 401

## Notfall-Lösung

Falls nichts funktioniert, kann manuell ein Dev-Token gesetzt werden:

**Browser-Konsole:**
```javascript
localStorage.setItem('access_token', 'dev-token')
location.reload()
```

Dies sollte das Problem umgehen und den Dialog öffnen.

