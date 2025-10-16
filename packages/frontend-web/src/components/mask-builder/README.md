# VALEO Mask Builder Framework

Das VALEO Mask Builder Framework ist ein wiederverwendbares System zur schnellen Erstellung von ERP-Masken mit einheitlichem Look & Feel.

## Übersicht

Das Framework besteht aus wiederverwendbaren Komponenten für verschiedene Masken-Typen:

- **ObjectPage**: Detailansicht mit Tabs für komplexe Objekte
- **ListReport**: Listen mit Filtern, Suche und Aktionen
- **Wizard**: Mehrschritt-Formulare mit Validierung
- **Worklist**: Aufgabenlisten mit Status-Tracking
- **OverviewPage**: Dashboards mit KPIs und Charts

## Architektur

```
packages/frontend-web/src/components/mask-builder/
├── index.ts              # Haupt-Export
├── types.ts              # TypeScript-Definitionen
├── ObjectPage.tsx        # ObjectPage-Komponente
├── ListReport.tsx        # ListReport-Komponente
├── Wizard.tsx            # Wizard-Komponente
├── Worklist.tsx          # Worklist-Komponente
├── OverviewPage.tsx      # OverviewPage-Komponente
├── hooks/                # Wiederverwendbare Hooks
│   ├── useMaskData.ts    # Daten-Management
│   ├── useMaskValidation.ts # Validierung
│   └── useMaskActions.ts # Aktionen
├── utils/                # Hilfsfunktionen
│   ├── formatting.ts     # Formatierung
│   ├── validation.ts     # Validierung
│   └── api.ts            # API-Client
└── README.md             # Dokumentation
```

## Verwendung

### 1. ObjectPage Beispiel

```tsx
import { ObjectPage } from '@/components/mask-builder'

const config = {
  title: 'PSM-Stammdaten',
  type: 'object-page',
  tabs: [
    {
      key: 'allgemein',
      label: 'Allgemein',
      fields: [
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'wirkstoff', label: 'Wirkstoff', type: 'text', required: true },
        { name: 'hersteller', label: 'Hersteller', type: 'lookup', endpoint: '/api/hersteller' }
      ]
    }
  ],
  actions: [
    { key: 'save', label: 'Speichern', type: 'primary' }
  ],
  api: {
    baseUrl: '/api/psm'
  }
}

function PSMStammPage() {
  return (
    <ObjectPage
      config={config}
      data={psmData}
      onSave={handleSave}
      onCancel={handleCancel}
    />
  )
}
```

### 2. ListReport Beispiel

```tsx
import { ListReport } from '@/components/mask-builder'

const config = {
  title: 'PSM-Liste',
  type: 'list-report',
  columns: [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'wirkstoff', label: 'Wirkstoff', filterable: true },
    { key: 'status', label: 'Status', render: (value) => <Badge>{value}</Badge> }
  ],
  filters: [
    { name: 'status', label: 'Status', type: 'select', options: [
      { value: 'aktiv', label: 'Aktiv' },
      { value: 'inaktiv', label: 'Inaktiv' }
    ]}
  ],
  api: {
    baseUrl: '/api/psm'
  }
}

function PSMListPage() {
  return (
    <ListReport
      config={config}
      data={psmList}
      total={totalCount}
      onCreate={handleCreate}
      onEdit={handleEdit}
    />
  )
}
```

### 3. Wizard Beispiel

```tsx
import { Wizard } from '@/components/mask-builder'

const config = {
  title: 'PSM-Beratung',
  type: 'wizard',
  steps: [
    {
      key: 'schadbild',
      title: 'Schadbild beschreiben',
      fields: [
        { name: 'beschreibung', label: 'Beschreibung', type: 'textarea', required: true },
        { name: 'kultur', label: 'Kultur', type: 'select', options: [] }
      ]
    },
    {
      key: 'empfehlungen',
      title: 'Empfehlungen',
      fields: [
        { name: 'psm', label: 'Empfohlene PSM', type: 'table', columns: [] }
      ]
    }
  ]
}

function PSMBeratungWizard() {
  return (
    <Wizard
      config={config}
      onComplete={handleComplete}
      onCancel={handleCancel}
    />
  )
}
```

## Features

### ✅ Automatische Validierung
- Zod-Schema-Integration
- Echtzeit-Validierung
- Feld-spezifische Fehlermeldungen

### ✅ Responsive Design
- Mobile-first Ansatz
- Adaptive Layouts
- Touch-optimierte Steuerelemente

### ✅ Accessibility
- ARIA-Labels
- Keyboard-Navigation
- Screen-Reader-Unterstützung

### ✅ Performance
- Lazy Loading
- Optimistische Updates
- Caching

### ✅ Erweiterbarkeit
- Plugin-System
- Custom Field Types
- Theme-Unterstützung

## Konfiguration

Jede Maske wird über eine Konfigurationsdatei definiert:

```typescript
interface MaskConfig {
  title: string
  subtitle?: string
  type: MaskType
  tabs?: Tab[]
  columns?: ListColumn[]
  steps?: WizardStep[]
  actions: Action[]
  api: ApiConfig
  validation?: ZodSchema
  permissions?: string[]
}
```

## Best Practices

1. **Konfiguration vor Code**: Definiere Masken deklarativ über Konfiguration
2. **Einheitliche Patterns**: Verwende immer die gleichen Feldtypen und Layouts
3. **Validierung zuerst**: Implementiere Validierung vor UI-Logik
4. **Mobile-first**: Optimiere für mobile Geräte
5. **Performance**: Verwende Pagination und Lazy Loading für große Datenmengen

## Erweiterungen

Das Framework kann durch Plugins erweitert werden:

- **Custom Field Types**: Eigene Feldtypen (z.B. DateRange, ColorPicker)
- **Custom Layouts**: Spezielle Layouts für bestimmte Use Cases
- **Integrationen**: Verbindung mit externen APIs (DMS, Maps, etc.)
- **Themes**: Verschiedene Farbschemata und Styles

## Migration

Bestehende Masken können schrittweise migriert werden:

1. Erstelle Konfiguration für bestehende Maske
2. Migriere eine Komponente nach der anderen
3. Teste Funktionalität nach jeder Migration
4. Entferne alten Code nach erfolgreicher Migration

## Support

Bei Fragen oder Problemen:
- Dokumentation: `/docs/mask-builder/`
- Issues: GitHub Issues
- Team: VALEO ERP Development Team