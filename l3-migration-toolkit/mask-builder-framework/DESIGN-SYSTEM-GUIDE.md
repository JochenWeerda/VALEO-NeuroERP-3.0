***REMOVED*** VALEO-NeuroERP Design System Guide

**Version:** 3.1.0  
**Datum:** 2025-10-26

***REMOVED******REMOVED*** 🎨 Übersicht

Dieser Guide definiert das einheitliche Design System für alle Masken in VALEO-NeuroERP.

***REMOVED******REMOVED*** 📐 Layout-Struktur

***REMOVED******REMOVED******REMOVED*** Frameset-Aufbau

```
┌─────────────────────────────────────────────────────────┐
│ HEADER (Sticky)                                         │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│ │ Primary Info │ │ Status/Tags  │ │ Quick Actions│     │
│ └──────────────┘ └──────────────┘ └──────────────┘     │
├─────────────────┬───────────────────────────────────────┤
│ NAV (Side)      │ CONTENT (Tabs/Sections)              │
│                 │                                       │
│ • Tab 1         │ ┌─────────────────────────────────┐ │
│ • Tab 2         │ │ Section 1                      │ │
│ • Tab 3         │ │ [Field] [Field] [Field]        │ │
│ • ...           │ └─────────────────────────────────┘ │
│                 │ ┌─────────────────────────────────┐ │
│                 │ │ Section 2                      │ │
│                 │ │ [Field] [Field]                │ │
│                 │ └─────────────────────────────────┘ │
├─────────────────┴───────────────────────────────────────┤
│ FOOTER (Info/Errors)                                    │
└─────────────────────────────────────────────────────────┘
```

***REMOVED******REMOVED*** 🧩 Komponenten

***REMOVED******REMOVED******REMOVED*** 1. Header
```json
{
  "sticky": true,
  "height": "64px",
  "background": "white",
  "shadow": "0 2px 4px rgba(0,0,0,0.1)"
}
```

**Elemente:**
- Primary Info (z.B. Nummer, Name)
- Status Badges
- Quick Actions (Speichern, Neu, etc.)

***REMOVED******REMOVED******REMOVED*** 2. Navigation
```json
{
  "width": "240px",
  "background": "***REMOVED***f8f9fa",
  "collapsible": true
}
```

**Mobile:** Bottom Navigation  
**Desktop:** Side Navigation

***REMOVED******REMOVED******REMOVED*** 3. Content Area
```json
{
  "padding": "1.5rem",
  "maxWidth": "1200px",
  "background": "white"
}
```

**Struktur:**
- Tabs (falls vorhanden)
- Sections (Cards)
- Fields (Grid)

***REMOVED******REMOVED******REMOVED*** 4. Footer
```json
{
  "height": "48px",
  "background": "***REMOVED***f8f9fa",
  "showValidationErrors": true
}
```

**Anzeige:**
- Info-Zeile
- Validierungsfehler
- Statistik

***REMOVED******REMOVED*** 📦 Komponenten-Bibliothek

***REMOVED******REMOVED******REMOVED*** Input Components

