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
| Browser-Anforderung | 🟡 | Chrome ≥111 / Safari ≥16.4 / Firefox ≥128 |
| Sofort-Prod-Update | 🔴 | ohne Pilot + Visual-Regression nicht empfohlen |

## A. Browser-Matrix (Entscheidungspunkt)

Tailwind 4 nutzt `@property` und `color-mix()`; Mindestanforderung Chrome 111 /
Safari 16.4 / Firefox 128. **Verbindliche Zielmatrix (Vorschlag, freizugeben):**

| Umgebung | Browser | Freigabe |
|----------|---------|:--------:|
| Administrierte Windows-Arbeitsplätze | aktueller Edge/Chrome | 🟢 |
| Büro-Mac | Safari ≥16.4 | 🟢 |
| Lager-/Waage-Terminals, alte iPads, embedded WebViews | prüfen | 🟡 offen |

> **Offen:** Falls Alt-Terminals/embedded Browser < Chrome 111 verbindlich unterstützt
> werden müssen, bleibt für diese Kanäle Tailwind 3.4. Freigabe der Matrix erforderlich,
> bevor der Gesamt-Build umgestellt wird.

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
| **Wertgleich, semantisch** (`--background`, `--muted`, `--border`, `--accent`, `--secondary`, Foregrounds …) | 15 | bleiben in den Theme-Dateien — referenzieren die theme-eigene `--color-gray-*`-Palette, die **namentlich mit Tailwind v4s eingebauter Palette kollidiert**; eine hoch-spezifische Neudefinition an `:root[data-theme]` würde Tailwinds (unlayered) `oklch`-Werte ziehen und `hsl(var(--background))` ungültig machen |
| **Wertverschieden** (Paletten `--color-primary-*`/`--color-harvest-*`/`--color-gray-*`, `--primary`, `--radius`, `--font-family-*`, Schatten, Sidebar, abweichende Schriftgrößen/Spacing/Motion …) | 97 | **keine Duplikate** — intentionale Theme-Varianten, bleiben je Theme |

Verifikation: Prod-Build grün; Meridian-Vollnutzungssmoke **14/14, 0 Fehler** (Default unverändert `--background: 210 20% 98%`); Theme-Kaskade intakt (`data-theme="terra"` schaltet kollisionsfreies `--primary` auf Waldgrün `158 64% 28%`).

> **Bekannter Folgepunkt (migrationsbedingt, unabhängig von der Dedup):** Die Theme-
> Paletten nutzen `--color-gray-*`, was mit Tailwind v4s eingebauter `--color-gray-*`
> (oklch, unlayered) kollidiert. Unter aktivem Terra ziehen `--background`/`--muted`/
> `--border` dadurch Tailwind-Werte. Das aktive Default-System (`index.css`) umgeht das
> bereits über nicht-kollidierende Namen (`--color-neutral-*-hsl`). Saubere Lösung:
> Theme-Paletten auf `--palette-*`/`--color-neutral-*` umbenennen (eigener Slice).
| 4 Nachweise | ✅ Prod-Build grün (25,5 s), `tsc` 0 Fehler, Docker-Prod-Image grün, Playwright-Vollnutzungssmoke **14/14, 0 Fehler**; CSS-Bundle 185→229 KB (v4-typisch). ⏳ offen: Screenshot-Diff-Gate, A11y-Benchmark |

**Bekannte Punkte:** CSS-Bundle +44 KB (v4-Preflight/mehr Varianten) — bei Bedarf via
Content-Purge/Prune prüfen. Browser-Matrix-Freigabe weiterhin erforderlich vor Merge nach
`main`. `@tailwindcss/vite`-Plugin optional (aktuell PostCSS-Plugin, funktioniert); Wechsel
als reine Performance-Optimierung möglich.

## Schlussurteil

Technische Kompatibilität ≈ 80 %. Der Stack ist gut vorbereitet; die Hauptaufgaben sind
Browserfreigabe, Vite-Integration, Token-Bridge-Migration, Ersatz entfernter Utilities und
visuelle Absicherung — nicht React/Radix/Mask-Runtime. Migration empfohlen als
kontrollierter Pilot.
