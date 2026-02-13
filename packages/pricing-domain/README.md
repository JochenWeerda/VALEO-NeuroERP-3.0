# @valero-neuroerp/pricing-domain

**Pricing & Quote Calculation Engine** für VALEO-NeuroERP 3.0

Zentrale Preisbildung für Landhandel (Getreide, Raps, Kraftfutter, Düngemittel).

## 📋 Überblick

Die Pricing-Domain ist verantwortlich für:

- **Preislisten** - Mit Tier-Breaks (Staffelpreise)
- **Konditionen** - Kunden/Segment-spezifisch (Rabatte, Aufschläge)
- **Dynamische Formeln** - Börsenindizes, Basis, Futures
- **Steuer/Abgaben** - Als Stammdaten (KEINE Buchungslogik!)
- **Price Quotes** - Berechnete Angebote (24h TTL)

## 🚫 Abgrenzung zu anderen Domains

| Domain | Was macht pricing NICHT |
|--------|-------------------------|
| **finance-domain** | ❌ Keine Konten, keine Buchungssätze, keine Steuerberechnung für FiBu |
| **contracts-domain** | ❌ Keine Kontraktverwaltung, nur Referenzen zu Futures/Basis |
| **sales-domain** | ❌ Keine Fakturierung, nur Price-Quotes bereitstellen |
| **inventory-domain** | ❌ Keine Bestandsbewertung, keine Kostenstellen |

**Pricing-Domain liefert NUR:** Berechnete Preise als Input für andere Domains!

## 🔄 Calculator-Pipeline

### 5-Stufen-Kalkulation

```
Input: { customerId, sku, qty, channel, ... }
  ↓
1. BASE: PriceList → Tier-Breaks
  ↓
2. CONDITIONS: Rabatte/Aufschläge (Customer/Segment)
  ↓
3. DYNAMIC: Formeln (MATIF + BASIS - FREIGHT)
  ↓
4. CHARGES: Fees, Levies (z.B. EnvFee)
  ↓
5. TAX: USt (nur Referenz!)
  ↓
Output: PriceQuote { components[], totalNet, totalGross }
```

## 🚀 Quick Start

```bash
npm install
cp .env.example .env
npm run migrate:up
npm run dev  # Port 3060
```

## 📡 API-Endpunkte

### Base URL
`http://localhost:3060/pricing/api/v1`

### Quotes (Kern-Feature!)

```
POST /quotes/calc       - Preis berechnen
GET  /quotes/:id        - Quote abrufen
```

### Health

```
GET  /health, /ready, /live
```

## 💡 Beispiel: Quote berechnen

```bash
POST /pricing/api/v1/quotes/calc
Content-Type: application/json
x-tenant-id: 123e4567-e89b-12d3-a456-426614174000

{
  "customerId": "CUST-001",
  "sku": "WHEAT-11.5",
  "qty": 25,
  "channel": "Web",
  "deliveryWindow": {
    "from": "2025-10-15T00:00:00Z",
    "to": "2025-11-15T00:00:00Z"
  }
}

# Response:
{
  "id": "quote-uuid",
  "tenantId": "...",
  "inputs": { ... },
  "components": [
    { "type": "Base", "key": "Base-WHEAT-11.5", "value": 5250.00, "description": "Weizen 11.5% @ 210 EUR/t" },
    { "type": "Condition", "key": "Discount-Volume", "value": -131.25, "description": "Volume Discount -2.5%" },
    { "type": "Charge", "key": "Charge-EnvFee", "value": 25.00, "description": "Umweltabgabe" },
    { "type": "Tax", "key": "Tax-VAT_7", "value": 358.06, "description": "USt 7%" }
  ],
  "totalNet": 5143.75,
  "totalGross": 5501.81,
  "currency": "EUR",
  "expiresAt": "2025-10-02T12:00:00Z"
}
```

## 🏗️ Domain-Modell

### 1. PriceList
- Lines mit SKU/Commodity
- Tier-Breaks (Staffelpreise)
- Status: Draft → Active → Archived

### 2. ConditionSet
- Customer/Segment-Konditionen
- Rules: Discount, Markup, Rebate, Surcharge
- Conflict-Strategy: Stack, MaxWins, FirstWins

### 3. DynamicFormula
- Expression: "MATIF_NOV + BASIS - FREIGHT"
- Inputs: Index, Futures, Basis, FX
- Rounding: step + mode
- Caps: min/max

### 4. TaxChargeRef
- VAT, Tax, Levy, Fee, Deposit
- Method: ABS oder PCT
- **Nur Stammdaten** (keine Buchung!)

### 5. PriceQuote
- Calculated Components (Breakdown)
- TTL: 24h
- Für sales-domain

## 🔔 Domain-Events

```
pricing.quote.calculated
pricing.pricelist.created|activated|archived
pricing.conditions.created|updated
pricing.formula.created|updated
```

## 🔗 Integration

### → Sales Domain
```
Price-Quote → Angebot/Order
```

### → Analytics Domain
```
Events → Margin-KPI, Elasticity
```

### ← Contracts Domain
```
Futures-Referenzen
```

## 🧪 Testing

```bash
npm run test
npm run test:coverage
```

## 📊 Observability

- OpenTelemetry
- Pino Logs
- Health-Checks

---

**Status:** ✅ Production-Ready (MVP)  
**Port:** 3060  
**Version:** 0.1.0

