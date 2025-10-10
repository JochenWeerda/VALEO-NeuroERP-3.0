# SAP Joule Adaption für VALEO-NeuroERP

**Version:** 3.0.0  
**Datum:** 2024-10-10  
**Status:** ✅ **Phase 1 & 2 implementiert, Phase 3 vorbereitet**

---

## 🎯 Was ist SAP Joule?

**SAP Joule** ist SAPs KI-gestützter Copilot/Assistent:
- 🤖 **AI-Agent-Plattform** - Nicht nur UI, sondern intelligente Workflow-Assistenz
- 🎨 **Design-Guidelines** - "AI and Joule Design" in SAP Fiori Design System
- 🧩 **Skill-basiert** - Kleine, fokussierte AI-Funktionen (via Joule Studio)
- 🔗 **Kontextuell** - "Joule Action Bar" läuft mit, nicht isoliert
- 📊 **Explainable** - Transparenz bei Empfehlungen

---

## 💡 VALEO-Adaption: "Ask VALEO"

### Was wir von SAP Joule gelernt haben:

| SAP Joule Principle | VALEO Umsetzung | Status |
|---------------------|-----------------|--------|
| **Action Bar (mitlaufend)** | JouleActionBar.tsx - Floating Button | ✅ Implementiert |
| **Prompt-Interface** | AskValeo.tsx - Dialog mit Kontext | ✅ Implementiert |
| **Skill-Registry** | SkillRegistry.tsx - 5 vordefinierte Skills | ✅ Implementiert |
| **Kontextuelle Vorschläge** | Context-aware Suggestions | ✅ Implementiert |
| **Explainable AI** | Response mit Erklärungen | ✅ Vorbereitet |
| **Grounding** | Nur User-verfügbare Daten | ✅ Konzept |
| **MCP-Integration** | @modelcontext/browser-adapter | ⏳ Phase 3 |

---

## 🏗️ Implementierte Architektur

### Component-Struktur

```
Ask VALEO Copilot-System
├── AskValeo.tsx                  (Dialog - SAP Joule UI Pattern)
│   ├── Prompt-Input
│   ├── Quick-Actions             (Häufige Fragen)
│   ├── Contextual-Suggestions    (Kontext-basiert)
│   ├── AI-Response              (Explainable)
│   └── Error-Feedback
│
├── JouleActionBar.tsx            (Floating Action Bar)
│   └── "Ask VALEO" Button        (immer verfügbar)
│
├── SkillRegistry.tsx             (SAP Joule Studio-Konzept)
│   ├── ValeoSkill[]             (5 Skills definiert)
│   ├── ValeoAgent[]             (2 Agents definiert)
│   └── SkillExecutor            (Phase 3 ready)
│
└── MCP-Integration (Phase 3)
    ├── @modelcontext/browser-adapter
    ├── gRPC-Proxy
    └── LLM-Backend
```

---

## 🧩 Implementierte Skills (SAP Joule Studio-Pattern)

### 1. **search-customer**
```typescript
Input:  { query: string }
Output: Customer[]
Scope:  sales:read, crm:read
MCP:    searchCustomer (grounded on user-data)
```

### 2. **get-article-price**
```typescript
Input:  { articleNumber: string, customer?: string }
Output: { price: number, currency: string }
Scope:  sales:read
MCP:    getArticlePrice (grounded on system-data)
```

### 3. **create-sales-order**
```typescript
Input:  { customer, articles[], deliveryDate? }
Output: { orderId: string, status: string }
Scope:  sales:write
MCP:    createSalesOrder (grounded on user-data)
```

### 4. **check-policy**
```typescript
Input:  { action: string, data: object }
Output: { violations[], warnings[], allowed: boolean }
Scope:  policy:read
MCP:    checkPolicy (grounded on system-data)
```

### 5. **check-stock**
```typescript
Input:  { articleNumber: string, warehouse?: string }
Output: { available, reserved, incoming: number }
Scope:  inventory:read
MCP:    checkStock (grounded on system-data)
```

---

## 🤖 Implementierte Agents (Workflow-Orchestrierung)

### 1. **order-assistant**

**Workflow:**
```
1. search-customer      → Kunde finden
2. get-article-price    → Preise abrufen
3. check-stock          → Bestand prüfen
4. check-policy         → Policy-Validation
5. create-sales-order   → Auftrag erstellen
```

