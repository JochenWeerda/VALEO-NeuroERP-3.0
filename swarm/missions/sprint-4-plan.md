# Sprint 4 Plan

**Datum:** 2025-01-30  
**Sprint:** 4  
**Phase:** P2 - Mittlere Priorität (Procurement)  
**Agent:** Agent-2 (Procurement)  
**Status:** 📋 Geplant

---

## 🎯 Sprint-Übersicht

### Ziel
Implementierung von 3 Procurement Capabilities (P2) für Sprint 4.

### Priorität
P2 - Mittel (SOLL, Priorität 2-3)

---

## 📋 Geplante Tasks

### Task 1: PROC-SUP-02 - Lieferantenbewertung
**Status:** ❌ Nicht vorhanden  
**Priorität:** P2 (SOLL, Priorität 3)

**Gaps:**
- ❌ Keine Bewertungs-UI/Score-System
- ❌ Keine Kriterien (Qualität, Termintreue, Preis, Service)
- ❌ Keine Scores + Trends
- ❌ Keine Sperr-/Freigabelogik

**Aktionen:**
1. Bewertungs-UI erstellen
2. Kriterien-System implementieren (Qualität, Termintreue, Preis, Service)
3. Score-Berechnung implementieren
4. Trend-Anzeige implementieren
5. Sperr-/Freigabelogik basierend auf Score
6. i18n vollständig integrieren

**Dependencies:**
- ✅ Lieferantenstamm vorhanden (Sprint 3)
- ⚠️ Backend-API für Bewertungen prüfen

**Effort:** 2-3 Wochen

---

### Task 2: PROC-RFQ-01 - Anfrage / RFQ
**Status:** ⚠️ Teilweise vorhanden  
**Priorität:** P2 (SOLL, Priorität 2)

**Vorhanden:**
- ✅ `packages/frontend-web/src/pages/einkauf/anfragen-liste.tsx`
- ✅ `packages/frontend-web/src/pages/einkauf/anfrage-stamm.tsx`
- ✅ Backend API vorhanden

**Gaps:**
- ❌ RFQ-Versand an Lieferanten fehlt
- ❌ RFQ-Status nachvollziehbar machen
- ❌ RFQ-Positionen vervollständigen

**Aktionen:**
1. Bestehende Seiten analysieren
2. RFQ-Versand-Funktionalität implementieren (Email/Portal)
3. RFQ-Status-Workflow vervollständigen
4. RFQ-Positionen vervollständigen
5. i18n vollständig integrieren

**Dependencies:**
- ✅ Frontend-Seiten vorhanden
- ✅ Backend-API vorhanden
- ⚠️ Email/Portal-Integration prüfen

**Effort:** 1-2 Wochen

---

### Task 3: PROC-REP-01 - Standardreports Einkauf
**Status:** ❌ Nicht vorhanden  
**Priorität:** P2 (MUSS, Priorität 2)

**Gaps:**
- ❌ Keine Procurement-Reports
- ❌ Offene Bestellungen-Report fehlt
- ❌ Spend-Analyse fehlt
- ❌ Lieferantenperformance-Report fehlt
- ❌ Toleranz-/Abweichungsreports fehlt

**Aktionen:**
1. Report-Infrastructure prüfen
2. Offene Bestellungen-Report erstellen
3. Spend-Analyse-Report erstellen
4. Lieferantenperformance-Report erstellen
5. Toleranz-/Abweichungsreports erstellen
6. Filter, Drilldown, Export implementieren
7. i18n vollständig integrieren

**Dependencies:**
- ✅ Daten vorhanden (PO, GR, IV, Supplier)
- ⚠️ Report-Infrastructure prüfen

**Effort:** 2-3 Wochen

---

## 📊 Sprint-Planung

### Woche 1-2
- **Tag 1-5:** PROC-RFQ-01 (RFQ vervollständigen)
- **Tag 6-10:** PROC-SUP-02 (Lieferantenbewertung) - Start

### Woche 3-4
- **Tag 11-15:** PROC-SUP-02 (Lieferantenbewertung) - Fortsetzung
- **Tag 16-20:** PROC-REP-01 (Standardreports) - Start

### Woche 5 (Puffer)
- **Tag 21-25:** PROC-REP-01 (Standardreports) - Fortsetzung
- Integration-Tests
- Bug-Fixes
- Dokumentation

---

## 🔄 Dependencies

### Agent-2 → Agent-1
- Keine neuen Dependencies

### Agent-2 → Agent-4
- PROC-REP-01 nutzt möglicherweise Report-Infrastructure

### Agent-2 → Agent-3
- Keine Dependencies

---

## ✅ Definition of Done

- [ ] Alle 3 P2 Capabilities implementiert
- [ ] i18n vollständig integriert
- [ ] Keine Linter-Fehler
- [ ] Handoff-Dokumente erstellt
- [ ] Status-Dokumente aktualisiert
- [ ] Keine Doppelstrukturen
- [ ] Integration mit Sprint 2 & 3 Features getestet

---

## 📝 Pre-Implementation Checklist

Vor Code-Erstellung:
- [ ] Bestehende Frontend-Seiten analysieren
- [ ] Backend-APIs prüfen
- [ ] Integration-Punkte identifizieren
- [ ] Doppelstrukturen vermeiden
- [ ] i18n-Übersetzungen planen

---

**Status:** 📋 **SPRINT 4 GEPLANT - BEREIT FÜR START**


