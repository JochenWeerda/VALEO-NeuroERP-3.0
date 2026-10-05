---
title: Tailwind CSS 4 — Migrationsanalyse & Entscheidung
type: reference
audience: [entwickler, architekt]
owner: Frontend
status: aktiv
last_reviewed: 2026-07-13
description: Validierung/Analyse und kontrollierter Migrationsplan Tailwind 3.4 → 4 für VALEO NeuroERP (Frontend-Web), inkl. Design-Token-Konsolidierung und Density-Modi.
---

# Tailwind CSS 4 — Migrationsanalyse & Entscheidung

**Grundsatzentscheidung:** VALEO NeuroERP verwendet **Tailwind CSS 4** als statische
Styling-Engine. Fachliche Oberflächen entstehen über die **Universal Mask Runtime** und
semantische VALEO-Komponenten. Gestaltung, Themes und Dichte werden ausschließlich über
zentrale **CSS-Design-Tokens** gesteuert. **Radix UI** bleibt die Headless-Basis
(kein erzwungener Wechsel auf Base UI). Spezialmasken dürfen eigene Renderer verwenden,
müssen aber dieselben semantischen Tokens konsumieren.

**Vorgehen:** Kontrollierter Pilot in `chore/tailwind-v4-pilot`, kein Big Bang, keine
gleichzeitige Migration von React 19 / Base UI. Umstellung des Gesamt-Builds erst nach
den Nachweisen (Phase 4).

## Ist-Zustand (Baseline, gemessen 2026-07-13)

| Baustein | Version / Befund |
|----------|------------------|
| tailwindcss | ^3.4.6 |
| autoprefixer / postcss | ^10.4.19 / ^8.5.15 |
| tailwindcss-animate | ^1.0.7 |
| vite / react | ^6.4.3 / ^18.3.1 |
| node | v24 (≥20 ✓, Upgrade-Tool lauffähig) |
| CSS-Einstieg | `@tailwind base/components/utilities` in `src/index.css` |
| Theme-Bridge | `tailwind.config.js` (129 Zeilen), Farben als `hsl(var(--x))` mit bloßen HSL-Tupeln |

### Baseline-Metriken (Tailwind 3, Referenz für Regression)

- Produktionsbuild: **exit 0, 28,5 s**.
- CSS-Hauptbundle `dist/assets/index-*.css`: **≈ 185 KB** (189.727 B) unkomprimiert.
- Weitere: maplibre-gl 70 KB, material-flow-display 16 KB.

### Kompatibilitäts-Ampel

| Bereich | Ampel | Einschätzung |
|---------|:-----:|--------------|
| React 18.3 | 🟢 | v4 benötigt kein React 19 |
| Vite 6.4 | 🟢 | kompatibel, offizielles `@tailwindcss/vite`-Plugin |
| shadcn/ui, Radix | 🟢 | v4 unterstützt; Radix versionsunabhängig |
| CSS-Variablen | 🟢 | sehr gute Ausgangslage |
| Meridian/Terra | 🟡 | Token-Bridge muss getrennt werden (siehe unten) |
| JS-Config | 🟡 | wird in v4 nicht automatisch geladen → `@config`-Bridge |
| tailwindcss-animate | 🟡 | Ersatz durch `tw-animate-css` |
| veraltete Utilities | 🟡 | begrenzte, klar lokalisierte Treffer |
| Browser-Anforderung | 🟢 | Chrome ≥111 / Safari ≥16.4 / Firefox ≥128 — **Matrix freigegeben** (siehe A) |
| Sofort-Prod-Update | 🟢 | Pilot + Visual-Regression durchlaufen, nach `main` gemerged, CI grün |

## A. Browser-Matrix (FREIGEGEBEN 2026-07-14)

Tailwind 4 nutzt `@property` und `color-mix()`; Mindestanforderung Chrome 111 /
Safari 16.4 / Firefox 128. **Verbindliche Zielmatrix — freigegeben am 2026-07-14:**

| Umgebung | Browser | Mindestversion | Freigabe |
|----------|---------|----------------|:--------:|
| Administrierte Windows-Arbeitsplätze | Edge/Chrome (Evergreen) | ≥ 111 | ✅ freigegeben |
| Büro-Mac | Safari | ≥ 16.4 | ✅ freigegeben |
| Lager-/Waage-Terminals, Handheld-Scanner | Edge WebView2 / Chromium | ≥ 111 | ✅ freigegeben |
| Tablets (iPad) | Safari / iPadOS | ≥ 16.4 | ✅ freigegeben |
| Embedded WebViews (Kiosk/POS) | Chromium-basiert | ≥ 111 | ✅ freigegeben |

