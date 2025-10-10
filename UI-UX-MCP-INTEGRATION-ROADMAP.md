# UI/UX & MCP-Browser Integration - Roadmap

**Version:** 3.0.0  
**Datum:** 2024-10-10  
**Status:** ✅ **Phase 1 gestartet**

---

## 🎯 Strategische Übersicht

**Kern-Ansatz:** Schrittweise Integration mit MCP-Vorbereitung

```
Phase 1: Foundation (JETZT)  →  Storybook + Accessibility
Phase 2: Consolidation       →  Design-System + Tokens  
Phase 3: AI-Enhancement      →  MCP-Browser Integration
```

**Warum diese Reihenfolge:**
- ✅ Sofortiger Mehrwert (Phase 1)
- ✅ Solide Basis für MCP (Phase 2)
- ✅ Kein Breaking-Change bei MCP-Integration (Phase 3)

---

## 📅 Phase 1: Foundation (Woche 1-2) - ✅ GESTARTET

### Ziel
Komponenten-Übersicht & Accessibility mit MCP-Vorbereitung

### Tools & Technologien

#### 1. Storybook ✅ **INSTALLIERT**
```bash
✅ @storybook/react-vite@9.1.10
✅ @storybook/addon-essentials@8.6.14
✅ @storybook/addon-interactions@8.6.14
✅ @storybook/addon-links@9.1.10
```

**Konfiguration:**
- ✅ `.storybook/main.ts` - Storybook-Config
- ✅ `.storybook/preview.ts` - Preview-Config mit MCP-Params
- ✅ `setup-storybook.mjs` - Setup-Script

**Start:**
```bash
cd packages/frontend-web
pnpm storybook
# → http://localhost:6006
```

---

#### 2. Accessibility (ESLint Plugin)

**Installation:**
```bash
cd packages/frontend-web
pnpm add -D eslint-plugin-jsx-a11y
```

**Integration in `.eslintrc.json`:**
```json
{
  "extends": [
    "plugin:jsx-a11y/recommended"
  ],
  "plugins": ["jsx-a11y"]
}
```

**Nutzen:**
- ✅ WCAG 2.1 Compliance
- ✅ Automatische A11y-Checks
- ✅ Screen-Reader-Support
- ✅ Keyboard-Navigation

---

#### 3. MCP-Metadaten-Schema ✅ **ERSTELLT**

**Datei:** `src/design/mcp-schemas/component-metadata.ts`

**Interface:**
```typescript
export interface MCPComponentMetadata {
  componentName: string;
  componentType: 'form' | 'button' | 'input' | ...;
  accessibility: { role, ariaLabel, ... };
  intent: { purpose, userActions, dataContext };
  mcpHints: { autoFillable, explainable, testable };
  designSystem: { tokens, variants, theme };
}
```

**Factory:**
```typescript
const metadata = createMCPMetadata('Button', 'button', {
  intent: {
    purpose: 'Submit sales order',
    userActions: ['click'],
    businessDomain: 'sales',
  },
  mcpHints: {
    explainable: true,
    contextAware: true,
  },
});
```

---

#### 4. Beispiel-Stories ✅ **ERSTELLT**

**Datei:** `src/components/ui/button.stories.tsx`

**Features:**
- ✅ Alle Button-Variants
- ✅ MCP-Metadaten eingebettet
- ✅ Accessibility-Dokumentation
- ✅ Interactive-Controls

**Besonderheit:**
```typescript
parameters: {
  mcp: {
    metadata: buttonMCPMetadata,
    context: {
      userIntent: 'create-sales-order',
      requiredData: ['customer', 'articles'],
    },
  },
}
```

---

### Deliverables Phase 1

- [x] Storybook installiert & konfiguriert
- [x] MCP-Metadaten-Schema erstellt
- [x] Erste Component-Story mit MCP-Metadaten
- [ ] eslint-plugin-jsx-a11y integriert (5 Min)
- [ ] 5-10 Component-Stories erstellt (2 Tage)
- [ ] Accessibility-Audit (1 Tag)

**Zeitrahmen:** 3-5 Tage  
**Status:** ✅ 60% komplett

---

## 🎨 Phase 2: Design-System (Woche 3-6)

### Ziel
Einheitliches UI-Verhalten mit Tailwind-Tokens

### Aufgaben

