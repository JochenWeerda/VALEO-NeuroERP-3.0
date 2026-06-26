# VALEO NeuroERP 3.0 — Design-Analyse: Ist-Soll-Bewertung

**Version:** 1.0 | **Datum:** 2026-05-18 | **Autor:** Design System Audit

---

## 1. Zusammenfassung

VALEO NeuroERP 3.0 besitzt eine technisch solide Design-Basis: Das Token-System
ueber HSL-Custom-Properties ist strukturiert, das Tailwind-Setup ist konsistent,
und der Dark-Mode sowie das Warehouse-Theme belegen, dass systematisch gedacht wurde.
Jedoch fehlt die letzte Konsequenz: Typografie-Regie, metrische Konsistenz bei
Abstaenden und Touch-Targets sowie eine klare visuelle Sprache, die VALEO von
generischen ERP-Systemen unterscheidet.

Der Gesamt-Score liegt bei **4.4 / 10** (gewichtet) — ein solides Fundament mit
klar definierten Hebeln fuer deutliche Verbesserung bei ueberschaubarem Aufwand.

---

## 2. Gewichtete Scoring-Tabelle

| Dimension | Gewicht | Ist-Wert | Soll-Wert | Score 0-10 | Delta-Prioritaet |
|---|---|---|---|---|---|
| Typografie-Konsistenz | 15 % | System-Font-Stack (keine explizite Schrift) | Inter/Plus Jakarta Sans, vollstaendige Skala | 3/10 | **HOCH** |
| Farb-Harmonie | 12 % | Blue HSL(221,83%,53%) + Green HSL(142,76%,36%) — kalt, generisch | Harmonische 3-Farben-Palette mit Agrar-Identitaet | 6/10 | MITTEL |
| Weissraum / Luftigkeit | 15 % | 4px-Basis, zu wenig Padding in Cards und Tabellen | Apple-Niveau: grosszuegige Abstaende, Hierarchien durch Raum | 4/10 | **HOCH** |
| Goldener Schnitt / phi | 8 % | Nicht systematisch angewandt; Tailwind-Skala arithmetisch | phi=1.618 als Leitprinzip fuer Verhaeltnisse | 2/10 | MITTEL |
| Ergonomie (DIN EN ISO 9241) | 12 % | h-9=36px Default-Button unter WCAG 44px | Alle interaktiven Elemente >=44px | 5/10 | **HOCH** |
| Accessibility (WCAG 2.2 AA) | 12 % | Gute Basis durch Radix UI; Kontraste nicht vollstaendig geprueft | 100 % WCAG 2.2 AA, Fokus-Ring sichtbar, Kontrast >=4.5:1 | 6/10 | MITTEL |
| Einheitlichkeit / Wiedererkennung | 10 % | Verschiedene Card-Stile, inkonsistente Abstaende | Jede Maske sofort als VALEO-Maske erkennbar | 4/10 | **HOCH** |
| Leserlichkeit | 10 % | System-Fonts inkonsistent; Zeilenlaengen nicht geregelt | Optimale x-Hoehe, 60-80 Zeichen, 1.5x Zeilenabstand | 4/10 | **HOCH** |
| ERP-spezifische Ergonomie | 6 % | Tastaturnavigation vorhanden; keine Shortcuts | Kompakte Tabellen, Keyboard-First, Shortcuts | 6/10 | NIEDRIG |
| Modernitaet / Zeitlosigkeit | (Info) | Tailwind-Standard-Look, erkennbar 2023-Style | Eigenstaendige visuelle Sprache, die 2030 frisch wirkt | 5/10 | MITTEL |

### Berechneter Gesamt-Score

```
Gewichtete Summe:
  Typografie:         0.15 x 3  = 0.450
  Farb-Harmonie:      0.12 x 6  = 0.720
  Weissraum:          0.15 x 4  = 0.600
  Goldener Schnitt:   0.08 x 2  = 0.160
  Ergonomie:          0.12 x 5  = 0.600
  Accessibility:      0.12 x 6  = 0.720
  Einheitlichkeit:    0.10 x 4  = 0.400
  Leserlichkeit:      0.10 x 4  = 0.400
  ERP-Ergonomie:      0.06 x 6  = 0.360
  ─────────────────────────────────────────
  Summe Gewichte:     1.00 (100%)
  GESAMT-SCORE:       4.41 / 10
```

