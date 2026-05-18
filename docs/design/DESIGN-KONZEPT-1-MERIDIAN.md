# Design-Konzept 1: MERIDIAN — Praezision trifft Waerme

**Inspiration:** Apple Human Interface Guidelines + SAP Fiori Horizon
**Charakter:** Vertrauenswuerdig, praezise, warmherzig — das Premium-ERP fuer anspruchsvolle Landhaendler
**Zielgruppe:** Genossenschaftsmanager, Einkaufsleiter, Buchhalter (40-60 Jahre, hohe Taeglichnutzung)

---

## 1. Design-DNA

Meridian verbindet die Praezision eines Schweizer Instruments mit der Waerme des Landhandels.
Die Schrift ist humanistisch (nicht technisch), die Farben sind tief und vertrauensvoll,
die Abstands-Philosophie ist grosszuegig. Jedes Element atmet.

**Leitsatz:** "Jede Zahl ist lesbar. Jede Aktion ist klar. Jede Maske ist einladend."

---

## 2. Typografie

### Schriftfamilie: Plus Jakarta Sans

- **Hersteller:** Tokotype (Google Fonts, kostenlos, SIL OFL)
- **Klassifikation:** Humanistisches Groteskschrift
- **Warum:** Hohe x-Hoehe (0.54), warmherzige Kurven, exzellent bei kleinen Groessen,
  tabellarische Ziffern verfuegbar, Italic fuer Hervorhebungen
- **Alternativen:** Inter (kuehlter), DM Sans (weicher), Outfit (moderner)

```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');
```

### Typografische Skala (phi-basiert, Faktor 1.272 = Viertelwurzel phi)

| Token | px | rem | Verwendung |
|---|---|---|---|
| `--font-size-xs` | 12px | 0.75rem | Captions, Timestamps, Hilfstexte |
| `--font-size-sm` | 14px | 0.875rem | Table-Body, Labels, Sekundaer-Info |
| `--font-size-base` | 16px | 1rem | Standard-Body-Text |
| `--font-size-lg` | 20px | 1.25rem | Card-Titel, Abschnitts-Ueberschriften |
| `--font-size-xl` | 26px | 1.625rem | Seitentitel, Modul-Ueberschriften |
| `--font-size-2xl` | 33px | 2.0625rem | Display-Elemente, Willkommen-Text |
| `--font-size-3xl` | 42px | 2.625rem | Hero-Zahlen, KPI-Werte |

### Zeilenabstaende und Gewichte

- Body: `font-weight: 400`, `line-height: 1.6`
- Labels: `font-weight: 500`, `line-height: 1.4`
- Ueberschriften: `font-weight: 600-700`, `line-height: 1.2`
- Zahlen in Tabellen: `font-variant-numeric: tabular-nums; font-weight: 500`

---

## 3. Farbpalette

### Primaer: Tiefes Ozeanblau

```
HSL(215, 85%, 42%)  — #0d5aa7
```

Psychologie: Vertrauen, Stabilitaet, Kompetenz. Tiefer als Standard-Blau → wirkt premium.
Kontrast auf Weiss: 7.1:1 → WCAG AAA.

### Akzent: Warmes Bernstein (Harvest)

```
HSL(38, 95%, 52%)   — #f5a623
```

Psychologie: Ernte, Getreide, Waerme, Energie. Verbindet mit der Agrar-Welt.
Verwendung: KPI-Highlights, aktive Zustands-Indikatoren, Ernte-bezogene Daten.

### Hintergrund: Off-White mit Blaustich

```
HSL(210, 20%, 98%)  — #f5f8fc
```

Nicht reines Weiss. Augenfreundlich bei Langzeitarbeit. Wirkt wie hochwertiges Papier.

### Vollstaendige Semantik-Palette

```
Oberflaechenhierarchie:
  --background:       210 20% 98%     (Seiten-Hintergrund)
  --surface:          210 25% 99%     (Card-Hintergrund)
  --surface-raised:   210 30% 100%    (Modal, Popover)
  --surface-sunken:   210 18% 95%     (Input-Hintergrund, Code-Blocks)

Primaer-System:
  --primary:          215 85% 42%     (Ocean Blue)
  --primary-hover:    215 85% 36%     (dunkler fuer Hover)
  --primary-active:   215 85% 30%     (Pressed-State)
  --primary-subtle:   215 85% 94%     (Hintergrund fuer Badges)
  --primary-fg:       0   0%  100%    (Weiss — Text auf Primary)

Harvest-Akzent:
  --harvest:          38  95% 52%     (Amber)
  --harvest-hover:    38  95% 44%
  --harvest-subtle:   38  95% 94%
  --harvest-fg:       38  95% 15%     (Dunkelbraun — Text auf Harvest)

Neutrals (mit Blaustich):
  --gray-50:          210 20% 98%
  --gray-100:         210 18% 95%
  --gray-200:         210 16% 90%
  --gray-300:         210 14% 82%
  --gray-400:         210 12% 68%
  --gray-500:         210 10% 50%
  --gray-600:         210 10% 38%
  --gray-700:         210 12% 26%
  --gray-800:         210 14% 16%
  --gray-900:         210 18% 10%

Semantik:
  --success:          142 76% 36%     (Bleibt gruenlich — Agrar-Sinn)
  --warning:          38  95% 52%     (= Harvest — Konsistenz)
  --error:            0   72% 51%
  --info:             215 85% 42%     (= Primary)

Oberflaechentext:
  --foreground:       210 18% 10%     (Haupt-Text)
  --muted-fg:         210 12% 42%     (Sekundaer-Text)
  --placeholder:      210 10% 60%
  --border:           210 18% 91%
  --border-focus:     215 85% 42%     (= Primary)
  --ring:             215 85% 42%
```

