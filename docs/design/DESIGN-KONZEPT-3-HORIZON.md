# Design-Konzept 3: HORIZON — Zukunft des Enterprise-UI

**Inspiration:** Microsoft Fluent 2 + Linear.app + Vercel Dashboard
**Charakter:** Premium, fokussiert, digital-nativ — das ERP der naechsten Generation
**Zielgruppe:** Controlling-Analysten, IT-Administratoren, Fuehrungskraefte (digital-affin)

---

## 1. Design-DNA

Horizon fragt: "Wie wuerde VALEO aussehen, wenn es heute von Grund auf neu gebaut wuerde?"
Die Antwort: Dunkler Standard, minimale Ablenkung, glasklare Hierarchien. Denken wie
Linear, skalieren wie SAP, kommunizieren wie Apple. Fuer ERP-Nutzer, die aus
privaten Premium-Apps (Notion, Linear, Vercel) hohe Qualitaetsansprueche mitbringen.

**Leitsatz:** "Weniger sehen. Mehr verstehen. Schneller handeln."

---

## 2. Wann passt Horizon?

Horizon passt wenn:
- Die Zielgruppe digital-affin ist und helle ERP-UIs als altmodisch empfindet
- Das Produkt im direkten Wettbewerb zu "coolen" SaaS-Produkten steht
- Controlling, Analytics und Dashboard-Arbeit im Vordergrund stehen
- Der Markenauftritt von VALEO "Technologie-First" kommunizieren soll
- Junges Management (unter 40) die Hauptzielgruppe ist

Horizon passt NICHT gut wenn:
- Aeltere Nutzer (55+) in schlechten Lichtverhältnissen (Lager, Scheune) arbeiten
- WCAG-Compliance fuer oeffentliche Verwaltung zwingend ist
- Die Genossenschafts-Identitaet im Vordergrund steht

---

## 3. Typografie

### Schriftfamilie: DM Sans (mit Geist als Wunsch-Alternative)