Mit der informativen Dimension Modernitaet als qualitativer Ergaenzung ergibt
sich ein Gesamteindruck von ca. **4.7 / 10** — ausbaufaehig, aber starkes Fundament.

---

## 3. Detailanalyse je Dimension

### 3.1 Typografie-Konsistenz — Score 3/10 (HOCH)

**Ist-Zustand:**
- Kein expliziter Font definiert; Tailwind-Default `font-sans` loest auf:
  `ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", ...`
- Windows: Segoe UI | macOS: SF Pro | Linux: Ubuntu/Cantarell
  → **drei verschiedene visuelle Erlebnisse auf drei Betriebssystemen**
- Typografische Skala linear: 12px, 14px, 16px, 18px, 20px, 24px — arithmetisch, nicht harmonisch
- Kein `text-rendering: optimizeLegibility` gesetzt
- Keine tabellarischen Ziffern in Datentabellen (Ziffern tanzen in Spalten)

**Soll-Zustand:**
- Eine einzige, explizit definierte Schriftfamilie (Empfehlung: Plus Jakarta Sans)
- Typografische Skala mit phi-Verhaeltnissen: 12 -> 14 -> 16 -> 20 -> 26 -> 42 px
- Lautstaerke-Hierarchie: Display > Headline > Title > Body > Caption
- `font-variant-numeric: tabular-nums` fuer alle Zahlenspalten
- Variable Font: ein einziger Font-Request fuer Gewichte 300-700

**Massnahmen:**
1. `@import` von Plus Jakarta Sans in `index.css` (oder `npm i @fontsource/plus-jakarta-sans`)
2. CSS Custom Properties `--font-family-sans`, `--font-size-xs` bis `--font-size-4xl`
3. Tailwind-Config: `fontFamily.sans` und `fontSize`-Skala ueberschreiben
4. Alle `<td>` mit numerischen Inhalten: Klasse `tabular-nums` hinzufuegen

---

### 3.2 Farb-Harmonie — Score 6/10 (MITTEL)

**Ist-Zustand:**
- Primary: HSL(221, 83%, 53%) — reines Informationsblau, kalt, identisch Tailwind `blue-600`
- Accent: HSL(142, 76%, 36%) — kraeftiges Gruen, zu satt
- Beide mit hoher Saettigung → visuelle Rivalitaet
- Neutral-Grays: ungefaerbt → farblich flach, nicht waeremnd
- Hintergrund: reines Weiss `#ffffff` → ermuedet bei Langzeitarbeit (8+ Stunden ERP)

**Soll:**
- Harmonische Triade: Primaer (dominant) + Warm-Akzent (Amber) + kuehl-neutrale Grays
- Off-White Hintergrund mit leichtem Blaustich: HSL(210, 20%, 98%)
- Neutral-Grays mit minimalem Farbstich der Primaerfarbe

---

### 3.3 Weissraum / Luftigkeit — Score 4/10 (HOCH)

**Ist-Zustand:**
- Cards: `p-4` (16px) → zu wenig Atemraum
- Listen-Items: `py-2` = 8px → unter dem Minimum fuer entspanntes Lesen
- Section-Abstaende: `gap-4` (16px) zwischen logischen Bloecken → zu eng
- Kein systematisches Anwenden des Naehe-Prinzips (Gestaltpsychologie)

**Soll:**
- Card-Standard-Padding: mindestens `p-6` (24px)
- Section-Abstaende: `gap-8` bis `gap-12` (32-48px)
- Gruppierung durch Raum, nicht durch Linien (Apple-Prinzip)
- Tabellen-Rows: `py-3` (12px) Normal, `py-2` (8px) Kompakt

---

### 3.4 Goldener Schnitt / phi-Proportionen — Score 2/10 (MITTEL)

**Ist-Zustand:**
- Sidebar-Breite nicht nach phi definiert
- Spaltenaufteilungen oft 50/50 statt 38/62 (phi)
- Abstands-Skala arithmetisch (4, 8, 12, 16px...)

**Soll:**
- Sidebar expanded: 240px | Content bei 1440px: 1160px → Verhaeltnis 1:4.8 (bewusste Entscheidung)
- 2-Spalten-Layouts: 38% / 62% statt 50/50
- Spacing-Skala: 8 -> 13 -> 21 -> 34 -> 55px (Fibonacci-Approximation von phi)

