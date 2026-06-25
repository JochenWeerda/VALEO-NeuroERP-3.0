# Lieferschein-Erfassung - Root Cause Analysis

**Datum:** 2025-01-16  
**Status:** ✅ Root Cause gefunden und behoben

## Root Cause

**Das Problem:** `VITE_OIDC_DISCOVERY_URL` ist in der `.env` Datei gesetzt, aber mit einem **Platzhalter-Wert**:

```
VITE_OIDC_DISCOVERY_URL=https://your-oidc-provider.com/.well-known/openid-configuration
```

**Die alte Logik:**
```typescript
const oidcConfigured = config.oidc.discoveryUrl.length > 0
```

**Problem:** Diese Prüfung erkennt den Platzhalter als "konfiguriert", obwohl es kein echter OIDC-Provider ist!

## Lösung

### Neue Prüfung: Erkennt Platzhalter-Werte

**Datei:** `packages/frontend-web/src/lib/auth.ts`

```typescript
// Helper: Check if OIDC is actually configured (not just placeholder)
const isOidcConfigured = (): boolean => {
  const discoveryUrl = import.meta.env.VITE_OIDC_DISCOVERY_URL ?? ''
  // Check if URL is empty or is a placeholder
  if (!discoveryUrl || discoveryUrl.length === 0) {
    return false
  }
  // Check for common placeholder patterns
  const placeholderPatterns = [
    'your-oidc-provider.com',
    'example.com',
    'keycloak.example.com',
    'login.microsoftonline.com/{tenant-id}',
    '{domain}.auth0.com',
    '{domain}.okta.com',
    '{tenant-id}',
    '{application-id}',
    '{client-id}',
    '{domain}',
  ]
  return !placeholderPatterns.some(pattern => discoveryUrl.includes(pattern))
}
```

### Alle Stellen aktualisiert

1. ✅ `packages/frontend-web/src/lib/auth.ts` - `isOidcConfigured()` Funktion
2. ✅ `packages/frontend-web/src/lib/axios.ts` - Platzhalter-Erkennung
3. ✅ `packages/frontend-web/src/lib/api-client.ts` - Platzhalter-Erkennung
4. ✅ `packages/frontend-web/src/components/auth/ProtectedRoute.tsx` - Platzhalter-Erkennung
5. ✅ `packages/frontend-web/src/hooks/useAuth.ts` - Platzhalter-Erkennung

## Test

1. **Seite neu laden:** F5
2. **Debitor-Auswahl öffnen:** Strg+F1
3. **Erwartung:** 
   - ✅ Dialog "AUSWAHL KUNDEN" öffnet sich
   - ✅ Keine Login-Seite
   - ✅ Dev-Token wird verwendet

## Erkannte Platzhalter-Patterns

- `your-oidc-provider.com`
- `example.com`
- `keycloak.example.com`
- `{tenant-id}`
- `{domain}`
- `{application-id}`
- `{client-id}`

Wenn einer dieser Patterns in der URL gefunden wird, wird OIDC als **nicht konfiguriert** behandelt.

## Nächste Schritte

1. **Option 1:** `.env` Datei anpassen und Platzhalter entfernen:
   ```env
   # VITE_OIDC_DISCOVERY_URL=  # Leer lassen für Dev-Mode
   ```

2. **Option 2:** Echten OIDC-Provider konfigurieren:
   ```env
   VITE_OIDC_DISCOVERY_URL=https://keycloak.example.com/realms/valeo/.well-known/openid-configuration
   ```

3. **Option 3:** Nichts tun - Platzhalter werden jetzt automatisch erkannt und ignoriert ✅

