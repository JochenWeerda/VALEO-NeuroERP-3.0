# VALEO-NeuroERP Mask Builder Framework

**Version:** 3.1.0  
**Status:** ✅ PRODUCTION-READY

## 🎯 Übersicht

Das VALEO-NeuroERP Mask Builder Framework ist ein vollständiges System zur Erstellung einheitlicher, moderner, KI-gestützter Masken für alle Module.

## 📁 Struktur

```
mask-builder-framework/
├── base-template.json          # Basis-Template für neue Masken
├── generate-mask.py            # Generator für neue Masken
├── DESIGN-PRINCIPLES.md        # Design-Prinzipien
├── DESIGN-SYSTEM-GUIDE.md      # Design System Dokumentation
├── README.md                   # Diese Datei
└── examples/                   # Beispiel-Masken
    ├── kundenstamm.json        # Kundenstamm (Beispiel)
    └── artikelstamm.json       # Artikelstamm (Beispiel)
```

## 🚀 Quick Start

### 1. Neue Maske erstellen

```bash
# Verwende Generator
python generate-mask.py

# Oder manuell aus Template
cp base-template.json neue-maske.json
```

### 2. Mask konfigurieren

```json
{
  "meta": {
    "name": "artikelstamm",
    "description": "Artikelstamm für VALEO-NeuroERP"
  },
  "resource": "artikel",
  "routing": {
    "basePath": "/lager/artikel-stamm",
    "param": "artikel_nr"
  },
  "fields": [...]
}
```

### 3. Mask importieren

- Öffne VALEO-NeuroERP Admin Panel
- Navigiere zu Mask Builder
- Import → Neue Maske hochladen
- Teste Funktionalität

## 📐 Design-Prinzipien

### 1. Mobile-First 📱
- Responsive Breakpoints
- Touch-optimiert
- Bottom-Navigation auf Mobile

### 2. KI-First 🤖
- Intent-Bar (⌘K)
- Autofill-Vorschläge
- Smart Validators

### 3. Progressive Disclosure 📋
- Übersicht → Details
- Tabs → Sections
- Accordions

### 4. Consistency 🎨
- Einheitliches Look & Feel
- Standard-Komponenten
- Gleiche Breakpoints

### 5. Performance ⚡
- Virtual Lists
- Lazy Loading
- Optimistic UI

### 6. Accessibility ♿
- ARIA-Labels
- Keyboard Navigation
- Screen-Reader Support

### 7. Data Integrity 🔒
- Client & Server Validation
- AI-Quality Checks
- Real-time Feedback

### 8. Flexibility 🔧
- Template-basiert
- Konfigurierbar
- Erweiterbar

## 🎨 Design System

### Komponenten
- Text, Email, Number, Select
- BadgeSelect, Date, Toggle
- TextArea, RichText
- Card, Accordion, Grid

### Colors
- Primary: #2563eb
- Success: #10b981
- Warning: #f59e0b
- Error: #ef4444

### Spacing
- xs: 4px, sm: 8px, md: 16px
- lg: 24px, xl: 32px, 2xl: 48px

### Typography
- Base: 1rem
- Small: 0.875rem
- Tiny: 0.75rem

## 📱 Responsive Breakpoints

| Breakpoint | Columns | Nav | Accordions |
|------------|---------|-----|------------|
| <640px     | 1       | Bottom | Yes |
| <1024px    | 2       | Side | No |
| ≥1024px    | 3       | Side | No |

## 🤖 KI-Features

### Intent-Bar (⌘K)
- Schnelle Befehle
- Kontextabhängige Actions
- AI-Unterstützung

### AI-Assist
- Autofill-Vorschläge
- Smart Validators
- Contextual Help

### RAG Panels
- Kontextinformationen
- Verwandte Einträge
- Next-Best-Actions

## 📊 Features

### Core Features
- ✅ Responsive Design
- ✅ Touch-Optimierung
- ✅ Keyboard Navigation
- ✅ Virtual Lists
- ✅ Lazy Loading
- ✅ Optimistic UI

### AI Features
- ✅ Intent-Bar
- ✅ Autofill
- ✅ Smart Validators
- ✅ RAG Panels
- ✅ MCP Tools
- ✅ Telemetry

### Accessibility
- ✅ ARIA-Labels
- ✅ Screen-Reader
- ✅ Reduced Motion
- ✅ Focus Management

## 🔧 Technische Details

### JSON Schema
- Version: 3.1.0
- Format: UTF-8
- Indentation: 2 Spaces
- Naming: camelCase

### Komponenten
- Type-safe
- Reusable
- Configurable
- Extensible

### Validation
- Client-side
- Server-side
- AI-powered
- Real-time

## 📖 Dokumentation

### Verfügbare Guides
1. **DESIGN-PRINCIPLES.md** - Design-Prinzipien
2. **DESIGN-SYSTEM-GUIDE.md** - Komponenten & Styles
3. **README.md** - Diese Übersicht

### Beispiele
- `examples/kundenstamm.json` - Vollständiges Beispiel
- `examples/artikelstamm.json` - Einfaches Beispiel

## 🎯 Best Practices

### DO ✅
- Verwende Template als Basis
- Befolge Design-Prinzipien
- Nutze Standard-Komponenten
- Implementiere Responsive Design
- Füge AI-Features hinzu
- Teste auf Mobile

### DON'T ❌
- Keine Custom Components ohne Genehmigung
- Keine Hardcoded Werte
- Keine Abweichungen vom Grid
- Keine fehlenden ARIA-Labels
- Keine Performance-Killer

## 🚀 Migration von alten Masken

### Schritt 1: Analyse
- Bestehende Felder dokumentieren
- Navigation-Struktur analysieren
- Validierungen identifizieren

### Schritt 2: Konvertierung
- Felder in neues Format übertragen
- Komponenten zuordnen
- Navigation erstellen

### Schritt 3: Enhancement
- Responsive Design hinzufügen
- AI-Features einbauen
- Performance optimieren

### Schritt 4: Testing
- Funktionale Tests
- Responsive Tests
- Accessibility Tests

## 📊 Erfolgsmetriken

### UX Metrics
- Zeit bis Datenerfassung: -30%
- Fehlerrate: -50%
- Mobile-Nutzung: +40%
- Zufriedenheit: +25%

### Performance Metrics
- Ladezeit: < 2s
- Interaktionszeit: < 100ms
- Bundle Size: < 500KB
- Accessibility Score: > 90

## 🔄 Maintenance

### Updates
- Quarterly Reviews
- User Feedback Integration
- Performance Monitoring
- A/B Testing

### Versioning
- Major: Breaking Changes
- Minor: New Features
- Patch: Bug Fixes

## 📞 Support

### Fragen?
- Design-Team: design@valeo-neuroerp.com
- Entwickler-Team: dev@valeo-neuroerp.com
- Dokumentation: docs.valeo-neuroerp.com

### Issues?
- GitHub: github.com/valeo-neuroerp/mask-builder
- Jira: valeoneuroerp.atlassian.net

---

**Version:** 3.1.0  
**Status:** ✅ PRODUCTION-READY  
**Letzte Aktualisierung:** 2025-10-26


