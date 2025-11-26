***REMOVED*** Sprint 2 - Procurement P0 Plan

**Datum:** 2025-01-27  
**Sprint:** 2  
**Phase:** P0 - Kritische Gaps (Procurement)  
**Agent:** Agent-2 (Procurement)

---

***REMOVED******REMOVED*** 🔍 Pre-Implementation Audit

***REMOVED******REMOVED******REMOVED*** ✅ Vorhandene Funktionalität (NICHT neu erstellen)

***REMOVED******REMOVED******REMOVED******REMOVED*** PROC-GR-01: Wareneingang

**Backend - ✅ Vorhanden:**
- `packages/purchase-domain/src/domain/services/purchase-order-workflow-service.ts`
  - `processGoodsReceipt()` Methode vorhanden
  - Three-way matching implementiert
  - Inventory-Update vorhanden
- `packages/purchase-domain/src/app/routes/purchase-workflow.ts`
  - `POST /orders/:orderId/goods-receipt` Endpoint vorhanden
- `packages/procurement-domain/src/core/entities/purchase-order.ts`
  - `recordReceipt()` Methode vorhanden

**Frontend - ⚠️ Teilweise vorhanden:**
- `packages/frontend-web/src/pages/einkauf/anlieferavis.tsx` - Anlieferavis (Delivery Note)
- `packages/frontend-web/src/pages/charge/wareneingang.tsx` - Charge-spezifischer Wareneingang
- `packages/frontend-web/src/pages/futtermittel/futtermittel-wareneingang.tsx` - Futtermittel-spezifisch

**Gaps:**
- ❌ Keine generische Wareneingang-Seite für Procurement
- ❌ Keine PO-Referenzierung in bestehenden Seiten
- ❌ Keine Teil-/Restmengen-Buchung in UI
- ❌ Keine Backorder-Verwaltung in UI
- ❌ Frontend nutzt Backend-API nicht (noch nicht integriert)

**Empfehlung:**
- ✅ **Backend NICHT neu erstellen** - API existiert bereits
- ⚠️ **Frontend erweitern** - Bestehende Seiten erweitern ODER neue generische Seite erstellen
- ✅ **Integration prüfen** - Prüfen ob Frontend bereits Backend-API nutzt

---

***REMOVED******REMOVED******REMOVED******REMOVED*** PROC-IV-02: 2/3-Wege-Abgleich

**Backend - ✅ Vorhanden:**
- `packages/purchase-domain/src/domain/services/purchase-order-workflow-service.ts`
  - Three-way matching bereits implementiert
  - PO-GR-IV Abgleich vorhanden

**Frontend - ❌ Nicht vorhanden:**
- Keine UI für Abgleich (`rechnung-abgleich.tsx`)

**Empfehlung:**
- ✅ **Backend NICHT neu erstellen** - Logik existiert
- ⚠️ **Frontend-UI erstellen** - `rechnung-abgleich.tsx` für manuellen Abgleich
- ⚠️ **Toleranz-Konfiguration** - UI für Toleranz-Regeln

---

***REMOVED******REMOVED******REMOVED******REMOVED*** PROC-PO-02: PO-Änderungen & Storno

**Backend - ⚠️ Teilweise vorhanden:**
- `packages/procurement-domain/src/core/entities/purchase-order.ts`
  - `version` Feld vorhanden
  - Status-Management vorhanden
- `app/documents/router.py`
  - Status-Transition-Logik vorhanden

**Gaps:**
- ❌ Kein Change-Log/Versionierung-System
- ❌ Keine Genehmigungslogik bei Änderungen
- ❌ Keine Storno-Funktionalität
- ❌ Kein Audit-Trail für Änderungen

**Empfehlung:**
- ⚠️ **Change-Log implementieren** - Nutze Audit-Trail-Infrastructure (Agent-4)
- ⚠️ **Storno-Funktionalität** - Implementieren
- ⚠️ **Genehmigungslogik** - Nutze Workflow-Engine (Agent-4)

---

***REMOVED******REMOVED******REMOVED******REMOVED*** PROC-REQ-01: Bedarfsmeldung (Purchase Requisition)

**Backend - ✅ Vorhanden:**
- `packages/purchase-domain/src/app/routes/purchase-workflow.ts`
  - `POST /requisitions` Endpoint vorhanden

**Frontend - ✅ Vorhanden:**
- `packages/frontend-web/src/pages/einkauf/anfragen-liste.tsx` - Liste
- `packages/frontend-web/src/pages/einkauf/anfrage-stamm.tsx` - Detail

