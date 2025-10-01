***REMOVED******REMOVED******REMOVED*** 4. REST API (10 Endpunkte)

```
Labels (4):
  POST /labels/evaluate       - ⭐ Label-Eligibility-Engine
  GET  /labels                - Liste
  GET  /labels/:id            - Details
  POST /labels/:id/revoke     - Widerruf

PSM (2):
  POST /psm/check             - BVL-Compliance-Check
  GET  /psm/search            - BVL-Suche

GHG (2):
  POST /ghg/calc              - THG-Berechnung (RED II + KTBL)
  GET  /ghg/pathways          - Pfade auflisten

KTBL (3): 🆕
  GET  /ktbl/status           - KTBL-Service-Status
  GET  /ktbl/crop-emissions/:crop - Crop-Emissionsparameter
  POST /ktbl/calculate        - Berechnung mit Farm-Daten

Health (2):
  GET  /health, /ready, /live
```

**Gesamt: 13 API-Endpunkte**

---

***REMOVED******REMOVED******REMOVED*** 8. KTBL-Integration (für THG-Landwirtschaft) 🆕

✅ **KTBL-API-Client** (`ktbl-api.ts`)
- Integration vorbereitet für [KTBL BEK-Parameter](https://www.ktbl.de/webanwendungen/bek-parameter)
- **Status:** KTBL aktuell offline (wird überarbeitet)
- **Fallback:** Literaturwerte für Raps, Weizen, Mais, Soja, Sonnenblume
- **Cache:** 7-Tage-TTL
- **Ready:** Automatische Aktivierung sobald KTBL online

✅ **Emission-Breakdown**
- Direkte Emissionen (N₂O aus Düngung)
- Indirekte Emissionen (Substanz-Umsetzungen)
- Vorgelagerte Emissionen (Betriebsmittel)

✅ **Yield & Fertilizer Adjustments**
- Höherer Ertrag → niedrigere Emissionen/t
- Mehr N-Dünger → höhere N₂O-Emissionen (IPCC-Faktor 4.5)

✅ **NUTS-2-Regionalisierung**
- Regionsspezifische Emissionsfaktoren
- Prepared für KTBL-Datenbank

---

***REMOVED******REMOVED*** 📊 Metriken (Final)

| Metrik | Wert |
|--------|------|
| **Entities** | 6 |
| **DB-Tabellen** | 6 |
| **Services** | 3 Core + 2 Integration |
| **API-Endpunkte** | 13 (10 + 3 KTBL) |
| **Domain-Events** | 12+ |
| **Label-Codes** | 10 |
| **Policy-Keys** | 10 |
| **Evidence-Types** | 13 |
| **Code-Zeilen** | ~4.000 |
| **Ext. Integrations** | 2 (BVL + KTBL) |

---

***REMOVED******REMOVED*** 🌐 Externe Datenquellen

***REMOVED******REMOVED******REMOVED*** BVL (Pflanzenschutzmittel)
- ✅ Mock-Implementierung
- ✅ 7-Tage-Cache
- 🔄 Production: CSV-Import oder Scraping

***REMOVED******REMOVED******REMOVED*** KTBL (Landwirtschafts-THG) 🆕
- ✅ Fallback-Daten aktiv
- ✅ Auto-Activation prepared
- 🔄 Wartend auf KTBL-Webanwendung
- 📞 Kontakt: ktbl@ktbl.de

---

***REMOVED******REMOVED*** 💡 Use Cases (Updated)

***REMOVED******REMOVED******REMOVED*** Use Case 4: KTBL-basierte THG-Berechnung 🆕
**Szenario:** Landwirt möchte Klimabilanz für Rapsanbau  
**Flow:**
1. POST `/ktbl/crop-emissions/Raps?region=DE21`
2. System nutzt KTBL-Fallback (850 kg CO2eq/t)
3. Anpassung: Yield 4.2 t/ha statt 3.5 → Emissionen sinken
4. Anpassung: N-Dünger 180 kg/ha statt 150 → N₂O steigt
5. Ergebnis: 820 kg CO2eq/t (angepasst)

**Sobald KTBL online:**
- Automatischer Switch von Fallback → KTBL BEK 2025
- Regionsspezifische Parameter (NUTS-2)
- Wissenschaftlich validiert

---

***REMOVED******REMOVED*** 🚀 Production-Readiness (Updated)

***REMOVED******REMOVED******REMOVED*** Voraussetzungen
- [x] PostgreSQL ≥ 14
- [x] NATS ≥ 2.8
- [x] Node.js ≥ 20
- [x] BVL-Integration (Mock oder CSV)
- [x] KTBL-Fallback-Daten ✅

***REMOVED******REMOVED******REMOVED*** External-Dependencies (in Zukunft)
- [ ] KTBL BEK-Parameter (wartend auf Re-Launch)
- [ ] BVL PSM-API (optional: CSV-Import)

---

***REMOVED******REMOVED*** 🎓 Rechtliche Compliance (Updated)

***REMOVED******REMOVED******REMOVED*** Implementierte Standards:

✅ **VLOG** - EGGenTDurchfG  
✅ **QS** - Futtermittelmonitoring-Leitfaden 01/2025  
✅ **RED II** - EU 2018/2001 (THG-Schwellen)  
✅ **Rückverfolgbarkeit** - VO (EG) 178/2002 & 183/2005  
✅ **BVL** - Pflanzenschutzmittel-Zulassungen  
✅ **KTBL BEK** - Klimabilanzen Landwirtschaft (mit Fallback) 🆕

---

***REMOVED******REMOVED*** 📚 Datenquellen

| Quelle | Zweck | Status | Integration |
|--------|-------|--------|-------------|
| **JRC Biofuels** | RED II Defaults | ✅ Online | Hardcoded |
| **BVL PSM** | Pestizid-Zulassungen | ✅ Online | Mock + Cache |
| **KTBL BEK** | Crop-Emissionen | ⏸️ Offline | Fallback aktiv |
| **VLOG Standard** | GVO-Regeln | ✅ Online | Policy-Rules |
| **QS Leitfaden** | Monitoring | ✅ Online | Policy-Rules |

---

**Aktualisiert:** 1. Oktober 2025  
**KTBL-Integration:** ✅ Vorbereitet & Fallback aktiv  
**Wartend auf:** KTBL BEK-Parameter-Webanwendung

🎉 **Die regulatory-domain ist jetzt der zentrale Compliance-Hub für VALEO-NeuroERP - inkl. KTBL-Integration!**