---

### 3.5 Ergonomie (DIN EN ISO 9241-110) — Score 5/10 (HOCH)

**Ist-Zustand:**
- Default-Button `h-9` = 36px → verletzt WCAG 2.5.5 (Target Size 44x44px Empfehlung)
- `h-10` = 40px fuer `size="lg"` — immer noch 4px zu klein
- Hover-States: nur Faerbung, kein Groessen-Feedback
- Keine konsequenten Keyboard-Shortcuts
- Icon-Only-Buttons fehlen teilweise `aria-label`

**Soll:**
- Alle Click-Targets >=44x44px
- `h-11` (44px) als neuer Default fuer alle Buttons
- Focus-Ring: 2px solid, Offset 2px
- Keyboard-Shortcuts: N (Neu), S (Speichern), / (Suche), Esc (Schliessen)

---

### 3.6 Accessibility (WCAG 2.2 AA) — Score 6/10 (MITTEL)

**Gut vorhanden:**
- Radix UI liefert korrekte ARIA-Semantik
- Dark Mode vorhanden
- Fokus-Management in Dialogen

**Luecken:**
- Farbkontraste nicht systematisch geprueft (Ziel: >=4.5:1 fuer Normal-Text)
- Fehlermeldungen nur visuell (rot) → kein `aria-live` fuer Screen-Reader
- Kein Skip-to-Content-Link
- Toasts ohne `role="status"` oder `role="alert"`

---

### 3.7 Einheitlichkeit / Wiedererkennung — Score 4/10 (HOCH)

**Ist-Zustand:**
- Verschiedene Card-Varianten koexistieren (Border+Shadow / nur Border / nur Shadow)
- Inkonsistente Header-Strukturen ueber Masken-Typen
- Kein definiertes Page-Level-Layout-Token
- Fehlende Branded-Momente

**Soll:**
- Genau 3 Card-Varianten: Default / Outlined / Elevated
- Jede ListReport-Maske: identisches Layout (Toolbar → Filter → Tabelle → Pagination)
- Jede ObjectPage-Maske: identisches Layout (Header-Band → Tabs → Content)

---

### 3.8 Leserlichkeit — Score 4/10 (HOCH)

**Ist-Zustand:**
- System-Fonts fuehren zu inkonsistenter x-Hoehe und Laufweite
- Keine Zeilenlaengen-Beschraenkung bei Fliesstext
- Zeilenabstand `leading-normal` = 1.5 OK, aber nicht konsequent eingehalten
- Kein `hyphens: auto` fuer lange deutsche Worte (z.B. "Erntemengenerfassungsformular")

**Soll:**
- Zeilenlaenge: 60-80 Zeichen (`max-w-prose` = 65ch) fuer Fliesstext
- Zeilenabstand: 1.5 fuer Body, 1.2 fuer Headlines
- `hyphens: auto` fuer alle Textelemente mit deutschen Inhalten
- Dedizierte Schrift mit guter x-Hoehe (Plus Jakarta Sans: x-Hoehe 0.54)

---

## 4. Top-5 Massnahmen nach ROI

Sortiert nach **(Wirkung x Abdeckungsbreite) / Implementierungsaufwand**

---

### Rang 1: Schriftfamilie definieren — ROI: Sehr hoch | Aufwand: 2 Stunden

Jede Textzeile auf jedem Screen profitiert sofort. Groesste Wirkung bei geringstem Aufwand.

```css
/* index.css */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

:root {
  --font-family-sans: 'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif;
}
```

```js
// tailwind.config.js
theme: {
  extend: {
    fontFamily: { sans: ['var(--font-family-sans)'] },
  }
}
```

**Wirkung:** +1.5 auf Typografie-Konsistenz, +0.5 auf Leserlichkeit.
Konsistenz auf allen Betriebssystemen garantiert.

---

### Rang 2: Button-Heights auf 44px — ROI: Hoch | Aufwand: 30 Minuten

WCAG-Verletzung beheben. Bessere Bedienbarkeit auf Aussen-Tablets und Wareneingang-Terminals.