***REMOVED******REMOVED******REMOVED******REMOVED*** Text
```json
{
  "comp": "Text",
  "bind": "field_name",
  "label": "Label",
  "placeholder": "Placeholder",
  "required": true,
  "maxLength": 100
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Email
```json
{
  "comp": "Email",
  "bind": "email",
  "label": "E-Mail",
  "validation": ["email", "required"]
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Number
```json
{
  "comp": "Number",
  "bind": "amount",
  "label": "Betrag",
  "min": 0,
  "max": 1000000,
  "unit": "EUR"
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Select
```json
{
  "comp": "Select",
  "bind": "status",
  "label": "Status",
  "options": ["Aktiv", "Inaktiv", "Gesperrt"],
  "searchable": true
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** BadgeSelect
```json
{
  "comp": "BadgeSelect",
  "bind": "priority",
  "label": "Priorität",
  "optionsRef": "common.priority",
  "showColors": true
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Date
```json
{
  "comp": "Date",
  "bind": "erstellt_am",
  "label": "Erstellt am",
  "format": "DD.MM.YYYY"
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Toggle
```json
{
  "comp": "Toggle",
  "bind": "is_active",
  "label": "Aktiv",
  "default": true
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** TextArea
```json
{
  "comp": "TextArea",
  "bind": "beschreibung",
  "label": "Beschreibung",
  "rows": 4,
  "maxLength": 500
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** RichText
```json
{
  "comp": "RichText",
  "bind": "notes",
  "label": "Notizen",
  "toolbar": ["bold", "italic", "list"]
}
```

***REMOVED******REMOVED******REMOVED*** Layout Components

***REMOVED******REMOVED******REMOVED******REMOVED*** Card
```json
{
  "comp": "Card",
  "title": "Titel",
  "collapsible": true,
  "defaultExpanded": true
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Accordion
```json
{
  "comp": "Accordion",
  "items": [
    { "title": "Item 1", "content": "..." },
    { "title": "Item 2", "content": "..." }
  ]
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Grid
```json
{
  "comp": "Grid",
  "columns": 3,
  "gap": "1rem"
}
```

***REMOVED******REMOVED*** 🎨 Typography

***REMOVED******REMOVED******REMOVED*** Headings
- H1: 2rem, Bold
- H2: 1.5rem, Bold
- H3: 1.25rem, Semibold
- H4: 1rem, Semibold

***REMOVED******REMOVED******REMOVED*** Body
- Base: 1rem, Regular
- Small: 0.875rem, Regular
- Tiny: 0.75rem, Regular

***REMOVED******REMOVED******REMOVED*** Labels
- Default: 0.875rem, Medium
- Required: 0.875rem, Medium + *
- Optional: 0.875rem, Medium + (optional)

***REMOVED******REMOVED*** 🎨 Colors

***REMOVED******REMOVED******REMOVED*** Primary
- Primary: ***REMOVED***2563eb
- Primary Dark: ***REMOVED***1e40af
- Primary Light: ***REMOVED***dbeafe

***REMOVED******REMOVED******REMOVED*** Status
- Success: ***REMOVED***10b981
- Warning: ***REMOVED***f59e0b
- Error: ***REMOVED***ef4444
- Info: ***REMOVED***3b82f6

***REMOVED******REMOVED******REMOVED*** Grays
- Gray 50: ***REMOVED***f9fafb
- Gray 100: ***REMOVED***f3f4f6
- Gray 200: ***REMOVED***e5e7eb
- Gray 300: ***REMOVED***d1d5db
- Gray 400: ***REMOVED***9ca3af
- Gray 500: ***REMOVED***6b7280
- Gray 600: ***REMOVED***4b5563
- Gray 700: ***REMOVED***374151
- Gray 800: ***REMOVED***1f2937
- Gray 900: ***REMOVED***111827

***REMOVED******REMOVED*** 📐 Spacing

***REMOVED******REMOVED******REMOVED*** Scale
- xs: 0.25rem (4px)
- sm: 0.5rem (8px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)
- 2xl: 3rem (48px)

***REMOVED******REMOVED******REMOVED*** Usage
- Field Gap: md (1rem)
- Section Gap: lg (1.5rem)
- Card Padding: md (1rem)
- Page Padding: lg (1.5rem)

***REMOVED******REMOVED*** 📱 Responsive Breakpoints

***REMOVED******REMOVED******REMOVED*** Mobile (<640px)
- Columns: 1
- Nav: Bottom
- Accordions: Enabled
- Sticky Footer: Enabled

***REMOVED******REMOVED******REMOVED*** Tablet (<1024px)
- Columns: 2
- Nav: Side
- Accordions: Disabled
- Sticky Footer: Enabled

***REMOVED******REMOVED******REMOVED*** Desktop (≥1024px)
- Columns: 3
- Nav: Side
- Accordions: Disabled
- Sticky Footer: Disabled

***REMOVED******REMOVED*** ♿ Accessibility

***REMOVED******REMOVED******REMOVED*** ARIA Labels
- Alle interaktiven Elemente haben ARIA-Labels
- Screen-Reader-kompatibel
- Fokus-Management

***REMOVED******REMOVED******REMOVED*** Keyboard Navigation
- Tab: Next Field
- Shift+Tab: Previous Field
- Enter: Submit/Action
- Escape: Cancel/Close
- Arrow Keys: Navigation

***REMOVED******REMOVED******REMOVED*** Focus Styles
```css
outline: 2px solid ***REMOVED***2563eb;
outline-offset: 2px;
```

***REMOVED******REMOVED*** 🤖 AI-Features

***REMOVED******REMOVED******REMOVED*** Intent Bar
- Shortcut: ⌘K / Ctrl+K
- Placeholder: "Befehl oder Frage eingeben..."
- Actions: Kontextabhängig

***REMOVED******REMOVED******REMOVED*** AI-Assist
- Autofill-Vorschläge
- Contextual Help
- Smart Validators

***REMOVED******REMOVED******REMOVED*** RAG Panels
- Kontextinformationen
- Verwandte Einträge
- Aktionen vorschlagen

***REMOVED******REMOVED*** 🚀 Performance

***REMOVED******REMOVED******REMOVED*** Virtual Lists
- Für Listen > 100 Items
- Lazy Loading
- Smooth Scrolling

***REMOVED******REMOVED******REMOVED*** Deferred Loading
- Heavy Panels verzögert laden
- Images lazy loaden
- Charts on-demand laden

***REMOVED******REMOVED******REMOVED*** Optimistic UI
- Sofortiges Feedback
- Background Sync
- Error Recovery

***REMOVED******REMOVED*** 📊 Validation

***REMOVED******REMOVED******REMOVED*** Client-Side
- Pattern Matching
- Min/Max Checks
- Required Checks
- AI-Validierung

***REMOVED******REMOVED******REMOVED*** Server-Side
- Komplette Validierung
- Duplicate Checks
- Business Rules

***REMOVED******REMOVED******REMOVED*** Error Display
- Inline Errors
- Summary Footer
- Toast Notifications

***REMOVED******REMOVED*** 🎯 Best Practices

***REMOVED******REMOVED******REMOVED*** DO ✅
- Verwende Standard-Komponenten
- Befolge Spacing-Regeln
- Nutze Grid-System
- Implementiere Responsive Design
- Füge AI-Features hinzu
- Teste auf Mobile

***REMOVED******REMOVED******REMOVED*** DON'T ❌
- Keine Custom Components ohne Genehmigung
- Keine Hardcoded Werte
- Keine Abweichungen vom Grid
- Keine fehlenden ARIA-Labels
- Keine Performance-Killer

---

**Version:** 3.1.0  
**Status:** ✅ PRODUCTION-READY  
**Gültig:** Bis 2026-01-26

