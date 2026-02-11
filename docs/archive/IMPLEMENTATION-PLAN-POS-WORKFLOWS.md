# 🛒 POS & Workflow Implementation Plan

**Datum:** 2025-10-11  
**Status:** 🚧 In Planung

---

## 🎯 SCOPE

### **A. POS-System (Haus- & Gartenmarkt)**
- Touch-Terminal (Tablet-ready)
- TSE-Integration (Kassensicherungsverordnung)
- Hardware-Integration (Scanner/EC/Drucker/Ladenkasse)
- B2B/B2C-Modi
- Artikelbilder (Auto-Suche)

### **B. Workflows**
- Tagesabschluss Kasse → Fibu
- Inventur (unterjährig + Jahresende)
- Formulare (Stundenzettel, Schulungsnachweise)
- KI-Assistenz für Compliance

---

## 📦 MODULE

### **1. POS-Terminal** (`pos/terminal.tsx`)

#### **Features:**
- ✅ Touch-optimierte Oberfläche
- ✅ Warenkorb mit Barcode-Scanner
- ✅ Artikelbilder (Grid/List-View)
- ✅ B2B-Modus (ERP-Beleg) / B2C-Modus (Kassenbon)
- ✅ Zahlungsarten (Bar, EC, PayPal)
- ✅ TSE-Signatur auf Kassenbon
- ✅ Kassenladen-Signal (Serial/USB)
- ✅ Etikettendruck

#### **Hardware-Integration:**
```typescript
interface POSHardware {
  scanner: BarcodeScanner      // USB HID
  ecTerminal: ECTerminal        // ZVT-Protocol
  cashDrawer: CashDrawer        // Serial/USB Signal
  labelPrinter: LabelPrinter    // EPL/ZPL
  receiptPrinter: ReceiptPrinter // ESC/POS
  tse: TSEDevice                // fiskaly/Swissbit
}
```

---

### **2. TSE-Integration** (`pos/tse-service.ts`)

#### **KassenSichV-Anforderungen:**
- ✅ Zertifizierte TSE (fiskaly, Swissbit, Epson)
- ✅ Signatur je Bon (QR-Code + Text)
- ✅ Transaktionsnummer (fortlaufend)
- ✅ Start-/Stop-Transaktionen
- ✅ DSFinV-K Export (DATEV)
- ✅ Tagesendsummenzähler
- ✅ Fehlerspeicher (TSE offline → Queue)

#### **API-Integration:**
```typescript
// fiskaly Cloud-TSE
const tse = {
  provider: 'fiskaly',
  apiKey: process.env.FISKALY_API_KEY,
  tssId: process.env.FISKALY_TSS_ID,
  clientId: process.env.FISKALY_CLIENT_ID,
}

// Bon signieren
async function signTransaction(tx: Transaction): Promise<TSESignature> {
  const response = await fiskaly.startTransaction(tx)
  return {
    transactionNumber: response.number,
    signature: response.signature_value,
    signatureCounter: response.signature_counter,
    timestamp: response.time_start,
    qrCode: generateQRCode(response),
  }
}
```

---

### **3. Tagesabschluss** (`pos/tagesabschluss.tsx`)

#### **Workflow:**
```
┌──────────────┐
│ POS-Terminal │
└──────┬───────┘
       │ Tagesabschluss (EOD)
       ├─► Kassenzählung (Bar)
       ├─► EC-Terminal-Abrechnung
       ├─► TSE-Export (DSFinV-K)
       ├─► Differenz-Prüfung (Soll/Ist)
       └─► Fibu-Buchung (SKR03: Kasse 1000 → Bank 1200)
```

#### **Features:**
- ✅ Soll-Berechnung (aus POS-Transaktionen)
- ✅ Ist-Eingabe (Bar-Zählung)
- ✅ Differenz-Handling (Über-/Unterdeckung)
- ✅ EC-Terminal-Import (Kassenschnitt)
- ✅ TSE-Tagesabschluss
- ✅ Auto-Fibu-Buchung
- ✅ PDF-Kassenbericht

