# Design-Konzept 2: TERRA — Agrar-Identitaet trifft Moderne

**Inspiration:** Earthy German Precision + Material Design 3
**Charakter:** Verwurzelt, verlaeesslich, praezise
**Zielgruppe:** Lageristen, Disponenten, Landwirte-Portal-Nutzer (breite Altersgruppe)

---

## 1. Design-DNA

Terra kommuniziert: "Wir verstehen Landwirtschaft." Die Farben kommen aus der Erde:
Waldgruen, Goldgelb, Terrakotta. Die Typografie ist industriell klar (Inter), die
Abstaende sind praezise und respektieren deutsche GmbH-Professionalitaet.

**Leitsatz:** "Entworfen fuer Bodenstaendigkeit. Skaliert fuer Wachstum."

---

## 2. Herkunft der Agrar-Identitaet

Terra speist sich aus fuenf visuellen Quellen des deutschen Landhandels:

1. **Waldgruen (Primaer):** Farbe der Felder und Genossenschafts-Logos (Raiffeisen-Gruen),
   Maschinenfarben (Fendt, Claas). Vertraut fuer jeden Landwirt.
2. **Goldgelb (Akzent):** Reifes Getreide. Universelles Sinnbild der Ernte.
3. **Terrakotta (Sekundaer):** Ackerboden, gepfluegter Lehm. Verbindet mit
   physischer Arbeit.
4. **Warm-Grau (Neutral):** Betonhallen, Lagerhallen, Silo-Beton.
5. **6px-Radius:** Praezise wie ein technisches Zeichenblatt. DIN-Stil.

---

## 3. Typografie

### Schriftfamilie: Inter (Variable Font)

- **Hersteller:** Rasmus Andersson (Google Fonts, SIL OFL)
- **Warum:** Industrieller Standard. Maximum Neutralitaet. Variable Font.
  Tabellarische Ziffern via `cv11 ss01`. Von Linear, Vercel, GitHub verwendet.
- **x-Hoehe:** 0.52 (sehr hoch — exzellente Lesbarkeit bei kleinen Groessen)

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
```

### Typografische Skala (DIN-A-Serie: Faktor sqrt(2) = 1.414)

| Token | px | rem | Verwendung |
|---|---|---|---|
| `--font-size-xs` | 11px | 0.6875rem | Legal, Micro-Labels, Timestamps |
| `--font-size-sm` | 14px | 0.875rem | Table-Body, Sekundaer-Info |
| `--font-size-base` | 16px | 1rem | Standard-Body |
| `--font-size-lg` | 20px | 1.25rem | Card-Titel |
| `--font-size-xl` | 28px | 1.75rem | Seitentitel |
| `--font-size-2xl` | 40px | 2.5rem | Display-Zahlen, KPI |

### Typografie-Regeln Terra

- Headlines: `font-weight: 700` — Autoritaet
- Body: `font-weight: 400`
- Labels: `font-weight: 600`
- Zahlen: `font-feature-settings: "tnum" 1, "cv11" 1` (Inter-spezifisch)
- Deutsche Komposita: `hyphens: auto; lang="de"`
- Fliesstext: `max-width: 70ch`

---

## 4. Farbpalette

### Primaer: Sattes Waldgruen

```
HSL(158, 64%, 28%)  -- #175c40
```

Assoziiert mit Raiffeisen (Genossenschaftsgedanke seit 1849).
Kontrast auf Warm-Grau-Hintergrund: 7.8:1 -- WCAG AAA.

### Akzent: Goldgelb (Getreide)

```
HSL(45, 93%, 47%)   -- #e6ab0b
```

Reifes Getreide, Ernte, Premium-Qualitaet. Funktioniert auch als Warning-Farbe.
Hinweis: Auf weissem Hintergrund Kontrast nur 2.9:1 -- immer mit dunklem Text paaren.

### Sekundaer: Terrakotta (Ackerboden)

```
HSL(15, 75%, 55%)   -- #d4724a
```

Boden, Erdung, Waerme. Fuer Bodenproben-Kategorie, Duengungsmodule.

### Hintergrund: Warm-Grau

```
HSL(40, 15%, 96%)   -- #f4f2ee
```

Subtiler Erdton. Erinnert an Lagerpapier und Lieferschein-Papier.

### Vollstaendige Semantik-Palette

```
Oberflaechenhierarchie:
  --background:       40  15% 96%
  --surface:          40  20% 99%
  --surface-raised:   40  25% 100%
  --surface-sunken:   40  12% 92%

