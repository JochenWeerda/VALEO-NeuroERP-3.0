# KTBL-Integration für THG-Berechnungen

## 📋 Überblick

Die **regulatory-domain** bereitet die Integration mit der [KTBL BEK-Parameter-Datenbank](https://www.ktbl.de/webanwendungen/bek-parameter) vor.

**KTBL** = Kuratorium für Technik und Bauwesen in der Landwirtschaft e.V.

**BEK** = Berechnungsstandard für einzelbetriebliche Klimabilanzen

## 🎯 Zweck

Die KTBL-Datenbank liefert wissenschaftlich fundierte Parameter für Treibhausgas-Emissionen in der Landwirtschaft:

- **Direkte Emissionen** - Unmittelbar im landwirtschaftlichen Prozess (z.B. N₂O aus Düngung)
- **Indirekte Emissionen** - Aus Umsetzungen emittierter Substanzen
- **Vorgelagerte Emissionen** - Aus Herstellung von Betriebsmitteln (Dünger, Pestizide, Diesel)

## ⚠️ Aktueller Status

**Die KTBL-Webanwendung ist derzeit offline** (Stand: Oktober 2025)

> _"Die Berechnungsparameter werden zur Zeit überarbeitet und stehen deshalb vorübergehend nicht zur Verfügung."_  
> Quelle: [KTBL Website](https://www.ktbl.de/webanwendungen/bek-parameter)

## ✅ Implementierter Fallback-Mechanismus

Die regulatory-domain verwendet **Literaturwerte** bis KTBL wieder verfügbar ist:

### Fallback-Daten (kg CO2eq/t)

| Crop | Direct | Indirect | Upstream | Total |
|------|--------|----------|----------|-------|
| **Raps** | 420 | 180 | 250 | **850** |
| **Weizen** | 380 | 160 | 220 | **760** |
| **Mais** | 400 | 170 | 240 | **810** |
| **Soja** | 350 | 150 | 200 | **700** |
| **Sonnenblume** | 390 | 165 | 230 | **785** |

Quellen: KTBL-Schriften (ältere Versionen), RED II Annex V, Literaturwerte

## 🔧 Integration vorbereitet

### 1. KTBL-API-Client

**Datei:** `src/infra/integrations/ktbl-api.ts`

```typescript
// Fetch KTBL emission parameters
await fetchKTBLEmissionParameters('Raps', 'DE21');

// Calculate with actual farm data
await calculateCropEmissions('Raps', {
  yieldPerHa: 4.2,        // t/ha (tatsächlicher Ertrag)
  fertilizer: 180,        // kg N/ha
  region: 'DE21',         // NUTS-2 (Oberbayern)
});

// Check KTBL service status
await getKTBLStatus();
```

### 2. GHG-Service integriert KTBL

**Automatische Nutzung** bei `method: 'Actual'`:

```typescript
POST /regulatory/api/v1/ghg/calc
{
  "commodity": "RAPE_OIL",
  "method": "Actual",
  "actualData": {
    "yieldPerHa": 4.2,
    "nitrogenFertilizer": 180,
    "useKTBL": true  // ← Aktiviert KTBL-Lookup
  },
  "originRegion": "DE21"
}
```

### 3. API-Endpunkte

```
GET  /regulatory/api/v1/ktbl/status
GET  /regulatory/api/v1/ktbl/crop-emissions/:crop?region=
POST /regulatory/api/v1/ktbl/calculate
```

## 🚀 Aktivierung (sobald KTBL online)

### Option 1: REST-API (falls KTBL bereitstellt)

```env
# .env
KTBL_API_ENABLED=true
KTBL_API_URL=https://www.ktbl.de/api/bek-parameter
KTBL_API_KEY=your-api-key  # Falls erforderlich
```

### Option 2: CSV-Import

```bash
# Download KTBL CSV-Export
curl -O https://www.ktbl.de/downloads/bek-parameters.csv

# Import in DB
npm run ktbl:import -- bek-parameters.csv
```

### Option 3: Web-Scraping

```typescript
// Implementierung in ktbl-api.ts
async function scrapeKTBLWebsite(crop: string) {
  const html = await axios.get(`https://www.ktbl.de/webanwendungen/bek-parameter?crop=${crop}`);
  // Parse HTML...
}
```

### Option 4: Lizensierte Datenbank

Kontakt: **ktbl@ktbl.de**

## 📊 Vorteile der KTBL-Integration

| Vorteil | Beschreibung |
|---------|--------------|
| **Wissenschaftlich** | Peer-reviewed Parameter |
| **Regionsspezifisch** | NUTS-2-Disaggregation |
| **Aktuell** | Regelmäßige Updates |
| **Detailliert** | Breakdown nach Emissionsquellen |
| **Rechtssicher** | Anerkannt für Klimabilanzen |

## 🔄 Workflow mit KTBL

### Aktuell (Fallback)
```
GHG-Calculation (Actual)
  → Operator Data (cultivationEmissions)
  → Berechnung
  → Result mit "Fallback Values"
```

### Mit KTBL (zukünftig)
```
GHG-Calculation (Actual)
  → KTBL-Lookup (crop, region, yield, N-fertilizer)
  → Cache (7 Tage)
  → Anpassung basierend auf tatsächlichem Ertrag/Düngung
  → Berechnung
  → Result mit "KTBL BEK 2025"
```

## 📈 Emissionsanpassungen

### Yield-Adjustment
```typescript
// Höherer Ertrag = niedrigere Emissionen pro Tonne
emissionsPerTon = ktbl.emissions.total * (ktbl.yieldPerHa / actualYieldPerHa)
```

### Fertilizer-Adjustment
```typescript
// Mehr N-Dünger = höhere N2O-Emissionen
additionalN2O = (actualFertilizer - ktbl.nitrogenFertilizer) * 4.5  // IPCC-Faktor
```

## 🧪 Testing

```bash
# Test KTBL status
curl http://localhost:3008/regulatory/api/v1/ktbl/status

# Test crop emissions
curl "http://localhost:3008/regulatory/api/v1/ktbl/crop-emissions/Raps?region=DE21"

# Test calculation
curl -X POST http://localhost:3008/regulatory/api/v1/ktbl/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "Raps",
    "yieldPerHa": 4.2,
    "fertilizer": 180,
    "region": "DE21"
  }'