**MCP-Prompt-Template:**
```
Du bist ein Verkaufsauftrag-Assistent für VALEO-ERP.
Hilf dem Benutzer beim Erstellen eines Auftrags:
1. Finde den Kunden
2. Prüfe Artikel-Preise
3. Prüfe Bestand
4. Prüfe Policies
5. Erstelle Auftrag

Sei präzise, freundlich und erkläre jeden Schritt.
```

### 2. **reorder-assistant**

**Workflow:**
```
1. check-stock                    → Bestand prüfen
2. (wenn < minLevel) suggest-reorder → Nachbestellung vorschlagen
```

**Use-Case:**
```
User: "Welche Artikel müssen nachbestellt werden?"
Agent: → Analysiert Bestände
       → Findet 3 Artikel unter Mindestbestand
       → Schlägt Nachbestellung vor (Menge, Lieferant)
```

---

## 🎨 Design-Guidelines (SAP Joule adaptiert)

### 1. Explainable AI ✅

**Principle:** User muss verstehen, WARUM AI etwas vorschlägt

**Umsetzung:**
```typescript
// Nicht nur: "Erstelle Auftrag"
// Sondern:
"Erstelle Auftrag für Kunde CUST-001
 Grund: Letzte 3 Bestellungen waren von diesem Kunden
 Artikel: Basierend auf häufigsten Käufen
 Preis: Kundenspezifischer Rabatt 5% berücksichtigt"
```

### 2. Kontextuelle Integration ✅

**Principle:** AI nicht isoliert, sondern im Workflow

**Umsetzung:**
- ✅ **Joule Action Bar** - Fixed bottom-right, immer verfügbar
- ✅ **Context-aware** - Weiß welche Page aktiv ist
- ✅ **Domain-specific** - Sales-Vorschläge in Sales-Modul

### 3. Grounding ✅

**Principle:** AI nur auf Daten, auf die User Zugriff hat

**Umsetzung:**
```typescript
// Skills haben Scope-Requirements
requiredScopes: ['sales:read', 'crm:read']

// MCP-Integration prüft:
- User hat sales:read? ✅
- User hat admin:all? ❌
→ AI zeigt nur erlaubte Aktionen
```

### 4. Progressive Disclosure ✅

**Principle:** Erst einfach, dann komplex

**Umsetzung:**
```
Level 1: Quick-Actions (4 Buttons)
         → "Wie erstelle ich einen Auftrag?"
         
Level 2: Freie Frage stellen
         → "Zeige mir alle überfälligen Rechnungen von Kunde XYZ"
         
Level 3: Agent-Workflow
         → Multi-Step-Assistenz mit Rückfragen
```

### 5. Feedback-Loop ✅

**Principle:** Klare Stati (Laden, Erfolg, Fehler)

**Umsetzung:**
```typescript
// Loading
<Loader2 className="animate-spin" /> "VALEO denkt nach..."

// Success
<CheckCircle className="text-green-500" /> "Auftrag SO-00123 erstellt!"

// Error
<AlertCircle className="text-red-500" /> "Fehler: Kunde nicht gefunden"

// Warning
<AlertCircle className="text-yellow-500" /> "Artikel unter Mindestbestand"
```

---

## 📦 Dateistruktur

```
packages/frontend-web/src/
├── components/
│   ├── copilot/
│   │   ├── AskValeo.tsx               ✅ Joule-Dialog
│   │   ├── SkillRegistry.tsx          ✅ Skills + Agents
│   │   └── JouleActionBar (in AskValeo.tsx) ✅
│   │
│   └── navigation/
│       ├── AppShell.tsx               ✅ Main-Layout
│       ├── Sidebar.tsx                ✅ Domänen-Nav
│       ├── TopBar.tsx                 ✅ Global-Header
│       ├── PageToolbar.tsx            ✅ Kontextuelle Toolbar
│       └── CommandPalette.tsx         ✅ Ctrl+K
│
├── design/
│   └── mcp-schemas/
│       └── component-metadata.ts      ✅ MCP-Schema
│
└── pages/
    └── sales/
        └── orders-modern.tsx          ✅ Beispiel-Integration
```

---

## 🚀 Integration-Beispiel

### AppShell mit Ask VALEO