---

### **4. Inventur** (`lager/inventur-wizard.tsx`)

#### **Unterjährige Inventur:**
- ✅ Stichproben-Inventur
- ✅ Barcode-Scan
- ✅ Soll/Ist-Vergleich
- ✅ Differenz-Buchung

#### **Jahresend-Inventur:**
- ✅ Vollständige Bestandsaufnahme
- ✅ Listen-Generator (nach Lagerplatz/Warengruppe)
- ✅ Mobile App (Tablet-Scan)
- ✅ Bewertung (EK/VK)
- ✅ Fibu-Buchung (SKR03: 3980 Bestandsveränderung)

---

### **5. Formulare & Dokumentation**

#### **LKW-Fahrer Stundenzettel** (`personal/stundenzettel.tsx`)
```
Felder:
- Fahrer-Name
- Datum
- Fahrzeug-Kennzeichen
- Touren (Start/Ende/Km/Pausen)
- Gesamt-Arbeitszeit
- Überstunden
- Unterschrift (Touch-Signature)
```

#### **Schulungsnachweise** (`personal/schulungen.tsx`)
```
Felder:
- Mitarbeiter
- Schulungsthema (PSM, Gefahrstoffe, Gabelstapler, etc.)
- Datum/Dauer
- Schulungsleiter
- Zertifikat-Upload
- Gültigkeitsdatum
- Auto-Erinnerung (60 Tage vor Ablauf)
```

---

### **6. KI-Assistenz** (`ai/compliance-copilot.tsx`)

#### **Features:**
- ✅ Chatbot für Compliance-Fragen
- ✅ Auto-Dokumentenprüfung (VVVO, Sachkunde, etc.)
- ✅ Frist-Monitoring (BVL, ENNI, STV)
- ✅ Vorausgefüllte Formulare (aus Stammdaten)
- ✅ Plausibilitätsprüfung (Meldungen)

#### **Use Cases:**
```
User: "Wann muss ich die BVL-Meldung abgeben?"
AI: "Die BVL PSM-Jahresumsatzmeldung ist bis 31. März fällig. 
     Aktueller Status: 3 Wirkstoffe erfasst, Gesamtmenge 2.420 kg."

User: "Kunde will PSM kaufen, Sachkunde OK?"
AI: "✅ Sachkunde gültig bis 15.03.2025 (läuft in 3 Monaten ab).
     ⚠️ Bitte Kunde informieren über Verlängerung."
```

---

## 🖥️ POS-TERMINAL UI

### **Layout:**
```
┌────────────────────────────────────────────────────────┐
│  VALEO POS - Haus & Gartenmarkt         🔔 B2C  👤 Max │
├────────────────────────────────────────────────────────┤
│                                                          │
│  Warenkorb                    Artikel (Touch)          │
│  ┌──────────────────┐         ┌─────┬─────┬─────┐     │
│  │ 1x Blumenerde    │         │[IMG]│[IMG]│[IMG]│     │
│  │    20L   12,99€  │         │ Erde│Dünge│Saatg│     │
│  │                  │         └─────┴─────┴─────┘     │
│  │ 2x Tomatensamen  │         ┌─────┬─────┬─────┐     │
│  │    2,99€ / St.   │         │[IMG]│[IMG]│[IMG]│     │
│  │                  │         │Töpfe│Gerät│Pflan│     │
│  │                  │         └─────┴─────┴─────┘     │
│  │                  │                                  │
│  │                  │         🔍 [Barcode-Scanner]     │
│  │                  │                                  │
│  │ Gesamt  18,97€   │         [ Artikel suchen... ]   │
│  └──────────────────┘                                  │
│                                                          │
│  [💰 Bar] [💳 EC] [📱 PayPal] [🧾 B2B-Beleg]         │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 TECHNISCHE SPECS

### **Frontend:**
- React + TypeScript
- Shadcn UI (Touch-optimiert)
- TanStack Query (Offline-Queue)
- Zustand (State Management)
- React-Signature-Canvas (Unterschrift)

### **Hardware-APIs:**
```typescript
// Barcode-Scanner (USB HID)
navigator.hid.requestDevice()

