# Design Tokens – VALEO NeuroERP

Dieses Dokument beschreibt, wie die vereinheitlichten Design Tokens in der Frontend-Codebasis eingesetzt werden.

## 1. Quelle der Wahrheit

- **Spec Datei:** `packages/frontend-web/specs/tokens.spec.json`
- **Typed Export:** `packages/frontend-web/src/design/tokens.ts`

Die Spec folgt dem [GitHub Spec Kit Schema](https://github.com/github/spec-kit). Der TypeScript-Wrapper stellt eine readonly-Repräsentation zur Verfügung:

```ts
import { designTokens, getColorToken } from "@/design/tokens";

getColorToken("brand.primary.500"); // "#3b82f6"
designTokens.spacing["4"];          // "1rem"
```

> **Hinweis:** `getToken(path)` erlaubt beliebige Dot-Pfade (`colors.brand.primary.500`). Bei ungültigen Pfaden wird ein Fehler geworfen.

## 2. Tailwind-Integration

Die zentralen CSS Custom Properties werden in `src/index.css` gesetzt. Für jede relevante Palette existieren HSL-Variablen wie `--color-brand-primary-500-hsl`. Die Tailwind-Theme-Variablen (`--primary`, `--background`, etc.) referenzieren diese Tokens:

```css
:root {
  --color-brand-primary-500-hsl: 217.2 91.2% 59.8%;
  --primary: var(--color-brand-primary-600-hsl);
  --primary-foreground: var(--color-neutral-50-hsl);
  /* ... */
}
```

Tailwind ordnet diese Variablen dem Theme zu (`tailwind.config.js → theme.extend.colors`). Dadurch können Komponenten wie gewohnt `bg-primary`, `text-muted-foreground` usw. verwenden, ohne Hexwerte zu duplizieren.

## 3. Dark-Mode

Die `.dark` Klasse überschreibt lediglich die Token-Zuordnung (z. B. `--background`, `--primary`). Die eigentlichen Werte stammen weiterhin aus der Spec. Dadurch bleibt Dark-Mode bei Token-Anpassungen automatisch konsistent.

## 4. Storybook & CI

- `pnpm --filter @valero-neuroerp/frontend-web build-storybook` (CI Step) erzeugt eine statische Dokumentation, die auf den Tokens basiert.
- Playwright-Visual-Regression Tests (`pnpm --filter @valero-neuroerp/frontend-web test:e2e`) laufen in der gleichen Pipeline und sichern die wichtigsten UI-Pfade.

## 5. Best Practices

1. **Keine hardcodierten Farben** in Komponenten – ausschließlich Tailwind-Utilities oder CSS-Variablen nutzen.
2. **Neue Tokens** zuerst in `tokens.spec.json` ergänzen, anschließend ggf. CSS-Variablen erweitern.
3. **Dokumentation** in Storybook aktualisieren (Controls/Docs Tab), falls neue Token-Kategorien hinzukommen.

## 6. Offene Punkte

- High-Contrast- und Reduced-Motion-Variablen aus der Spec sind vorbereitet, aber noch nicht in allen Komponenten angewendet.
- Für Team-übergreifende Freigaben sollte der Token-Katalog regelmäßig in Produkt-Workshops abgestimmt werden.

Stand: 2025‑10‑12
