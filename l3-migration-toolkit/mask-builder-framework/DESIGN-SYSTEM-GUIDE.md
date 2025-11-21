# VALEO-NeuroERP Design System Guide

**Version:** 3.1.0  
**Datum:** 2025-10-26

## 🎨 Übersicht

Dieser Guide definiert das einheitliche Design System für alle Masken in VALEO-NeuroERP.

## 📐 Layout-Struktur

### Frameset-Aufbau

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

## 🧩 Komponenten

### 1. Header
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

### 2. Navigation
```json
{
  "width": "240px",
  "background": "#f8f9fa",
  "collapsible": true
}
```

**Mobile:** Bottom Navigation  
**Desktop:** Side Navigation

### 3. Content Area
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

### 4. Footer
```json
{
  "height": "48px",
  "background": "#f8f9fa",
  "showValidationErrors": true
}
```

**Anzeige:**
- Info-Zeile
- Validierungsfehler
- Statistik

## 📦 Komponenten-Bibliothek

### Input Components

#### Text
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

#### Email
```json
{
  "comp": "Email",
  "bind": "email",
  "label": "E-Mail",
  "validation": ["email", "required"]
}
```

#### Number
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

#### Select
```json
{
  "comp": "Select",
  "bind": "status",
  "label": "Status",
  "options": ["Aktiv", "Inaktiv", "Gesperrt"],
  "searchable": true
}
```

#### BadgeSelect
```json
{
  "comp": "BadgeSelect",
  "bind": "priority",
  "label": "Priorität",
  "optionsRef": "common.priority",
  "showColors": true
}
```

#### Date
```json
{
  "comp": "Date",
  "bind": "erstellt_am",
  "label": "Erstellt am",
  "format": "DD.MM.YYYY"
}
```

#### Toggle
```json
{
  "comp": "Toggle",
  "bind": "is_active",
  "label": "Aktiv",
  "default": true
}
```

#### TextArea
```json
{
  "comp": "TextArea",
  "bind": "beschreibung",
  "label": "Beschreibung",
  "rows": 4,
  "maxLength": 500
}
```

#### RichText
```json
{
  "comp": "RichText",
  "bind": "notes",
  "label": "Notizen",
  "toolbar": ["bold", "italic", "list"]
}
```

### Layout Components

#### Card
```json
{
  "comp": "Card",
  "title": "Titel",
  "collapsible": true,
  "defaultExpanded": true
}
```

#### Accordion
```json
{
  "comp": "Accordion",
  "items": [
    { "title": "Item 1", "content": "..." },
    { "title": "Item 2", "content": "..." }
  ]
}
```

#### Grid
```json
{
  "comp": "Grid",
  "columns": 3,
  "gap": "1rem"
}
```

## 🎨 Typography

### Headings
- H1: 2rem, Bold
- H2: 1.5rem, Bold
- H3: 1.25rem, Semibold
- H4: 1rem, Semibold

### Body
- Base: 1rem, Regular
- Small: 0.875rem, Regular
- Tiny: 0.75rem, Regular

### Labels
- Default: 0.875rem, Medium
- Required: 0.875rem, Medium + *
- Optional: 0.875rem, Medium + (optional)

## 🎨 Colors

### Primary
- Primary: #2563eb
- Primary Dark: #1e40af
- Primary Light: #dbeafe

### Status
- Success: #10b981
- Warning: #f59e0b
- Error: #ef4444
- Info: #3b82f6

### Grays
- Gray 50: #f9fafb
- Gray 100: #f3f4f6
- Gray 200: #e5e7eb
- Gray 300: #d1d5db
- Gray 400: #9ca3af
- Gray 500: #6b7280
- Gray 600: #4b5563
- Gray 700: #374151
- Gray 800: #1f2937
- Gray 900: #111827

## 📐 Spacing

### Scale
- xs: 0.25rem (4px)
- sm: 0.5rem (8px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)
- 2xl: 3rem (48px)

### Usage
- Field Gap: md (1rem)
- Section Gap: lg (1.5rem)
- Card Padding: md (1rem)
- Page Padding: lg (1.5rem)

## 📱 Responsive Breakpoints

### Mobile (<640px)
- Columns: 1
- Nav: Bottom
- Accordions: Enabled
- Sticky Footer: Enabled

### Tablet (<1024px)
- Columns: 2
- Nav: Side
- Accordions: Disabled
- Sticky Footer: Enabled

### Desktop (≥1024px)
- Columns: 3
- Nav: Side
- Accordions: Disabled
- Sticky Footer: Disabled

## ♿ Accessibility

### ARIA Labels
- Alle interaktiven Elemente haben ARIA-Labels
- Screen-Reader-kompatibel
- Fokus-Management

### Keyboard Navigation
- Tab: Next Field
- Shift+Tab: Previous Field
- Enter: Submit/Action
- Escape: Cancel/Close
- Arrow Keys: Navigation

### Focus Styles
```css
outline: 2px solid #2563eb;
outline-offset: 2px;
```

## 🤖 AI-Features

### Intent Bar
- Shortcut: ⌘K / Ctrl+K
- Placeholder: "Befehl oder Frage eingeben..."
- Actions: Kontextabhängig

### AI-Assist
- Autofill-Vorschläge
- Contextual Help
- Smart Validators

### RAG Panels
- Kontextinformationen
- Verwandte Einträge
- Aktionen vorschlagen

## 🚀 Performance

### Virtual Lists
- Für Listen > 100 Items
- Lazy Loading
- Smooth Scrolling

### Deferred Loading
- Heavy Panels verzögert laden
- Images lazy loaden
- Charts on-demand laden

### Optimistic UI
- Sofortiges Feedback
- Background Sync
- Error Recovery

## 📊 Validation

### Client-Side
- Pattern Matching
- Min/Max Checks
- Required Checks
- AI-Validierung

### Server-Side
- Komplette Validierung
- Duplicate Checks
- Business Rules

### Error Display
- Inline Errors
- Summary Footer
- Toast Notifications

## 🎯 Best Practices

### DO ✅
- Verwende Standard-Komponenten
- Befolge Spacing-Regeln
- Nutze Grid-System
- Implementiere Responsive Design
- Füge AI-Features hinzu
- Teste auf Mobile

### DON'T ❌
- Keine Custom Components ohne Genehmigung
- Keine Hardcoded Werte
- Keine Abweichungen vom Grid
- Keine fehlenden ARIA-Labels
- Keine Performance-Killer

---

**Version:** 3.1.0  
**Status:** ✅ PRODUCTION-READY  
**Gültig:** Bis 2026-01-26

