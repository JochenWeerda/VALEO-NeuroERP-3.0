# 🔐 TSE-Integration Vergleich & Roadmap

**Datum:** 2025-10-11  
**Referenzen:**
- [fiskaly-sdk-java](https://github.com/fiskaly/fiskaly-sdk-java) (Cloud-TSE, KassenSichV)
- [TSE-Simulator](https://github.com/DeJuPo/TSE-Simulator) (BSI TR-03153)
- [fiskaly-sdk-php](https://github.com/fiskaly/fiskaly-sdk-php)
- [python-tse](https://github.com/bwurst/python-tse)

---

## 📊 VERGLEICH: Mock vs. Real-TSE

| Feature | VALERO Mock-TSE | fiskaly Cloud-TSE | BSI TR-03153 |
|---------|----------------|-------------------|--------------|
| **Signierung** | ✅ Mock (Date.now()) | ✅ Echte Krypto-Signatur | ✅ Zertifiziert |
| **Transaction-Lifecycle** | ❌ Nur Checkout | ✅ Start/Update/Finish | ✅ Start/Update/Finish |
| **Authentifizierung** | ❌ Keine | ✅ API-Key + Secret (JWT) | ✅ Admin/TimeAdmin-Rollen |
| **Client-Registrierung** | ❌ Keine | ✅ TSS/Client-ID | ✅ Pflicht (registerClient) |
| **Offline-Handling** | ❌ Keine | ✅ Queue + Retry | ✅ Anwendungserlass § 146a AO |
| **Persistence** | ❌ Keine | ✅ Cloud | ✅ persistentValues.ser |
| **Export DSFinV-K** | ⚠️ Button (Mock) | ✅ API-Endpoint | ✅ Standard-konform |
| **Log-Storage** | ❌ Keine | ✅ 10 Jahre Cloud | ✅ normalStoring (lokal) |
| **Failure-Handling** | ❌ Keine | ✅ Automatic Retry | ✅ Fehlerspeicher |
| **Compliance** | ❌ Mock | ✅ KassenSichV-zertifiziert | ✅ BSI CC-PP-0105-2019 |

---

## 🏗️ ARCHITEKTUR-VERGLEICH

### **VALERO Mock-TSE (Aktuell):**
```typescript
// POS-Terminal
async function handleCheckout() {
  const tseSignature = {
    transactionNumber: Math.floor(Math.random() * 10000),  // ❌ Nicht fortlaufend
    signature: 'TSE_SIG_' + Date.now(),                    // ❌ Keine Krypto
    timestamp: new Date().toISOString(),
    qrCode: 'V0;VALERO-POS;fiskaly-TSS-12345;...',        // ❌ Kein echter QR
  }
  // ❌ Kein TSE-API-Call
  // ❌ Keine Fehlerbehandlung
  // ❌ Keine Persistence
}
```

### **fiskaly Cloud-TSE (Korrekt):**
```typescript
// 1. Authentifizierung
const client = new FiskalyHttpClient(apiKey, apiSecret, 'https://kassensichv.io/api/v1')

// 2. TSS erstellen/abrufen
const tss = await client.request('PUT', `/tss/${tssId}`)

// 3. Client registrieren
const tseClient = await client.request('PUT', `/tss/${tssId}/client/${clientId}`)

// 4. Transaction starten
const tx = await client.request('PUT', `/tss/${tssId}/tx/${txId}`, {
  state: 'ACTIVE',
  client_id: clientId,
})

// 5. Daten hinzufügen
await client.request('PUT', `/tss/${tssId}/tx/${txId}`, {
  state: 'ACTIVE',
  client_id: clientId,
  schema: {
    standard_v1: {
      receipt: {
        receipt_type: 'RECEIPT',
        amounts_per_vat_rate: [
          { vat_rate: 19, amount: '18.97' }
        ],
        amounts_per_payment_type: [
          { payment_type: 'CASH', amount: '18.97' }
        ],
      }
    }
  }
})

// 6. Transaction beenden
const finishedTx = await client.request('PUT', `/tss/${tssId}/tx/${txId}`, {
  state: 'FINISHED',
  client_id: clientId,
})

// ✅ Echte Signatur:
{
  "number": 7843,
  "time_start": 1728640523,
  "time_end": 1728640530,
  "signature": {
    "value": "MEUCIQDx...",  // Echte ECDSA-Signatur
    "counter": 1234,
    "algorithm": "ecdsa-plain-SHA256"
  },
  "qr_code_data": "V0;VALERO-POS;Prozesstyp;Prozessdaten;TransaktionsNr;SignaturZähler;Startzeit;Logtime;SignAlgorithmus;LogTimeFormat;Signatur;PublicKey;SerialNumber"
}
```

### **BSI TR-03153 Simulator (Lokal):**
```java
// TSEController (Java)
TSEController tse = new TSEController("/path/to/config");

// Login als Admin
tse.authenticateUser("root", new byte[]{1,2,3,4,5,6});

// Client registrieren
tse.registerClient("POS-001");

// Transaction
TransactionResponse tx = tse.startTransaction(
  "POS-001",
  "processData",
  "processType"
);

tse.updateTransaction(
  "POS-001",
  tx.transactionNumber,
  "updateData",
  "updateType"
);

FinishTransactionResponse finished = tse.finishTransaction(
  "POS-001",
  tx.transactionNumber,
  "finalData",
  "finalType"
);

// ✅ Lokale Signatur + Persistence
// ✅ persistentValues.ser
// ✅ normalStoring (Log-Files)
```

---

## 🔧 KORREKTE IMPLEMENTATION

### **1. fiskaly SDK für TypeScript/Node.js:**

```typescript
// packages/frontend-web/src/lib/services/fiskaly-tse.ts

import axios, { AxiosInstance } from 'axios'
import { v4 as uuidv4 } from 'uuid'

export class FiskalyTSE {
  private client: AxiosInstance
  private apiKey: string
  private apiSecret: string
  private tssId: string
  private clientId: string
  private accessToken: string | null = null

  constructor(config: {
    apiKey: string
    apiSecret: string
    tssId: string
    clientId: string
  }) {
    this.apiKey = config.apiKey
    this.apiSecret = config.apiSecret
    this.tssId = config.tssId
    this.clientId = config.clientId

    this.client = axios.create({
      baseURL: 'https://kassensichv.io/api/v1',
      timeout: 30000,
    })

    // Auto-Inject Access-Token
    this.client.interceptors.request.use(async (config) => {
      if (!this.accessToken) {
        await this.authenticate()
      }
      config.headers.Authorization = `Bearer ${this.accessToken}`
      return config
    })

    // Auto-Refresh bei 401
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          await this.authenticate()
          return this.client.request(error.config)
        }
        return Promise.reject(error)
      },
    )
  }

  /**
   * Authentifizierung mit API-Key/Secret
   */
  private async authenticate(): Promise<void> {
    const response = await axios.post(
      'https://kassensichv.io/api/v1/auth',
      { api_key: this.apiKey, api_secret: this.apiSecret },
    )
    this.accessToken = response.data.access_token
  }

  /**
   * TSS initialisieren
   */
  async initializeTSS(): Promise<void> {
    await this.client.put(`/tss/${this.tssId}`, {
      state: 'INITIALIZED',
      description: 'VALERO POS-Terminal',
    })
  }

  /**
   * Client registrieren
   */
  async registerClient(): Promise<void> {
    await this.client.put(`/tss/${this.tssId}/client/${this.clientId}`, {
      serial_number: 'POS-001',
    })
  }

  /**
   * Transaction starten
   */
  async startTransaction(processData: string, processType: string): Promise<{
    txId: string
    number: number
    time_start: number
  }> {
    const txId = uuidv4()
    
    const response = await this.client.put(`/tss/${this.tssId}/tx/${txId}`, {
      state: 'ACTIVE',
      client_id: this.clientId,
    })
    
    return {
      txId,
      number: response.data.number,
      time_start: response.data.time_start,
    }
  }

  /**
   * Transaction aktualisieren (Artikel hinzufügen)
   */
  async updateTransaction(
    txId: string,
    cart: Array<{ name: string; price: number; quantity: number }>,
  ): Promise<void> {
    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
    
    await this.client.put(`/tss/${this.tssId}/tx/${txId}`, {
      state: 'ACTIVE',
      client_id: this.clientId,
      schema: {
        standard_v1: {
          receipt: {
            receipt_type: 'RECEIPT',
            amounts_per_vat_rate: [
              { vat_rate: 19, amount: total.toFixed(2) },
            ],
          },
        },
      },
    })
  }

  /**
   * Transaction beenden & signieren
   */
  async finishTransaction(
    txId: string,
    paymentType: 'CASH' | 'NON_CASH' | 'INTERNAL',
    amount: number,
  ): Promise<{
    number: number
    signature: {
      value: string
      counter: number
      algorithm: string
    }
    time_start: number
    time_end: number
    qr_code_data: string
  }> {
    const response = await this.client.put(`/tss/${this.tssId}/tx/${txId}`, {
      state: 'FINISHED',
      client_id: this.clientId,
      schema: {
        standard_v1: {
          receipt: {
            receipt_type: 'RECEIPT',
            amounts_per_payment_type: [
              { payment_type: paymentType, amount: amount.toFixed(2) },
            ],
          },
        },
      },
    })

    return response.data
  }

  /**
   * DSFinV-K Export
   */
  async exportDSFinVK(startDate: string, endDate: string): Promise<Blob> {
    const response = await this.client.get(`/tss/${this.tssId}/export`, {
      params: { start_date: startDate, end_date: endDate },
      responseType: 'blob',
    })
    
    return response.data
  }
}
```

---

## 🔄 MIGRATION: Mock → Real-TSE

### **Vorher (Mock):**
```typescript
// ❌ Unsicher, nicht GoBD-konform
const tseSignature = {
  transactionNumber: Math.floor(Math.random() * 10000),
  signature: 'TSE_SIG_' + Date.now(),
  timestamp: new Date().toISOString(),
  qrCode: 'V0;VALERO-POS;...',
}
```

### **Nachher (fiskaly):**
```typescript
// ✅ KassenSichV-zertifiziert
const tse = new FiskalyTSE({
  apiKey: process.env.VITE_FISKALY_API_KEY!,
  apiSecret: process.env.VITE_FISKALY_API_SECRET!,
  tssId: process.env.VITE_FISKALY_TSS_ID!,
  clientId: 'POS-001',
})

// Transaction-Lifecycle
const tx = await tse.startTransaction('Verkauf', 'Beleg')
await tse.updateTransaction(tx.txId, cart)
const signed = await tse.finishTransaction(tx.txId, 'CASH', total)

// ✅ Echte ECDSA-Signatur
// ✅ Fortlaufende Transaction-Nummer
// ✅ BSI-konformer QR-Code
```

---

## 🆚 FEATURE-BY-FEATURE COMPARISON

### **1. Authentifizierung**

**Mock:**
```typescript
// ❌ Keine Auth
```

**fiskaly:**
```typescript
// ✅ JWT-basiert
POST /auth
{
  "api_key": "...",
  "api_secret": "..."
}
→ { "access_token": "eyJ...", "expires_in": 86400 }
```

**BSI Simulator:**
```java
// ✅ User-Rollen
tse.authenticateUser("root", new byte[]{1,2,3,4,5,6});  // admin
tse.authenticateUser("timekeeper", new byte[]{0,9,8,7,6,5});  // timeAdmin
```

---

### **2. Transaction-Lifecycle**

**Mock:**
```typescript
// ❌ Single-Step (nur Checkout)
handleCheckout() → TSE-Signatur
```

**fiskaly:**
```typescript
// ✅ 3-Step-Lifecycle
1. startTransaction()    → TX-ID + Nummer
2. updateTransaction()   → Artikel hinzufügen
3. finishTransaction()   → Signatur + QR-Code
```

**BSI Simulator:**
```java
// ✅ BSI TR-03153 Standard
startTransaction()
updateTransaction()   // Optional, mehrfach möglich
finishTransaction()
```

---

### **3. Signatur-Format**

**Mock:**
```typescript
{
  signature: 'TSE_SIG_1728640523',  // ❌ Nur Timestamp
  transactionNumber: 7843,           // ❌ Random
  qrCode: 'V0;...'                   // ❌ Ungültig
}
```

**fiskaly:**
```typescript
{
  "signature": {
    "value": "MEUCIQDx7K...",        // ✅ ECDSA (256bit)
    "counter": 1234,                 // ✅ Fortlaufend
    "algorithm": "ecdsa-plain-SHA256"
  },
  "number": 7843,                    // ✅ TSE-verwaltet
  "qr_code_data": "V0;VALERO-POS;Prozesstyp;Prozessdaten;7843;1234;1728640523;1728640530;ecdsa-plain-SHA256;unixTime;MEUCIQDx...;BHKh...;TSS-123"
}
```

---

### **4. Offline-Handling**

**Mock:**
```typescript
// ❌ Keine Offline-Queue
if (!navigator.onLine) {
  alert('Keine Internetverbindung!')
}
```

**fiskaly SDK:**
```typescript
// ✅ Automatic Retry + Queue
const client = new FiskalyHttpClient(apiKey, apiSecret, baseUrl, {
  retries: 3,
  timeout: 30000,
  offlineQueue: true,  // Speichert Requests in IndexedDB
})

// Bei Reconnect: Automatisches Nachsenden
```

**BSI Simulator:**
```java
// ✅ Lokale Persistence
gracefulShutdown();  
// → Speichert persistentValues.ser
// → Bei Neustart: Automatisches Laden
```

---

### **5. DSFinV-K Export**

**Mock:**
```typescript
// ❌ Button ohne Funktion
<Button>DSFinV-K Export</Button>
```

**fiskaly:**
```typescript
// ✅ Echter Export
const blob = await tse.exportDSFinVK('2025-01-01', '2025-12-31')
const url = URL.createObjectURL(blob)
const link = document.createElement('a')
link.href = url
link.download = 'dsfinvk_2025.tar'
link.click()
```

**Format:**
```
dsfinvk/
  ├─ bonpos_aufbau.json
  ├─ bonpos_einzelaufzeichnung.json
  ├─ bonpos_referenzen.json
  ├─ kassenabschluss.json
  ├─ stamm_abschluss.json
  ├─ stamm_orte.json
  ├─ stamm_terminal.json
  └─ tse_transaktionen.json
```

---

## 📋 PFLICHT-ANFORDERUNGEN (KassenSichV)

### **✅ Erfüllt mit fiskaly:**
- ✅ Zertifizierte TSE (BSI CC-PP-0105-2019)
- ✅ Unveränderbare Signatur (ECDSA)
- ✅ Fortlaufende Transaktionsnummer
- ✅ Zeitstempel (unixTime)
- ✅ QR-Code auf Bon (V0-Format)
- ✅ 10 Jahre Speicherung (Cloud)
- ✅ DSFinV-K Export (DATEV/Finanzamt)
- ✅ Offline-Dokumentation (Anwendungserlass § 146a AO)

### **❌ Fehlt in Mock:**
- ❌ Echte Krypto-Signatur
- ❌ Zertifizierung
- ❌ Unveränderbarkeit
- ❌ Rechtssicherheit

---

## 🚀 IMPLEMENTIERUNGS-ROADMAP

### **Phase 1: fiskaly Integration** (1 Woche)

#### **A. Dependencies installieren:**
```bash
pnpm add uuid @types/uuid
```

#### **B. Service erstellen:**
```typescript
// lib/services/fiskaly-tse.ts (siehe oben)
export class FiskalyTSE { ... }
```

#### **C. POS-Terminal anpassen:**
```typescript
import { fiskalyTSE } from '@/lib/services/fiskaly-tse'

async function handleCheckout() {
  try {
    // 1. Transaction starten
    const tx = await fiskalyTSE.startTransaction('Verkauf', 'Beleg')
    
    // 2. Artikel hinzufügen
    await fiskalyTSE.updateTransaction(tx.txId, cart)
    
    // 3. Zahlung abschließen
    const signed = await fiskalyTSE.finishTransaction(
      tx.txId,
      paymentMethod === 'bar' ? 'CASH' : 'NON_CASH',
      total,
    )
    
    // 4. TSE-Journal speichern
    await saveTSETransaction({
      bonnummer: `BON-${Date.now()}`,
      tseTransactionNumber: signed.number,
      tseSignature: signed.signature.value,
      tseCounter: signed.signature.counter,
      betrag: total,
      zahlungsart: paymentMethod,
      qrCode: signed.qr_code_data,
      fibuStatus: 'offen',
    })
    
    // 5. Bon drucken (mit QR-Code)
    printReceipt(cart, signed)
    
  } catch (error) {
    // Offline-Queue
    await offlineQueue.add({ cart, paymentMethod, total })
  }
}
```

#### **D. Environment (.env):**
```bash
VITE_FISKALY_API_KEY=test_your_key_here
VITE_FISKALY_API_SECRET=test_your_secret_here
VITE_FISKALY_TSS_ID=your-tss-id
VITE_FISKALY_CLIENT_ID=POS-001
```

---

### **Phase 2: Offline-Queue** (3 Tage)

```typescript
// lib/services/offline-queue.ts

import { openDB, DBSchema } from 'idb'

interface OfflineQueueDB extends DBSchema {
  transactions: {
    key: string
    value: {
      id: string
      cart: CartItem[]
      paymentMethod: string
      total: number
      timestamp: string
      retries: number
    }
  }
}

export class OfflineQueue {
  private db: IDBPDatabase<OfflineQueueDB>

  async init() {
    this.db = await openDB<OfflineQueueDB>('tse-offline-queue', 1, {
      upgrade(db) {
        db.createObjectStore('transactions', { keyPath: 'id' })
      },
    })
  }

  async add(tx: { cart; paymentMethod; total }) {
    await this.db.add('transactions', {
      id: uuidv4(),
      ...tx,
      timestamp: new Date().toISOString(),
      retries: 0,
    })
  }

  async processQueue() {
    const pending = await this.db.getAll('transactions')
    
    for (const tx of pending) {
      try {
        await fiskalyTSE.startTransaction(...)
        // ...
        await this.db.delete('transactions', tx.id)
      } catch (error) {
        // Retry-Counter erhöhen
        await this.db.put('transactions', { ...tx, retries: tx.retries + 1 })
      }
    }
  }
}
```

---

### **Phase 3: BSI Simulator (Alternative)** (Optional)

**Für lokale Tests ohne Internet:**

```typescript
// Backend: Python + BSI TSE-Simulator

from tse_simulator import TSEController

class LocalTSE:
    def __init__(self, config_path: str):
        self.tse = TSEController(config_path)
        self.tse.authenticate_user("root", b"\x01\x02\x03\x04\x05\x06")
        self.tse.register_client("POS-001")
    
    def start_transaction(self, process_data: str, process_type: str):
        return self.tse.startTransaction("POS-001", process_data, process_type)
    
    def finish_transaction(self, tx_number: int, data: str, type: str):
        return self.tse.finishTransaction("POS-001", tx_number, data, type)
```

---

## 📊 KOSTEN-VERGLEICH

| Lösung | Setup | Monatlich | Pro Transaction | Zertifizierung |
|--------|-------|-----------|-----------------|----------------|
| **fiskaly Cloud-TSE** | 0 € | 25 € | 0,01 € | ✅ BSI |
| **Swissbit Hardware-TSE** | 199 € | 0 € | 0 € | ✅ BSI |
| **BSI Simulator** | 0 € | 0 € | 0 € | ❌ Nur Test |
| **Mock (aktuell)** | 0 € | 0 € | 0 € | ❌ Illegal |

**Empfehlung:** **fiskaly Cloud-TSE** (einfachste Integration, SaaS, automatische Updates)

---

## ✅ NÄCHSTE SCHRITTE

### **Sofort (kritisch):**
1. ⏭️ **fiskaly Account erstellen** (dashboard.fiskaly.com)
2. ⏭️ **TSS anlegen** (bekommt TSS-ID)
3. ⏭️ **API-Keys generieren** (Key + Secret)
4. ⏭️ **FiskalyTSE Service implementieren** (siehe oben)
5. ⏭️ **POS-Terminal anpassen** (3-Step-Lifecycle)
6. ⏭️ **Offline-Queue** (IndexedDB)
7. ⏭️ **QR-Code-Generator** (qrcode.react)
8. ⏭️ **Bon-Drucker** (ESC/POS)

### **Kurzfristig:**
9. ⏭️ **E2E-Tests** (echte TSE in Staging)
10. ⏭️ **DSFinV-K Export** implementieren
11. ⏭️ **Finanzamt-Prüfung** vorbereiten
12. ⏭️ **Schulung Mitarbeiter**

---

## 📖 DOKUMENTATION

### **fiskaly Developer Portal:**
- https://developer.fiskaly.com
- https://dashboard.fiskaly.com (Account + TSS verwalten)

### **BSI TR-03153:**
- Technische Richtlinie für TSE
- https://www.bsi.bund.de

### **Kassensichv.io API:**
- https://kassensichv.io/api/v1/docs

---

## 🎯 FAZIT

**AKTUELLER STATUS:**
- ✅ **UI/UX fertig** (POS-Terminal, TSE-Journal, Tagesabschluss)
- ✅ **Workflows definiert** (TSE → Fibu mit Datum-Tracking)
- ⚠️ **TSE-Integration** nur Mock (nicht produktiv nutzbar!)

**MIGRATION ERFORDERLICH:**
- ⏭️ Mock → fiskaly Cloud-TSE (1 Woche Aufwand)
- ⏭️ Dependencies: uuid, idb, qrcode.react
- ⏭️ Kosten: ~25 €/Monat + 0,01 €/Bon
- ⏭️ Rechtssicherheit: ✅ Voll GoBD/KassenSichV-konform

**PRIORITÄT:** 🔴 **KRITISCH** (ohne echte TSE illegal ab 2020!)

---

**Erstellt:** 2025-10-11  
**Status:** 📋 **ANALYSE KOMPLETT**  
**Next:** fiskaly Account + SDK-Integration

