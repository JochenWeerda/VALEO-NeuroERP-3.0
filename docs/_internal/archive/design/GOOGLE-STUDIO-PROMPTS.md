# Google Studio / AI Image Generation Prompts
## VALEO NeuroERP 3.0 — Design-Visualisierungen

> Diese Prompts erzeugen hochwertige UI-Mockup-Visualisierungen für Präsentationen,
> Stakeholder-Reviews und Design-Pitches. Optimiert für Google ImageFX, Midjourney,
> Stable Diffusion (SDXL) und DALL·E 3.

---

## Konzept 1: MERIDIAN

### Prompt 1A — Dashboard-Übersicht
```
Ultra-realistic UI mockup screenshot of a modern enterprise ERP dashboard called
"VALEO NeuroERP", professional agricultural management software. Design language:
Linear.app meets Apple HIG. Color palette: deep ocean blue (#0d5aa7) primary,
harvest amber (#f5a623) accent, off-white (#f5f8fc) background. Dark navy blue
sidebar (240px) on the left with white icons. Top bar with breadcrumb navigation.
Main content area showing 4 KPI cards with large numbers (Ernte 4.280t, Umsatz
€183.420, Offene BE 127, Ø Weizen €198,50). Below: two panels - left shows
"Ernteerfassung" list with timestamps, right shows a simple line chart
"Preisentwicklung". Typography: Plus Jakarta Sans. Border radius 12px on all cards.
Clean minimal shadows. German language UI labels. 1440x900px resolution, 2x retina,
no device frame.
```

### Prompt 1B — DataTable / Bestellübersicht
```
Professional ERP data table interface screenshot, agricultural software "VALEO
NeuroERP". Ocean blue and amber color scheme. Dark navy sidebar visible on left edge.
Main content: filterable list "Bestellungen" (purchase orders). Table with columns:
BE-Nr, Datum, Lieferant, Artikel, Menge, Status. Status badges: colored pills
(blue=Offen, green=Geliefert, gray=Abgeschlossen). Table header in light gray with
small uppercase labels. Row height 40px, hover state visible on one row in soft blue.
Top toolbar with search field and filter dropdowns. "+ Neu" primary button in ocean
blue top right. Font: Plus Jakarta Sans 14px. German labels. Clean white background,
1-pixel dividers between rows. 1440x900px screenshot, 2x retina quality.
```

### Prompt 1C — ObjectPage Kontrakt-Detail
```
Enterprise ERP detail view, agricultural contract management screen "VALEO NeuroERP".
Left: dark navy sidebar with navigation items and icons. Main area: Contract detail
page "KT-2026-00089" with header showing contract number, supplier name, quantity
and status badge "Bestätigt" in green. Below header: horizontal tab navigation
(Stammdaten, Positionen, Lieferungen, Dokumente, Historie). Content area split
61.8%/38.2% golden ratio: left side shows form fields (Vertragspartner, Konditionen),
right side shows delivery progress bar with harvest amber fill. Ocean blue (#0d5aa7)
as primary color, Plus Jakarta Sans typography, 12px border radius cards, professional
German-language agricultural ERP interface. 1440x900px, ultra HD, no chrome/browser.
```

---

## Konzept 2: TERRA

### Prompt 2A — Dashboard mit Agrar-Identität
```
Modern agricultural ERP dashboard "VALEO NeuroERP", Terra design concept. Color
palette: forest green primary (#166534), warm amber accent (#f59e0b), warm sand
white (#fafaf9) background. Light white sidebar on left with green active states.
KPI cards with left colored border accents (green for quantities, amber for harvest
metrics). Dashboard showing German agricultural cooperative data: grain harvest
tonnage, open purchase orders, daily turnover. Organic, earthy aesthetic — not
corporate. Typography: Plus Jakarta Sans. Cards with 10px border radius, warm gray
shadows. Progress bar showing harvest completion in forest green. German UI labels.
Feels like it belongs in a grain trading office. 1440x900px, photorealistic UI.
```

