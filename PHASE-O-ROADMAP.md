# 🧾 PHASE O - FORMBUILDER & BELEGFLUSS-ENGINE ROADMAP

## 📋 Übersicht

Nach erfolgreicher Implementierung der **Phasen K-N** (Policy, Auth, Security) ist der nächste logische Fokus die **fachlichen Masken und Belegfolgen** – das Herz des operativen ERP-Workflows.

---

## ✅ **Was bisher erreicht wurde (Phasen K-N):**

### **Phase K - Policy-Framework** ✅
- Alert-Actions mit Workflow-Buttons
- Policy-Engine (Frontend)
- Audit-Logging
- PolicyBadge UI-Komponente

### **Phase L - Policy Manager** ✅
- Frontend Admin-UI (CRUD, Import/Export, Simulator)
- Backend TypeScript (Express + SQLite)
- Backend Python (FastAPI + SQLite)
- WebSocket Realtime-Updates
- DB-Backup/Restore

### **Phase M - Security Hardening & OIDC** ✅
- OIDC Integration mit Auto-JWKS
- Multi-Provider-Support
- Security Headers Middleware
- Correlation Middleware
- Protected Endpoints

### **Phase N - Red Team Lite & IR** ✅
- OWASP ZAP automated scanning
- Multi-scanner pipeline (6 Tools)
- ASVS Level 2 compliance
- Secret rotation automation
- Incident Response Playbook
- Security Dashboard API

---

## 🎯 **Phase O - Ziel:**

**Automatisch generierbare, reaktionsfähige Formulare + Belegnavigator für operative Workflows**

### **Was sind Belegfolgen?**

Im ERP-Kontext ist das die dokumentenbasierte Prozesskette:

| Bereich | Typische Belegfolge |
|---------|---------------------|
| **Einkauf** | Anfrage → Angebot → Bestellung → Wareneingang → Rechnung → Gutschrift |
| **Verkauf** | Angebot → Auftrag → Lieferschein → Rechnung → Zahlung |
| **Produktion** | Produktionsauftrag → Rückmeldung → Fertigmeldung → Lagerumbuchung |
| **Logistik** | Wiegeschein → Lieferschein → Frachtabrechnung |

→ Jeder Beleg erzeugt Folgebelege mit **Verknüpfung, Status und Workflow-Trigger**.

---

## 📊 **Aktueller Stand:**

### **Vorhanden:**
- ✅ BFF-Domain-Matrix (Sales, Contracts, Inventory, etc.)
- ✅ Screenshots & Feldanalysen aus zvoove Handel
- ✅ JSON-Modelle pro Modul (Customer, Supplier, Article)
- ✅ Policy-Engine für Regelprüfung

### **Fehlt:**
- ❌ Masken-Layouts (Eingabe, Anzeige, Folgebeleg)
- ❌ Feld-Mapping ↔ Domain-Model
- ❌ Validierungs- & Workflow-Logik
- ❌ Belegfolgen-Engine

---

## 🧩 **Phase O - Komponenten:**

### **1. Belegfolgen-Engine**
**Funktion:**
- Definiert welcher Beleg welchen Folgebeleg erzeugt
- Beispiel: `sales.order → sales.delivery → sales.invoice`
- Persistiert Metadaten (Status, Verknüpfung, Policy)

**API:**
```typescript
POST /api/mcp/flows/create-follow-up
{
  "sourceId": "order-123",
  "targetType": "delivery",
  "copyFields": ["customer", "items", "address"]
}
```

### **2. Form-Builder**
**Funktion:**
- Liest Domain-Specs (YAML/JSON-Schema)
- Generiert dynamische Eingabemasken
- Shadcn/Tailwind-kompatibel, Typ-sicher

**Komponente:**
```tsx
<FormBuilder
  schema="/api/mcp/form-specs/sales_order"
  data={currentOrder}
  onSubmit={(values) => saveOrder(values)}
  onValidate={(values) => runPolicy("sales", "validate", values)}
/>
```

### **3. UI-Navigation**
**Funktion:**
- Beleg-Explorer: Tree oder Timeline-Ansicht
- Klick auf Beleg → öffnet Eingabemaske (Edit/Read-Mode)
- Folgebelege als Tabs oder Buttons

**Komponente:**
```tsx
<BelegFlowPanel
  documentId="order-123"
  onCreateFollowUp={(type) => createFollowUp(type)}
/>
```

### **4. Regelprüfung**
**Funktion:**
- Policy-Integration (Phase L)
- Beispiel: "Warnung, Marge < 15%"
- Validierung inline, sofortiges Feedback
- Logging in Audit-Trail

**Hook:**
```tsx
const { validate, warnings } = usePolicyValidation("sales.order")
```

