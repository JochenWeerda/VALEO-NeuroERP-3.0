# Frontend Routing

## Entscheidung

Das Web-Frontend verwendet seit `ROUTER-NEXT-001` ausschliesslich TanStack
Router als Browser-Router. Die fruehere zentrale React-Router-Splat-Runtime
(`params['*']`) und ihre separaten App-/Portal-Runtimes sind entfernt.

Der Route Tree wird reproduzierbar durch
`packages/frontend-web/scripts/generate-tanstack-routes.mjs` erzeugt. Der
Generator fuehrt die bestehenden Route-Aliase und generierten Seitengruppen
zu expliziten TanStack-Routen zusammen.

## Source of Truth

- `src/app/route-aliases.json`: fachlich gepflegte Route-zu-Modul-Zuordnung
- `src/app/route-builders/auto-groups/generated/`: automatisch geerntete Seiten
- `src/app/routing/legacy-redirects.json`: explizit freigegebene alte URLs
- `src/app/routing/route-tree.gen.tsx`: generiertes Ergebnis, nicht manuell editieren
- `src/app/routing/route-contract.ts`: typisierte Deep-Link- und Search-API

Vor `dev`, `build` und `type-check` laeuft automatisch `pnpm routes:generate`.

## Compile-Time-Vertrag

`buildRoute()` akzeptiert nur generierte Pfade. Dynamische Pfade verlangen
exakt ihre benannten Parameter und URL-kodieren deren Werte.

`appendRouteSearch()` akzeptiert nur Query-Keys, die der Generator aus den
produktiven `searchParams.get(...)`-Zugriffen ermittelt. Werte sind auf
URL-serialisierbare Primitive und Arrays davon begrenzt.

Neue Navigationen sollen diese API oder die registrierten TanStack-APIs
verwenden. Der Adapter `react-router-compat.tsx` erhaelt bestehende
Komponenten waehrend der schrittweisen Aufrufermigration, erzeugt aber keinen
zweiten Browser-Router.

## Metadaten und Layouts

Jede generierte Route besitzt `staticData` fuer Breadcrumb, Seitenmodul und
Legacy-Pfad. Breadcrumbs lesen den aktiven TanStack-Match. App, Portal und
oeffentliche Auth-Routen sind getrennte Route-Layouts; Auth wird am
App-Layout durch `ProtectedRoute` durchgesetzt.

Legacy-Redirects werden nur explizit aufgenommen. Pauschale Redirects nach
Modul sind unzulaessig, weil einzelne Module fachlich verschiedene Listen-,
Neu- und Detail-URLs bedienen.

## Qualitaetsgates

```text
pnpm --filter @valero-neuroerp/frontend-web type-check
pnpm --filter @valero-neuroerp/frontend-web check:routing-integrity
pnpm --filter @valero-neuroerp/frontend-web test:run
pnpm --filter @valero-neuroerp/frontend-web build
pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/tanstack-router-smoke.spec.ts
```

Der Browser-Smoke prueft App-Route, dynamischen Deep Link, Login, Portal und
einen kanonischen Legacy-Redirect.
