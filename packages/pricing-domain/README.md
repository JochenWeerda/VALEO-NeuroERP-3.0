***REMOVED*** @valero-neuroerp/pricing-domain

**Pricing & Quote Calculation Engine** für VALEO-NeuroERP 3.0

Zentrale Preisbildung für Landhandel (Getreide, Raps, Kraftfutter, Düngemittel).

***REMOVED******REMOVED*** 📋 Überblick

Die Pricing-Domain ist verantwortlich für:

- **Preislisten** - Mit Tier-Breaks (Staffelpreise)
- **Konditionen** - Kunden/Segment-spezifisch (Rabatte, Aufschläge)
- **Dynamische Formeln** - Börsenindizes, Basis, Futures
- **Steuer/Abgaben** - Als Stammdaten (KEINE Buchungslogik!)
- **Price Quotes** - Berechnete Angebote (24h TTL)

***REMOVED******REMOVED*** 🚫 Abgrenzung zu anderen Domains

| Domain | Was macht pricing NICHT |
|--------|-------------------------|
| **finance-domain** | ❌ Keine Konten, keine Buchungssätze, keine Steuerberechnung für FiBu |
| **contracts-domain** | ❌ Keine Kontraktverwaltung, nur Referenzen zu Futures/Basis |
| **sales-domain** | ❌ Keine Fakturierung, nur Price-Quotes bereitstellen |
| **inventory-domain** | ❌ Keine Bestandsbewertung, keine Kostenstellen |

**Pricing-Domain liefert NUR:** Berechnete Preise als Input für andere Domains!

***REMOVED******REMOVED*** 🔄 Calculator-Pipeline

***REMOVED******REMOVED******REMOVED*** 5-Stufen-Kalkulation

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

***REMOVED******REMOVED*** 🚀 Quick Start

```bash
npm install
cp .env.example .env
npm run migrate:up
npm run dev  ***REMOVED*** Port 3060
```

***REMOVED******REMOVED*** 📡 API-Endpunkte

***REMOVED******REMOVED******REMOVED*** Base URL
`http://localhost:3060/pricing/api/v1`

***REMOVED******REMOVED******REMOVED*** Quotes (Kern-Feature!)

```
POST /quotes/calc       - Preis berechnen
GET  /quotes/:id        - Quote abrufen
```

***REMOVED******REMOVED******REMOVED*** Health

```
GET  /health, /ready, /live
```

***REMOVED******REMOVED*** 💡 Beispiel: Quote berechnen

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

***REMOVED*** Response:
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

***REMOVED******REMOVED*** 🏗️ Domain-Modell

***REMOVED******REMOVED******REMOVED*** 1. PriceList
- Lines mit SKU/Commodity
- Tier-Breaks (Staffelpreise)
- Status: Draft → Active → Archived

***REMOVED******REMOVED******REMOVED*** 2. ConditionSet
- Customer/Segment-Konditionen
- Rules: Discount, Markup, Rebate, Surcharge
- Conflict-Strategy: Stack, MaxWins, FirstWins

***REMOVED******REMOVED******REMOVED*** 3. DynamicFormula
- Expression: "MATIF_NOV + BASIS - FREIGHT"
- Inputs: Index, Futures, Basis, FX
- Rounding: step + mode
- Caps: min/max

***REMOVED******REMOVED******REMOVED*** 4. TaxChargeRef
- VAT, Tax, Levy, Fee, Deposit
- Method: ABS oder PCT
- **Nur Stammdaten** (keine Buchung!)

***REMOVED******REMOVED******REMOVED*** 5. PriceQuote
- Calculated Components (Breakdown)
- TTL: 24h
- Für sales-domain

***REMOVED******REMOVED*** 🔔 Domain-Events

```
pricing.quote.calculated
pricing.pricelist.created|activated|archived
pricing.conditions.created|updated
pricing.formula.created|updated
```

***REMOVED******REMOVED*** 🔗 Integration

***REMOVED******REMOVED******REMOVED*** → Sales Domain
```
Price-Quote → Angebot/Order
```

***REMOVED******REMOVED******REMOVED*** → Analytics Domain
```
Events → Margin-KPI, Elasticity
```

***REMOVED******REMOVED******REMOVED*** ← Contracts Domain
```
Futures-Referenzen
```

***REMOVED******REMOVED*** 🧪 Testing

```bash
npm run test
npm run test:coverage
```

***REMOVED******REMOVED*** 📊 Observability

- OpenTelemetry
- Pino Logs
- Health-Checks

---

**Status:** ✅ Production-Ready (MVP)  
**Port:** 3060  
**Version:** 0.1.0