### **5. Audit-Trail**
**Funktion:**
- Alle Belegänderungen werden geloggt
- Wer, Wann, Was, Warum
- Integration mit bestehendem Audit-System

---

## 🛠️ **Technische Umsetzung:**

### **Frontend (React/TypeScript):**

```
packages/frontend-web/src/
├── components/
│   ├── FormBuilder/
│   │   ├── FormBuilder.tsx           # Haupt-Komponente
│   │   ├── FieldRenderer.tsx         # Dynamische Felder
│   │   ├── ValidationProvider.tsx    # Policy-Integration
│   │   └── types.ts                  # Form-Spec Types
│   │
│   └── BelegFlow/
│       ├── BelegFlowPanel.tsx        # Flow-Visualisierung
│       ├── BelegTimeline.tsx         # Timeline-Ansicht
│       └── FollowUpButton.tsx        # Folgebeleg-Aktionen
│
├── hooks/
│   ├── useFormSpec.ts                # Lädt Form-Specs
│   ├── usePolicyValidation.ts        # Policy-Hook
│   └── useBelegFlow.ts               # Flow-Navigation
│
└── pages/
    └── documents/
        ├── [type].tsx                # Dynamische Beleg-Seiten
        └── index.tsx                 # Beleg-Übersicht
```

### **Backend (FastAPI):**

```python
# app/documents/
├── models.py                         # Document, DocumentLine, Flow
├── schemas.py                        # Pydantic Schemas
├── service.py                        # Business Logic
├── router.py                         # API Endpoints
└── form_specs/
    ├── sales_order.json              # Form-Spec für Auftrag
    ├── sales_delivery.json           # Form-Spec für Lieferschein
    └── sales_invoice.json            # Form-Spec für Rechnung
```

### **API-Endpoints:**

| Endpoint | Methode | Funktion |
|----------|---------|----------|
| `/api/mcp/documents` | GET | Liste aller Belege |
| `/api/mcp/documents/{id}` | GET | Einzelner Beleg |
| `/api/mcp/documents` | POST | Beleg erstellen |
| `/api/mcp/documents/{id}` | PUT | Beleg aktualisieren |
| `/api/mcp/documents/{id}/follow-up` | POST | Folgebeleg erzeugen |
| `/api/mcp/form-specs/{type}` | GET | Form-Spec laden |
| `/api/mcp/flows` | GET | Alle Flow-Definitionen |
| `/api/mcp/flows/{from}/{to}` | GET | Spezifischer Flow |

---

## 📊 **Datenmodell:**

### **Neue Tabellen:**

```sql
-- Beleg-Header
CREATE TABLE document_header (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,              -- 'order', 'delivery', 'invoice'
    number TEXT UNIQUE NOT NULL,     -- Belegnummer
    status TEXT NOT NULL,            -- 'draft', 'confirmed', 'completed'
    date DATE NOT NULL,
    customer_id TEXT,
    total DECIMAL(10,2),
    ref_id TEXT,                     -- Referenz auf Vorgänger
    next_id TEXT,                    -- Referenz auf Nachfolger
    created_by TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Beleg-Positionen
CREATE TABLE document_line (
    id TEXT PRIMARY KEY,
    header_id TEXT NOT NULL,
    line_number INTEGER,
    article_id TEXT,
    description TEXT,
    quantity DECIMAL(10,3),
    price DECIMAL(10,2),
    vat_rate DECIMAL(5,2),
    total DECIMAL(10,2),
    FOREIGN KEY (header_id) REFERENCES document_header(id)
);

-- Belegfluss-Definitionen
CREATE TABLE document_flow (
    id TEXT PRIMARY KEY,
    from_type TEXT NOT NULL,         -- 'order'
    to_type TEXT NOT NULL,           -- 'delivery'
    relation TEXT,                   -- 'creates', 'references'
    copy_fields TEXT,                -- JSON: ["customer", "items"]
    rules TEXT                       -- JSON: Policy-Regeln
);

-- Form-Specs
CREATE TABLE form_spec (
    id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,            -- 'sales', 'purchase'
    document_type TEXT NOT NULL,     -- 'order', 'invoice'
    json_schema TEXT NOT NULL,       -- JSON-Schema für Form
    version INTEGER DEFAULT 1
);
```

---

## 🚀 **Implementierungs-Schritte:**

### **Schritt 1: Form-Spec-Generator** (Aufwand: Mittel)
**Ziel:** Einlesen aller Domain-Schemas, JSON → UI-Config

**Deliverables:**
- [ ] JSON-Schema-Parser
- [ ] UI-Config-Generator
- [ ] Feld-Type-Mapping (string → Input, enum → Select, etc.)
- [ ] Validierungs-Regeln-Extraktion

### **Schritt 2: Belegfolge-Mapping** (Aufwand: Mittel)
**Ziel:** Technische Abbildung aller Prozessketten