Primaer-System (Waldgruen):
  --primary:          158 64% 28%
  --primary-hover:    158 64% 22%
  --primary-active:   158 64% 18%
  --primary-subtle:   158 64% 92%
  --primary-fg:       0   0%  100%
  --primary-muted:    158 40% 50%

Harvest-Akzent (Goldgelb):
  --harvest:          45  93% 47%
  --harvest-hover:    45  93% 38%
  --harvest-subtle:   45  93% 92%
  --harvest-fg:       45  93% 15%
  --harvest-on-dark:  45  93% 65%

Terrakotta-Sekundaer:
  --terra:            15  75% 55%
  --terra-hover:      15  75% 45%
  --terra-subtle:     15  75% 93%
  --terra-fg:         15  75% 18%

Warm-Neutrals:
  --gray-50:          40  15% 96%
  --gray-100:         40  12% 92%
  --gray-200:         40  10% 86%
  --gray-300:         40   8% 76%
  --gray-400:         40   6% 62%
  --gray-500:         40   5% 48%
  --gray-600:         40   5% 36%
  --gray-700:         40   6% 25%
  --gray-800:         40   8% 16%
  --gray-900:         40  10% 10%

Semantik:
  --success:          158 64% 28%
  --warning:          45  93% 47%
  --error:            0   70% 48%
  --info:             210 70% 45%

Text:
  --foreground:       40  10% 12%
  --muted-fg:         40   6% 46%
  --placeholder:      40   5% 60%
  --border:           40  10% 88%
  --border-focus:     158 64% 28%
```

---

## 5. Abstands- und Groessen-System

### Spacing-Skala (strikt 8px-Basis, linear)

Terra setzt auf ein streng lineares 8px-Grid -- professionell, vorhersehbar,
DIN-nah. Klare Entwickler-Vorhersagbarkeit.

```
--space-1:   8px   (xs)
--space-2:  16px   (sm)
--space-3:  24px   (md)
--space-4:  32px   (lg)
--space-5:  48px   (xl)
--space-6:  64px   (2xl)
```

### Layout-Konstanten

```
--sidebar-expanded:   256px
--sidebar-collapsed:   56px
--content-max:       1440px
--content-padding:     32px
--header-height:       60px
--toolbar-height:      52px
--table-row-height:    48px
--table-row-compact:   36px
```

### Border-Radius

```
--radius-xs:   2px
--radius-sm:   4px
--radius:      6px    (Terra-Standard -- praezise, professionell)
--radius-lg:   8px
--radius-xl:  12px
--radius-full: 9999px
```

---

## 6. Komponenten-Beschreibungen

### Button (Primaer)

```
height:  44px
Padding: 0 18px
Radius:  6px
Font:    Inter 14px, weight 600
Farbe:   bg=primary, text=white
Hover:   bg=primary-hover, scale(1.01)
Active:  bg=primary-active, scale(0.99)
Focus:   2px ring primary, offset 2px
```

Tailwind:
```
h-11 px-[18px] rounded-[6px] bg-primary text-white
font-semibold text-sm tracking-tight
hover:bg-primary/90 hover:scale-[1.01]
active:scale-[0.99]
focus-visible:outline-none focus-visible:ring-2
focus-visible:ring-primary focus-visible:ring-offset-2
transition-all duration-[120ms]
```

### Card

```
Hintergrund: surface (fast weiss)
Border:      1px solid border (warm-gray)
Radius:      6px
Padding:     24px
Shadow:      keiner -- Terra ist ehrlich, nicht "elevated"
Hover:       border-color = primary (Waldgruen)
```

### Status-Badge (Agrar-spezifisch)

```
Waldgruen:   bg=primary-subtle, text=primary     --> "Aktiv"
Goldgelb:    bg=harvest-subtle, text=harvest-fg  --> "In Ernte"
Terrakotta:  bg=terra-subtle, text=terra-fg      --> "Pruefung"
Grau:        bg=gray-100, text=gray-600          --> "Archiviert"
Rot:         bg=red-50, text=red-700             --> "Fehler"
```

### Qualitaets-Check-Panel (Terra-Original)

```
+---------------------------------------------+
|  Qualitaetspruefung  Probe #4721             |
|  -------------------------------------------  |
|  Feuchte          14.2 %   [====-----]  OK   |
|  Protein          12.8 %   [=====----]  Gut  |
|  Fallzahl          312 s   [=========]  Sehr |
|  Verunreinigung    1.2 %   [====-----]  OK   |
|  Spez. Gewicht    782 g/l  [=====----]  Gut  |
|                                               |
|  Gesamtbewertung:  [======---]  62 Pkt.      |
|  Einstufung: [ Brot-Weizen E ]               |
|                                               |
|  [Probe speichern]    [Neu messen]           |
+---------------------------------------------+