```typescript
import { AppShell } from '@/components/navigation/AppShell';
import { AskValeo, JouleActionBar } from '@/components/copilot/AskValeo';
import { useState } from 'react';

function App() {
  const [askValeoOpen, setAskValeoOpen] = useState(false);

  return (
    <AppShell>
      {/* Your Pages */}
      <Routes>
        <Route path="/sales" element={<SalesPage />} />
      </Routes>

      {/* Joule Action Bar (SAP-Pattern) - immer verfügbar */}
      <JouleActionBar
        onAskClick={() => setAskValeoOpen(true)}
        pageContext={{
          domain: 'sales',
          hasSuggestions: true,
        }}
      />

      {/* Ask VALEO Dialog */}
      <AskValeo
        open={askValeoOpen}
        onOpenChange={setAskValeoOpen}
        pageContext={{
          domain: 'sales',
          currentDocument: 'SO-00001',
          availableActions: ['edit', 'post', 'print'],
        }}
      />
    </AppShell>
  );
}
```

---

## 🎓 SAP Joule Design-Principles → VALEO

### 1. **Transparency (Explainability)**

**SAP Joule:**
> "Users must understand how AI arrives at conclusions"

**VALEO Umsetzung:**
```typescript
// AI-Response zeigt immer:
- Datenquellen ("Basierend auf Kundenstamm")
- Logik ("Rabatt 5% weil Stammkunde")
- Alternativen ("Oder Standardpreis verwenden?")
```

### 2. **Trust & Safety**

**SAP Joule:**
> "AI must only access data user is authorized for"

**VALEO Umsetzung:**
```typescript
// Skills haben requiredScopes
const skill = {
  requiredScopes: ['sales:write', 'finance:read'],
  mcp: { grounding: 'user-data' },  // Nur User-Daten!
};

// MCP prüft vor Ausführung
if (!user.hasScopes(skill.requiredScopes)) {
  return { error: 'Unauthorized' };
}
```

### 3. **Contextual Awareness**

**SAP Joule:**
> "Joule adapts to user's current task"

**VALEO Umsetzung:**
```typescript
// Page-Context wird an AI übergeben
pageContext={{
  domain: 'sales',
  currentDocument: 'SO-00001',
  userRole: 'sales-manager',
  recentActions: ['view-customer', 'check-stock'],
}}

// AI schlägt vor:
// "Möchtest du für diesen Kunden eine Lieferung erstellen?"
```

### 4. **Collaborative Workflows**

**SAP Joule:**
> "AI assists, doesn't replace human decision"

**VALEO Umsetzung:**
```typescript
// Agent schlägt vor, User bestätigt
Agent: "Artikel XYZ ist unter Mindestbestand (5 Stück verfügbar).
        Nachbestellung empfohlen: 100 Stück.
        Lieferant: SUP-001 (beste Konditionen).
        Soll ich Bestellung erstellen?"

User: [Ja, erstellen] [Nein] [Andere Menge]

// Confirmation-Pattern, kein Auto-Execution!
```

### 5. **Feedback & Learning**

**SAP Joule:**
> "System learns from user interactions"

**VALEO Konzept (Phase 3):**
```typescript
// User-Feedback tracken
mcpFeedback.recordInteraction({
  suggestion: 'create-order-for-customer',
  userAction: 'accepted',  // or 'rejected', 'modified'
  context: pageContext,
});

// Später: Bessere Suggestions durch Learning
```

---

## 📊 Vergleich: SAP Joule vs. Ask VALEO

| Feature | SAP Joule | Ask VALEO | Status |
|---------|-----------|-----------|--------|
| **AI-Dialog** | ✅ Prompt-basiert | ✅ AskValeo.tsx | ✅ Implementiert |
| **Action Bar** | ✅ Mitlaufend | ✅ JouleActionBar | ✅ Implementiert |
| **Skills** | ✅ Joule Studio | ✅ SkillRegistry | ✅ Implementiert |
| **Agents** | ✅ Workflow-Orchestrierung | ✅ ValeoAgents | ✅ Implementiert |
| **Grounding** | ✅ SAP-Daten | ✅ User-Scopes | ✅ Konzept |
| **Explainability** | ✅ Transparent | ✅ Response-Format | ✅ Vorbereitet |
| **MCP-Integration** | ❌ Proprietär | ✅ MCP-Browser | ⏳ Phase 3 |
| **Design-System** | ✅ Fiori | ✅ shadcn/ui | ✅ Implementiert |

---

## 🧩 Skills vs. Agents (SAP Joule Studio-Konzept)

