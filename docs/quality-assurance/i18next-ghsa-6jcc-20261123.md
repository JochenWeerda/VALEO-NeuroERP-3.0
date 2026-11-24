---
title: i18next GHSA-6jcc-5g8w-32mx — Herstellerfix
type: qa
audience: [entwickler, qa, sicherheit]
owner: Cursor
status: zur Abnahme
last_reviewed: 2026-11-23
version: 1.0.0
---

# i18next GHSA-6jcc-5g8w-32mx — Herstellerfix

Slice: M0-I18NEXT-GHSA-6JCC-20261123 (Meilenstein M0).

## Befund

Am 23.11.2026 um 20:53 UTC wurde GHSA-6jcc-5g8w-32mx veroeffentlicht:
`deepExtend` in i18next rekursiert in geerbte Built-ins und kann geteilte
Built-in-Objekte veraendern (DoS, Schwere moderate). Betroffen ist i18next
< 26.3.4; das Frontend loeste 25.5.3 auf. Der Node-Dependency-Gate
(`Dependency Scan (blocking high/critical)`, `Python and Node Dependency Audit`)
sperrt damit jede PR mit `No exact source repair for this finding`.

Der Pfad ist im Produkt erreichbar: `loadLanguage` in
`packages/frontend-web/src/i18n/config.ts` mischt Uebersetzungen aus
`/api/translations/{lng}` mit `addResourceBundle(lng, 'translation', bundle, true, true)`
tief ein — das ist der `deepExtend`-Weg.

## Entscheidung

Herstellerfix statt Quellbackport (ADR-080 sieht Backports nur ohne
Herstellerrelease vor): `i18next` in `packages/frontend-web/package.json` auf
`^26.3.4`, Lockfile mit `pnpm install --lockfile-only` aktualisiert. Aufgeloest
wird 26.7.2. `react-i18next` 16.0.0 bleibt (Peer `i18next >= 25.5.2`, ohne
Obergrenze); weitere Pakete aendern sich nicht.

Die Breaking Changes von i18next 26.0.0 betreffen den Code nicht: keine
Verwendung von `initImmediate`, der alten `interpolation.format`-Funktion,
`simplifyPluralSuffix` oder `showSupportNotice` (Suche ueber `packages/`).
Die Initialisierung nutzt nur `resources`, `lng`, `fallbackLng`,
`supportedLngs`, `detection`, `interpolation.escapeValue` und `react.useSuspense`.

## Abnahme

- `Dependency Scan (blocking high/critical)` und `Python and Node Dependency Audit` gruen.
- `Frontend Tests & Build`, `Frontend (lint + typecheck + build)` und `E2E @critical` gruen.
