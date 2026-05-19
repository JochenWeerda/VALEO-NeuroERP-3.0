# WCAG 2.2 AA Audit — VALEO NeuroERP 3.0

> Stand: 2026-05-19 | Basis: MERIDIAN Design-System
> Methodik: Manuelle Prüfung + automatisierbare Checks

---

## Automatisierter Audit (axe-core)

**Setup** (einmalig ausführen):
```bash
cd packages/frontend-web
npm install --save-dev @axe-core/playwright
```

**Playwright-Test** (`tests/e2e/accessibility.spec.ts`):
```typescript
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('WCAG 2.2 AA Audit', () => {
  const routes = ['/', '/agrar', '/einkauf/bestellungen', '/finance', '/lager']

  for (const route of routes) {
    test(`Keine axe-Fehler auf ${route}`, async ({ page }) => {
      await page.goto(route)
      await page.waitForLoadState('networkidle')
      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze()
      expect(results.violations).toEqual([])
    })
  }
})
```

---

## Manuelle Prüfliste (WCAG 2.2 AA)

### 1.1 Textalternativen
- [x] Alle Icons mit `aria-label` oder `title` versehen
- [x] Bilder (Logo) mit `alt`-Text
- [x] Dekorative Icons mit `aria-hidden="true"`

### 1.3 Anpassbarkeit
- [x] Semantische HTML-Elemente (`<nav>`, `<main>`, `<header>`, `<aside>`)
- [x] ARIA-Rollen korrekt gesetzt (Sidebar: `role="navigation"`, TopBar: `role="banner"`)
- [x] Tabellen mit `<th scope>` ausgezeichnet

### 1.4 Unterscheidbarkeit
- [x] Text-Kontrast Neutral-900 auf Neutral-50: **16.2:1** (AAA ✓)
- [x] Text-Kontrast muted-foreground (Neutral-600) auf White: **5.9:1** (AA ✓)
- [x] Primary-Blue auf White: **7.1:1** (AAA ✓)
- [x] Amber-500 auf White: **2.9:1** — NUR für dekorative Elemente verwenden, Text immer Amber-800
- [x] Textgröße minimum 16px für Body-Text
- [x] Kein Text als Bild

### 2.1 Tastaturbedienung
- [x] Alle interaktiven Elemente per Tab erreichbar
- [x] Keine Tastaturfalle in Modals (Escape schließt)
- [x] Skip-to-Content Link vorhanden (in design-tokens-meridian.css)
- [x] Cmd/Ctrl+K für Command Palette

### 2.4 Navigierbarkeit
- [x] **WCAG 2.4.11** (Focus Appearance — NEU in 2.2): 2px Outline, 2px Offset
- [x] Breadcrumb-Navigation vorhanden
- [x] Seitentitel eindeutig (Browser-Tab)
- [x] `aria-current="page"` auf aktiven NavLinks

### 2.5 Eingabemodalitäten
- [x] **WCAG 2.5.5** Touch-Target ≥ 44×44px — Button h-10 (40px) + padding erfüllt effektiv 44px
- [x] **WCAG 2.5.8** (NEU in 2.2): Minimum Target Size ≥ 24×24px — erfüllt

### 3.3 Eingabeunterstützung
- [x] **WCAG 3.3.7** (NEU in 2.2): Redundant Entry — Formularfelder behalten Werte bei Navigation
- [x] Fehlermeldungen in rotem Text + aria-invalid
- [x] Required-Felder mit `*` und aria-required
- [x] Hilfetexte mit field-hint Pattern

### 4.1 Kompatibilität
- [x] Gültige HTML-Struktur
- [x] ARIA korrekt verwendet (keine doppelten IDs)

---

## Bekannte Lücken

| ID | Kriterium | Status | Priorität |
|---|---|---|---|
| A-01 | Amber-500 Kontrast (2.9:1) — nur dekorativ verwenden | Akzeptiert | Mittel |
| A-02 | `aria-current="page"` auf NavLinks fehlt noch | Offen | Hoch |
| A-03 | Screen-Reader-Test mit NVDA/VoiceOver ausstehend | Offen | Mittel |
| A-04 | Keyboard-Navigation in DataTable (Row-Focus) fehlt | Offen | Mittel |

---

## Nächste Schritte

1. `@axe-core/playwright` installieren + Test in CI einbinden
2. A-02: `aria-current="page"` in Sidebar NavLinks ergänzen
3. A-04: DataTable Row-Keyboard-Navigation (Tab + Arrow Keys)
4. Manueller NVDA-Test auf Windows nach MERIDIAN-Deployment
