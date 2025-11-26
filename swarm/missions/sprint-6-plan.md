# Sprint 6 Plan

**Datum:** 2025-01-30  
**Sprint:** 6  
**Phase:** P2/P3 - Mittlere/Niedrige Priorität (Procurement)  
**Agent:** Agent-2 (Procurement)  
**Status:** 📋 Geplant

---

## 🎯 Sprint-Übersicht

### Ziel
Implementierung von 3 weiteren Procurement Capabilities (P2/P3) für Sprint 6.

### Priorität
P2/P3 - Mittel/Niedrig (SOLL/KANN, Priorität 3-4)

---

## 📋 Geplante Tasks

### Task 1: PROC-PO-03 - PO-Kommunikation
**Status:** ⚠️ Partial (Print vorhanden)  
**Priorität:** P2 (SOLL, Priorität 3)

**Gaps:**
- ✅ Print-Funktion vorhanden
- ❌ Email/Portal-Versand fehlt
- ❌ Sprachen/Branding unklar

**Aktionen:**
1. Email-Versand-Funktionalität implementieren
2. Portal-Versand-Funktionalität implementieren
3. Sprachauswahl für PO-Dokumente
4. Branding-Optionen prüfen
5. i18n vollständig integrieren

**Dependencies:**
- ✅ PO-Detail-Seite vorhanden (Sprint 2)
- ⚠️ Email-Infrastructure prüfen

**Effort:** 1-2 Wochen

---

### Task 2: PROC-GR-02 - Retouren an Lieferant
**Status:** ❌ Nicht vorhanden  
**Priorität:** P2 (SOLL, Priorität 3)

**Gaps:**
- ❌ Keine Retouren-Funktionalität gefunden
- ❌ Rücksendung, Gründe, Gutschriftbezug fehlen

**Aktionen:**
1. Retouren-UI erstellen
2. Rücksendungs-Gründe erfassen
3. Gutschriftbezug implementieren
4. Integration mit Wareneingang
5. i18n vollständig integrieren

**Dependencies:**
- ✅ Wareneingang vorhanden (Sprint 2)
- ⚠️ Gutschrift-API prüfen

**Effort:** 1-2 Wochen

---

### Task 3: PROC-PAY-02 - Lieferantengutschriften / Belastungen
**Status:** ❌ Nicht vorhanden  
**Priorität:** P2 (SOLL, Priorität 3)

**Gaps:**
- ❌ Keine Credit/Debit-Memo-Funktionalität gefunden
- ❌ Verrechnung fehlt

**Aktionen:**
1. Credit-Memo-UI erstellen
2. Debit-Memo-UI erstellen
3. Verrechnungslogik implementieren
4. Integration mit AP-Invoices
5. i18n vollständig integrieren

**Dependencies:**
- ✅ AP-Invoices vorhanden (Sprint 3)
- ⚠️ Credit/Debit-Memo-API prüfen

**Effort:** 2-3 Wochen

---

## 📊 Sprint-Planung

### Woche 1-2
- **Tag 1-5:** PROC-PO-03 (PO-Kommunikation) - Email/Portal-Versand
- **Tag 6-10:** PROC-PO-03 (PO-Kommunikation) - Sprachen/Branding

### Woche 3-4
- **Tag 11-15:** PROC-GR-02 (Retouren an Lieferant) - Start
- **Day 16-20:** PROC-GR-02 (Retouren an Lieferant) - Fortsetzung

### Woche 5-6
- **Tag 21-30:** PROC-PAY-02 (Lieferantengutschriften / Belastungen)
- Integration-Tests
- Bug-Fixes
- Dokumentation

---

## 🔄 Dependencies

### Agent-2 → Agent-1
- PROC-PAY-02 nutzt möglicherweise Finance-APIs

### Agent-2 → Agent-4
- PROC-PO-03 nutzt möglicherweise Email-Infrastructure

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
- [ ] Integration mit Sprint 2, 3, 4 & 5 Features getestet

---

## 📝 Pre-Implementation Checklist

Vor Code-Erstellung:
- [ ] Bestehende Frontend-Seiten analysieren
- [ ] Backend-APIs prüfen
- [ ] Integration-Punkte identifizieren
- [ ] Doppelstrukturen vermeiden
- [ ] i18n-Übersetzungen planen

---

**Status:** 📋 **SPRINT 6 GEPLANT - BEREIT FÜR START**