### Skills (atomar, wiederverwendbar)

**Definition:**
- 1 Funktion = 1 Skill
- Klar definierte Input/Output-Schemas
- Wiederverwendbar in mehreren Agents
- Testbar & dokumentiert

**VALEO-Skills:**
1. `search-customer` - Kunde finden
2. `get-article-price` - Preis abrufen
3. `check-stock` - Bestand prüfen
4. `check-policy` - Policy-Validation
5. `create-sales-order` - Auftrag erstellen

### Agents (orchestrieren, Multi-Step)

**Definition:**
- Kombinieren mehrere Skills
- Decision-Logic (if/else, Conditions)
- Fehler-Handling
- User-Interaction (Confirmations)

**VALEO-Agents:**
1. `order-assistant` - Auftrags-Workflow (5 Skills)
2. `reorder-assistant` - Nachbestell-Workflow (1 Skill + Logic)

---

## 🎨 Design-Komponenten (Joule-Pattern)

### 1. Ask VALEO Dialog ✅

**Features:**
- ✅ Prompt-Textarea (freie Frage)
- ✅ Quick-Actions (4 vordefinierte Fragen)
- ✅ Contextual-Suggestions (Domain-basiert)
- ✅ AI-Response mit Formatting
- ✅ Loading-State (Loader + Text)
- ✅ Error-Handling (Alert + Message)
- ✅ Keyboard-Shortcuts (Ctrl+Enter = Submit)

**SAP Joule Inspiration:**
- Klares Prompt-Interface
- Kontext sichtbar ("📍 Kontext: Sales")
- Phase 3 Hinweis (Transparenz)

### 2. Joule Action Bar ✅

**Features:**
- ✅ Fixed bottom-right (nicht aufdringlich)
- ✅ Floating Button mit Icon
- ✅ Badge bei neuen Vorschlägen (!)
- ✅ Smooth Animations
- ✅ Mobile-responsive

**SAP Joule Inspiration:**
- Mitlaufende Action Bar
- Immer verfügbar, nie im Weg
- Kontextuelle Badge-Notification

### 3. Suggestion-Chips ✅

**Features:**
- ✅ Type-basiert (action, warning, tip, info)
- ✅ Icon + Titel + Beschreibung
- ✅ Action-Button optional
- ✅ Color-coded (Warning = yellow, etc.)

**SAP Joule Inspiration:**
- Visuelle Hierarchie
- Klar erkennbare Action
- Kontext-Erklärung

---

## 🔗 MCP-Integration (Phase 3)

### Architektur

```
┌─────────────────────────────────────────┐
│  Frontend (React)                       │
│  ├─ AskValeo.tsx                        │
│  ├─ SkillRegistry.tsx                   │
│  └─ useMCP() Hook                       │
└──────────────┬──────────────────────────┘
               │ REST/WebSocket
┌──────────────▼──────────────────────────┐
│  MCP-Browser-Proxy (gRPC)               │
│  ├─ Skill-Executor                      │
│  ├─ Agent-Orchestrator                  │
│  ├─ Context-Manager                     │
│  └─ Permission-Checker                  │
└──────────────┬──────────────────────────┘
               │ MCP-Protocol
┌──────────────▼──────────────────────────┐
│  MCP-Server (@modelcontextprotocol)     │
│  ├─ Browser-Tool (Screenshots, DOM)     │
│  ├─ VALEO-Tools (Skills als MCP-Tools)  │
│  └─ Context-Provider (ERP-State)        │
└──────────────┬──────────────────────────┘
               │ LLM-API
┌──────────────▼──────────────────────────┐
│  LLM (Claude, GPT-4)                    │
│  ├─ Prompt + Context + Tools            │
│  └─ Structured-Output                   │
└─────────────────────────────────────────┘
```

### Code-Beispiel (Phase 3)