### Prompt 2B — Mobile Warehouse Terminal
```
Mobile tablet UI for warehouse operations, VALEO NeuroERP Terra theme. Large touch-
optimized buttons (48px minimum), forest green primary color, harvest amber for
warnings. Screen shows "Einlagerung" (storage) workflow: camera barcode scanner
button prominent, large quantity input with +/- buttons, storage location selector
with color-coded status. High contrast design for use in dusty warehouse environment.
German labels. Organic warm color palette. iPad Pro 12.9" size, landscape orientation,
no device chrome. Ultra realistic screenshot.
```

---

## Konzept 3: HORIZON

### Prompt 3A — Analytics Dashboard
```
Futuristic yet professional ERP analytics dashboard "VALEO NeuroERP", Horizon design
concept. Color palette: indigo (#4f46e5) primary, cyan (#0891b2) charts accent,
pure white cards on light gray (#f3f4f6) page background. Cards appear to float
with subtle shadows — elevation through contrast, not color. Semi-transparent dark
sidebar with backdrop blur effect. Multiple chart types visible: line chart for
price development, bar chart for delivery volumes, donut chart for contract status.
Density toggle in toolbar (Kompakt/Standard/Komfortabel). Modern, Stripe-dashboard-
like quality. German agricultural data labels. Plus Jakarta Sans typography.
1440x900px, premium UI screenshot quality.
```

### Prompt 3B — Command Palette / Suche
```
Enterprise software command palette overlay "VALEO NeuroERP", Horizon concept.
Semi-transparent dark background with blur behind a centered search modal. Modal:
white, 680px wide, rounded corners 16px, prominent search field with "⌘K" badge.
Below search: recent items list with icons (Kontrakt, Bestellung, Rechnung),
quick actions section, keyboard shortcuts shown. Indigo (#4f46e5) as accent color
for highlighted items. Clean, linear.app-inspired. German labels. The underlying
dashboard is blurred but visible — shows agricultural ERP context. 1440x900px.
```

---

## Allgemeine Prompts (konzept-unabhängig)

### Prompt G1 — Brand/Splash Screen
```
Premium enterprise software splash screen / loading screen for "VALEO NeuroERP 3.0".
Centered layout with company logo (abstract V shape in gradient from ocean blue to
harvest amber). Tagline below: "Ihr Agrar-ERP der Zukunft". Background: deep
gradient from navy blue (#0f1e2e) to dark teal. Subtle animated grain texture overlay
(static version). Professional, trustworthy, German agricultural software aesthetic.
16:9 format, 1920x1080px, cinematic quality.
```

### Prompt G2 — Team / Onboarding
```
Modern enterprise software onboarding screen, agricultural ERP. Shows "Willkommen,
Jochen" personalized greeting with user avatar. Clean card-based layout showing
module quick-access tiles: Agrar, Einkauf, Finanzen, Lager with meaningful icons.
Ocean blue primary color, harvest amber highlights. Large readable typography,
German labels. Spacious padding, card-based layout on white background. Feels
premium and welcoming — not generic. 1440x900px UI screenshot.
```

---

## Tipps für beste Ergebnisse

**Midjourney:** Füge `--ar 16:9 --style raw --v 6 --q 2` an
**DALL·E 3:** Präzise Beschreibungen wie oben — GPT-4 Vision als Feedback-Loop
**Stable Diffusion:** Verwende `realistic_vision_v5.1` oder `dreamshaper_xl` Checkpoint
**Google ImageFX:** Prompts direkt wie angegeben, Qualität "Highest"

**Post-Processing (Figma/Photoshop):**
1. Erzeugtes Bild als Background-Layer
2. Echte UI-Komponenten aus dem Projekt drüber-rendern
3. Text mit echter Schrift ersetzen (Plus Jakarta Sans)
4. Für Präsentation: Device-Frame hinzufügen (MacBook Pro 14" oder Dell UltraSharp)
