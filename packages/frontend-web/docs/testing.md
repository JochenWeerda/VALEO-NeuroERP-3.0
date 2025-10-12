# Frontend Testing Guidelines

## Vitest

- **Command:** `pnpm --filter @valero-neuroerp/frontend-web test:run`
- **Setup:** `src/test-setup.ts`
  - aktiviert `@testing-library/jest-dom/vitest`
  - polyfills für `matchMedia` & `ResizeObserver`, damit JSDOM-Komponenten ohne Browser-APIs funktionieren.

## Playwright

- **Command:** `pnpm --filter @valero-neuroerp/frontend-web test:e2e`
- **CI:** `.github/workflows/ci.yml` installiert Browser + lädt den Report als Artefakt.

## Storybook Smoke-Test

- **Command:** `pnpm --filter @valero-neuroerp/frontend-web storybook:smoke`
- **CI:** der Build-Artefakt (`storybook-static`) wird hochgeladen und kann für visuelle Reviews genutzt werden.