// Serial (Kassenladen)
navigator.serial.requestPort()

// WebUSB (Etikettendrucker)
navigator.usb.requestDevice()
```

### **TSE-Provider:**
- **fiskaly** - Cloud-TSE (API-basiert, SaaS)
- **Swissbit** - Hardware-TSE (USB-Stick)
- **Epson** - Drucker mit eingebauter TSE

### **Kassensysteme-Compliance:**
- GoBD (Grundsätze ordnungsmäßiger Buchführung)
- KassenSichV (Kassensicherungsverordnung)
- DSFinV-K (Digitale Schnittstelle Finanzverwaltung)

---

## 📊 DATEV-EXPORT

### **DSFinV-K Format:**
```xml
<DSFinV-K>
  <Stammdaten>
    <Kassensystem>VALERO-POS</Kassensystem>
    <TSE>fiskaly-TSS-12345</TSE>
  </Stammdaten>
  <Belege>
    <Beleg>
      <Bonnummer>123</Bonnummer>
      <Datum>2025-10-11</Datum>
      <Betrag>18.97</Betrag>
      <TSE-Signatur>...</TSE-Signatur>
    </Beleg>
  </Belege>
  <Tagesabschluesse>
    <Z-Bon>
      <Datum>2025-10-11</Datum>
      <Umsatz-Bar>450.30</Umsatz-Bar>
      <Umsatz-EC>890.20</Umsatz-EC>
    </Z-Bon>
  </Tagesabschluesse>
</DSFinV-K>
```

---

## 🚀 IMPLEMENTATION ROADMAP

### **Phase 1: POS-Core** (2 Wochen)
- [ ] POS-Terminal UI (Touch)
- [ ] Warenkorb-Logik
- [ ] Artikelsuche mit Bildern
- [ ] Basic-Zahlung (Bar/EC)

### **Phase 2: TSE-Integration** (1 Woche)
- [ ] fiskaly API-Integration
- [ ] Bon-Signierung
- [ ] QR-Code-Generation
- [ ] Offline-Queue

### **Phase 3: Hardware** (1 Woche)
- [ ] Barcode-Scanner
- [ ] EC-Terminal (ZVT)
- [ ] Kassenladen-Signal
- [ ] Etikettendrucker

### **Phase 4: Workflows** (1 Woche)
- [ ] Tagesabschluss → Fibu
- [ ] Inventur-Listen
- [ ] Formulare (Stundenzettel, Schulungen)

### **Phase 5: KI-Assistenz** (1 Woche)
- [ ] Compliance-Chatbot
- [ ] Auto-Dokumentenprüfung
- [ ] Frist-Monitoring

---

## 📝 OPEN-SOURCE POS (GitHub)

### **Empfohlene Repos:**
1. **unicorn-utterances/pos-system** - React POS
2. **loystar/open-pos** - TypeScript POS
3. **salespoint/salespoint** - Java POS Framework

### **TSE-Libraries:**
- `fiskaly-sdk-node` - Node.js SDK
- `swissbit-tse` - Hardware-TSE Driver

---

## ✅ NEXT STEPS

1. ⏭️ POS-Terminal Prototyp erstellen
2. ⏭️ TSE-Integration (fiskaly) implementieren
3. ⏭️ Tagesabschluss-Wizard
4. ⏭️ Inventur-Module
5. ⏭️ Formulare (Stundenzettel, Schulungen)
6. ⏭️ KI-Compliance-Copilot

---

**Erstellt:** 2025-10-11  
**Status:** 📋 **BEREIT FÜR UMSETZUNG**