---

## 4. Abstands- und Groessen-System

### Spacing-Skala (phi-basiert, Basis: 8px)

```
--space-0:  4px    (micro — Icon-Padding)
--space-1:  8px    (xs    — Badge, Tag-Padding)
--space-2: 13px    (sm    — Button-Padding, Input-Padding)
--space-3: 21px    (md    — Card-Padding, Formular-Gap)
--space-4: 34px    (lg    — Section-Abstand)
--space-5: 55px    (xl    — Page-Level-Abstand)
--space-6: 89px    (2xl   — Hero-Abstand, sehr selten)
```

### Layout-Konstanten

```
--sidebar-expanded:   240px
--sidebar-collapsed:   64px
--content-max:       1400px
--content-padding:     32px  (= --space-4 + Abrundung)
--header-height:       64px
--toolbar-height:      56px
--table-row-height:    52px  (normal)
--table-row-compact:   40px  (dicht)
```

### Border-Radius

```
--radius-sm:   6px    (Chips, Badges, kleine Elemente)
--radius:     12px    (Buttons, Inputs, Cards — Meridian-Standard)
--radius-lg:  16px    (Modals, Popovers)
--radius-xl:  24px    (grosse Feature-Cards)
--radius-full: 9999px (Pills, Avatar)
```

---

## 5. Komponenten-Beschreibungen

### Button (Primaer)

```
Groesse:    height: 44px (--space-3 + 2px)
Padding:    0 20px
Radius:     12px (--radius)
Font:       14px, weight 600, Plus Jakarta Sans
Farbe:      bg=primary, text=primary-fg
Hover:      bg=primary-hover, shadow: 0 2px 8px rgba(13,90,167,0.25)
Active:     bg=primary-active, translateY(1px)
Focus:      ring 2px primary, offset 2px
Transition: all 150ms ease-out
```

Tailwind-Klassen:
```
h-11 px-5 rounded-[12px] bg-primary text-primary-foreground
font-semibold text-sm tracking-wide
hover:bg-primary/90 hover:shadow-md
active:translate-y-px
focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2
transition-all duration-150
```

### Card

```
Hintergrund: surface (HSL 210 25% 99%)
Border:      1px solid border (HSL 210 18% 91%)
Radius:      12px
Padding:     24px (--space-3)
Shadow:      0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)
Hover:       shadow: 0 4px 12px rgba(0,0,0,0.08)
```

Tailwind-Klassen:
```
bg-card border border-border rounded-[12px] p-6
shadow-[0_1px_3px_rgba(0,0,0,0.06),0_1px_2px_rgba(0,0,0,0.04)]
hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)]
transition-shadow duration-200
```

### Input / Textfeld

```
Hoehe:       44px
Padding:     0 12px
Radius:      8px (--radius-sm + 2px, etwas kleiner als Button)
Font:        14px, weight 400
Border:      1px solid border
Hintergrund: surface-sunken
Fokus:       border-color = primary, ring 2px primary mit 50% Opazitaet
Placeholder: muted-fg
```

### DataTable

```
Header:      bg=gray-100, font-weight 600, text-size 12px uppercase tracking-wide
Row Normal:  bg=transparent, border-bottom 1px border, py-3
Row Hover:   bg=primary-subtle (HSL 215 85% 94%)
Row Selected:bg=primary-subtle, border-left 3px solid primary
Zahlenfelder:font-variant-numeric: tabular-nums, text-align: right
Aktions-Col: icons mit h-8 w-8 (32px Touch-Target + 6px unsichtbare Erweiterung via padding)
```

### Sidebar (Meridian)

