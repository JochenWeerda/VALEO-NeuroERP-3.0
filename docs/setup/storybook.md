# Storybook Dokumentation

## Ziel
Storybook dient als UI-Katalog fuer Komponenten, States und Regression-Checks.

## Lokaler Start
1. Abhaengigkeiten installieren.
2. Storybook starten:

```bash
npm run storybook
```

Falls kein Script vorhanden ist, alternativ:

```bash
npx storybook dev -p 6006
```

## Build fuer CI
```bash
npx storybook build
```

## Mindestumfang fuer neue Komponenten
- Default State
- Loading State
- Error State
- Disabled/ReadOnly State
- Mobile Viewport (falls relevant)

## Ablage
- Stories im selben Modul wie die Komponente (`*.stories.tsx`).
- Domain-spezifische Stories unter `packages/frontend-web/src/**`.