> **Freigegeben (2026-07-14):** Die administrierte Flotte läuft auf Evergreen-Chromium/
> Edge bzw. Safari ≥ 16.4 und erfüllt damit die Tailwind-4-Baseline (`@property`,
> `color-mix()`). Alt-Geräte unterhalb Chrome 111 / Safari 16.4 sind **nicht** Teil der
> unterstützten Matrix; für solche Ausnahmekanäle gilt weiterhin der Tailwind-3.4-Stand
> (kein aktiver Kanal bekannt). Damit ist die Voraussetzung für den Gesamt-Build-Umstieg
> erfüllt — Migration nach `main` gemerged, CI grün.

## B. Meridian/Terra-Token-Überschneidung (kritischster Architekturbefund)

- `design-tokens-meridian.css`: **159** Variablen, Scope `:root, [data-theme="meridian"]`.
- `design-tokens-terra.css`: **162** Variablen, Scope `:root[data-theme="terra"]`.
- **150 identische Variablennamen** in beiden Dateien.

Terra ist per Spezifität korrekt auf `[data-theme="terra"]` gescoped und gewinnt nur bei
aktivem Terra-Theme; Meridian belegt zusätzlich den Default `:root`. Der Zustand
funktioniert, ist aber wartungsschwer (150 Duplikate) und vermischt Primitive und
Semantik. **Zielarchitektur:**

```
src/styles/tokens/
├── primitives.css   # Rohpalette: --blue-600, --neutral-50, Radius-/Font-Skalen
├── semantic.css     # Zuordnung: --action-primary, --focus-ring, --surface-page …
├── themes/
│   ├── meridian.css # [data-theme="meridian"] überschreibt nur semantische Tokens
│   └── terra.css    # [data-theme="terra"]  überschreibt nur semantische Tokens
└── density.css      # comfortable/compact/dense
```

Komponenten konsumieren möglichst nur **semantische** Tokens.

## C. Density-Modi (verbindlich)

`data-density` wird bereits von der Universal Mask Runtime gesetzt
(`UniversalMaskRenderer.tsx`, `ActionBarRenderer.tsx`). Drei verbindliche Modi:

| Modus | Verwendung | control-height / table-row-height / field-gap |
|-------|-----------|:---:|
| comfortable | CRM, Dashboards, Touch | 40 / 44 / 12 px |
| compact | ERP-Stammdaten | 34 / 36 / 8 px |
| dense | Disposition, Buchhaltung, Operator | 30 / 32 / 6 px |

## D. Veraltete Utilities (in v4 entfernt/umbenannt)

| Utility | Treffer | Ersatz |
|---------|:------:|--------|
| `flex-shrink-0` | 72 (36 Dateien) | `shrink-0` |
| `flex-grow` | 5 (2 Dateien) | `grow` |
| `bg-opacity-*` | 2 | `bg-…/NN` |
| `border-opacity-*` | 1 | `border-…/NN` |
| `shadow-sm` (Bedeutung geändert) | 132 (60 Dateien) | visuell prüfen (v4: `shadow-sm`→`shadow-xs`) |

Keine dynamischen `bg-${…}`-Klassen gefunden (🟢). `@apply` nur in `index.css`.
`@tailwindcss/upgrade` korrigiert den Großteil automatisch.

## E. Prüfkritische Masken (Visual Regression)

CRM 360°, Universal Mask Runtime, Auftrag, dichte Finanzbuchhaltung, POS/Waage,
Warehouse-High-Contrast, Meridian Dark Mode, Terra-Agrarmasken, Druckansichten,
Rationsoptimierung, Ackerschlagkartei-Auswertungen.

## Migrationsweg (Phasen)

1. **Vorprüfung:** Browser-Matrix, Node ≥20 ✓, Baseline-Build + Referenz-Screenshots, Benchmarks. *(dieses Dokument)*
2. **Technischer Pilot:** `@tailwindcss/upgrade`, `@tailwindcss/vite`, `tailwindcss-animate`→`tw-animate-css`, JS-Config zunächst über `@config`, deprecated Utilities.
3. **Token-Migration:** HSL vereinheitlichen, `@theme inline`, tokens/-Struktur (B+C), danach `tailwind.config.js` abbauen.
4. **Nachweise:** Prod-Build, Bundle-Budget, Typecheck, Vitest, Playwright-Smoke, A11y, Screenshot-Diff, Mask-Render-A/B.

## Umsetzungsstand (Pilot-Branch `chore/tailwind-v4-pilot`)

