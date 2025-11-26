# i18n-Übersetzungen Fix

## Problem

Die deutschen Übersetzungen wurden nicht angezeigt. Stattdessen wurden die Übersetzungsschlüssel selbst angezeigt (z.B. `crud.list.title` statt "Angebote Liste").

## Root Cause

1. **i18n-Konfiguration nicht initialisiert**: Die i18n-Konfiguration in `packages/frontend-web/src/i18n/config.ts` wurde nie importiert, daher wurde i18next nie initialisiert.

2. **Backend-Plugin Konflikt**: Die Konfiguration verwendete sowohl das Backend-Plugin (zum Laden von Übersetzungen über HTTP) als auch direkte Ressourcen-Imports. Das Backend-Plugin versuchte, Übersetzungen von `/locales/{{lng}}/{{ns}}.json` zu laden, was fehlschlug.

## Lösung

### 1. i18n-Import in main.tsx hinzugefügt

**Datei**: `packages/frontend-web/src/main.tsx`

```typescript
import '@/i18n/config' // Initialize i18n
```

Dies stellt sicher, dass i18next beim Start der Anwendung initialisiert wird.

### 2. Backend-Plugin entfernt

**Datei**: `packages/frontend-web/src/i18n/config.ts`

- Entfernt: `import Backend from 'i18next-http-backend'`
- Entfernt: `.use(Backend)` aus der i18n-Konfiguration
- Entfernt: `backend` Konfigurationsobjekt

Die Übersetzungen werden jetzt direkt aus dem importierten JSON geladen, was schneller und zuverlässiger ist.

## Ergebnis

Nach dem Neustart des Frontend-Servers oder Neuladen der Seite (F5) sollten alle deutschen Übersetzungen korrekt angezeigt werden:

- ✅ `crud.list.title` → "Angebote Liste"
- ✅ `crud.list.overview` → "Übersicht aller Angebote"
- ✅ `crud.actions.new` → "Neu"
- ✅ `crud.actions.filter` → "Filtern"
- ✅ `crud.actions.search` → "Suchen"
- ✅ `crud.print.export` → "Exportieren"
- ✅ `crud.list.showing` → "Zeige X von Y Angebote"

## Verifikation

1. Frontend-Server neu starten (falls nötig)
2. Seite im Browser neu laden (F5)
3. `http://localhost:3000/sales` öffnen
4. Alle Texte sollten jetzt auf Deutsch angezeigt werden

