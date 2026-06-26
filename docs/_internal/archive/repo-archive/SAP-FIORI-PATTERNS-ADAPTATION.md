# SAP Fiori Patterns - Adaption für VALEO-NeuroERP

**Quelle:** [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com)  
**Version:** 3.0.0  
**Datum:** 2024-10-10  
**Status:** ✅ **Analyse komplett, Patterns identifiziert**

---

## 🎯 Übersicht: SAP Fiori Floorplans

SAP Fiori definiert **Standard-Layouts** (Floorplans) für typische ERP-Use-Cases.

### Die wichtigsten für VALEO:

| Fiori-Pattern | Use-Case | VALEO-Anwendung |
|---------------|----------|-----------------|
| **List Report** | Daten-Übersicht + Filter | Sales Orders Liste, Kunden-Liste |
| **Object Page** | Detail-Ansicht + Edit | Sales Order Details, Kunden-Stamm |
| **Worklist** | Aufgaben-Liste mit Actions | Offene Aufträge, Genehmigungen |
| **Overview Page** | Dashboard mit KPIs | Verkaufs-Dashboard, Lager-Übersicht |
| **Wizard** | Multi-Step-Prozess | Artikel-Anlage, Kunden-Onboarding |
| **Initial Page** | Landing mit Quick-Actions | ERP-Startseite |

---

## 📋 Pattern 1: List Report (Wichtigstes Pattern!)

### SAP Fiori Definition

**Use-Case:** Liste + Filter + Suche + Actions

**Layout:**
```
┌────────────────────────────────────────────┐
│ [Titel]                    [+ Neu] [Export]│ ← Toolbar
├────────────────────────────────────────────┤
│ [🔍 Suche]  [Filter: Status ▼] [Filter ▶] │ ← Filter-Bar
├────────────────────────────────────────────┤
│ ☑ │ Nr.     │ Kunde   │ Datum  │ Betrag  │ ← Table-Header
│───┼─────────┼─────────┼────────┼─────────│
│ ☐ │ SO-001  │ CUST-A  │ 10.10  │ 1.250 € │ ← Rows
│ ☐ │ SO-002  │ CUST-B  │ 09.10  │ 2.100 € │
│ ☐ │ SO-003  │ CUST-A  │ 08.10  │   890 € │
├────────────────────────────────────────────┤
│ 3 von 156 | [◀] Seite 1 von 52 [▶]        │ ← Pagination
└────────────────────────────────────────────┘
```

### VALEO-Implementation

**Datei:** `src/components/patterns/ListReport.tsx`

```typescript
import { PageToolbar } from '@/components/navigation/PageToolbar';
import { DataTable } from '@/components/ui/data-table';
import { FilterBar } from '@/components/ui/filter-bar';

interface ListReportProps<T> {
  title: string;
  data: T[];
  columns: ColumnDef<T>[];
  onNew?: () => void;
  onExport?: () => void;
  filterOptions?: FilterOption[];
  // MCP-Metadaten
  mcpContext?: {
    domain: string;
    entityType: string;
  };
}

export function ListReport<T>({
  title,
  data,
  columns,
  onNew,
  onExport,
  filterOptions,
  mcpContext,
}: ListReportProps<T>) {
  return (
    <>
      {/* Toolbar mit Actions (Fiori-Pattern) */}
      <PageToolbar
        title={title}
        primaryActions={[
          onNew && {
            id: 'new',
            label: 'Neu',
            icon: <Plus />,
            onClick: onNew,
            shortcut: 'Ctrl+N',
          },
          onExport && {
            id: 'export',
            label: 'Export',
            icon: <Download />,
            onClick: onExport,
            variant: 'outline',
          },
        ].filter(Boolean)}
        mcpContext={mcpContext}
      />

      <div className="p-6 space-y-4">
        {/* Filter-Bar (Fiori-Pattern) */}
        {filterOptions && (
          <FilterBar options={filterOptions} />
        )}

        {/* Data-Table (Fiori-Pattern) */}
        <DataTable
          columns={columns}
          data={data}
          selectable
          pagination
          // MCP-Metadaten
          data-mcp-pattern="list-report"
          data-mcp-entity={mcpContext?.entityType}
        />
      </div>
    </>
  );
}
```

