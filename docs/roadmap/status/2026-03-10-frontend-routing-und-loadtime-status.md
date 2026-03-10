# Frontend Routing und Load-Time Status

**Stand:** 2026-03-10

## Ziel

Stabiler Seitenaufruf nach der Runtime-Entkopplung und konsistente Route-Aufloesung fuer Haupt-App und Kundenportal.

## Umgesetzte Architekturpunkte

- `AppRuntime`, Router-Bootstrap und Runtime-Services getrennt
- `routes.tsx` in Builder- und Runtime-Pfade zerlegt
- Haupt-App-Routing auf domanenspezifische Gruppen und lazy Runtime-Pfade umgestellt
- `page-module-loader` eingefuehrt und auf Gruppen `core`, `commercial`, `finance`, `operations`, `portal` aufgeteilt
- `portal/*` weiter separat belassen, aber technisch an denselben Alias-Matcher wie die Haupt-App angeglichen

## Konkrete Resolver-Fixes

- `page-module-loader.ts`
  - Modul-Key-Aufloesung auf `../../pages/...` korrigiert
  - Portal-Gruppe als zulaessige Page-Module-Gruppe aufgenommen
- `PortalRouteRuntime.tsx`
  - keine direkte `import.meta.glob`-Pfadheuristik mehr
  - Alias-Group `portal` wird geladen und ueber gemeinsamen Matcher aufgeloest
- `AppRouteRuntime.tsx`
  - Alias-Matching auf gemeinsamen Helper umgestellt
- `alias-matching.ts`
  - gemeinsame Normalisierung, Priorisierung und Match-Logik fuer Alias-Routen

## Integritaetspruefung

Geprueft wurden:

- Auto- und Alias-Gruppen der Haupt-App
- Navigation-Resolver
- Portal-Alias-Gruppe gegen reale `pages/portal/*.tsx`

Ergebnis:

- keine offenen Unknown-Module im geprueften Routing-Pfad
- `portal`-Aliasse vollstaendig
- `portal`-Module vollstaendig

## Verifikation

- `pnpm --filter @valero-neuroerp/frontend-web run type-check`
- `pnpm --filter @valero-neuroerp/frontend-web run build`

Beide erfolgreich.

## Betriebsrelevante Hinweise

- Die Fehlermeldung `Route references unknown module` war ein Frontend-Resolver-Fehler, kein Dockerfile- oder Container-Build-Problem.
- Browser-Extension-Fehler wie `content.js ... reading 'query'` sind davon getrennt und nicht Teil des App-Routings.

## Aktueller Zustand

- Haupt-App und Portal verwenden nun denselben Alias-Matching-Standard
- Portal bleibt dennoch ein eigener Runtime-Pfad mit eigenem Layout und eigenem Einstieg
- Das ist fuer Performance und Wartbarkeit der saubere Zielzustand
