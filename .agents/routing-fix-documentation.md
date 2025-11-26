***REMOVED*** Routing-Fix: /sales Route korrigiert

***REMOVED******REMOVED*** Problem

Beim Öffnen von `http://localhost:3000/sales` wurde eine rudimentäre Sales-Übersicht angezeigt statt der Angebots-Liste.

***REMOVED******REMOVED*** Root Cause

1. **Auto-Routing-System**: Das System in `app/routes.tsx` erstellt automatisch Routes basierend auf Dateipfaden
2. **Konflikt**: `pages/sales.tsx` wurde automatisch auf `/sales` geroutet
3. **Alias-Route überschrieben**: Die Alias-Route aus `route-aliases.json` (die `/sales` auf `angebote-liste` zeigen sollte) wurde durch die Auto-Route überschrieben

***REMOVED******REMOVED*** Lösung

**Datei gelöscht**: `packages/frontend-web/src/pages/sales.tsx`

Diese Datei war eine alte, rudimentäre Sales-Übersicht, die nicht mehr benötigt wird. Die vollständige Angebots-Funktionalität ist in `pages/sales/angebote-liste.tsx` implementiert.

***REMOVED******REMOVED*** Ergebnis

Nach dem Löschen der Datei:
- `/sales` zeigt jetzt korrekt die Angebots-Liste (`angebote-liste.tsx`)
- Angebote können erstellt werden über den "Neu Angebot" Button
- Alle i18n-Übersetzungen funktionieren korrekt

***REMOVED******REMOVED*** Route-Konfiguration

Die Route ist korrekt in `route-aliases.json` definiert:
```json
{
  "module": "@/pages/sales/angebote-liste",
  "path": "sales"
}
```

***REMOVED******REMOVED*** Verifikation

Nach dem Neustart des Frontend-Servers sollte `/sales` die vollständige Angebots-Liste mit allen Funktionen anzeigen.