**Verwendung:**
```typescript
<ListReport
  title="Verkaufsaufträge"
  data={salesOrders}
  columns={orderColumns}
  onNew={() => navigate('/sales/orders/new')}
  onExport={handleExport}
  filterOptions={[
    { field: 'status', label: 'Status', type: 'select', options: ['Offen', 'Verbucht'] },
    { field: 'customer', label: 'Kunde', type: 'search' },
  ]}
  mcpContext={{ domain: 'sales', entityType: 'sales-order' }}
/>
```

---

## 📄 Pattern 2: Object Page (Detail-Ansicht)

### SAP Fiori Definition

**Use-Case:** Detailansicht mit Sections + Edit-Mode

**Layout:**
```
┌────────────────────────────────────────────┐
│ ← Zurück  SO-00123              [Edit] [⋯]│ ← Header
├────────────────────────────────────────────┤
│ Kunde: CUST-001 | Status: Offen | 1.250 €  │ ← Key-Info
├────────────────────────────────────────────┤
│ [Allgemein] [Positionen] [Lieferung] [...]│ ← Tabs
├────────────────────────────────────────────┤
│ Section: Allgemeine Daten                  │ ← Sections
│ ┌──────────────────────────────────────┐   │
│ │ Kundennummer:    CUST-001            │   │
│ │ Auftragsdatum:   10.10.2024          │   │
│ │ Lieferdatum:     17.10.2024          │   │
│ └──────────────────────────────────────┘   │
│                                            │
│ Section: Positionen                        │
│ ┌──────────────────────────────────────┐   │
│ │ [Table mit Artikeln]                 │   │
│ └──────────────────────────────────────┘   │
├────────────────────────────────────────────┤
│                    [Speichern] [Verwerfen] │ ← Sticky-Footer
└────────────────────────────────────────────┘
```

### VALEO-Implementation

**Datei:** `src/components/patterns/ObjectPage.tsx`

```typescript
import { useState } from 'react';
import { PageToolbar } from '@/components/navigation/PageToolbar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';

interface ObjectPageProps {
  title: string;
  subtitle?: string;
  keyInfo?: React.ReactNode;
  sections: ObjectPageSection[];
  onEdit?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  editMode?: boolean;
  // MCP
  mcpContext?: {
    domain: string;
    documentType: string;
    documentId: string;
  };
}

interface ObjectPageSection {
  id: string;
  label: string;
  icon?: React.ReactNode;
  content: React.ReactNode;
}

export function ObjectPage({
  title,
  subtitle,
  keyInfo,
  sections,
  onEdit,
  onSave,
  onCancel,
  editMode = false,
  mcpContext,
}: ObjectPageProps) {
  return (
    <>
      {/* Header mit Actions (Fiori-Pattern) */}
      <PageToolbar
        title={title}
        subtitle={subtitle}
        primaryActions={[
          !editMode && onEdit && {
            id: 'edit',
            label: 'Bearbeiten',
            onClick: onEdit,
            shortcut: 'Ctrl+E',
          },
        ].filter(Boolean)}
        mcpContext={mcpContext}
      />

      <div className="p-6">
        {/* Key-Info-Bar (Fiori-Pattern) */}
        {keyInfo && (
          <div className="mb-6 rounded-lg border bg-card p-4">
            {keyInfo}
          </div>
        )}

        {/* Tabs für Sections (Fiori-Pattern) */}
        <Tabs defaultValue={sections[0]?.id} className="space-y-4">
          <TabsList>
            {sections.map((section) => (
              <TabsTrigger key={section.id} value={section.id}>
                {section.icon}
                <span className="ml-2">{section.label}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          {sections.map((section) => (
            <TabsContent key={section.id} value={section.id} className="space-y-4">
              {section.content}
            </TabsContent>
          ))}
        </Tabs>
      </div>

      {/* Sticky-Footer mit Save-Actions (Fiori-Pattern) */}
      {editMode && (onSave || onCancel) && (
        <div className="sticky bottom-0 border-t bg-background/95 backdrop-blur p-4">
          <div className="flex justify-end gap-2">
            {onCancel && (
              <Button variant="outline" onClick={onCancel}>
                Verwerfen
              </Button>
            )}
            {onSave && (
              <Button onClick={onSave} shortcut="Ctrl+S">
                Speichern
              </Button>
            )}
          </div>
        </div>
      )}
    </>
  );
}
```