```
Breite expanded:  240px
Breite collapsed:  64px
Hintergrund:       HSL(215, 30%, 14%)   (Dunkles Navy-Blue)
Text:              HSL(210, 20%, 80%)
Aktiv-Item:        bg=HSL(215, 85%, 42%), text=white
Hover-Item:        bg=HSL(215, 30%, 20%)
Transition:        width 250ms cubic-bezier(0.4, 0, 0.2, 1)
Logo-Bereich:      height 64px, border-bottom 1px solid HSL(215,30%,20%)
```

### KPI-Card (Ernte/Harvest)

```
Border-left: 4px solid harvest (Bernstein)
Hintergrund: harvest-subtle (HSL 38 95% 94%)
Zahl:        font-size 42px, weight 700, color harvest (dunkler Ton)
Label:       font-size 12px, weight 600, uppercase, muted-fg
Trend:       kleiner Pfeil-Indikator + Delta-Prozent
```

---

## 6. ASCII-Wireframe: ListReport-Maske

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ VALEO NeuroERP                                         [?] [Tenant] [JW ▾]    │
│ ─── ▸ Einkauf ▸ Bestellungen                                                   │
├────────┬───────────────────────────────────────────────────────────────────────┤
│        │                                                                        │
│  [≡]   │  Bestellungen                                          [+ Neu]        │
│        │                                                                        │
│  🏠    │  ┌─────────────────────────────────────────────────────────────────┐  │
│  Agrar │  │  Suche...              │ Status ▾ │ Lieferant ▾ │ Zeitraum ▾   │  │
│        │  └─────────────────────────────────────────────────────────────────┘  │
│  📋    │                                                                        │
│  Eink. │  ┌──────┬──────────┬─────────────┬──────────┬────────┬───────────┐   │
│   ▸ BS │  │ BE-Nr│ Datum    │ Lieferant   │ Artikel  │  Menge │ Status    │   │
│   ▸ KT │  ├──────┼──────────┼─────────────┼──────────┼────────┼───────────┤   │
│   ▸ LF │  │10045 │15.05.26  │ Agrarmarkt  │ Weizen   │4.500 t │ ■ Offen   │   │
│        │  │10044 │14.05.26  │ Raiffeisen  │ Gerste   │2.100 t │ ■ Best.   │   │
│  💰    │  │10043 │13.05.26  │ Baywa       │ Raps     │  850 t │ ● Geliefert│  │
│  Fin.  │  │10042 │12.05.26  │ Agrarmarkt  │ Mais     │3.200 t │ ● Geliefert│  │
│        │  │10041 │11.05.26  │ Genoss. NW  │ Weizen   │1.750 t │ ✓ Abgeschl.│  │
│  📊    │  │10040 │10.05.26  │ Raiffeisen  │ Triticale│  420 t │ ✓ Abgeschl.│  │
│  Ctrl. │  │10039 │09.05.26  │ Baywa       │ Gerste   │  960 t │ ✗ Storniert│  │
│        │  │10038 │08.05.26  │ Agrarmarkt  │ Raps     │2.300 t │ ■ Offen   │   │
│  🌾    │  ├──────┴──────────┴─────────────┴──────────┴────────┴───────────┤   │
│  Agrar │  │  Gesamt: 127 Eintraege   [< 1 2 3 ... 13 >]    25 pro Seite ▾  │   │
│        │  └─────────────────────────────────────────────────────────────────┘  │
│  🚛    │                                                                        │
│  Log.  │  Summen: 16.080 t gesamt │ 4 Offen │ 2 Bestaetigt │ 3 Geliefert      │
│        │                                                                        │
└────────┴───────────────────────────────────────────────────────────────────────┘

Legende: ■ Blau (Offen/Bestaetigt)  ● Gruenlich (Geliefert)  ✓ Grau (Abgeschl.)
         Sidebar: 240px Navy-Blue   Content: Off-White   Header: Weiss