**Deliverables:**
- [ ] Flow-Matrix-Definition (YAML/JSON)
- [ ] Flow-Engine-Implementierung
- [ ] Copy-Rules (welche Felder werden kopiert)
- [ ] Status-Transitions

### **Schritt 3: UI-Renderer** (Aufwand: Hoch)
**Ziel:** Masken generieren + Policy-Integration

**Deliverables:**
- [ ] FormBuilder-Komponente
- [ ] FieldRenderer für alle Feldtypen
- [ ] ValidationProvider mit Policy-Hook
- [ ] BelegFlowPanel-Komponente
- [ ] FollowUp-Button-Logic

### **Schritt 4: Backend-Connector** (Aufwand: Mittel)
**Ziel:** CRUD + Flow-Logik + Audit

**Deliverables:**
- [ ] Document-Service (CRUD)
- [ ] Flow-Service (Folgebeleg-Erzeugung)
- [ ] Form-Spec-API
- [ ] Audit-Integration

### **Schritt 5: UX-Feinschliff** (Aufwand: Gering)
**Ziel:** Filter, Suche, Druck

**Deliverables:**
- [ ] Beleg-Suche & Filter
- [ ] PDF-Export
- [ ] Druckvorlagen
- [ ] Keyboard-Shortcuts

---

## 💡 **Beispiel: Verkaufsprozess**

### **Flow-Definition:**
```yaml
flows:
  - from: sales.quote
    to: sales.order
    copy_fields:
      - customer
      - items
      - delivery_address
      - payment_terms
    rules:
      - validate_customer_credit_limit
      - check_item_availability

  - from: sales.order
    to: sales.delivery
    copy_fields:
      - customer
      - items
      - delivery_address
    rules:
      - check_stock_levels
      - validate_delivery_date

  - from: sales.delivery
    to: sales.invoice
    copy_fields:
      - customer
      - items
      - delivery_date
    rules:
      - validate_delivery_completed
      - calculate_invoice_total
```

### **Form-Spec (sales.order):**
```json
{
  "type": "sales.order",
  "title": "Verkaufsauftrag",
  "fields": [
    {
      "name": "customer",
      "type": "lookup",
      "label": "Kunde",
      "required": true,
      "lookup": "/api/customers"
    },
    {
      "name": "date",
      "type": "date",
      "label": "Auftragsdatum",
      "required": true,
      "default": "today"
    },
    {
      "name": "items",
      "type": "grid",
      "label": "Positionen",
      "columns": [
        { "name": "article", "type": "lookup", "lookup": "/api/articles" },
        { "name": "quantity", "type": "number" },
        { "name": "price", "type": "currency" },
        { "name": "total", "type": "currency", "computed": true }
      ]
    },
    {
      "name": "total",
      "type": "currency",
      "label": "Gesamtsumme",
      "computed": true,
      "readonly": true
    }
  ],
  "actions": [
    { "type": "save", "label": "Speichern" },
    { "type": "follow-up", "target": "sales.delivery", "label": "Lieferschein erstellen" }
  ]
}
```

---

## ✅ **Definition of Done (Phase O):**

- [ ] **Form-Spec-Generator** funktioniert für alle Domains
- [ ] **Belegfolge-Matrix** definiert und implementiert
- [ ] **FormBuilder-Komponente** generiert dynamische Masken
- [ ] **BelegFlowPanel** visualisiert Dokumenten-Flow
- [ ] **Policy-Integration** validiert Eingaben inline
- [ ] **Backend-API** für Documents, Flows, Form-Specs
- [ ] **Audit-Trail** loggt alle Belegänderungen
- [ ] **Beispiel-Prozess** (Angebot → Auftrag → Rechnung) funktioniert
- [ ] **Dokumentation** vollständig

---

## 📚 **Referenzen:**

- **Spec-Kit Integration:** `packages/frontend-web/docs/spec-kit-integration.md`
- **Domain-Specs:** `packages/frontend-web/specs/features/`
- **Policy-Engine:** Phase L Dokumentation
- **Security:** Phase M/N Dokumentation

---

## 🎯 **Nächste Schritte:**

1. **Kick-off Phase O** - Architektur-Review
2. **Form-Spec-Generator** - Prototyp
3. **Belegfolge-Matrix** - Definition
4. **FormBuilder MVP** - Erste Maske
5. **Integration & Testing**

---

**Bereit für Phase O?** 🚀

Soll ich mit der Implementierung beginnen? Ich starte mit:
1. Form-Spec-Generator (JSON-Schema → UI-Config)
2. Beispiel-Flow-Definition (Verkauf)
3. FormBuilder-Komponente (React)
4. Backend-API-Grundgerüst

**Los geht's?** 😊