```tsx
// components/ui/button.tsx — cva-Varianten
const buttonVariants = cva(
  "...",
  {
    variants: {
      size: {
        default: 'h-11 px-4 py-2',   // war: h-9
        sm:      'h-9 rounded-md px-3',
        lg:      'h-12 rounded-md px-8',
        icon:    'h-11 w-11',          // war: h-9 w-9
      },
    },
  }
)
```

**Wirkung:** +1.5 auf Ergonomie, WCAG-Compliance 2.5.5 hergestellt.

---

### Rang 3: Off-White Hintergrund — ROI: Hoch | Aufwand: 1 Stunde

Reduziert Augenermüdung. Eigenstaendiger Charakter statt "weisses Browser-Fenster".

```css
/* index.css :root */
--background:    210 20% 98%;   /* war: 0 0% 100% */
--card:          210 25% 99%;
--muted:         210 15% 95%;
--border:        210 18% 91%;
```

**Wirkung:** +1 auf Weissraum-Wahrnehmung, +0.5 auf Modernitaet, Augenschutz.

---

### Rang 4: Spacing-System mit phi-Abstaenden — ROI: Mittel-Hoch | Aufwand: 1 Tag

Gibt der Oberflaeche sofort mehr Atem. Macht Abstands-Entscheidungen fuer alle Entwickler eindeutig.

```css
:root {
  --space-1:  8px;   /* micro — Padding in Chips/Badges */
  --space-2: 13px;   /* small — Padding in kompakten Elementen */
  --space-3: 21px;   /* base  — Card-Standard-Padding */
  --space-4: 34px;   /* large — Section-Abstand */
  --space-5: 55px;   /* xl    — Page-Level-Abstand */
}
```

**Wirkung:** +2 auf Weissraum, +1 auf Einheitlichkeit.

---

### Rang 5: Harvest-Amber als Agrar-Identitaets-Akzent — ROI: Mittel | Aufwand: 3 Stunden

Gibt VALEO eine visuelle Identitaet, die sofort "Landhandel" kommuniziert.
Differenziert von SAP/Microsoft-Blau-Monotonie.

```css
:root {
  --color-harvest:    38 95% 52%;    /* Amber — Ernte, Getreide */
  --color-harvest-fg: 38 95% 15%;    /* Dunkel fuer Text auf Amber */
  --color-harvest-bg: 38 95% 95%;    /* Sehr hell fuer Hintergruende */
}
```

Verwendung: KPI-Badges (Erntemengen, Preise), Status-Tags "Kontrakt aktiv", Harvest-Charts.

**Wirkung:** +1.5 auf Farb-Harmonie, +1 auf Einheitlichkeit/Identitaet.

---

## 5. Technische Schulden — Quick-Fix-Liste

| Problem | Datei | Fix |
|---|---|---|
| Button h-9 (36px) | `components/ui/button.tsx` | Default auf `h-11` (44px) |
| System-Font | `index.css` | Plus Jakarta Sans importieren |
| Reines Weiss #fff | `index.css :root` | `--background: 210 20% 98%` |
| Fehlende tabular-nums | Alle Tabellen-TDs mit Zahlen | `font-variant-numeric: tabular-nums` |
| Fehlender Skip-Link | AppShell-Komponente | `<a href="#main" class="sr-only focus:not-sr-only">Zum Inhalt</a>` |
| Fehlende aria-live Toasts | Toast-Komponente | `role="status" aria-live="polite"` |
| Input-Focus kaum sichtbar | `components/ui/input.tsx` | `focus-visible:ring-2 focus-visible:ring-offset-2` |

---

## 6. Benchmark-Vergleich

| System | Typografie | Farbe | Spacing | Gesamt |
|---|---|---|---|---|
| SAP Fiori Horizon 2024 | 8/10 | 7/10 | 7/10 | 7.3 |
| Microsoft Dynamics 365 | 7/10 | 6/10 | 6/10 | 6.3 |
| Odoo 17 | 7/10 | 7/10 | 7/10 | 7.0 |
| **VALEO NeuroERP (Ist)** | **3/10** | **6/10** | **4/10** | **4.4** |
| **VALEO NeuroERP (Soll nach Konzept)** | **9/10** | **9/10** | **8/10** | **8.7** |

Mit konsequenter Umsetzung eines der drei Konzepte kann VALEO alle Wettbewerber
in der visuellen Qualitaet uebertreffen — bei deutlich niedrigerem Aufwand,
da kein Legacy-CSS vorhanden ist.