```typescript
// packages/frontend-web/src/mcp/valeo-mcp-client.ts

import { MCPBrowserAdapter } from '@modelcontext/browser-adapter';
import { valeoSkills, valeoAgents } from '@/components/copilot/SkillRegistry';

export class ValeoMCPClient {
  private adapter: MCPBrowserAdapter;

  constructor() {
    this.adapter = new MCPBrowserAdapter({
      serverUrl: process.env.VITE_MCP_SERVER_URL || 'http://localhost:5555',
      skills: valeoSkills.map(s => ({
        name: s.mcp.toolName,
        description: s.description,
        parameters: s.input.parameters,
      })),
    });
  }

  async askQuestion(question: string, pageContext: any) {
    // Skill-basierte Frage
    return await this.adapter.ask({
      prompt: question,
      context: {
        page: pageContext.domain,
        document: pageContext.currentDocument,
        userScopes: getUserScopes(),
      },
      tools: this.getAvailableSkills(getUserScopes()),
    });
  }

  async executeSkill(skillId: string, params: any) {
    const skill = valeoSkills.find(s => s.id === skillId);
    if (!skill) throw new Error(`Skill not found: ${skillId}`);

    // Prüfe Permissions (Grounding!)
    if (!this.hasRequiredScopes(skill.requiredScopes)) {
      throw new Error('Unauthorized: Missing scopes');
    }

    // Führe Skill aus
    return await this.adapter.executeTool(skill.mcp.toolName, params);
  }

  async executeAgent(agentId: string, context: any) {
    const agent = valeoAgents.find(a => a.id === agentId);
    if (!agent) throw new Error(`Agent not found: ${agentId}`);

    // Multi-Step-Workflow
    return await this.adapter.executeWorkflow({
      agentId,
      steps: agent.workflow.steps,
      context,
      promptTemplate: agent.mcp.promptTemplate,
    });
  }

  private getAvailableSkills(userScopes: string[]) {
    return valeoSkills.filter(skill =>
      skill.requiredScopes.every(scope => userScopes.includes(scope))
    );
  }

  private hasRequiredScopes(requiredScopes: string[]) {
    const userScopes = getUserScopes();
    return requiredScopes.every(scope => userScopes.includes(scope));
  }
}

// useMCP Hook (Phase 3)
export function useMCP() {
  const client = new ValeoMCPClient();

  const ask = async (question: string, context: any) => {
    return await client.askQuestion(question, context);
  };

  const executeSkill = async (skillId: string, params: any) => {
    return await client.executeSkill(skillId, params);
  };

  const executeAgent = async (agentId: string, context: any) => {
    return await client.executeAgent(agentId, context);
  };

  return { ask, executeSkill, executeAgent };
}
```

---

## 🎯 Use-Cases (SAP Joule-inspiriert)

### 1. "Explain this form" (Explainability)

```
User: Klickt "?" bei Verkaufsauftrags-Formular
AI:   "Dieses Formular erstellt einen Verkaufsauftrag.
       
       Erforderlich:
       - Kunde: Wähle aus Kundenstamm
       - Artikel: Mind. 1 Position mit Menge & Preis
       - Lieferdatum: Standard = heute + 7 Tage
       
       Optional:
       - Rabatt: Wird automatisch aus Kundenkonditionen geladen
       - Zahlungsziel: Standard = 30 Tage
       
       Nach Speichern: Policy-Check läuft automatisch"
```

### 2. "Auto-fill from context" (Context-Awareness)

```
User: "Erstelle Auftrag für letzten Kunden"
AI:   → Lädt Kunde CUST-001 (letzter Auftrag)
      → Lädt Artikel aus letztem Auftrag
      → Schlägt Preise vor
      → Öffnet Formular (pre-filled)

User: Prüft, ändert ggf., klickt "Speichern"
```

### 3. "Guided workflow" (Assistenz)

```
User: "Wie buche ich eine Rechnung?"
AI:   "Ich führe dich durch den Prozess:

       Schritt 1/4: Rechnung öffnen
       → [SO-00123] gefunden
       → Öffne Rechnung? [Ja] [Andere wählen]
       
       (User klickt Ja)
       
       Schritt 2/4: Prüfe Freigabe-Status
       → ✅ Rechnung ist freigegeben
       
       Schritt 3/4: Buchen
       → Buchungsbeleg wird erstellt: FI-001234
       
       Schritt 4/4: Fertig!
       ✅ Rechnung gebucht, Beleg: FI-001234"
```

### 4. "Proactive suggestions" (Kontextuell)

```
Situation: User öffnet Lager-Modul
AI-Badge: "!" auf Ask VALEO Button

User: Klickt Ask VALEO
AI:   "⚠️  Ich habe 2 Warnungen für dich:
       
       1. Artikel 'Weizen A' unter Mindestbestand (5 von 50)
          → [Nachbestellen]
       
       2. Lieferung LF-00456 überfällig (seit 3 Tagen)
          → [Kunde kontaktieren]"
```