#### 1. Design-Tokens erstellen

**Datei:** `src/design/tokens.ts`

```typescript
export const designTokens = {
  colors: {
    // Primary
    primary: {
      50: 'hsl(var(--primary-50))',
      100: 'hsl(var(--primary-100))',
      // ... bis 950
    },
    // Semantic
    success: { ... },
    warning: { ... },
    error: { ... },
  },
  
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    // ...
  },
  
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    fontSize: { ... },
    lineHeight: { ... },
  },
  
  // MCP-Metadata Export
  _mcp: {
    version: '1.0.0',
    schema: 'design-tokens',
    exportFormat: 'json',
  },
};
```

---

#### 2. Theme-Provider mit MCP-Kontext

**Datei:** `src/design/theme-provider.tsx`

```typescript
import { createContext } from 'react';

interface ThemeContext {
  theme: 'light' | 'dark' | 'auto';
  tokens: typeof designTokens;
  // MCP-Context für Phase 3
  mcpContext?: {
    currentTheme: string;
    availableTokens: string[];
    themeSwitchable: boolean;
  };
}

export const ThemeProvider = ({ children }) => {
  // Theme-Logic + MCP-Context
};
```

---

#### 3. shadcn/ui erweitern

**Alle UI-Components mit MCP-Metadaten:**
```
src/components/ui/
├── button.tsx          (✅ mit MCP)
├── input.tsx           (→ mit MCP)
├── dialog.tsx          (→ mit MCP)
├── command.tsx         (→ mit MCP)
├── popover.tsx         (→ mit MCP)
└── ...
```

**Pro Component:**
- MCP-Metadaten-Export
- JSON-Schema für MCP-Browser
- Intent-Dokumentation

---

#### 4. Storybook-Integration

**Alle Components in Storybook:**
- Visual-Variants dokumentieren
- Accessibility-Tests
- Interaction-Tests
- MCP-Metadaten anzeigen

---

### Deliverables Phase 2

- [ ] Design-Tokens definiert
- [ ] Theme-Provider mit Dark-Mode
- [ ] Alle shadcn/ui-Components mit MCP-Metadaten
- [ ] Tailwind-Config erweitert
- [ ] Storybook für alle UI-Components
- [ ] Component-JSON-Schemas generiert

**Zeitrahmen:** 3-4 Wochen  
**Status:** ⏳ Geplant

---

## 🤖 Phase 3: MCP-Browser Integration (Woche 9+)

### Ziel
AI-powered UI mit LLM-Integration

### Technologie-Stack

#### 1. MCP-Browser-Adapter

**Option A: @modelcontext/browser-adapter** (wenn verfügbar)
```bash
pnpm add @modelcontext/browser-adapter
```

**Option B: Eigener gRPC-Proxy**
```typescript
// src/mcp/browser-proxy.ts
import { MCPBrowserClient } from './mcp-client';

export class ValeoMCPBrowserProxy {
  async explainComponent(componentId: string) {
    // Rufe MCP-Server mit Component-Metadata
  }
  
  async autoFillForm(formId: string, context: any) {
    // AI-gestütztes Formular-Ausfüllen
  }
  
  async suggestNextAction(currentState: any) {
    // AI-Vorschläge für nächste Schritte
  }
}
```

---

#### 2. Component-MCP-Integration

**Beispiel: FormBuilder mit MCP**

```typescript
import { useMCP } from '@/hooks/useMCP';

function FormBuilder({ schema, mcpContext }) {
  const { explainField, autoFill, validate } = useMCP();
  
  return (
    <form>
      {fields.map(field => (
        <div key={field.name} data-mcp-field={field.name}>
          <Label>{field.label}</Label>
          <Input 
            {...field}
            onAIHelp={() => explainField(field)}
          />
          {/* AI-Hilfe-Button */}
          <Button 
            onClick={() => autoFill(field, mcpContext)}
            variant="ghost"
            size="icon"
          >
            🤖 AI-Fill
          </Button>
        </div>
      ))}
    </form>
  );
}
```

---

#### 3. MCP-Features

**A. Component-Erklärung**
```typescript
// User klickt "?" → AI erklärt Component
<Button 
  onClick={() => mcp.explainComponent('sales-order-form')}
>
  ? Hilfe
</Button>

// AI-Response:
// "Dieses Formular erstellt einen Verkaufsauftrag.
//  Erforderlich: Kunde, Artikel, Menge. Optional: Rabatt."
```