**Primaere Wahl: DM Sans** (Google Fonts, kostenlos)
- Humanistisches Groteskschrift, geometrische Grundformen
- Wirkt modern ohne kalt zu sein
- Ausgezeichnet fuer Dark Mode (hohe x-Hoehe)
- Variable Font verfuegbar

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
```

**Ideale Alternative: Geist** (Vercel, Open Source)
```css
/* npm i geist */
@import 'geist/dist/fonts/geist-sans/style.css';
```

### Typografische Skala (Fluid, auf Dark Mode optimiert)

| Token | px | rem | Verwendung |
|---|---|---|---|
| `--font-size-xs` | 11px | 0.6875rem | Keyboard Hints, Meta-Labels |
| `--font-size-sm` | 13px | 0.8125rem | Table-Body, Sekundaer (leicht kleiner) |
| `--font-size-base` | 15px | 0.9375rem | Standard-Body (leicht kleiner fuer Dense-UI) |
| `--font-size-lg` | 18px | 1.125rem | Section-Ueberschriften |
| `--font-size-xl` | 24px | 1.5rem | Page-Titel |
| `--font-size-2xl` | 36px | 2.25rem | KPI-Werte, Hero-Zahlen |

Dark Mode nutzt leicht kleinere Font-Groessen, weil helle Schrift auf dunklem Grund
optisch groesser wirkt als dunkle auf hellem.

---

## 4. Farbpalette

### Primaer: Near-Black mit Violett-Tint

```
HSL(250, 20%, 15%)  -- #1c1a2e  (Dark Mode Hintergrund)
HSL(250, 15%, 11%)  -- #15131e  (Tiefstes Dunkel)
```

### Akzent: Electric Blue

```
HSL(220, 100%, 60%) -- #3b82f6
```

Digital-nativ. Hoch-Energie. Auf dunklem Hintergrund exzellenter Kontrast.
Bekannt aus Tailwind `blue-500` -- aber hier als bewusste Entscheidung, nicht Default.

### Oberflaechenfarben (Glasmorphism-Schichten)

```
--surface-1: HSL(250, 18%, 11%)   (Seiten-Hintergrund)
--surface-2: HSL(250, 16%, 14%)   (Cards, Panels)
--surface-3: HSL(250, 14%, 18%)   (Hover-States, Sub-Panels)
--surface-4: HSL(250, 12%, 22%)   (Aktiv-States, Inputs)
```

### Glazed White (Hell-Modus Text und Akzente)

```
HSL(0, 0%, 99%)    -- Primaertext auf dunkel
HSL(0, 0%, 70%)    -- Sekundaertext (muted)
HSL(0, 0%, 45%)    -- Tertiaertext (sehr muted)
HSL(0, 0%, 25%)    -- Rahmen/Trennlinien auf dunkel
```

### Light Mode (optionale Variante)

```
--background-light: HSL(0, 0%, 99%)    (Glazed White)
--surface-light:    HSL(0, 0%, 97%)
--foreground-light: HSL(250, 20%, 12%)
```

### Vollstaendige Token-Palette

```
Dark Mode (Standard):
  --background:       250 20% 11%
  --surface:          250 18% 14%
  --surface-hover:    250 16% 17%
  --surface-active:   250 14% 20%
  --border:           250 15% 22%
  --border-subtle:    250 15% 18%

  --primary:          220 100% 60%     (Electric Blue)
  --primary-hover:    220 100% 55%
  --primary-active:   220 100% 50%
  --primary-subtle:   220 100% 15%     (Dunkel-Blau fuer Badges auf dunkel)
  --primary-fg:       0   0%  100%

  --foreground:       0   0%  97%      (Weisslicher Text)
  --muted-fg:         250 8%  62%      (Gedaempft)
  --placeholder:      250 6%  45%

  --success:          142 70% 45%      (Leuchtendes Gruen auf dunkel)
  --warning:          38  95% 60%      (Amber, heller als in Light-Mode)
  --error:            0   80% 60%      (Leuchtrot)
  --info:             220 100% 60%     (= Primary)

Glassmorphism-Overlays:
  --glass-bg:         rgba(255, 255, 255, 0.04)
  --glass-border:     rgba(255, 255, 255, 0.08)
  --glass-hover:      rgba(255, 255, 255, 0.06)
  --glass-backdrop:   blur(12px) saturate(180%)
```

---

## 5. Glassmorphism-Effekte

Horizon nutzt Glasmorphism sparsam und gezielt. Nicht fuer normale Cards, sondern:
- Modale Fenster (frosted overlay)
- Command-Palette (Linear-Stil)
- AI-Copilot-Panel
- Floating Toolbars
- Toast-Benachrichtigungen

### Glassmorphism CSS-Muster

```css
.glass-panel {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-radius: 16px;
}