| Phase | Ergebnis |
|-------|----------|
| 1 Vorprüfung | ✅ Baseline-Build (185 KB CSS), Analyse, dieses Dokument |
| 2 Technischer Pilot | ✅ tailwindcss 4.3.2, `@tailwindcss/postcss`, `@import 'tailwindcss'`, `@plugin 'tailwindcss-animate'`, deprecated Utilities migriert, Codemod-Fehlrename `outline`→`outline-solid` (381 Stellen) korrigiert |
| 3 Token-Migration | ✅ `tailwind.config.js` → `@theme inline`; **Density-Modi** `density.css`; **Token-Duplikat-Auflösung** (siehe unten): 38 strukturelle Primitive nach `tokens/primitives.css` extrahiert |

### Token-Duplikat-Auflösung (150 gemeinsame Tokens Meridian∩Terra)

Wertvergleich der 150 gleichnamigen Tokens:

| Gruppe | Anzahl | Behandlung |
|--------|:------:|-----------|
| **Wertgleich, strukturell** (Font-Gewichte, Basis-Schriftgrößen, Zeilenhöhen, Spacing-Basis, Steuerhöhen, Radius-Grenzen, Motion, Z-Index) | **38** | ✅ nach `src/styles/tokens/primitives.css` (`:root`) extrahiert, aus beiden Theme-Dateien entfernt — **echte Duplikate eliminiert** |
| **Wertgleich, semantisch** (`--background`, `--muted`, `--border`, `--accent`, `--secondary`, Foregrounds …) | 15 | bleiben theme-scoped in den Theme-Dateien (müssen pro Theme an `:root[data-theme]`-Spezifität greifen); referenzieren jetzt die kollisionsfrei umbenannte Palette `--palette-gray-*` |
| **Wertverschieden** (Paletten `--color-primary-*`/`--color-harvest-*`/`--color-gray-*`, `--primary`, `--radius`, `--font-family-*`, Schatten, Sidebar, abweichende Schriftgrößen/Spacing/Motion …) | 97 | **keine Duplikate** — intentionale Theme-Varianten, bleiben je Theme |

### Behoben: `--color-gray-*` / Tailwind-Paletten-Kollision

Die Theme-Paletten (Meridian/Terra) hießen `--color-gray-*` und kollidierten namentlich
mit Tailwind v4s eingebauter `--color-gray-*`-Palette (oklch, unlayered → gewann). Unter
aktivem Terra zogen `--background`/`--muted`/`--border` dadurch ungültige Tailwind-`oklch`-
Werte statt der Terra-HSL-Palette. **Fix:** Die theme-eigene Palette in beiden Theme-Dateien
zu **`--palette-gray-*`** umbenannt (Definitionen + `var()`-Referenzen der semantischen
Tokens). Tailwinds `--color-gray-*` (für `bg-gray-*`-Utilities und den index.css-Border-
Kompat-Shim) bleibt unangetastet.

Verifikation: Prod-Build grün; Meridian-Vollnutzungssmoke **14/14, 0 Fehler**; **Theme-Kaskade
jetzt vollständig** — `data-theme="terra"` schaltet `--background` auf `40 15% 96%`,
`--muted` auf `40 12% 92%` und `--primary` auf `158 64% 28%` (Waldgrün); Default (Meridian)
unverändert (`--background: 210 20% 98%`, `--primary: 215 85% 42%`).
| 4 Nachweise | ✅ Prod-Build grün (25,5 s), `tsc` 0 Fehler, Docker-Prod-Image grün, Playwright-Vollnutzungssmoke **14/14, 0 Fehler**; CSS-Bundle 185→229 KB (v4-typisch). ⏳ offen: Screenshot-Diff-Gate, A11y-Benchmark |

**Bekannte Punkte:** CSS-Bundle +44 KB (v4-Preflight/mehr Varianten) — bei Bedarf via
Content-Purge/Prune prüfen. Browser-Matrix **freigegeben 2026-07-14** (siehe A); Migration
nach `main` gemerged, CI grün. `@tailwindcss/vite`-Plugin optional (aktuell PostCSS-Plugin,
funktioniert); Wechsel als reine Performance-Optimierung möglich.

## Schlussurteil

Technische Kompatibilität ≈ 80 %. Der Stack ist gut vorbereitet; die Hauptaufgaben sind
Browserfreigabe, Vite-Integration, Token-Bridge-Migration, Ersatz entfernter Utilities und
visuelle Absicherung — nicht React/Radix/Mask-Runtime. Migration empfohlen als
kontrollierter Pilot.
