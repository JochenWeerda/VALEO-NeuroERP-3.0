***REMOVED*** VALEO-NeuroERP Mask Builder Framework

**Version:** 3.1.0  
**Status:** ✅ PRODUCTION-READY

***REMOVED******REMOVED*** 🎯 Übersicht

Das VALEO-NeuroERP Mask Builder Framework ist ein vollständiges System zur Erstellung einheitlicher, moderner, KI-gestützter Masken für alle Module.

***REMOVED******REMOVED*** 📁 Struktur

```
mask-builder-framework/
├── base-template.json          ***REMOVED*** Basis-Template für neue Masken
├── generate-mask.py            ***REMOVED*** Generator für neue Masken
├── DESIGN-PRINCIPLES.md        ***REMOVED*** Design-Prinzipien
├── DESIGN-SYSTEM-GUIDE.md      ***REMOVED*** Design System Dokumentation
├── README.md                   ***REMOVED*** Diese Datei
└── examples/                   ***REMOVED*** Beispiel-Masken
    ├── kundenstamm.json        ***REMOVED*** Kundenstamm (Beispiel)
    └── artikelstamm.json       ***REMOVED*** Artikelstamm (Beispiel)
```

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** 1. Neue Maske erstellen

```bash
***REMOVED*** Verwende Generator
python generate-mask.py

***REMOVED*** Oder manuell aus Template
cp base-template.json neue-maske.json
```

***REMOVED******REMOVED******REMOVED*** 2. Mask konfigurieren

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

***REMOVED******REMOVED******REMOVED*** 3. Mask importieren

- Öffne VALEO-NeuroERP Admin Panel
- Navigiere zu Mask Builder
- Import → Neue Maske hochladen
- Teste Funktionalität

***REMOVED******REMOVED*** 📐 Design-Prinzipien

***REMOVED******REMOVED******REMOVED*** 1. Mobile-First 📱
- Responsive Breakpoints
- Touch-optimiert
- Bottom-Navigation auf Mobile

***REMOVED******REMOVED******REMOVED*** 2. KI-First 🤖
- Intent-Bar (⌘K)
- Autofill-Vorschläge
- Smart Validators

***REMOVED******REMOVED******REMOVED*** 3. Progressive Disclosure 📋
- Übersicht → Details
- Tabs → Sections
- Accordions

***REMOVED******REMOVED******REMOVED*** 4. Consistency 🎨
- Einheitliches Look & Feel
- Standard-Komponenten
- Gleiche Breakpoints

***REMOVED******REMOVED******REMOVED*** 5. Performance ⚡
- Virtual Lists
- Lazy Loading
- Optimistic UI

***REMOVED******REMOVED******REMOVED*** 6. Accessibility ♿
- ARIA-Labels
- Keyboard Navigation
- Screen-Reader Support

***REMOVED******REMOVED******REMOVED*** 7. Data Integrity 🔒
- Client & Server Validation
- AI-Quality Checks
- Real-time Feedback

***REMOVED******REMOVED******REMOVED*** 8. Flexibility 🔧
- Template-basiert
- Konfigurierbar
- Erweiterbar

***REMOVED******REMOVED*** 🎨 Design System

***REMOVED******REMOVED******REMOVED*** Komponenten
- Text, Email, Number, Select
- BadgeSelect, Date, Toggle
- TextArea, RichText
- Card, Accordion, Grid

***REMOVED******REMOVED******REMOVED*** Colors
- Primary: ***REMOVED***2563eb
- Success: ***REMOVED***10b981
- Warning: ***REMOVED***f59e0b
- Error: ***REMOVED***ef4444

***REMOVED******REMOVED******REMOVED*** Spacing
- xs: 4px, sm: 8px, md: 16px
- lg: 24px, xl: 32px, 2xl: 48px

***REMOVED******REMOVED******REMOVED*** Typography
- Base: 1rem
- Small: 0.875rem
- Tiny: 0.75rem

***REMOVED******REMOVED*** 📱 Responsive Breakpoints

| Breakpoint | Columns | Nav | Accordions |
|------------|---------|-----|------------|
| <640px     | 1       | Bottom | Yes |
| <1024px    | 2       | Side | No |
| ≥1024px    | 3       | Side | No |

***REMOVED******REMOVED*** 🤖 KI-Features

***REMOVED******REMOVED******REMOVED*** Intent-Bar (⌘K)
- Schnelle Befehle
- Kontextabhängige Actions
- AI-Unterstützung

***REMOVED******REMOVED******REMOVED*** AI-Assist
- Autofill-Vorschläge
- Smart Validators
- Contextual Help

***REMOVED******REMOVED******REMOVED*** RAG Panels
- Kontextinformationen
- Verwandte Einträge
- Next-Best-Actions