.glass-modal-overlay {
  background: rgba(15, 14, 20, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.glass-toast {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.10);
  backdrop-filter: blur(16px);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.3),
    0 10px 15px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.glass-command-palette {
  background: rgba(22, 20, 34, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(20px) saturate(200%);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.05),
    0 20px 40px rgba(0, 0, 0, 0.6);
}
```

---

## 6. Abstands- und Groessen-System

### Dreistufiges Spacing-System

```
Atomic (4px):   Fuer feinste Justierungen, Icon-Gaps
  --space-0: 4px

Semantic (8px-Basis):  Standard-Layout
  --space-1:  8px
  --space-2: 12px    (8 + 4)
  --space-3: 16px    (2 x 8)
  --space-4: 24px    (3 x 8)
  --space-5: 32px    (4 x 8)

Structural (16px-Basis):  Grosse Layouts
  --space-6:  48px
  --space-7:  64px
  --space-8:  96px
```

### Layout-Konstanten

```
--sidebar-default:    48px    (Icons-Only, kompakter Default)
--sidebar-expanded:  220px    (Text + Icons, expandiert)
--content-max:      1440px
--content-padding:    24px    (etwas weniger als Meridian -- dichtere Nutzung)
--header-height:      52px    (schlanker als Meridian)
--toolbar-height:     48px
--table-row-height:   44px    (kompakter fuer Analytics)
--table-row-compact:  36px
```

### Border-Radius

```
--radius-sm:   6px
--radius:     16px    (Horizon-Standard: weich und modern)
--radius-lg:  20px
--radius-xl:  24px
--radius-full: 9999px
```

---

## 7. Komponenten-Beschreibungen

### Button (Primaer)

```
height:  44px
Padding: 0 16px
Radius:  16px (sehr rund -- moderner Charakter)
Font:    DM Sans 14px, weight 600, letter-spacing -0.01em
Farbe:   bg=primary, text=white
Hover:   bg=primary-hover, glow-Effekt
Active:  scale(0.97)
Focus:   ring 2px primary, offset 2px
Glow:    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25)
```

Tailwind:
```
h-11 px-4 rounded-2xl bg-primary text-white
font-semibold text-sm tracking-tight
hover:bg-primary/90 hover:shadow-[0_0_0_3px_rgba(59,130,246,0.25)]
active:scale-[0.97]
focus-visible:outline-none focus-visible:ring-2
focus-visible:ring-primary focus-visible:ring-offset-2
transition-all duration-150
```

### Card (Dark Mode Standard)

```
Hintergrund: surface (HSL 250 18% 14%)
Border:      1px solid rgba(255,255,255,0.06)
Radius:      16px
Padding:     20px
Shadow:      0 4px 6px rgba(0,0,0,0.3)
Hover:       border-color = rgba(255,255,255,0.12)
             shadow: 0 8px 24px rgba(0,0,0,0.4)