```

---

## 7. ASCII-Wireframe: Dashboard / Startseite

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ VALEO NeuroERP 3.0                                      [🔔 3] [JW ▾] [⚙]    │
├────────┬───────────────────────────────────────────────────────────────────────┤
│        │                                                                        │
│  [≡]   │  Guten Morgen, Jochen.  Mittwoch, 18. Mai 2026                       │
│        │                                                                        │
│  🏠    │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ Home   │  │ Ernte 2026  │ │ Offene BE   │ │ Tages-Ums.  │ │ Ø Weizen    │    │
│        │  │             │ │             │ │             │ │             │    │
│  🌾    │  │  4.280 t    │ │    127      │ │  €183.420   │ │ €198,50/t   │    │
│  Agrar │  │  ▲ +12%     │ │  ▼ -3 neu  │ │  ▲ +7%      │ │  ▲ +2,1%   │    │
│        │  │  [amber]    │ │  [blue]     │ │  [blue]     │ │  [amber]    │    │
│  📋    │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │
│  Eink. │                                                                        │
│        │  ┌──────────────────────────┐  ┌──────────────────────────────────┐  │
│  💰    │  │  Ernteerfassung heute    │  │  Offene Aufgaben                 │  │
│  Fin.  │  │  ─────────────────────  │  │  ──────────────────────────────  │  │
│        │  │  07:30  Hof Meier  42t  │  │  [ ] 3 Bestellungen bestaetigen  │  │
│  📊    │  │  08:15  Gut Morell 28t  │  │  [ ] EUDR-Meldung bis 20.05.    │  │
│  Ctrl. │  │  09:00  Fam. Koch  61t  │  │  [ ] Monatsbericht Juni          │  │
│        │  │  10:30  Hof Braun  35t  │  │  [x] Lieferant Baywa angelegt   │  │
│  🚛    │  │  ...    ...         ...  │  │  [ ] Qualitaetspruefung 10044   │  │
│  Log.  │  │             [Alle zeigen]│  │                   [Alle Aufgaben]│  │
│        │  └──────────────────────────┘  └──────────────────────────────────┘  │
│  ⚙     │                                                                        │
│  Admin │  ┌──────────────────────────────────────────────────────────────────┐ │
│        │  │  Preisentwicklung Weizen (CHI)  — letzte 30 Tage                 │ │
│        │  │  220 ┤                                         ╭──╮               │ │
│        │  │  210 ┤                               ╭─────╮  │  │               │ │
│        │  │  200 ┤          ╭──╮          ╭──╮   │     ╰──╯  │               │ │
│        │  │  190 ┤╭─────────╯  ╰──────────╯  ╰───╯           │               │ │
│        │  │  180 ┼┤ Apr 28                              Mai 18│               │ │
│        │  └──────────────────────────────────────────────────────────────────┘ │
└────────┴───────────────────────────────────────────────────────────────────────┘
```

---

## 8. Token-Referenz

Vollstaendige CSS-Token-Datei: `docs/design/meridian-tokens.css`
Deploybare Frontend-Datei: `packages/frontend-web/src/styles/design-tokens-meridian.css`

---

## 9. Vorteile und Nachteile

### Vorteile

- **Zeitlos:** Humanistische Groteskschriften wie Plus Jakarta Sans altern sehr langsam.
  SAP Fiori nutzt seit 2020 72/Fiori Next — aehnliche Philosophie.
- **Zielgruppen-gerecht:** 40-60 Jahre: warmherzige Aesthetik, grosszuegige Abstande,
  hohe Kontraste. Nicht "zu modern" um fremd zu wirken, nicht "zu klassisch" um alt zu wirken.
- **Agrar-Identitaet:** Bernstein-Akzent kommuniziert Ernte und Getreide ohne Klischee.
  Tiefes Ozeanblau: vertrauensvoll, nicht korporativ.
- **WCAG-konform:** Ozean-Blau auf Off-White: 7.1:1 (AAA). Amber auf dunkel: 4.6:1 (AA).
- **Differenzierung:** Kein anderes Agrar-ERP nutzt dieses Farbprofil.
  SAP: Corporate-Blau. Microsoft: Fluent-Blau. Odoo: Violett. VALEO: Ozean + Ernte.
- **Implementierbar in 2-3 Sprints:** Kein Breaking Change. Nur Token-Werte aendern.

### Nachteile

- **Plus Jakarta Sans muss geladen werden:** Erster Page-Load +50-80KB (WOFF2 subset).
  Loesbar: `font-display: swap` + Preload-Link-Tag. Nach erstem Load gecacht.
- **Amber-Akzent braucht Disziplin:** Zu viel Amber = chaotisch. Muss auf <10% der
  UI-Flaeche beschraenkt bleiben. Erfordert klare Nutzungs-Guidelines.
- **Ocean Blue kann kuehl wirken:** Erst in Kombination mit Amber-Akzenten und
  Off-White-Hintergrund entfaltet sich die Waerme. Allein wirkt es aehnlich kalt
  wie das bisherige Blau.
- **Navy-Sidebar:** Benutzer, die helles Sidebar-Theme bevorzugen, koennten unzufrieden sein.
  Loesbar: helles Sidebar-Theme als Option anbieten.

---

## 10. Implementierungsreihenfolge

1. `index.css`: Font-Import + Hintergrund-Token aendern (2h)
2. `design-tokens-meridian.css` importieren als Theme-Override (1h)
3. `button.tsx`, `input.tsx`, `card.tsx`: Radius und Height anpassen (3h)
4. Sidebar: Navy-Blue-Farben, Breiten-Konstanten (4h)
5. Datatable: Row-Heights, Tabular-Nums, Hover-States (4h)
6. Dashboard: KPI-Card mit Amber-Akzent (3h)
7. Vollstaendiger QA-Durchlauf und Kontrast-Check (4h)

**Gesamt: ca. 21 Stunden = 3 Arbeitstage**