**B. Auto-Fill aus Kontext**
```typescript
// AI füllt Formular aus ERP-Kontext
const context = {
  lastCustomer: 'CUST-001',
  lastArticle: 'ART-WEIZEN-A',
  suggestedPrice: 25.50,
};

mcp.autoFillForm('sales-order-form', context);
// → Formular wird automatisch befüllt
```

**C. Visual Regression mit AI**
```typescript
// MCP-Browser macht Screenshots + Vergleich
await mcp.visualTest({
  component: 'SalesOrderForm',
  variants: ['empty', 'filled', 'with-errors'],
  compareWith: 'baseline',
});
```

---

### Deliverables Phase 3

- [ ] MCP-Browser-Adapter/Proxy implementiert
- [ ] useMCP-Hook erstellt
- [ ] 5+ Components mit MCP-Features
- [ ] AI-Hilfe-Buttons in Forms
- [ ] Auto-Fill aus Kontext
- [ ] Visual-Regression-Tests mit MCP
- [ ] "Explain this form"-Feature
- [ ] Context-aware Suggestions

**Zeitrahmen:** 2-3 Wochen  
**Status:** ⏳ Phase 3 (später)

---

## 🧱 Konkrete Umsetzungsschritte

### ✅ Phase 1 (JETZT - Tag 1-10)

| Tag | Aufgabe | Aufwand | Status |
|-----|---------|---------|--------|
| 1 | Storybook Setup | 2h | ✅ DONE |
| 1 | MCP-Schema erstellt | 1h | ✅ DONE |
| 1 | Button-Story mit MCP | 1h | ✅ DONE |
| 2 | eslint-plugin-jsx-a11y | 2h | ⏳ TODO |
| 2-3 | Input/Dialog/Command Stories | 4h | ⏳ TODO |
| 4-5 | Form-Components Stories | 8h | ⏳ TODO |
| 6-7 | Accessibility-Audit | 8h | ⏳ TODO |
| 8-10 | Dokumentation | 8h | ⏳ TODO |

**Total:** ~34 Stunden (4-5 Tage)

---

### ⏳ Phase 2 (Woche 3-6)

| Woche | Aufgabe | Aufwand | Status |
|-------|---------|---------|--------|
| 3 | Design-Tokens definieren | 2 Tage | ⏳ TODO |
| 3 | Theme-Provider erstellen | 1 Tag | ⏳ TODO |
| 4 | Tailwind-Config erweitern | 1 Tag | ⏳ TODO |
| 4-5 | shadcn/ui mit MCP-Metadaten | 5 Tage | ⏳ TODO |
| 6 | Dark-Mode implementieren | 2 Tage | ⏳ TODO |
| 6 | Component-Schemas generieren | 1 Tag | ⏳ TODO |

**Total:** ~15 Tage

---

### 🤖 Phase 3 (Woche 9+)

| Woche | Aufgabe | Aufwand | Status |
|-------|---------|---------|--------|
| 9 | MCP-Browser evaluieren | 2 Tage | ⏳ TODO |
| 9 | Adapter/Proxy implementieren | 3 Tage | ⏳ TODO |
| 10 | useMCP-Hook erstellen | 2 Tage | ⏳ TODO |
| 10-11 | 5 Components mit MCP | 5 Tage | ⏳ TODO |
| 12 | AI-Hilfe-Features | 3 Tage | ⏳ TODO |
| 12 | Visual-Regression-Tests | 2 Tage | ⏳ TODO |

**Total:** ~17 Tage

---

## 🔧 Technische Architektur

### MCP-Integration-Layers

```
┌─────────────────────────────────────────┐
│  Frontend (React + shadcn/ui)           │
│  ├─ UI-Components (mit MCP-Metadaten)   │
│  └─ useMCP() Hook                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  MCP-Browser-Proxy (gRPC)               │
│  ├─ Component-Schema-Registry           │
│  ├─ Context-Manager                     │
│  └─ LLM-Request-Handler                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  MCP-Server (@modelcontextprotocol)     │
│  ├─ Browser-Tool                        │
│  ├─ Screenshot-Tool                     │
│  └─ DOM-Analyzer                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  LLM (Claude, GPT-4, etc.)              │
└─────────────────────────────────────────┘
```