```

## 📚 Quellen

- **KTBL Website:** [ktbl.de](https://www.ktbl.de)
- **BEK-Parameter:** [ktbl.de/webanwendungen/bek-parameter](https://www.ktbl.de/webanwendungen/bek-parameter)
- **KTBL-Schriften:** [ktbl.de/themen/klima](https://www.ktbl.de/themen/klima)
- **Kontakt:** ktbl@ktbl.de, +49 6151 7001-0

## 📞 Nächste Schritte

1. **Monitoring** - Prüfe regelmäßig ob KTBL-Webanwendung wieder online
2. **Kontakt** - Anfrage an KTBL bzgl. API-Zugang oder CSV-Export
3. **Alternative** - Prüfe andere Datenquellen (z.B. Agri-footprint, Ecoinvent)
4. **Validierung** - Vergleiche Fallback-Werte mit KTBL sobald verfügbar

## ⚡ Quick Start (aktuell)

Die KTBL-Integration ist **bereits implementiert** und nutzt automatisch Fallback-Daten:

```bash
# GHG-Berechnung mit KTBL-Fallback
POST /regulatory/api/v1/ghg/calc
{
  "commodity": "RAPE_OIL",
  "method": "Actual",
  "actualData": {
    "yieldPerHa": 4.2,
    "nitrogenFertilizer": 180,
    "useKTBL": true
  },
  "originRegion": "DE21"
}

# Response enthält:
# - cultivationEmissions (aus KTBL-Fallback)
# - dataSource: "Fallback Values (KTBL offline)"
```

## 🎯 Production-Ready

✅ Fallback-Mechanismus funktioniert  
✅ Cache-Strategie implementiert (7 Tage)  
✅ Automatisches Retry wenn KTBL verfügbar  
✅ Fehlerbehandlung & Logging  
⏳ KTBL-Aktivierung sobald online

---

**Status:** ✅ Implementiert & Ready for KTBL-Activation  
**Wartend auf:** KTBL BEK-Parameter-Webanwendung  
**Alternative:** Fallback-Daten basierend auf Literatur

