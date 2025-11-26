***REMOVED*** Sprint 1, Day 1 - Opportunity-Detail-Seite

**Datum:** 2025-01-27  
**Sprint:** Sprint 1 (Week 1-2)  
**Mission:** Phase 1.1 - Opportunities / Deals

***REMOVED******REMOVED*** ✅ Abgeschlossen

***REMOVED******REMOVED******REMOVED*** Opportunity-Detail-Seite ✅

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Hauptkomponente
- ✅ `opportunity-detail.tsx` erstellt
- ✅ ObjectPage-Integration mit Mask Builder
- ✅ Create/Edit-Modus (neu/bestehend)
- ✅ Navigation zurück zur Liste

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. Formular-Tabs
- ✅ **Grundinformationen**:
  - number (read-only, auto-generated)
  - name (required)
  - description
  - status (select)
  - stage (select)
  - customer_id (select)
  - contact_id (select)
  - owner_id
  - assigned_to

- ✅ **Deal-Informationen**:
  - amount
  - currency (EUR, USD, GBP, CHF)
  - probability (0-100)
  - expected_revenue (read-only, auto-calculated)
  - expected_close_date
  - actual_close_date

- ✅ **Quelle & Marketing**:
  - lead_source
  - source (web, referral, email, phone, trade_show, other)
  - campaign_id

- ✅ **Notizen**:
  - notes (textarea)

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Sidebar-Komponenten
- ✅ **History-Tab**:
  - Lädt History von API
  - Zeigt Feld-Änderungen
  - old_value → new_value Darstellung
  - changed_by & changed_at
  - change_reason (optional)

- ✅ **Quotes-Tab**:
  - Platzhalter für Quotes-Liste
  - "Angebot erstellen" Button
  - TODO: Quotes API-Integration

***REMOVED******REMOVED******REMOVED******REMOVED*** 4. Aktionen
- ✅ Save (Create/Update)
- ✅ Cancel
- ✅ Convert to Quote (Placeholder)
- ✅ Mark as Won
- ✅ Mark as Lost

***REMOVED******REMOVED******REMOVED******REMOVED*** 5. Validierung
- ✅ Zod-Schema für Opportunities
- ✅ Auto-Berechnung expected_revenue
- ✅ Auto-Set owner_id von assigned_to
- ✅ Validation-Feedback

***REMOVED******REMOVED******REMOVED******REMOVED*** 6. i18n-Integration
- ✅ Alle Labels übersetzt
- ✅ Neue Übersetzungen hinzugefügt:
  - `crud.stages.*` (8 Stages)
  - `crud.sources.*` (6 Sources)
  - `crud.detail.dealInfo`
  - `crud.detail.sourceAndMarketing`
  - `crud.detail.quotes`
  - `crud.actions.convertToQuote`
  - `crud.actions.createQuote`
  - `crud.actions.markAsWon`
  - `crud.actions.markAsLost`
  - `crud.fields.expectedRevenue`
  - `crud.fields.expectedCloseDate`
  - `crud.fields.actualCloseDate`
  - `crud.fields.campaign`
  - `crud.fields.owner`
  - `crud.fields.stage`
  - `crud.fields.probability`
  - `crud.messages.noHistory`
  - `crud.messages.noQuotes`
  - `crud.messages.comingSoon`
  - `crud.tooltips.placeholders.*` (12 neue)

***REMOVED******REMOVED*** 📋 Nächste Schritte

1. **Pipeline-Kanban** (Drag & Drop)
2. **Forecast-Report** (Visualisierungen)
3. **Tests** (Unit, Integration, E2E)

***REMOVED******REMOVED*** 📊 Fortschritt

**Sprint 1 (Frontend):**
- ✅ 50% - Opportunities-Liste
- ✅ 50% - Opportunity-Detail
- ⏳ 0% - Pipeline-Kanban
- ⏳ 0% - Forecast-Report

**Gesamt Phase 1.1:**
- ✅ 100% - Backend
- ✅ 50% - Frontend (Liste + Detail fertig)
- ⏳ 0% - Tests

---

**Nächster Update:** Nach Pipeline-Kanban