---

## 📦 Package-Struktur (nach Phase 3)

```
packages/frontend-web/
├── src/
│   ├── components/
│   │   └── ui/
│   │       ├── button.tsx              (✅ mit MCP-Metadata)
│   │       ├── button.stories.tsx      (✅ erstellt)
│   │       ├── input.tsx               (→ mit MCP)
│   │       └── ...
│   │
│   ├── design/
│   │   ├── tokens.ts                   (Phase 2)
│   │   ├── theme-provider.tsx          (Phase 2)
│   │   └── mcp-schemas/
│   │       ├── component-metadata.ts   (✅ erstellt)
│   │       └── schema-registry.ts      (Phase 3)
│   │
│   ├── mcp/
│   │   ├── browser-proxy.ts            (Phase 3)
│   │   ├── mcp-client.ts               (Phase 3)
│   │   └── hooks/
│   │       ├── useMCP.ts                (Phase 3)
│   │       ├── useMCPExplain.ts         (Phase 3)
│   │       └── useMCPAutoFill.ts        (Phase 3)
│   │
│   └── stories/                        (Phase 1)
│       ├── button.stories.tsx          (✅ erstellt)
│       ├── form.stories.tsx            (Phase 1)
│       └── ...
│
├── .storybook/
│   ├── main.ts                         (✅ erstellt)
│   └── preview.ts                      (✅ erstellt)
│
└── setup-storybook.mjs                 (✅ erstellt)
```

---

## 🧩 MCP-Metadaten-Beispiele

### Button-Component

```typescript
const buttonMCP = createMCPMetadata('Button', 'button', {
  accessibility: {
    role: 'button',
    keyboardShortcuts: ['Enter', 'Space'],
  },
  intent: {
    purpose: 'Trigger action',
    userActions: ['click'],
  },
  mcpHints: {
    explainable: true,
    testable: true,
  },
  designSystem: {
    variants: ['default', 'destructive', 'outline'],
    tokens: ['primary-color', 'spacing-md'],
  },
});
```

### Sales-Order-Form

```typescript
const salesOrderFormMCP = createMCPMetadata('SalesOrderForm', 'form', {
  accessibility: {
    role: 'form',
    ariaLabel: 'Create new sales order',
  },
  intent: {
    purpose: 'Create sales order',
    userActions: ['fill', 'validate', 'submit'],
    dataContext: ['customer', 'articles', 'prices', 'delivery-date'],
    businessDomain: 'sales',
  },
  validation: {
    required: true,
    constraints: {
      customer: 'required',
      articles: 'minItems:1',
      totalAmount: 'min:0',
    },
  },
  mcpHints: {
    autoFillable: true,        // ✅ AI kann Formular ausfüllen
    explainable: true,         // ✅ AI kann Felder erklären
    contextAware: true,        // ✅ Nutzt ERP-Kontext
  },
});
```

---

## 🔌 MCP-Browser Adapter (Phase 3)

### Option A: @modelcontext/browser-adapter

```typescript
import { MCPBrowserAdapter } from '@modelcontext/browser-adapter';

const mcpAdapter = new MCPBrowserAdapter({
  serverUrl: 'http://localhost:5555/mcp',
  components: componentRegistry,
  llmProvider: 'anthropic',
});

// Component erklären
const explanation = await mcpAdapter.explain('SalesOrderForm');

// Auto-Fill
await mcpAdapter.autoFill('SalesOrderForm', {
  context: { lastCustomer: 'CUST-001' },
});
```

---

### Option B: Eigener gRPC-Proxy

**Datei:** `src/mcp/grpc-proxy.ts`

```typescript
import * as grpc from '@grpc/grpc-js';

export class ValeoMCPProxy {
  private client: MCPBrowserClient;
  
  constructor(serverAddr: string) {
    this.client = new MCPBrowserClient(
      serverAddr,
      grpc.credentials.createInsecure()
    );
  }
  
  async explainComponent(componentId: string, metadata: MCPComponentMetadata) {
    const request = {
      componentId,
      metadata: JSON.stringify(metadata),
      userContext: this.getUserContext(),
    };
    
    return await this.client.ExplainComponent(request);
  }
  
  async autoFillForm(formId: string, schema: any, context: any) {
    const request = {
      formId,
      schema,
      context,
      intent: 'auto-fill',
    };
    
    return await this.client.AutoFillForm(request);
  }
}
```