---

## 🔄 Pattern 3: Worklist (Aufgaben-Management)

### SAP Fiori Definition

**Use-Case:** Meine Aufgaben / Work-Queue

**Layout:**
```
┌────────────────────────────────────────────┐
│ Meine Aufgaben             [Filter] [Sort]│
├────────────────────────────────────────────┤
│ ⚠️  │ Auftrag SO-123 freigeben              │ ← Priority-Item
│     │ Kunde: CUST-001 | Betrag: 5.000 €    │
│     │ [Genehmigen] [Ablehnen]              │
│─────┼──────────────────────────────────────│
│ ⚠️  │ Rechnung RE-456 prüfen                │
│     │ [Details]                            │
│─────┼──────────────────────────────────────│
│     │ Lieferung LF-789 überfällig           │
│     │ [Kunde kontaktieren]                 │
└────────────────────────────────────────────┘
```

### VALEO-Implementation

**Datei:** `src/components/patterns/Worklist.tsx`

```typescript
interface WorkItem {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  actions: {
    label: string;
    onClick: () => void;
    variant?: 'default' | 'destructive';
  }[];
  // MCP
  mcp?: {
    intent: string;
    requiresApproval?: boolean;
  };
}

export function Worklist({ items }: { items: WorkItem[] }) {
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div
          key={item.id}
          className={cn(
            'flex items-start gap-4 rounded-lg border p-4',
            item.priority === 'high' && 'border-l-4 border-l-destructive'
          )}
          data-mcp-work-item={item.id}
          data-mcp-priority={item.priority}
        >
          {/* Priority-Indicator (Fiori) */}
          {item.priority === 'high' && (
            <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
          )}

          {/* Content */}
          <div className="flex-1">
            <h4 className="font-semibold">{item.title}</h4>
            <p className="text-sm text-muted-foreground">{item.description}</p>

            {/* Actions */}
            <div className="mt-3 flex gap-2">
              {item.actions.map((action, idx) => (
                <Button
                  key={idx}
                  size="sm"
                  variant={action.variant}
                  onClick={action.onClick}
                >
                  {action.label}
                </Button>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 📊 Pattern 4: Overview Page (Dashboard)

### SAP Fiori Definition

**Use-Case:** Executive-Dashboard mit KPI-Cards

**Layout:**
```
┌────────────────────────────────────────────┐
│ Verkaufs-Übersicht                         │
├──────────────┬──────────────┬──────────────┤
│ Umsatz heute │ Offene Auftr.│ Überfällig   │ ← KPI-Cards
│ 12.450 €     │ 23           │ 5            │
│ +12% ↑      │ -3 ↓         │ +2 ↑        │
├──────────────┴──────────────┴──────────────┤
│ [Chart: Umsatz-Trend]                      │ ← Visualisierung
├────────────────────────────────────────────┤
│ Top-Kunden (letzte 30 Tage)                │ ← List
│ 1. CUST-001  5.600 €                       │
│ 2. CUST-005  4.200 €                       │
└────────────────────────────────────────────┘
```

### VALEO-Implementation

**Datei:** `src/components/patterns/OverviewPage.tsx`

```typescript
interface KPICard {
  label: string;
  value: string | number;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  icon?: React.ReactNode;
  onClick?: () => void;
}