Balken-Farben: Waldgruen=Gut, Goldgelb=Mittel, Terrakotta=Maessig, Rot=Kritisch
```

### Sidebar (Terra)

```
Hintergrund:   HSL(158, 45%, 15%)   -- Sehr dunkles Waldgruen
Akzent-Stripe: 3px Goldgelb links am aktiven Item
Text normal:   HSL(40, 10%, 70%)    -- Warm-Grau
Text aktiv:    HSL(45, 93%, 75%)    -- Helles Gold
Hover:         HSL(158, 45%, 20%)
```

---

## 7. ASCII-Wireframe: Ernte-Annahme-Maske

```
+--------------------------------------------------------------------------------+
|  VALEO NeuroERP         > Agrar > Ernte-Annahme                [JW v] [Einst] |
+--------+-----------------------------------------------------------------------+
|        |                                                                        |
|  [=]   |  Ernte-Annahme 2026                         [Neue Annahme +]          |
|        |                                                                        |
| [Home] |  +---------------------------------------------------------------------+
|        |  | Suche nach Hof, Fahrer, Schein...  | Sorte v | Datum v |  [X Clear]|
| [Agrar]|  +---------------------------------------------------------------------+
|  EA  > |                                                                        |
|  KTR > |  +--------+------------+--------------+----------+-------+------------+|
|  FB  > |  | Schein | Eingang    | Betrieb      | Sorte    |Brutto | Status     ||
|  PSM > |  +--------+------------+--------------+----------+-------+------------+|
|        |  |  24091 | 10:42 Uhr  | Hof Meier    | A-Weizen | 42.8t | [Annahme] ||
| [Lager]|  |  24090 | 09:15 Uhr  | Gut Morell   | B-Gerste | 28.1t | [Annahme] ||
|        |  |  24089 | gestern    | Fam. Koch    | A-Weizen | 61.0t | [Abgechn.] ||
| [Fin.] |  |  24088 | gestern    | Hof Braun    | Raps     | 35.4t | [Abgechn.] ||
|        |  |  24087 | 17.05.     | Agrar-Gem.   | Triticale| 19.2t | [Pruefung] ||
| [Ctrl] |  +--------+------------+--------------+----------+-------+------------+|
|        |  |  47 Eintraege diese Saison                     Gesamt: 4.280 t     ||
|        |  +---------------------------------------------------------------------+|
|        |                                                                        |
|        |  Saison:  Weizen 2.840t | Gerste 820t | Raps 620t                    |
|        |  Silos:   Silo 1: 78% [=======--]  Silo 2: 45% [====----]            |
+--------+-----------------------------------------------------------------------+
```

---

## 8. ASCII-Wireframe: Dashboard

```
+--------------------------------------------------------------------------------+
|  VALEO NeuroERP 3.0   Ernte-Saison 2026                [Bell] [JW v]          |
+--------+-----------------------------------------------------------------------+
|        |                                                                        |
|  [=]   |  Ernte-Cockpit -- Mittwoch, 18. Mai 2026                              |
|        |                                                                        |
| [Home] |  +--------------+ +--------------+ +--------------+ +-------------+  |
|        |  | ERNTE 2026   | | OFFENE ANH.  | | KONTRAKTE    | | EIS-PREIS   |  |
| [Agrar]|  |              | |              | |              | |             |  |
|  EA  > |  |  4.280 t     | |  127 Stk     | |  83 % erf.  | | 198,50 E/t  |  |
|  KTR > |  | [=====---]   | |  8 neu heute | | [======--]  | | + 2,1 %     |  |
|        |  | Ziel: 6.500t | |              | | 4.280/5.160t| | + Bonus      |  |
| [Lager]|  +--------------+ +--------------+ +--------------+ +-------------+  |
|        |                                                                        |
| [Fin.] |  +-------------------------------+ +-------------------------------+  |
|        |  | Silostand heute               | | Anlieferungen heute           |  |
| [Ctrl] |  | Silo 1  [=======--] 78 %      | | 07:30  Hof Meier    42,8 t   |  |
|        |  | Silo 2  [====-----] 45 %      | | 08:15  Gut Morell   28,1 t   |  |
| [Log.] |  | Silo 3  [======---] 62 %      | | 09:00  Fam. Koch    61,0 t   |  |
|        |  | Silo 4  [==-------] 23 %      | | 11:15  (erwartet)             |  |
|        |  | Gesamt: 1.920 t / 3.200 t     | | 12:00  Gut Steinberg 55,0 t  |  |
|        |  | [Alle Silos]                  | | [Vollstaendiger Plan]         |  |
|        |  +-------------------------------+ +-------------------------------+  |
+--------+-----------------------------------------------------------------------+
```

---

## 9. Vorteile und Nachteile

### Vorteile

- **Maximale Agrar-Identitaet:** Kein anderes Agrar-ERP nutzt Waldgruen als Primary.
  Raiffeisen-Assoziationskette erzeugt sofortiges Vertrauen bei der Zielgruppe.
- **Inter ist der bewiesene Standard:** Nullrisiko. Alle modernen Enterprise-Tools
  nutzen Inter. Keine Lizenzfragen, beste Browser-Optimierung.
- **Robust fuer Aussenbedingungen:** Waldgruen + Goldgelb haben hohe Unterscheidbarkeit.
  Funktioniert auf Tablets im Sonnenlicht, auf alten Monitoren im Lager.
- **Deutsche GmbH-Aesthetik:** 6px-Radius + strikte 8px-Skala wirkt ernst.
  Passend zur Genossenschaftskultur.
- **Terrakotta gibt Tiefe:** Dritte Farbe ohne Chaos, inhaltlich passend.

### Nachteile

- **Waldgruen kann dunkel wirken:** Bei niedrigen Bildschirm-Helligkeiten sorgfaeltige
  Kontrastpruefung noetig.
- **Drei Farben erfordern Disziplin:** Zu viele Farben auf einer Seite = visueller Laerm.
  Klare Nutzungsregeln benoetigt.
- **Weniger zeitlos als Meridian:** Erdtoene sind 2024-2026 im Trend. Konsequente
  Umsetzung notwenig fuer Langzeit-Tragfaehigkeit.
- **Goldgelb nicht fuer kleine Texte:** Schlechter Kontrast auf weissem Hintergrund.

---

## 10. Implementierungsreihenfolge

1. `index.css`: Inter-Import + Warm-Grau Hintergrund (2h)
2. `design-tokens-terra.css` importieren (1h)
3. Primary-Farbe auf Waldgruen: Button, Badge, Link (3h)
4. Sidebar: Dunkelgruen mit Gold-Akzent-Stripe (4h)
5. KPI-Cards mit Goldgelb-Akzent (4h)
6. Terrakotta fuer Bodenproben/Duengung-Modul (3h)
7. DataTable: Tabular-Nums, Row-Heights, Hover-States (3h)
8. Kontrast-Audit aller Farbkombinationen (4h)

**Gesamt: ca. 24 Stunden = 3 Arbeitstage**