```

### Sidebar (Horizon -- Icons-Only Default)

```
Standard:    48px breit -- nur Icons, keine Labels
Expanded:   220px breit -- Icons + Labels
Hintergrund: HSL(250, 20%, 9%)   (noch dunkler als Cards)
Icons:       24px, Farbe: muted-fg
Aktiv-Icon:  Farbe: primary, bg: primary-subtle, radius 10px
Hover:       bg: surface-hover
Toggle:      unten am Rand, Pfeil-Icon
```

### Command Palette (Horizon-Highlight)

```
Aufruf: Cmd+K / Ctrl+K
Overlay: frosted-glass-modal-overlay
Panel:   glass-command-palette, 640px breit, zentriert
Input:   grosses Input-Feld oben, 18px Font
Results: Liste mit Icons + Titel + Category-Badge
Shortcut-Hints: rechts an jedem Item
Animation: scale(0.96) -> scale(1), opacity 0 -> 1, 150ms
```

### Status-Indikatoren (Horizon-Stil)

```
Aktiv/Gruen:   bg: rgba(34,197,94,0.15),  text: #4ade80  border: rgba(34,197,94,0.3)
Warnung/Amber: bg: rgba(251,191,36,0.15), text: #fbbf24  border: rgba(251,191,36,0.3)
Fehler/Rot:    bg: rgba(248,113,113,0.15),text: #f87171  border: rgba(248,113,113,0.3)
Info/Blau:     bg: rgba(59,130,246,0.15), text: #60a5fa  border: rgba(59,130,246,0.3)
```

---

## 8. ASCII-Wireframe: Prozess-Monitoring (Dark Mode)

```
+================================================================================+
#  [V]                              VALEO NeuroERP                [P] [W] [JW] #
+====+===========================================================================+
#    #                                                                            #
# [H]#  Prozess-Monitoring -- Live                     [Auto-Refresh: 30s] [x]  #
#    #                                                                            #
# [A]#  +-----------+ +-----------+ +-----------+ +-----------+                  #
# [E]#  | [bullet]  | | [bullet]  | | [bullet]  | | [bullet]  |                  #
# [B]#  | ERNTE-SYS | | EINKAUF   | | FINANZEN  | | COMPLIANCE|                  #
# [F]#  | Aktiv     | | 3 offen   | | OK        | | 1 Aktion  |                  #
#    #  | 99.9 %    | | 127 BE    | | Perioden  | | EUDR-Due  |                  #
# [L]#  +-----------+ +-----------+ +-----------+ +-----------+                  #
#    #                                                                            #
# [C]#  +--------------------------------------+ +-----------------------------+ #
#    #  | Aktivitaets-Feed                     | | AI-Copilot                  | #
# [D]#  | ------------------------------------ | | --------------------------- | #
#    #  | 10:43  BE #10045 bestaetigt     [->] | | Guten Morgen. Heute 3       | #
#    #  | 10:41  Ernte-Probe #4721 OK     [->] | | Aufgaben priorisiert:       | #
#    #  | 10:38  Silo 3: 62% erreicht    [!]  | |                             | #
#    #  | 10:35  Lieferant Baywa aktiv   [OK] | | 1. EUDR-Meldung bis Mo.    | #
#    #  | 10:29  Neue Annahme: Hof Meier [->] | | 2. 127 Bestellungen pruefen| #
#    #  | 10:22  Journal-Import OK       [OK] | | 3. Silo 4: Kapazitaet      | #
#    #  | ...                                 | |    fast erschoepft          | #
#    #  |                     [Alle zeigen]   | |                             | #
#    #  +--------------------------------------+ | Befehl eingeben... [Cmd+K] | #
#    #                                          +-----------------------------+ #
+====+===========================================================================+
# Sidebar: Icons-Only (48px), Hintergrund sehr dunkel, Aktiv-Icon Electric Blue  #
# Cards: Dunkle Oberflaehen, subtile weisse Borders                               #
# Feed-Icons: Farbige Status-Punkte (Gruen/Amber/Blau)                            #
# AI-Panel: Glassmorphism-Effekt, leicht heller als Hintergrund                   #
#=================================================================================#
```

---

## 9. ASCII-Wireframe: ListReport (Horizon, Dark)

```
+================================================================================+
#  [V]                    VALEO                         [Search: Ctrl+K] [JW]  #
+====+===========================================================================+
#    #                                                                            #
# [H]#  Bestellungen            [+ Neu]                               [Filter]   #
#    #                                                                            #
# [A]#  Alle (127) | Offen (4) | Bestaetigt (12) | Abgeschlossen (111)           #
# [E]#  ___________________________________________________________              #
# [B]#                                                                            #
# [F]#  +--------+------------+-------------+---------+-------+----------------+ #
#    #  | BE-Nr  | Datum      | Lieferant   | Artikel | Menge | Status         | #
#    #  +--------+------------+-------------+---------+-------+----------------+ #
# [L]#  | 10045  | 15.05.26   | Agrarmarkt  | Weizen  | 4.500t| [Offen]        | #
#    #  | 10044  | 14.05.26   | Raiffeisen  | Gerste  | 2.100t| [Offen]        | #
# [C]#  | 10043  | 13.05.26   | Baywa       | Raps    |   850t| [Bestaetigt]   | #
#    #  | 10042  | 12.05.26   | Agrarmarkt  | Mais    | 3.200t| [Bestaetigt]   | #
# [D]#  | 10041  | 11.05.26   | Genoss. NW  | Weizen  | 1.750t| [Geliefert]   | #
#    #  +--------+------------+-------------+---------+-------+----------------+ #
#    #                                                                            #
#    #  Seite 1 von 13    [< Zurueck]  1 2 3 ... 13  [Weiter >]    25 / Seite  #
+====+===========================================================================+
# Sidebar: 48px, Icons only, sehr dunkel                                          #
# Header: Dunkel, Tab-Navigation mit aktivem blauen Unterstrich                   #
# Tabelle: Dunkle Rows, subtile Border, Hover = leicht heller                     #
# Status-Badges: Transparente Hintergruende, gluehende Farben                     #
# Keyboard-Hint: [N] Neu  [/] Suche  immer sichtbar rechts-unten                 #
#=================================================================================#
```

---

## 10. Motion-Design

Horizon nutzt Animationen gezielt:

```css
/* Standard-Uebergang */
transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);