**Status:**
- ✅ Frontend existiert
- ⚠️ Prüfen ob vollständig (Status-Workflow, Freigabe)

**Empfehlung:**
- ✅ **NICHT neu erstellen** - Frontend existiert bereits
- ⚠️ **Vervollständigen** - Status-Workflow prüfen und vervollständigen

---

***REMOVED******REMOVED*** 🎯 Sprint 2 Aufgaben

***REMOVED******REMOVED******REMOVED*** Task 1: PROC-GR-01 - Wareneingang Frontend erweitern

**Status:** ⚠️ Frontend teilweise vorhanden, Backend vorhanden

**Aktionen:**
1. ✅ Prüfen ob `anlieferavis.tsx` Backend-API nutzt
2. ⚠️ Falls nicht: Integration mit `POST /orders/:orderId/goods-receipt` API
3. ⚠️ Erweitern: PO-Referenzierung, Teil-/Restmengen, Backorder
4. ⚠️ ODER: Neue generische `wareneingang.tsx` Seite erstellen (falls bestehende nicht erweiterbar)

**Dependencies:**
- ✅ Backend-API vorhanden (Agent-4)
- ✅ PO-System vorhanden
- ✅ Inventory-System vorhanden

---

***REMOVED******REMOVED******REMOVED*** Task 2: PROC-IV-02 - 2/3-Wege-Abgleich Frontend-UI

**Status:** ❌ Frontend fehlt, Backend vorhanden

**Aktionen:**
1. ⚠️ Frontend-UI erstellen: `rechnung-abgleich.tsx`
2. ⚠️ Toleranz-Regeln konfigurierbar machen
3. ⚠️ Blockierung bei Abweichungen in UI
4. ⚠️ Begründungspflicht für Abweichungen

**Dependencies:**
- ✅ Backend-Logik vorhanden
- ✅ PO-System vorhanden
- ✅ GR-System vorhanden
- ✅ Invoice-System vorhanden

---

***REMOVED******REMOVED******REMOVED*** Task 3: PROC-PO-02 - PO-Änderungen & Storno

**Status:** ⚠️ Teilweise vorhanden

**Aktionen:**
1. ⚠️ Change-Log/Versionierung implementieren (nutze Audit-Trail von Agent-4)
2. ⚠️ Genehmigungslogik bei Änderungen (nutze Workflow-Engine von Agent-4)
3. ⚠️ Storno-Funktionalität implementieren
4. ⚠️ Audit-Trail für Änderungen

**Dependencies:**
- ✅ Audit-Trail-Infrastructure (Agent-4)
- ✅ Workflow-Engine (Agent-4)
- ✅ PO-System vorhanden

---

***REMOVED******REMOVED******REMOVED*** Task 4: PROC-REQ-01 - Bedarfsmeldung vervollständigen

**Status:** ✅ Frontend vorhanden, Backend vorhanden

**Aktionen:**
1. ✅ Prüfen ob vollständig
2. ⚠️ Falls nicht: Status-Workflow vervollständigen
3. ⚠️ Freigabe-Workflow prüfen

**Dependencies:**
- ✅ Frontend vorhanden
- ✅ Backend vorhanden
- ⚠️ Workflow-Engine (Agent-4)

---

***REMOVED******REMOVED*** 📋 Implementierungs-Strategie

***REMOVED******REMOVED******REMOVED*** Phase 1: Prüfung & Integration (Heute)
1. ✅ Bestehende Frontend-Seiten analysieren
2. ✅ Backend-APIs prüfen
3. ✅ Integration-Punkte identifizieren
4. ✅ Doppelstrukturen vermeiden

***REMOVED******REMOVED******REMOVED*** Phase 2: Erweiterung (Sprint 2)
1. ⚠️ Frontend erweitern (nicht neu erstellen)
2. ⚠️ Backend-Integration vervollständigen
3. ⚠️ Fehlende UI-Komponenten erstellen

***REMOVED******REMOVED******REMOVED*** Phase 3: Vervollständigung (Sprint 2-3)
1. ⚠️ Change-Log/Versionierung
2. ⚠️ Storno-Funktionalität
3. ⚠️ Audit-Trail Integration

---

***REMOVED******REMOVED*** ✅ Keine Doppelstrukturen

**Bestätigt:**
- ✅ Backend-APIs existieren bereits - NICHT neu erstellen
- ✅ Frontend-Seiten teilweise vorhanden - Erweitern statt neu erstellen
- ✅ Infrastructure nutzen - Audit-Trail, Workflow-Engine von Agent-4

---

**Status:** ✅ **AUDIT ABGESCHLOSSEN - BEREIT FÜR IMPLEMENTIERUNG**