export function OverviewPage({
  title,
  kpis,
  charts,
  lists,
}: {
  title: string;
  kpis: KPICard[];
  charts?: React.ReactNode[];
  lists?: React.ReactNode[];
}) {
  return (
    <>
      <PageToolbar title={title} />

      <div className="p-6 space-y-6">
        {/* KPI-Cards (Fiori-Pattern) */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {kpis.map((kpi, idx) => (
            <div
              key={idx}
              className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={kpi.onClick}
              data-mcp-kpi={kpi.label}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  {kpi.label}
                </span>
                {kpi.icon}
              </div>
              <div className="mt-2 text-3xl font-bold">
                {kpi.value}
              </div>
              {kpi.trend && (
                <div className={cn(
                  'mt-1 text-sm flex items-center gap-1',
                  kpi.trend.direction === 'up' ? 'text-green-600' : 'text-red-600'
                )}>
                  {kpi.trend.direction === 'up' ? '↑' : '↓'}
                  {Math.abs(kpi.trend.value)}%
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Charts (Fiori-Pattern) */}
        {charts && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {charts.map((chart, idx) => (
              <div key={idx} className="rounded-lg border bg-card p-6">
                {chart}
              </div>
            ))}
          </div>
        )}

        {/* Lists (Fiori-Pattern) */}
        {lists && (
          <div className="space-y-4">
            {lists.map((list, idx) => (
              <div key={idx} className="rounded-lg border bg-card p-6">
                {list}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
```

---

## 🧙 Pattern 5: Wizard (Multi-Step-Prozess)

### SAP Fiori Definition

**Use-Case:** Komplexe Prozesse in Steps

**Layout:**
```
┌────────────────────────────────────────────┐
│ Neuen Artikel anlegen                      │
├────────────────────────────────────────────┤
│ 1. Stammdaten ━ 2. Preise ─ 3. Lager ─ 4. ✓│ ← Stepper
├────────────────────────────────────────────┤
│ Schritt 1: Stammdaten                      │
│ ┌──────────────────────────────────────┐   │
│ │ Artikelnummer: [_____________]       │   │
│ │ Bezeichnung:   [_____________]       │   │
│ │ Kategorie:     [▼ Rohstoffe  ]       │   │
│ └──────────────────────────────────────┘   │
├────────────────────────────────────────────┤
│         [Abbrechen]    [Weiter →]          │ ← Footer
└────────────────────────────────────────────┘
```

### VALEO-Implementation

**Datei:** `src/components/patterns/Wizard.tsx`

```typescript
interface WizardStep {
  id: string;
  label: string;
  content: React.ReactNode;
  validation?: () => boolean;
  // MCP
  mcp?: {
    intent: string;
    requiredFields?: string[];
  };
}

export function Wizard({
  title,
  steps,
  onComplete,
  onCancel,
}: {
  title: string;
  steps: WizardStep[];
  onComplete: (data: any) => void;
  onCancel: () => void;
}) {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<Record<string, any>>({});

  const canProceed = () => {
    return !steps[currentStep].validation || steps[currentStep].validation();
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">{title}</h1>

      {/* Stepper (Fiori-Pattern) */}
      <div className="mb-8">
        <div className="flex items-center">
          {steps.map((step, idx) => (
            <div key={step.id} className="flex items-center flex-1">
              <div className={cn(
                'flex h-8 w-8 items-center justify-center rounded-full',
                idx <= currentStep ? 'bg-primary text-primary-foreground' : 'bg-muted'
              )}>
                {idx < currentStep ? '✓' : idx + 1}
              </div>
              <span className="ml-2 text-sm">{step.label}</span>
              {idx < steps.length - 1 && (
                <div className={cn(
                  'mx-4 h-0.5 flex-1',
                  idx < currentStep ? 'bg-primary' : 'bg-muted'
                )} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step-Content */}
      <div className="mb-8 min-h-96">
        {steps[currentStep].content}
      </div>

      {/* Footer mit Navigation (Fiori-Pattern) */}
      <div className="flex justify-between pt-4 border-t">
        <Button variant="outline" onClick={onCancel}>
          Abbrechen
        </Button>
        <div className="flex gap-2">
          {currentStep > 0 && (
            <Button variant="outline" onClick={() => setCurrentStep(currentStep - 1)}>
              ← Zurück
            </Button>
          )}
          {currentStep < steps.length - 1 ? (
            <Button 
              onClick={() => setCurrentStep(currentStep + 1)}
              disabled={!canProceed()}
            >
              Weiter →
            </Button>
          ) : (
            <Button 
              onClick={() => onComplete(data)}
              disabled={!canProceed()}
            >
              ✓ Abschließen
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## 📝 Pattern 6: Form-Patterns (Ein- und Ausgabemasken)

### SAP Fiori Form-Guidelines

**1. Smart Forms (intelligente Validierung)**
```typescript
// Fiori-Principle: Inline-Validation mit Icons
<Input
  label="Artikelnummer"
  value={value}
  validation={{
    required: true,
    pattern: /^ART-\d{5}$/,
  }}
  // Visual-Feedback (Fiori)
  error={error}
  success={success}
  hint="Format: ART-12345"
/>

// ✓ Grün = Valid
// ⚠️  Gelb = Warning
// ✗ Rot = Error
```

**2. Value-Help (F4-Pattern)**
```typescript
// Fiori: Lookup mit Dialog
<LookupField
  label="Kunde"
  value={customer}
  onSearch={searchCustomers}
  valueHelpDialog
  // Zeigt: Liste mit Details + Suche
/>
```

**3. Smart-Fields (Auto-Vervollständigung)**
```typescript
// Fiori: Auto-Fill bei Selection
<LookupField
  label="Artikel"
  onChange={(article) => {
    // Auto-Fill:
    setPrice(article.price);
    setCost(article.cost);
    setUnit(article.unit);
  }}
/>
```

**4. Field-Grouping (Sections)**
```typescript
// Fiori: Logische Gruppierung
<Form>
  <Section title="Allgemeine Daten">
    <Field name="customer" />
    <Field name="date" />
  </Section>
  
  <Section title="Positionen">
    <Table ... />
  </Section>
  
  <Section title="Konditionen">
    <Field name="payment" />
    <Field name="discount" />
  </Section>
</Form>
```

---

## 🎨 Fiori-Design-Principles für VALEO

### 1. **Role-Based** ✅

**Fiori:**
> "Zeige nur was der User braucht und darf"

**VALEO:**
```typescript
// Actions basierend auf Scopes
{hasScope('sales:write') && <Button>Neu</Button>}
{hasScope('sales:approve') && <Button>Genehmigen</Button>}
{hasScope('admin:all') && <Button>Löschen</Button>}
```

### 2. **Responsive** ✅

**Fiori:**
> "Desktop, Tablet, Mobile - gleiches UX"

**VALEO:**
```typescript
// Breakpoints (Tailwind)
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  {/* Auto-responsive */}
</div>
```

### 3. **Coherent** ✅

**Fiori:**
> "Gleiches Pattern = Gleiches Verhalten"

**VALEO:**
- ListReport = Immer gleicher Aufbau
- ObjectPage = Immer Tabs + Sections
- Wizard = Immer Stepper + Footer

### 4. **Simple** ✅

**Fiori:**
> "Nur 3-5 Actions sichtbar, Rest im Overflow"

**VALEO:**
```typescript
primaryActions={[...]}    // Max 3-4
overflowActions={[...]}   // Rest
```

### 5. **Delightful** ✅

**Fiori:**
> "Micro-Interactions, Smooth-Transitions"

**VALEO:**
```typescript
// Framer-Motion für Micro-Interactions
<motion.div
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
>
  <KPICard />
</motion.div>
```

---

## 📦 VALEO Fiori-Pattern-Library

### Dateien-Struktur

```
packages/frontend-web/src/components/patterns/
├── ListReport.tsx          (Liste + Filter)
├── ObjectPage.tsx          (Detail-Ansicht)
├── Worklist.tsx            (Aufgaben)
├── OverviewPage.tsx        (Dashboard)
├── Wizard.tsx              (Multi-Step)
├── InitialPage.tsx         (Landing)
└── README.md               (Pattern-Docs)
```

### Verwendung

```typescript
// Sales Orders Page
import { ListReport } from '@/components/patterns/ListReport';

export function SalesOrdersPage() {
  return (
    <ListReport
      title="Verkaufsaufträge"
      data={orders}
      columns={columns}
      onNew={() => navigate('/sales/orders/new')}
      mcpContext={{ domain: 'sales', entityType: 'sales-order' }}
    />
  );
}

// Sales Order Details
import { ObjectPage } from '@/components/patterns/ObjectPage';

export function SalesOrderDetailsPage() {
  return (
    <ObjectPage
      title="Verkaufsauftrag SO-00123"
      sections={[
        { id: 'general', label: 'Allgemein', content: <GeneralSection /> },
        { id: 'items', label: 'Positionen', content: <ItemsTable /> },
      ]}
      mcpContext={{ domain: 'sales', documentType: 'sales-order', documentId: 'SO-00123' }}
    />
  );
}
```

---

## 🔗 SAP Fiori → VALEO Mapping

| SAP Fiori App-Type | VALEO Use-Case | Pattern | Status |
|--------------------|----------------|---------|--------|
| **Manage Sales Orders** | Verkaufsaufträge verwalten | ListReport | ✅ Ready |
| **Display Sales Order** | Auftrags-Details | ObjectPage | ✅ Ready |
| **Approve Sales Orders** | Genehmigungen | Worklist | ✅ Ready |
| **Sales Overview** | Verkaufs-Dashboard | OverviewPage | ✅ Ready |
| **Create Customer** | Kunden-Anlage | Wizard | ✅ Ready |
| **My Home** | ERP-Startseite | InitialPage | ⏳ TODO |

---

## 💡 Quick-Wins aus Fiori-Library

### 1. **Smart-Defaults** (Auto-Fill)

**Fiori-Principle:**
> "Reduce user-effort durch intelligente Defaults"

```typescript
// Beispiel: Lieferdatum = Heute + 7 Tage
const defaultDeliveryDate = new Date();
defaultDeliveryDate.setDate(defaultDeliveryDate.getDate() + 7);

<DatePicker 
  label="Lieferdatum"
  defaultValue={defaultDeliveryDate}
  // Fiori: Zeige Default als Hint
  hint="Standard: 7 Tage Lieferzeit"
/>
```

### 2. **Visual-Density** (Compact-Mode)

```typescript
// Fiori: Toggle für Power-User
const [density, setDensity] = useState<'cozy' | 'compact'>('cozy');

<Table density={density}>
  {/* Compact = kleinere row-height, mehr Daten sichtbar */}
</Table>
```

### 3. **Semantic-Colors** (Fiori-Palette)

```typescript
// Fiori: Farben mit Bedeutung
const semanticColors = {
  neutral: 'hsl(var(--muted))',        // Standard
  positive: 'hsl(var(--success))',     // Erfolg, Gewinn
  critical: 'hsl(var(--destructive))', // Fehler, Verlust
  negative: 'hsl(var(--warning))',     // Warnung
  informative: 'hsl(var(--primary))',  // Info, Hinweis
};

// Beispiel: Betrags-Anzeige
<span className={amount > 0 ? 'text-success' : 'text-destructive'}>
  {amount} €
</span>
```

### 4. **Empty-States** (Motivierend)

```typescript
// Fiori: Leere Liste nicht nur "No Data"
<EmptyState
  icon={<Package />}
  title="Noch keine Aufträge"
  description="Erstelle deinen ersten Verkaufsauftrag"
  action={
    <Button onClick={() => navigate('/sales/orders/new')}>
      + Ersten Auftrag erstellen
    </Button>
  }
/>
```

---

## 📚 Ressourcen

**SAP Fiori:**
- Apps Library: https://fioriappslibrary.hana.ondemand.com
- Design Guidelines: https://experience.sap.com/fiori-design-web/
- Floorplans: https://experience.sap.com/fiori-design-web/floorplans/
- UI-Patterns: https://experience.sap.com/fiori-design-web/ui-patterns/

**VALEO-Implementation:**
- Moderne Navigation: `MODERNE-NAVIGATION-OHNE-RIBBON.md`
- SAP Joule-Adaption: `SAP-JOULE-ADAPTATION-VALEO.md`
- MCP-Roadmap: `UI-UX-MCP-INTEGRATION-ROADMAP.md`

---

## 🚀 Frontend Roadmap & TODO (Stand 2024-10-10)

| Priorität | Fokusbereich | Deliverables | Status | Nächster Schritt |
|-----------|--------------|--------------|--------|------------------|
| 1 | Navigation aktivieren | `AppShell` in `main.tsx`, Sidebar-Konfiguration, Command Palette Shortcuts | Offen | `AppLayout` ablösen, Smoke-Test mit `pnpm dev` |
| 1 | Fiori-Patterns fertigstellen | `ObjectPage`, `Wizard`, `OverviewPage` + Stories inkl. MCP-Metadaten | Offen | Komponenten-Gerüst in `src/components/patterns` anlegen |
| 1 | i18n-Loader abschließen | Custom Backend-Loader + Fallback-Handling, Language Switcher | In Arbeit | Loader implementieren, gegen Translation-API testen |
| 2 | Agrar-Masken Welle 1 | Saatgut-Stamm (ObjectPage), Saatgut-Bestellung (Wizard), Dünger-Liste (ListReport) | Offen | Mock-Datenquelle anbinden, Seiten unter `pages/agrar` erzeugen |
| 2 | Routing & API-Wiring | Agrar-Routing, React Query Keys, Service-Layer für Saatgut/Dünger | Offen | Routen im Router ergänzen, BFF/Backend-Stubs prüfen |
| 3 | Storybook & QA | Stories für Patterns + Navigation, A11y-Linting (`node setup-storybook.mjs`), Visual Smoke Tests | Offen | Stories hinzufügen, `pnpm storybook` + `pnpm lint` ausführen |
| 3 | Observability UX | Loading/Empty/Error-State-Kit, Telemetry-Hooks, KPI-Tiles für OverviewPage | Backlog | Nach Welle 1 priorisieren |

### Priorität 1 – nächste Session (2–3 h)
1. **AppShell live schalten:** `packages/frontend-web/src/main.tsx` auf `AppShell` migrieren, Sidebar-Domainlinks synchronisieren, Command Palette Shortcut testen.
2. **ObjectPage & Wizard:** Komponenten-Framework nach Fiori-Spezifikation bauen, Form-Slots + Header-Actions definieren, Storybook-Stories mit MCP-Parametern versehen.
3. **OverviewPage:** KPI-Cards, Analytic-Tiles und Quick-Actions bereitstellen, Mock-Daten aus Saatgut-Prognosen verwenden.
4. **i18n-Backend-Loader:** Loader an Translation-Endpoints hängen, Fallback-Strategie dokumentieren und Language Switcher in TopBar verdrahten.

### Priorität 2 – Umsetzung danach (4–6 h)
1. **Agrar-Masken (10 Stück):** Start mit Saatgut-Stamm/-Liste/-Bestellung, Dünger-Stamm/-Liste nachziehen; Patterns wiederverwenden, i18n-Keys anlegen.
2. **Routing & API:** Agrar-Modul unter `/agrar/*`, Service-Hooks (React Query) für Saatgut/Dünger, erste Mock-APIs an Backend anbinden.
3. **Belegfolge & Policies:** Nummernkreise im Wizard berücksichtigen, Policy-Checks via MCP-Skill registrieren.

### Priorität 3 – Ergänzungen (2 h)
1. **Storybook-Abdeckung:** Navigation + Patterns + Ask VALEO integrieren, Controls & Docs Tabs pflegen.
2. **A11y & QA:** `eslint-plugin-jsx-a11y` aktivieren, Keyboard-Paths & Screenreader-Labels prüfen.
3. **Telemetry & Logging:** UX-Metriken für OverviewPage (KPI-Ladezeiten), Error-Boundaries mit Toast-Feedback.

### Laufende Pflege
- Fortschritt nach jedem Block in `AGRAR-MASKEN-IMPLEMENTATION-STATUS.md` und diesem Dokument spiegeln.
- Neue i18n-Keys sofort in Translation-API-Seed aufnehmen (`app/seeds/translations_seed.py`).
- Jede neue Page erhält MCP-Metadaten (siehe `UI-UX-MCP-INTEGRATION-ROADMAP.md` Vorgaben).

---

**🎯 SAP FIORI BEST-PRACTICES FÜR VALEO: BEREIT! 📚**

**Moderne Patterns, keine veralteten Ribbons, MCP-ready!**