/* Spring-Animation fuer Dialoge */
@keyframes dialog-in {
  from { opacity: 0; transform: scale(0.95) translateY(-8px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}
animation: dialog-in 200ms cubic-bezier(0.34, 1.56, 0.64, 1);

/* Sidebar-Expand */
transition: width 250ms cubic-bezier(0.4, 0, 0.2, 1);

/* Card-Hover-Glow */
transition: box-shadow 200ms ease, border-color 200ms ease;
```

---

## 11. Vorteile und Nachteile

### Vorteile

- **Hoechste Modernitaet:** Linear, Vercel, Notion -- alle grossen modernen Tools
  nutzen dunkle Themes als primären Modus. VALEO positioniert sich als Technologie-Leader.
- **Fokus-Foerderung:** Dunkle Hintergründe reduzieren visuelle Ablenkung.
  Zahlen und Status-Farben stehen sofort im Vordergrund.
- **Exzellent fuer Analytics:** Daten-Visualisierungen und Charts wirken auf dunklem
  Hintergrund intensiver und wirkungsvoller.
- **Glassmorphism:** Modernes visuelles Statement. Unterscheidet VALEO von SAP
  und Microsoft nahezu vollstaendig.
- **Keyboard-First:** Command-Palette (Cmd+K), Keyboard-Shortcuts -- Horizon wird
  von Power-Usern geliebt.

### Nachteile

- **Falsche Zielgruppe fuer VALEO-Kern:** Der typische Lagerist (55+) in der
  Genossenschaft ist NICHT die Zielgruppe von Horizon. Dark Mode ist fuer diese
  Gruppe oft unklar und unbequem.
- **Hoechster Implementierungsaufwand:** Dark Mode als primäres Theme erfordert
  vollstaendige Ueberpruefung aller Komponenten, Icons, Charts, PDFs.
- **Glassmorphism: Performance-Risiko:** `backdrop-filter: blur()` ist GPU-intensiv.
  Auf alten Lager-PCs (Core i5 2015, integrierte Grafik) koennte es laggen.
- **Nicht fuer Aussenbereich:** Im Sonnenlicht ist ein dunkles Theme fast unlesbar.
  Aussendienstmitarbeiter und Lageristen mit Tablets sind benachteiligt.
- **PDF-Export-Problem:** Ausdrucke von dunklen Screens sehen auf Papier schlecht aus.
  Lieferscheine, Rechnungen -- alles muesste separates Print-CSS haben.

---

## 12. Empfehlung fuer Horizon

Horizon sollte NICHT das Default-Theme von VALEO sein, aber als optionales
"Pro Dark Mode"-Theme angeboten werden. Power-User (Controlling-Analysten,
IT-Administratoren, Entwickler) wuerden es lieben.

**Optimales Vorgehen:**
1. Meridian oder Terra als Default-Theme (helle Modus)
2. Horizon als optional aktivierbares Dark-Mode-Theme in den Benutzer-Einstellungen
3. Gleiche Design-Token-Struktur -- nur die Token-Werte wechseln

---

## 13. Implementierungsreihenfolge

1. Dark-Mode-Token-Schicht auf Meridian-Basis aufsetzen (4h)
2. Sidebar: Icons-Only-Variante mit Expand-Toggle (6h)
3. Glassmorphism-CSS-Klassen definieren und testen (4h)
4. Command-Palette-Komponente (Cmd+K) (8h)
5. Status-Badge-Varianten fuer Dark Mode (2h)
6. Chart-Bibliothek auf Dark-Colors umstellen (4h)
7. Print-CSS fuer alle Masken (separate Aufgabe, kritisch) (8h)
8. Performance-Test auf schwacher Hardware (2h)

**Gesamt: ca. 38 Stunden = 5 Arbeitstage**