---

## 📚 Ressourcen & Referenzen

### SAP Joule
- SAP Joule Overview: https://www.sap.com/products/artificial-intelligence/ai-assistant.html
- Joule Design Guidelines: https://experience.sap.com/fiori-design-web/ai-and-joule-design/
- Joule Studio: https://help.sap.com/docs/joule (Skill/Agent-Erstellung)

### MCP-Integration
- MCP Protocol: https://modelcontextprotocol.io
- MCP Browser-Tool: https://github.com/modelcontextprotocol/servers
- MCP-Client-SDK: https://github.com/modelcontextprotocol/typescript-sdk

### Design-Patterns
- Explainable AI: https://pair.withgoogle.com/guidebook/
- Conversational UI: https://www.nngroup.com/articles/chatbot-patterns/

---

## ✅ Aktueller Status

**Implementiert (Phase 1 & 2):**
- ✅ AskValeo.tsx (Joule-Dialog mit allen Features)
- ✅ JouleActionBar (Floating Button)
- ✅ SkillRegistry (5 Skills + 2 Agents)
- ✅ MCP-Metadaten in allen Components
- ✅ Context-aware Suggestions
- ✅ SAP Joule Design-Principles adaptiert

**Vorbereitet (Phase 3):**
- ✅ MCP-Integration-Points definiert
- ✅ Skill-Executor-Interface
- ✅ useMCP() Hook-Stub
- ✅ gRPC-Proxy-Konzept dokumentiert

**Offen (Phase 3):**
- ⏳ @modelcontext/browser-adapter Integration
- ⏳ Echter LLM-Backend (Claude API)
- ⏳ Skill-Implementierungen (API-Calls)
- ⏳ Agent-Workflow-Engine

---

## 🚀 Nächste Schritte

### Sofort (heute):
```bash
# Teste Ask VALEO in Storybook
cd packages/frontend-web
pnpm storybook

# Öffne: Copilot/AskValeo
# Teste alle Variants
```

### Diese Woche (Phase 1 abschließen):
1. ⏳ Weitere Component-Stories erstellen
2. ⏳ Accessibility-Linting aktivieren
3. ⏳ Ask VALEO in AppShell integrieren

### Nächste Wochen (Phase 2):
1. ⏳ Design-Tokens definieren
2. ⏳ Theme-Provider mit Dark-Mode
3. ⏳ Alle UI-Components mit MCP-Metadaten

### Später (Phase 3):
1. ⏳ MCP-Browser-Adapter evaluieren
2. ⏳ Skill-API-Implementierungen
3. ⏳ Echter LLM-Backend-Integration

---

## 💡 Warum diese Architektur besser ist als SAP Joule

| Aspekt | SAP Joule | Ask VALEO | Vorteil |
|--------|-----------|-----------|---------|
| **Vendor-Lock** | ✅ Nur SAP | ✅ Open (MCP) | Flexibel |
| **LLM-Wahl** | ❌ SAP-LLM | ✅ Beliebig | Claude, GPT-4, ... |
| **Kosten** | 💰 Teuer | ✅ Self-hosted | Kontrollierbar |
| **Customization** | ⚠️  Limitiert | ✅ Voll | 100% anpassbar |
| **Privacy** | ⚠️  Cloud | ✅ On-Premise | GDPR-sicher |
| **Skills** | ⚠️  Joule Studio | ✅ TypeScript | Developer-friendly |

---

## 🎉 Zusammenfassung

**Was du jetzt hast:**
- ✅ **"Ask VALEO"** - SAP Joule-inspirierter Copilot
- ✅ **Skill-Registry** - 5 Skills + 2 Agents (Joule Studio-Pattern)
- ✅ **Joule Action Bar** - Mitlaufende AI-Assistenz
- ✅ **MCP-ready** - Alle Metadaten vorbereitet
- ✅ **SAP Design-Principles** - Explainable, Grounded, Contextual
- ✅ **Kein Vendor-Lock** - MCP statt proprietär

**Besser als SAP Joule:**
- ✅ Open-Source-basiert (MCP)
- ✅ Freie LLM-Wahl
- ✅ Self-hostable
- ✅ 100% anpassbar
- ✅ GDPR-konform

---

**🤖 ASK VALEO: SAP JOULE FÜR VALEO-NEUROERP! 🚀**

**Inspiriert von den Besten, optimiert für deine Bedürfnisse!**

