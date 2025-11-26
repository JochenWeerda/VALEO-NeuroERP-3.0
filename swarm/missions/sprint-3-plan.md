# Sprint 3 Plan

**Datum:** 2025-01-30  
**Sprint:** 3  
**Phase:** P1 - Wichtige Gaps (Procurement)  
**Agent:** Agent-2 (Procurement)  
**Status:** 📋 Geplant

---

## 🎯 Sprint-Übersicht

### Ziel
Implementierung der 4 wichtigsten Procurement Capabilities (P1) für Sprint 3.

### Priorität
P1 - Hoch (MUSS, Priorität 2)

---

## 📋 Geplante Tasks

### Task 1: PROC-SUP-01 - Lieferantenstamm vervollständigen
**Status:** ⚠️ Teilweise vorhanden  
**Priorität:** P1 (MUSS, Priorität 2)

**Vorhanden:**
- ✅ `packages/frontend-web/src/pages/einkauf/lieferanten-liste.tsx`
- ✅ `packages/frontend-web/src/pages/einkauf/lieferanten-stamm.tsx`
- ✅ Adressen, Ansprechpartner vorhanden

**Gaps:**
- ❌ Bankdaten/Steuerinfos unklar
- ❌ Lieferantengruppen/Klassifikationen unklar
- ❌ Sperren/Archivieren unklar
- ❌ Dublettencheck unklar

**Aktionen:**
1. Bestehende Seiten analysieren
2. Fehlende Felder identifizieren
3. Bankdaten/Steuerinfos hinzufügen
4. Lieferantengruppen/Klassifikationen hinzufügen
5. Sperren/Archivieren-Funktionalität hinzufügen
6. Dublettencheck implementieren
7. i18n vollständig integrieren

**Dependencies:**
- ✅ Frontend-Seiten vorhanden
- ⚠️ Backend-API prüfen

**Effort:** 1 Woche

---

### Task 2: PROC-PO-01 - Bestellung erstellen vervollständigen
**Status:** ⚠️ Teilweise vorhanden  
**Priorität:** P1 (MUSS, Priorität 1)

**Vorhanden:**
- ✅ `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`
- ✅ `packages/frontend-web/src/pages/einkauf/bestellungen-liste.tsx`
- ✅ `packages/frontend-web/src/pages/einkauf/bestellung-stamm.tsx`
- ✅ API: `/api/mcp/documents/purchase_order`

**Gaps:**
- ❌ Incoterms unklar
- ❌ Referenzierung zu Bedarf/RFQ/Vertrag unklar
- ❌ Vollständigkeit der Felder prüfen

**Aktionen:**
1. Bestehende Seiten analysieren
2. Incoterms-Feld hinzufügen (falls fehlt)
3. Referenzierung zu Bedarf/RFQ/Vertrag hinzufügen
4. Vollständigkeit prüfen
5. i18n vollständig integrieren

**Dependencies:**
- ✅ Frontend-Seiten vorhanden
- ✅ Backend-API vorhanden
- ⚠️ Requisition-Integration (aus Sprint 2)

**Effort:** 1 Woche

---

### Task 3: PROC-IV-01 - Eingangsrechnung vervollständigen
**Status:** ⚠️ Teilweise vorhanden  
**Priorität:** P1 (MUSS, Priorität 1)

**Vorhanden:**
- ✅ `packages/frontend-web/src/pages/einkauf/rechnungseingang.tsx`
- ✅ `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx`
- ✅ Backend API: `app/api/v1/endpoints/ap_invoices.py`
- ✅ GL Integration (aus Sprint 1)

**Gaps:**
- ❌ PDF/OCR/API-Import fehlt
- ❌ Steuer/Kontierung prüfen
- ❌ Anlagebezug (PO, GR) prüfen

**Aktionen:**
1. Bestehende Seiten analysieren
2. PDF/OCR/API-Import-Funktionalität planen (optional für Sprint 3)
3. Steuer/Kontierung prüfen und vervollständigen
4. Anlagebezug (PO, GR) prüfen und vervollständigen
5. Integration mit PROC-IV-02 (2/3-Wege-Abgleich aus Sprint 2)
6. i18n vollständig integrieren

**Dependencies:**
- ✅ Frontend-Seiten vorhanden
- ✅ Backend-API vorhanden
- ✅ GL Integration vorhanden (Agent-1)
- ✅ 2/3-Wege-Abgleich vorhanden (Sprint 2)

**Effort:** 1-2 Wochen

---

### Task 4: PROC-PAY-01 - Zahlungsläufe vervollständigen
**Status:** ⚠️ Teilweise vorhanden  
**Priorität:** P1 (MUSS, Priorität 1)

**Vorhanden:**
- ✅ `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
- ✅ SEPA-UI vorhanden

**Gaps:**
- ❌ SEPA XML Export prüfen
- ❌ Status/Rückläufer prüfen
- ❌ Skonto prüfen

**Aktionen:**
1. Bestehende Seite analysieren
2. SEPA XML Export prüfen und vervollständigen
3. Status/Rückläufer-Funktionalität prüfen
4. Skonto-Berechnung prüfen
5. i18n vollständig integrieren

**Dependencies:**
- ✅ Frontend-Seite vorhanden
- ⚠️ Backend-API prüfen
- ⚠️ SEPA-Library prüfen

**Effort:** 1 Woche

---

## 📊 Sprint-Planung

### Woche 1
- **Tag 1-2:** PROC-SUP-01 (Lieferantenstamm)
- **Tag 3-4:** PROC-PO-01 (Bestellung erstellen)
- **Tag 5:** Review & Integration

### Woche 2
- **Tag 1-3:** PROC-IV-01 (Eingangsrechnung)
- **Tag 4-5:** PROC-PAY-01 (Zahlungsläufe)

### Woche 3 (Puffer)
- Integration-Tests
- Bug-Fixes
- Dokumentation

---

## 🔄 Dependencies

### Agent-2 → Agent-1
- PROC-IV-01 nutzt GL Integration (bereits vorhanden)
- PROC-PAY-01 nutzt Payment-Matching (bereits vorhanden)

### Agent-2 → Agent-4
- Keine neuen Dependencies

### Agent-2 → Agent-3
- Keine Dependencies

---

## ✅ Definition of Done

- [ ] Alle 4 P1 Capabilities implementiert
- [ ] i18n vollständig integriert
- [ ] Keine Linter-Fehler
- [ ] Handoff-Dokumente erstellt
- [ ] Status-Dokumente aktualisiert
- [ ] Keine Doppelstrukturen
- [ ] Integration mit Sprint 2 Features getestet

---

## 📝 Pre-Implementation Checklist

Vor Code-Erstellung:
- [ ] Bestehende Frontend-Seiten analysieren
- [ ] Backend-APIs prüfen
- [ ] Integration-Punkte identifizieren
- [ ] Doppelstrukturen vermeiden
- [ ] i18n-Übersetzungen planen

---

**Status:** 📋 **SPRINT 3 GEPLANT - BEREIT FÜR START**