***REMOVED******REMOVED*** 📊 Features

***REMOVED******REMOVED******REMOVED*** Core Features
- ✅ Responsive Design
- ✅ Touch-Optimierung
- ✅ Keyboard Navigation
- ✅ Virtual Lists
- ✅ Lazy Loading
- ✅ Optimistic UI

***REMOVED******REMOVED******REMOVED*** AI Features
- ✅ Intent-Bar
- ✅ Autofill
- ✅ Smart Validators
- ✅ RAG Panels
- ✅ MCP Tools
- ✅ Telemetry

***REMOVED******REMOVED******REMOVED*** Accessibility
- ✅ ARIA-Labels
- ✅ Screen-Reader
- ✅ Reduced Motion
- ✅ Focus Management

***REMOVED******REMOVED*** 🔧 Technische Details

***REMOVED******REMOVED******REMOVED*** JSON Schema
- Version: 3.1.0
- Format: UTF-8
- Indentation: 2 Spaces
- Naming: camelCase

***REMOVED******REMOVED******REMOVED*** Komponenten
- Type-safe
- Reusable
- Configurable
- Extensible

***REMOVED******REMOVED******REMOVED*** Validation
- Client-side
- Server-side
- AI-powered
- Real-time

***REMOVED******REMOVED*** 📖 Dokumentation

***REMOVED******REMOVED******REMOVED*** Verfügbare Guides
1. **DESIGN-PRINCIPLES.md** - Design-Prinzipien
2. **DESIGN-SYSTEM-GUIDE.md** - Komponenten & Styles
3. **README.md** - Diese Übersicht

***REMOVED******REMOVED******REMOVED*** Beispiele
- `examples/kundenstamm.json` - Vollständiges Beispiel
- `examples/artikelstamm.json` - Einfaches Beispiel

***REMOVED******REMOVED*** 🎯 Best Practices

***REMOVED******REMOVED******REMOVED*** DO ✅
- Verwende Template als Basis
- Befolge Design-Prinzipien
- Nutze Standard-Komponenten
- Implementiere Responsive Design
- Füge AI-Features hinzu
- Teste auf Mobile

***REMOVED******REMOVED******REMOVED*** DON'T ❌
- Keine Custom Components ohne Genehmigung
- Keine Hardcoded Werte
- Keine Abweichungen vom Grid
- Keine fehlenden ARIA-Labels
- Keine Performance-Killer

***REMOVED******REMOVED*** 🚀 Migration von alten Masken

***REMOVED******REMOVED******REMOVED*** Schritt 1: Analyse
- Bestehende Felder dokumentieren
- Navigation-Struktur analysieren
- Validierungen identifizieren

***REMOVED******REMOVED******REMOVED*** Schritt 2: Konvertierung
- Felder in neues Format übertragen
- Komponenten zuordnen
- Navigation erstellen

***REMOVED******REMOVED******REMOVED*** Schritt 3: Enhancement
- Responsive Design hinzufügen
- AI-Features einbauen
- Performance optimieren

***REMOVED******REMOVED******REMOVED*** Schritt 4: Testing
- Funktionale Tests
- Responsive Tests
- Accessibility Tests

***REMOVED******REMOVED*** 📊 Erfolgsmetriken

***REMOVED******REMOVED******REMOVED*** UX Metrics
- Zeit bis Datenerfassung: -30%
- Fehlerrate: -50%
- Mobile-Nutzung: +40%
- Zufriedenheit: +25%

***REMOVED******REMOVED******REMOVED*** Performance Metrics
- Ladezeit: < 2s
- Interaktionszeit: < 100ms
- Bundle Size: < 500KB
- Accessibility Score: > 90

***REMOVED******REMOVED*** 🔄 Maintenance

***REMOVED******REMOVED******REMOVED*** Updates
- Quarterly Reviews
- User Feedback Integration
- Performance Monitoring
- A/B Testing

***REMOVED******REMOVED******REMOVED*** Versioning
- Major: Breaking Changes
- Minor: New Features
- Patch: Bug Fixes

***REMOVED******REMOVED*** 📞 Support

***REMOVED******REMOVED******REMOVED*** Fragen?
- Design-Team: design@valeo-neuroerp.com
- Entwickler-Team: dev@valeo-neuroerp.com
- Dokumentation: docs.valeo-neuroerp.com

***REMOVED******REMOVED******REMOVED*** Issues?
- GitHub: github.com/valeo-neuroerp/mask-builder
- Jira: valeoneuroerp.atlassian.net

---

**Version:** 3.1.0  
**Status:** ✅ PRODUCTION-READY  
**Letzte Aktualisierung:** 2025-10-26

