# Masken-Referenz: Lieferschein-Erfassungsmaske

## Übersicht

Diese Dokumentation dient als Referenz für die Implementierung weiterer Eingabemasken im VALEO NeuroERP System. Sie beschreibt die vollständige Implementierung der Lieferschein-Erfassungsmaske (1:1 nach zvoove ERP) und definiert Best Practices, Patterns und Architektur-Entscheidungen.

**Erstellt:** 2025-02-16  
**Status:** ✅ Vollständig implementiert  
**Referenz:** zvoove ERP Lieferschein-Erfassungsmaske

---

## 📋 Inhaltsverzeichnis

1. [Architektur & Struktur](#architektur--struktur)
2. [Datenstrukturen](#datenstrukturen)
3. [API-Integrationen](#api-integrationen)
4. [UI-Komponenten](#ui-komponenten)
5. [Keyboard-Shortcuts](#keyboard-shortcuts)
6. [State-Management](#state-management)
7. [Validierungen & Business-Logic](#validierungen--business-logic)
8. [Best Practices](#best-practices)
9. [Code-Beispiele](#code-beispiele)

---

## 🏗️ Architektur & Struktur

### Datei-Struktur

```
packages/frontend-web/src/
├── pages/verkauf/
│   └── lieferschein-erfassung.tsx          # Hauptkomponente
├── components/sales/
│   ├── CustomerSelectionDialog.tsx         # Kundenauswahl-Dialog
│   ├── ArtikelSuchDialog.tsx               # Artikelauswahl-Dialog
│   ├── LieferscheinDruckDialog.tsx         # Druck-Dialog
│   └── AttestationDialog.tsx                # Bestätigungs-Dialog
├── components/shortcuts/
│   ├── GlobalShortcutProvider.tsx          # Globaler Shortcut-Provider
│   └── ShortcutHelpPanel.tsx               # Shortcut-Hilfe-Panel
└── lib/shortcuts/
    └── global-shortcuts.ts                 # Shortcut-Definitionen
```

### Backend-Struktur

```
app/api/v1/endpoints/
├── sales_delivery_notes.py                 # Lieferschein-CRUD
├── sales_orders.py                         # Bestellungen (erweitert)
├── branches.py                             # Niederlassungen
└── pricing.py                              # Preisberechnung
```

---

## 📊 Datenstrukturen

### Frontend State (`LieferscheinState`)

```typescript
type LieferscheinState = {
  id: string | null                          // UUID vom Backend
  lieferscheinNr: string                    // Vom Backend generiert (read-only)
  niederlassung: number                      // Gemappt zu branch_id
  vertreter: string                          // Sales-Rep (read-only)
  bediener: string                           // Operator (read-only)
  lieferDatum: string                        // Format: yyyy-MM-dd
  uhrzeit: string                            // Format: HH:mm
  kostenstelle: number                       // Cost Center (read-only)
  lkwNr: number                              // Truck Number (read-only)
  gutschriftKennz: boolean                  // Credit Note Flag
  selbstabholung: boolean                    // Self-Pickup Flag
  fruehbezugRechnung: boolean               // Early Payment Flag
  reNrBezug: string                          // Reference Invoice (read-only)
  statusGedruckt: boolean                    // Printed Status
  statusAusgeliefert: boolean                // Delivered Status
  fakturiertRechnNr: string                  // Invoice Number (read-only, Backend-generiert)
  customer: Customer | null                  // Ausgewählter Kunde
  positionen: Position[]                      // Lieferschein-Positionen
  aktivePositionIndex: number | null         // Aktuell ausgewählte Position
}
```

### Position Type

```typescript
export type Position = {
  posNr: number                              // Positionsnummer (10, 20, 30, ...)
  artikelNr: string                          // Artikelnummer
  artikelId: string | null                   // Artikel-UUID (für Backend)
  bezeichnung: string                        // Artikelbezeichnung
  bezeichnung2: string                       // Zweite Bezeichnung
  menge: number                              // Menge
  einheit: string                            // Einheit (Stk, kg, etc.)
  listenpreis: number                        // Listenpreis
  rabatt: number                             // Rabatt in Prozent
  art: string                                // Art
  nettoPreis: number                         // Netto-Preis (berechnet)
  nettoBetrag: number                        // Netto-Betrag (berechnet)
  niederlassung: string                      // Niederlassung
  lagerhalle: string                         // Lagerhalle
  lagerfach: string                          // Lagerfach
  charge: string                             // Charge
  serienNr: string                           // Seriennummer
  gefPunkt: string                           // Gefahrgut-Punkte (String für Anzeige)
  gefahrgutPunkte: number                   // Gefahrgut-Punkte pro Einheit
  gesamtGefahrgutPunkte: number             // Gesamt-Gefahrgut-Punkte
  naBio: string                              // NA/Bio
  musterNr: string                           // Musternummer
  strecke: string                            // Strecke
  zusBeleg: string                           // Zusatzbeleg
  anerken: string                            // Anerkennung
  erloskonto: string                         // Erlöskonto
  mwstProzent: number                       // MWSt-Satz
  gewicht: number                            // Gewicht pro Einheit
  gesamtGewicht: number                      // Gesamtgewicht
  kontraktNr: string                         // Vertragsnummer
  skontierf: boolean                         // Skontierfähig
  fremdware: boolean                         // Fremdware
}
```

### Backend Response (`DeliveryNoteResponse`)

```typescript
type DeliveryNoteResponse = {
  id: string
  delivery_note_number: string               // Vom Backend generiert
  customer_id: string | null
  branch_id: string | null                   // UUID der Niederlassung
  sales_rep_id: string | null                // UUID des Vertreters
  operator_id: string | null                 // UUID des Operators
  delivery_date: string                      // ISO Date
  delivery_time: string | null               // HH:mm:ss
  cost_center_id: string | null
  truck_number: number | null
  is_credit_note: boolean
  is_self_pickup: boolean
  is_early_payment: boolean
  reference_invoice_number: string | null
  status: string                             // 'draft', 'posted', etc.
  is_printed: boolean
  is_delivered: boolean
  invoice_number: string | null               // Vom Backend nach Fakturierung gesetzt
  positionen: Array<{
    id: string
    delivery_note_id: string
    pos_nr: number
    artikel_id: string | null
    artikel_nr: string | null
    bezeichnung: string | null
    bezeichnung2: string | null
    menge: number
    einheit: string | null
    listenpreis: number | null
    rabatt: number
    art: string | null
    netto_preis: number | null
    netto_betrag: number | null
    niederlassung: number | null
    lagerhalle: string | null
    lagerfach: string | null
    charge: string | null
    serien_nr: string | null
    erloskonto: string | null
    mwst_prozent: number
    kontrakt_nr: string | null
    skontierf: boolean
    fremdware: boolean
    gef_punkt: string | null
    na_bio: string | null
    muster_nr: string | null
    strecke: string | null
    zus_beleg: string | null
    anerken: string | null
    created_at: string
    updated_at: string
  }>
}
```

---

## 🔌 API-Integrationen

### Backend-Endpoints

#### 1. Lieferschein-CRUD

**Erstellen:**
```typescript
POST /api/v1/sales/delivery-notes
Body: DeliveryNoteCreate
Response: DeliveryNote
```

**Abrufen:**
```typescript
GET /api/v1/sales/delivery-notes/{ls_id}
Response: DeliveryNote
```

**Aktualisieren:**
```typescript
PUT /api/v1/sales/delivery-notes/{ls_id}
Body: DeliveryNoteUpdate
Response: DeliveryNote
```

**Liste:**
```typescript
GET /api/v1/sales/delivery-notes?customer_id={id}&status={status}
Response: DeliveryNote[]
```

**Letzter Lieferschein (für "Wie vorheriger Beleg"):**
```typescript
GET /api/v1/sales/delivery-notes/last?operator_id={id}&customer_id={id}
Response: DeliveryNote | null
```

#### 2. Kunden

```typescript
GET /api/v1/crm/customers
GET /api/v1/crm/customers/{id}
```

#### 3. Artikel

```typescript
GET /api/v1/articles
GET /api/v1/articles/{id}
```

#### 4. Preisberechnung

```typescript
GET /api/v1/pricing/calculate?article_id={id}&customer_id={id}&quantity={qty}
Response: {
  list_price: number
  discount: number
  net_price: number
  source: string
  price_list_id: string | null
  contract_id: string | null
}
```

#### 5. Bestellungen

```typescript
GET /api/v1/sales/orders?customer_id={id}
Response: PaginatedResponse<SalesOrder>
```

#### 6. Niederlassungen

```typescript
GET /api/v1/admin/branches
GET /api/v1/admin/branches/{id}
```

### API-Client Verwendung

```typescript
import { apiClient } from '@/lib/axios'

// GET Request
const response = await apiClient.get<DeliveryNoteResponse>(
  `/api/v1/sales/delivery-notes/${id}`
)

// POST Request
const response = await apiClient.post<DeliveryNote>(
  '/api/v1/sales/delivery-notes',
  payload
)

// Query Parameters
const response = await apiClient.get<any>('/api/v1/sales/orders', {
  params: {
    customer_id: customerId,
    limit: 10,
  },
})
```

---

## 🎨 UI-Komponenten

### Hauptkomponente

**Datei:** `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx`

**Struktur:**
- Header mit Lieferschein-Nummer und Status
- Tabs für Kunden-Details (Kunde, Lieferanschrift, Rechnungsanschrift, Bestellung, etc.)
- Positionen-Tabelle
- Positions-Details (aktuelle Position)
- Summen-Bereich
- Toolbar mit Aktionen

### Dialog-Komponenten

#### CustomerSelectionDialog
- **Zweck:** Kundenauswahl mit Suche und Filterung
- **Features:**
  - Client-side Suche (Wildcard-Support)
  - Tabs: ALL, PROSPECTS, ACTIVE, FORMER
  - Erweiterte Suche (alle Felder)
  - Sortierung alphabetisch

#### ArtikelSuchDialog
- **Zweck:** Artikelauswahl mit Suche
- **Features:**
  - Client-side Suche über mehrere Felder
  - Filter: Blockiert, Zweck, EAN, Verpackung, etc.
  - Tabs für verschiedene Artikel-Ansichten

#### LieferscheinDruckDialog
- **Zweck:** Druck-Konfiguration
- **Features:**
  - Drucker-Auswahl
  - Formular-Vorlage
  - Anzahl Kopien
  - Sortierung
  - Checkboxen für Druck-Inhalt

#### AttestationDialog
- **Zweck:** Bestätigung bei Änderungen an gebuchten Belegen
- **Features:**
  - Grund-Eingabe
  - Aktion-Auswahl (print, modify, cancel, post, reopen)

### Layout-Komponenten

- **Card:** Container für Bereiche
- **Tabs:** Tab-Navigation (Radix UI)
- **Table:** Positionen-Tabelle
- **Input:** Eingabefelder
- **Button:** Aktionen
- **Label:** Feldbeschriftungen

---

## ⌨️ Keyboard-Shortcuts

### Globale Shortcuts

Das System verwendet ein zentrales Shortcut-System (`global-shortcuts.ts`), das konsistent über alle Masken hinweg funktioniert.

**Standard-Shortcuts:**

| Shortcut | Aktion | Handler |
|----------|--------|---------|
| **Strg+F1** | Kundenauswahl öffnen | `open-customer-selection` |
| **Strg+F2** | Artikelauswahl öffnen | `open-article-selection` |
| **Strg+F3** | Position OK | `confirm-position` |
| **Strg+F4** | Dokument speichern | `save-document` |
| **Strg+F5** | Dokument drucken | `print-document` |
| **Strg+F6** | Dokument löschen | `delete-document` |
| **Strg+F7** | Dokument schließen | `close-document` |
| **Strg+F8** | Wie vorheriger (nur Positionen) | `copy-previous-positions` |
| **Strg+F9** | Sofort-Rechnung | `create-invoice` |
| **Strg+F10** | Unterlagen | `open-attachments` |
| **F11** | Wie vorheriger Beleg (alle Daten) | `copy-previous-full` |
| **Strg+F12** | Information | `show-information` |
| **Esc** | Abbrechen | `cancel` |

### Implementation

```typescript
import { useGlobalShortcuts } from '@/lib/shortcuts/global-shortcuts'

useGlobalShortcuts({
  'open-customer-selection': () => setShowCustomerDialog(true),
  'open-article-selection': () => setShowArticleDialog(true),
  'confirm-position': () => handlePositionOK(),
  'save-document': () => void handleSave(),
  'print-document': () => setShowPrintDialog(true),
  'close-document': () => navigate(-1),
  'copy-previous-full': async () => {
    // Implementierung
  },
  // ...
})
```

### Shortcut-Hilfe-Panel

- **Anzeige-Modi:**
  - `always`: Immer sichtbar (für Anfänger)
  - `hover`: Erscheint bei Hover (für Geübte)
  - `hidden`: Versteckt (für Experten)
- **Toggle:** `Strg+N` zyklisch durch Modi
- **Position:** Rechts am Bildschirmrand

---

## 🔄 State-Management

### React Hooks

**useState:**
- Haupt-State (`LieferscheinState`)
- Dialog-States
- Current Position Details
- Bestellungen

**useMemo:**
- Summen-Berechnung (Netto, MWSt, Brutto, Gewicht, Gefahrgut-Punkte)
- Gefilterte Kunden/Artikel (Client-side)

**useEffect:**
- Laden bestehender Lieferscheine (URL-Parameter)
- Berechnung abgeleiteter Felder (Preis, Betrag)
- Keyboard-Shortcut-Registrierung

**useCallback:**
- Event-Handler (optional, für Performance)

### State-Updates

```typescript
// Einfaches Update
setState((prev) => ({
  ...prev,
  niederlassung: newValue,
}))

// Komplexes Update mit Validierung
setState((prev) => {
  if (validation) {
    return { ...prev, field: newValue }
  }
  return prev
})
```

---

## ✅ Validierungen & Business-Logic

### Frontend-Validierungen

#### 1. Pflichtfelder
```typescript
if (!state.customer) {
  push('Bitte wählen Sie einen Kunden aus')
  return
}

if (state.positionen.length === 0) {
  push('Bitte fügen Sie mindestens eine Position hinzu')
  return
}
```

#### 2. Gefahrgut-Punkte Validierung
```typescript
const newTotalGefahrgutPunkte = summen.gefahrgutPunkte + gesamtGefahrgutPunkte
if (newTotalGefahrgutPunkte > 1000) {
  push(`Fehler: Gesamt-Gefahrgut-Punkte (${newTotalGefahrgutPunkte.toFixed(2)}) überschreiten das Limit von 1000.`)
  return
}
```

#### 3. Preisberechnung
```typescript
// Netto-Preis = Listenpreis × (1 - Rabatt / 100)
const nettoPreis = currentPosition.listenpreis * (1 - currentPosition.rabatt / 100)

// Netto-Betrag = Netto-Preis × Menge
const nettoBetrag = nettoPreis * currentPosition.mengeGebinde
```

#### 4. Summen-Berechnung
```typescript
const summen = useMemo(() => {
  const netto = state.positionen.reduce((sum, pos) => sum + pos.nettoBetrag, 0)
  const mwst = state.positionen.reduce((sum, pos) => {
    const mwstBetrag = (pos.nettoBetrag * pos.mwstProzent) / 100
    return sum + mwstBetrag
  }, 0)
  const brutto = netto + mwst
  const gesamtGewicht = state.positionen.reduce((sum, pos) => sum + (pos.gesamtGewicht || 0), 0)
  const gesamtGefahrgutPunkte = state.positionen.reduce((sum, pos) => sum + (pos.gesamtGefahrgutPunkte || 0), 0)
  
  return { netto, mwst, brutto, gesamt: brutto, gewicht: gesamtGewicht, gefahrgutPunkte: gesamtGefahrgutPunkte }
}, [state.positionen])
```

### Backend-Validierungen

- Lieferschein-Nummer wird automatisch generiert
- Rechnungsnummer wird nach Fakturierung vom Backend gesetzt
- Totals werden im Backend berechnet und validiert

---

## 🎯 Best Practices

### 1. Read-Only Felder

Felder, die nur vom System gesetzt werden dürfen:
- `lieferscheinNr`: Backend-generiert
- `fakturiertRechnNr`: Backend-generiert nach Fakturierung
- `vertreter`: Aus Kunden-Stammdaten
- `bediener`: Aus Session
- `niederlassung`: Aus User-Context (optional)
- `kostenstelle`: Aus User-Context (optional)
- `lkwNr`: Aus User-Context (optional)
- `reNrBezug`: Aus vorherigem Beleg (optional)

**Implementation:**
```typescript
<Input
  value={state.lieferscheinNr}
  readOnly
  className="bg-muted cursor-not-allowed"
  title="Wird automatisch vom System vergeben"
/>
```

### 2. Datum-Formatierung

**Input-Feld:** `yyyy-MM-dd` (HTML5 date input)
**Anzeige:** `dd.MM.yyyy` (deutsches Format)
**Backend:** ISO Date String

```typescript
const formatDateForInput = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
```

### 3. Mapping zwischen Frontend und Backend

**Niederlassung:**
- Frontend: `niederlassung: number` (0, 1, 2, ...)
- Backend: `branch_id: string` (UUID)
- Mapping über Branches-API mit Caching

```typescript
const getBranchId = async (niederlassung: number): Promise<string | null> => {
  // Cache prüfen
  if (branchCache.has(niederlassung)) {
    return branchCache.get(niederlassung) || null
  }
  
  // API-Call
  const branches = await apiClient.get<any[]>('/api/v1/admin/branches')
  const branch = branches.find((b: any) => b.branch_number === niederlassung)
  
  if (branch) {
    setBranchCache((prev) => new Map(prev).set(niederlassung, branch.id))
    return branch.id
  }
  
  return null
}
```

### 4. Error Handling

```typescript
try {
  const response = await apiClient.post('/api/v1/sales/delivery-notes', payload)
  push('Lieferschein erfolgreich gespeichert')
} catch (error: any) {
  // eslint-disable-next-line no-console
  console.error('Fehler beim Speichern:', error)
  push(`Fehler: ${error.response?.data?.detail || error.message}`)
}
```

### 5. Loading States

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['delivery-notes', id],
  queryFn: async () => {
    return await apiClient.get(`/api/v1/sales/delivery-notes/${id}`)
  },
  enabled: !!id,
})

if (isLoading) return <Skeleton />
if (error) return <ErrorDisplay error={error} />
```

### 6. Client-Side Filtering

Für bessere UX: Alle Daten einmal laden, dann client-side filtern.

```typescript
const { data: customersData } = useQuery({
  queryKey: ['customers', 'all'],
  queryFn: async () => {
    const response = await apiClient.get('/api/v1/crm/customers', {
      params: { limit: '200' },
    })
    return response.items || response
  },
})

const filteredCustomers = useMemo(() => {
  let result = customersData || []
  
  // Tab-Filter
  if (activeTab === 'active') {
    result = result.filter(c => c.is_active === true)
  }
  
  // Search-Filter
  if (searchTerm) {
    const term = searchTerm.toLowerCase()
    result = result.filter(c =>
      c.name.toLowerCase().includes(term) ||
      c.customerNumber.includes(term)
    )
  }
  
  return result.sort((a, b) => b.name.localeCompare(a.name, 'de'))
}, [customersData, searchTerm, activeTab])
```

---

## 💻 Code-Beispiele

### Vollständige Komponente-Struktur

```typescript
import { useState, useMemo, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/useAuth'
import { useGlobalShortcuts } from '@/lib/shortcuts/global-shortcuts'
import { apiClient } from '@/lib/axios'

export default function MyMaskPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()
  const { user } = useAuth()
  const { id } = useParams<{ id?: string }>()

  // State
  const [state, setState] = useState<MyState>({
    // Initial state
  })

  // Dialogs
  const [showDialog, setShowDialog] = useState(false)

  // Berechnungen
  const summen = useMemo(() => {
    // Berechnungen
    return { /* ... */ }
  }, [state])

  // Laden bestehender Datensatz
  useEffect(() => {
    if (!id) return
    
    const loadData = async () => {
      try {
        const response = await apiClient.get(`/api/v1/my-endpoint/${id}`)
        setState(/* map response */)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Fehler:', error)
        push('Fehler beim Laden')
      }
    }
    
    void loadData()
  }, [id, push])

  // Handler
  const handleSave = async (): Promise<void> => {
    try {
      const payload = {
        // Map state to payload
      }
      
      const response = await apiClient.post('/api/v1/my-endpoint', payload)
      push('Erfolgreich gespeichert')
      
      // Navigate or update state
      navigate(`/my-route/${response.id}`)
    } catch (error: any) {
      // eslint-disable-next-line no-console
      console.error('Fehler:', error)
      push(`Fehler: ${error.response?.data?.detail || error.message}`)
    }
  }

  // Shortcuts
  useGlobalShortcuts({
    'save-document': () => void handleSave(),
    'close-document': () => navigate(-1),
    // ...
  })

  return (
    <div className="flex h-full flex-col p-4">
      {/* Header */}
      {/* Main Content */}
      {/* Dialogs */}
    </div>
  )
}
```

### Dialog-Integration

```typescript
const [showCustomerDialog, setShowCustomerDialog] = useState(false)

const handleCustomerSelect = async (customer: Customer): Promise<void> => {
  setState((prev) => ({
    ...prev,
    customer,
  }))
  
  // Lade abhängige Daten
  try {
    const orders = await apiClient.get('/api/v1/sales/orders', {
      params: { customer_id: customer.id },
    })
    setBestellungen(orders.items || [])
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('Fehler:', error)
  }
}

return (
  <>
    <Button onClick={() => setShowCustomerDialog(true)}>
      Kunde auswählen
    </Button>
    
    <CustomerSelectionDialog
      open={showCustomerDialog}
      onClose={() => setShowCustomerDialog(false)}
      onSelect={handleCustomerSelect}
    />
  </>
)
```

### Preisberechnung mit API

```typescript
const handleArticleSelect = (article: any): void => {
  setCurrentPosition((prev) => ({
    ...prev,
    artikelNr: article.article_number,
    listenpreis: article.sales_price || 0,
  }))
  
  // Lade Listenpreis aus Preisliste
  if (article.id && state.customer?.id) {
    void (async () => {
      try {
        const pricingResponse = await apiClient.get('/api/v1/pricing/calculate', {
          params: {
            article_id: article.id,
            customer_id: state.customer.id,
            quantity: currentPosition.mengeGebinde || 1,
          },
        })
        
        if (pricingResponse.list_price) {
          setCurrentPosition((prev) => ({
            ...prev,
            listenpreis: pricingResponse.list_price,
          }))
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.warn('Fehler beim Abrufen des Listenpreises:', error)
      }
    })()
  }
}
```

---

## 📝 Checkliste für neue Masken

### ✅ Vorbereitung

- [ ] Screenshots/Referenz der Ziel-Maske sammeln
- [ ] Datenfelder analysieren (Input, Linked, Calculated)
- [ ] API-Endpoints identifizieren
- [ ] Datenstrukturen definieren

### ✅ Frontend-Implementierung

- [ ] Hauptkomponente erstellen
- [ ] State-Struktur definieren
- [ ] Dialog-Komponenten implementieren
- [ ] Tab-Navigation (falls benötigt)
- [ ] Tabellen für Listen
- [ ] Eingabefelder mit Validierung
- [ ] Read-Only Felder markieren
- [ ] Berechnungen (useMemo)
- [ ] Error Handling
- [ ] Loading States

### ✅ Backend-Integration

- [ ] API-Endpoints erstellen/erweitern
- [ ] Request/Response Types definieren
- [ ] Validierungen implementieren
- [ ] Business-Logic
- [ ] Error Responses

### ✅ Keyboard-Shortcuts

- [ ] Shortcuts in `global-shortcuts.ts` definieren
- [ ] Handler in Komponente registrieren
- [ ] Shortcut-Hints an Buttons
- [ ] Shortcut-Hilfe-Panel testen

### ✅ Testing

- [ ] CRUD-Operationen testen
- [ ] Validierungen testen
- [ ] Berechnungen verifizieren
- [ ] Shortcuts testen
- [ ] Error-Cases testen

### ✅ Dokumentation

- [ ] Code-Kommentare
- [ ] README/Dokumentation aktualisieren
- [ ] API-Dokumentation

---

## 🔗 Verwandte Dokumentationen

- [MASKEN.md](./MASKEN.md) - Übersicht aller Masken
- [lieferschein-datenfeld-analyse.md](./lieferschein-datenfeld-analyse.md) - Datenfeld-Analyse
- [lieferschein-keyboard-shortcuts.md](./lieferschein-keyboard-shortcuts.md) - Shortcut-Details
- [global-shortcuts-system.md](./global-shortcuts-system.md) - Shortcut-System

---

## 📌 Wichtige Hinweise

1. **Konsistenz:** Alle Masken sollten dem gleichen Pattern folgen
2. **Read-Only Felder:** System-generierte Felder niemals editierbar machen
3. **Validierung:** Immer Frontend UND Backend validieren
4. **Error Handling:** User-freundliche Fehlermeldungen
5. **Performance:** Client-side Filtering für bessere UX
6. **Caching:** API-Responses cachen wo möglich
7. **Shortcuts:** Konsistent über alle Masken hinweg

---

**Letzte Aktualisierung:** 2025-02-16  
**Version:** 1.0  
**Status:** ✅ Referenz-Dokumentation vollständig