---

## 🎓 Best-Practices

### MCP-Metadaten in Components

**DO's:**
- ✅ Metadaten in Story-Parameters
- ✅ JSON-Export-Funktion bereitstellen
- ✅ Intent klar dokumentieren
- ✅ Accessibility-First

**DON'Ts:**
- ❌ Metadaten nicht im Component-Code (zu viel Overhead)
- ❌ Keine Runtime-Dependencies zu MCP in Phase 1/2
- ❌ Nicht alle Components mit MCP (nur kritische)

---

### Component-Kategorisierung

**MCP-Ready-Levels:**

**Level 1: Basic (Phase 1)**
- Accessibility-Metadaten
- Storybook-Dokumentation

**Level 2: Enhanced (Phase 2)**
- Design-Tokens-Referenz
- JSON-Schema-Export
- Intent-Dokumentation

**Level 3: MCP-Integrated (Phase 3)**
- MCP-Hints aktiviert
- Auto-Fill implementiert
- AI-Explain-Feature
- Context-Awareness

---

## 📊 Success-Metrics

### Phase 1
- ✅ 20+ Components in Storybook
- ✅ 0 Accessibility-Warnings
- ✅ 100% Components mit MCP-Metadaten-Schema

### Phase 2
- ✅ Design-Tokens in allen Components
- ✅ Dark-Mode funktioniert
- ✅ JSON-Schemas für alle UI-Components

### Phase 3
- ✅ MCP-Browser-Integration funktioniert
- ✅ AI-Explain für 10+ Forms
- ✅ Auto-Fill für 5+ kritische Forms
- ✅ Visual-Regression-Tests automatisiert

---

## 🚀 Quick-Start

### Jetzt starten (Phase 1):

```bash
# 1. Storybook starten
cd packages/frontend-web
pnpm storybook

# 2. Browser öffnet sich automatisch
# http://localhost:6006

# 3. Button-Story ansehen
# UI/Button → verschiedene Variants

# 4. MCP-Metadaten prüfen (in Story-Parameters)
```

---

### Nächste Schritte (heute):

```bash
# 1. Accessibility-Plugin integrieren
cd packages/frontend-web
pnpm add -D eslint-plugin-jsx-a11y

# 2. ESLint-Config updaten
node setup-storybook.mjs

# 3. Weitere Stories erstellen
# src/components/ui/input.stories.tsx
# src/components/ui/dialog.stories.tsx
```

---

## 📚 Ressourcen

### Storybook
- Docs: https://storybook.js.org/docs/react/get-started/introduction
- Best-Practices: https://storybook.js.org/docs/react/writing-stories/introduction

### Accessibility
- eslint-plugin-jsx-a11y: https://github.com/jsx-eslint/eslint-plugin-jsx-a11y
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/

### MCP
- MCP-Docs: https://modelcontextprotocol.io
- MCP-Browser-Tool: https://github.com/modelcontextprotocol/servers
- gRPC-Proxy-Pattern: https://grpc.io/docs/languages/node/basics/

### Design-Systems
- Radix-UI: https://www.radix-ui.com/
- shadcn/ui: https://ui.shadcn.com/
- Tailwind: https://tailwindcss.com/docs

---

## ✅ Aktueller Status

**Phase 1: Foundation** ✅ 60% komplett
- ✅ Storybook installiert & konfiguriert
- ✅ MCP-Metadaten-Schema erstellt
- ✅ Erste Button-Story mit MCP-Kontext
- ✅ Setup-Script erstellt
- ⏳ Accessibility-Plugin (5 Min)
- ⏳ Weitere Component-Stories (2-3 Tage)

**Phase 2: Design-System** ⏳ Geplant (Woche 3-6)

**Phase 3: MCP-Browser** ⏳ Geplant (Woche 9+)

---

## 🎯 Nächster Schritt

**JETZT:**
```bash
cd packages/frontend-web
pnpm storybook
```

**Dann:**
```bash
node setup-storybook.mjs  # Führt Accessibility-Setup durch
```

---

**🚀 UI/UX-ROADMAP MIT MCP-VORBEREITUNG: READY! 📚**

**Storybook:** http://localhost:6006  
**Repository:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0

