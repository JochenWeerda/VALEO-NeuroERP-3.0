# Sprint 5 Plan

**Datum:** 2025-01-30  
**Sprint:** 5  
**Phase:** P2/P3 - Mittlere/Niedrige Priorität (Procurement)  
**Agent:** Agent-2 (Procurement)  
**Status:** 📋 Geplant

---

## 🎯 Sprint-Übersicht

### Ziel
Implementierung von 3 weiteren Procurement Capabilities (P2/P3) für Sprint 5.

### Priorität
P2/P3 - Mittel/Niedrig (SOLL/KANN, Priorität 3-4)

---

## 📋 Geplante Tasks

### Task 1: PROC-SUP-03 - Compliance / Dokumente
**Status:** ❌ Nicht vorhanden  
**Priorität:** P2 (SOLL, Priorität 3)

**Gaps:**
- ❌ Keine Dokumentenverwaltung für Lieferanten
- ❌ Zertifikate, Rahmenverträge, NDA, ESG fehlen
- ❌ Gültigkeit/Erinnerungen fehlen

**Aktionen:**
1. Dokumentenverwaltung-UI erstellen
2. Dokument-Typen implementieren (Zertifikat, Rahmenvertrag, NDA, ESG)
3. Gültigkeitsdatum-Tracking
4. Erinnerungsfunktion für ablaufende Dokumente
5. Sperr-/Freigabelogik bei abgelaufenen Dokumenten
6. i18n vollständig integrieren

**Dependencies:**
- ✅ Lieferantenstamm vorhanden (Sprint 3)
- ⚠️ Backend-API für Dokumente prüfen

**Effort:** 2-3 Wochen

---

### Task 2: PROC-RFQ-02 - Lieferantenangebote / Bids
**Status:** ❌ Nicht vorhanden  
**Priorität:** P2 (SOLL, Priorität 3)

**Gaps:**
- ❌ Keine Bid-Erfassung gefunden
- ❌ Keine Angebots-Import-Funktionalität
- ❌ Keine Vergleichsmöglichkeit

**Aktionen:**
1. Bid-Erfassungs-UI erstellen
2. Angebots-Import-Funktionalität (CSV/Excel)
3. Bid-Vergleichsansicht
4. Integration mit PROC-RFQ-01
5. i18n vollständig integrieren

**Dependencies:**
- ✅ RFQ vorhanden (Sprint 4)
- ⚠️ Backend-API für Bids prüfen

**Effort:** 2-3 Wochen

---

### Task 3: PROC-RFQ-03 - Angebotsvergleich / Award
**Status:** ❌ Nicht vorhanden  
**Priorität:** P2 (SOLL, Priorität 3)

**Gaps:**
- ❌ Keine Vergleichsmatrix gefunden (Preis/Leadtime/Score)
- ❌ Keine Entscheidungsdoku

**Aktionen:**
1. Vergleichsmatrix-UI erstellen
2. Multi-Kriterien-Vergleich (Preis, Leadtime, Score)
3. Award-Entscheidungsdokumentation
4. Integration mit PROC-RFQ-02
5. i18n vollständig integrieren

**Dependencies:**
- ✅ RFQ vorhanden (Sprint 4)
- ⚠️ PROC-RFQ-02 sollte vorher abgeschlossen sein

**Effort:** 1-2 Wochen

---

## 📊 Sprint-Planung

### Woche 1-2
- **Tag 1-5:** PROC-SUP-03 (Compliance / Dokumente) - Start
- **Tag 6-10:** PROC-SUP-03 (Compliance / Dokumente) - Fortsetzung

### Woche 3-4
- **Tag 11-15:** PROC-RFQ-02 (Lieferantenangebote / Bids) - Start
- **Day 16-20:** PROC-RFQ-02 (Lieferantenangebote / Bids) - Fortsetzung

### Woche 5
- **Tag 21-25:** PROC-RFQ-03 (Angebotsvergleich / Award)
- Integration-Tests
- Bug-Fixes
- Dokumentation

---

## 🔄 Dependencies

### Agent-2 → Agent-1
- Keine neuen Dependencies

### Agent-2 → Agent-4
- PROC-SUP-03 nutzt möglicherweise Dokumenten-Infrastructure

### Agent-2 → Agent-3
- Keine Dependencies

---

## ✅ Definition of Done

- [ ] Alle 3 P2/P3 Capabilities implementiert
- [ ] i18n vollständig integriert
- [ ] Keine Linter-Fehler
- [ ] Handoff-Dokumente erstellt
- [ ] Status-Dokumente aktualisiert
- [ ] Keine Doppelstrukturen
- [ ] Integration mit Sprint 2, 3 & 4 Features getestet

---

## 📝 Pre-Implementation Checklist

Vor Code-Erstellung:
- [ ] Bestehende Frontend-Seiten analysieren
- [ ] Backend-APIs prüfen
- [ ] Integration-Punkte identifizieren
- [ ] Doppelstrukturen vermeiden
- [ ] i18n-Übersetzungen planen

---

**Status:** 📋 **SPRINT 5 GEPLANT - BEREIT FÜR START**

