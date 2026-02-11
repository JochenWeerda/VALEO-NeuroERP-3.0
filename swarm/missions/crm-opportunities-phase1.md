# Phase 1.1: Opportunities / Deals (Sales Pipeline)

**Status:** 🚀 In Progress  
**Priorität:** 🔴 Kritisch  
**Sprint:** Sprint 1-2 (Weeks 1-4)  
**Owner:** Sales-Team  
**Capability:** CRM-OPP-01

## Mission Overview

Implementierung der Sales Pipeline mit Opportunities/Deals, Stages, Probabilities und Forecast-Funktionalität.

**Referenz:**
- GAP-Card: `gap/gaps-crm-marketing.md` → CARD CRM-MKT-001
- Capability: `gap/capability-model-crm-marketing.md` → CRM-OPP-01

## Sprint 1: Backend & Datenmodell (Week 1-2)

### Backend Tasks

#### Task 1.1.1: Service erstellen
- [ ] `services/crm-sales/` Verzeichnis anlegen
- [ ] `services/crm-sales/README.md` erstellen
- [ ] `services/crm-sales/app/main.py` erstellen (FastAPI)
- [ ] `services/crm-sales/app/db/models.py` erstellen (SQLAlchemy)
- [ ] `services/crm-sales/app/db/schemas.py` erstellen (Pydantic)
- [ ] `services/crm-sales/app/api/opportunities.py` erstellen
- [ ] Docker-Compose Eintrag hinzufügen
- [ ] Health-Check Endpoint implementieren

**Definition of Done:**
- ✅ Service startet ohne Fehler
- ✅ Health-Check antwortet 200 OK
- ✅ Service ist im Docker-Netzwerk erreichbar

---

#### Task 1.1.2: Datenmodell implementieren
- [ ] `Opportunity` Entity erstellen:
  - id, tenant_id, number, name
  - account_id, contact_id, owner_id
  - stage, probability, value, currency
  - close_date, expected_revenue
  - status (open, won, lost, abandoned)
  - source, campaign_id
  - notes, description
  - created_at, updated_at, created_by, updated_by
- [ ] `OpportunityStage` Entity erstellen (Lookup):
  - id, tenant_id, name, order, probability_default
  - required_fields (JSON)
- [ ] `OpportunityHistory` Entity erstellen (Audit):
  - id, opportunity_id, field_name, old_value, new_value
  - changed_by, changed_at
- [ ] Migration erstellen: `alembic/versions/xxx_create_opportunities.py`
- [ ] Seed-Daten erstellen (Beispiel-Stages)

**Definition of Done:**
- ✅ Migration läuft ohne Fehler
- ✅ Seed-Daten werden geladen
- ✅ Alle Entities haben Tenant-Isolation

---

#### Task 1.1.3: API-Endpoints implementieren
- [ ] `GET /api/v1/opportunities` - Liste mit Filter/Pagination
- [ ] `GET /api/v1/opportunities/{id}` - Detail
- [ ] `POST /api/v1/opportunities` - Erstellen
- [ ] `PUT /api/v1/opportunities/{id}` - Aktualisieren
- [ ] `DELETE /api/v1/opportunities/{id}` - Löschen
- [ ] `GET /api/v1/opportunities/stages` - Stages-Liste
- [ ] `GET /api/v1/opportunities/pipeline` - Pipeline-Aggregation
- [ ] `GET /api/v1/opportunities/forecast` - Forecast-Daten
- [ ] Validierung mit Pydantic
- [ ] Error-Handling implementieren

**Definition of Done:**
- ✅ Alle Endpoints funktionieren
- ✅ Validierung greift
- ✅ Error-Responses sind konsistent
- ✅ API-Dokumentation (OpenAPI) ist vollständig

---

### Integration Tasks

#### Task 1.1.4: Events implementieren
- [ ] `crm.opportunity.created` Event
- [ ] `crm.opportunity.updated` Event
- [ ] `crm.opportunity.stage-changed` Event
- [ ] `crm.opportunity.won` Event
- [ ] `crm.opportunity.lost` Event
- [ ] Event-Bus Integration (RabbitMQ/Kafka)
- [ ] Event-Payload definieren

**Definition of Done:**
- ✅ Events werden bei Aktionen ausgelöst
- ✅ Events sind im Event-Log sichtbar
- ✅ Event-Payload ist dokumentiert

---

## Sprint 2: Frontend & UI (Week 3-4)

### Frontend Tasks

#### Task 1.2.1: Opportunities-Liste
- [ ] `packages/frontend-web/src/pages/crm/opportunities-liste.tsx` erstellen
- [ ] ListReport-Konfiguration mit i18n
- [ ] Spalten: Number, Name, Account, Stage, Value, Probability, Close Date, Owner, Status
- [ ] Filter: Stage, Status, Owner, Close Date Range
- [ ] Sortierung: Standard nach Close Date
- [ ] Bulk-Actions: Convert to Quote, Mark as Won/Lost
- [ ] Export-Funktionalität (CSV)
- [ ] API-Integration mit React Query

**Definition of Done:**
- ✅ Liste zeigt alle Opportunities
- ✅ Filter funktionieren
- ✅ Sortierung funktioniert
- ✅ Bulk-Actions funktionieren
- ✅ Export funktioniert
- ✅ i18n vollständig

---

#### Task 1.2.2: Opportunity-Detail
- [ ] `packages/frontend-web/src/pages/crm/opportunity-detail.tsx` erstellen
- [ ] ObjectPage-Konfiguration mit i18n
- [ ] Tabs: Grunddaten, Aktivitäten, Anhänge, Historie
- [ ] Felder: Name, Account, Contact, Owner, Stage, Probability, Value, Close Date, Source, Campaign, Notes
- [ ] Stage-Wechsel mit Validierung
- [ ] Related Items: Activities, Quotes, Orders
- [ ] API-Integration mit React Query
- [ ] Save/Cancel-Handling

**Definition of Done:**
- ✅ Detail-View zeigt alle Daten
- ✅ Stage-Wechsel funktioniert mit Validierung
- ✅ Related Items werden angezeigt
- ✅ Save/Cancel funktioniert
- ✅ i18n vollständig

---

#### Task 1.2.3: Pipeline-Kanban
- [ ] `packages/frontend-web/src/pages/crm/pipeline-kanban.tsx` erstellen
- [ ] Kanban-Komponente (z.B. @dnd-kit)
- [ ] Spalten pro Stage
- [ ] Drag & Drop für Stage-Wechsel
- [ ] Karten zeigen: Name, Account, Value, Close Date
- [ ] Filter: Owner, Account, Date Range
- [ ] Aggregation: Summe pro Stage, Conversion-Rate
- [ ] API-Integration mit React Query

**Definition of Done:**
- ✅ Kanban zeigt alle Opportunities
- ✅ Drag & Drop funktioniert
- ✅ Stage-Wechsel via Drag & Drop
- ✅ Filter funktionieren
- ✅ Aggregation wird angezeigt
- ✅ i18n vollständig

---

#### Task 1.2.4: Forecast-Report
- [ ] `packages/frontend-web/src/pages/crm/forecast-report.tsx` erstellen
- [ ] Chart-Komponente (z.B. recharts)
- [ ] Filter: Periode (Monat/Quartal), Owner, Team
- [ ] Visualisierung: Forecast nach Stage, Owner, Periode
- [ ] Tabelle: Detail-Daten
- [ ] Export-Funktionalität (PDF/Excel)
- [ ] API-Integration mit React Query

**Definition of Done:**
- ✅ Forecast wird korrekt berechnet
- ✅ Visualisierung ist aussagekräftig
- ✅ Filter funktionieren
- ✅ Export funktioniert
- ✅ i18n vollständig

---

### Integration Tasks

#### Task 1.2.5: Sales-Modul Integration
- [ ] Link Opportunity → Quote
- [ ] Link Opportunity → Order
- [ ] Belegkette-Visualisierung
- [ ] Convert to Quote-Funktion
- [ ] Revenue-Attribution

**Definition of Done:**
- ✅ Verknüpfungen funktionieren
- ✅ Belegkette wird angezeigt
- ✅ Convert to Quote funktioniert
- ✅ Revenue wird korrekt attribuiert

---

## Testing

### Task 1.3.1: E2E Tests
- [ ] `tests/e2e/crm-marketing/opportunities.spec.ts` erstellen
- [ ] Test: Opportunity erstellen
- [ ] Test: Opportunity bearbeiten
- [ ] Test: Stage wechseln
- [ ] Test: Pipeline-Kanban Drag & Drop
- [ ] Test: Forecast-Report
- [ ] Test: Convert to Quote
- [ ] Test: Export

**Definition of Done:**
- ✅ Alle Tests grün
- ✅ Test-Coverage > 80%
- ✅ Tests sind stabil (nicht flaky)

---

## Documentation

### Task 1.4.1: Dokumentation
- [ ] API-Dokumentation aktualisieren
- [ ] User-Guide für Opportunities erstellen
- [ ] Screenshots für Evidence
- [ ] Handoff-Notiz für nächste Phase

**Definition of Done:**
- ✅ Dokumentation ist vollständig
- ✅ Screenshots vorhanden
- ✅ Handoff-Notiz erstellt

---

## Definition of Done (Gesamt)

- ✅ Opportunities können erstellt, bearbeitet, gelöscht werden
- ✅ Pipeline-Visualisierung zeigt Funnel mit Conversion-Rates
- ✅ Forecast-Reports aggregieren nach Stage/Owner/Periode
- ✅ Integration mit Sales-Modul funktional
- ✅ Alle Tests grün
- ✅ Evidence aktualisiert (Screenshots, Traces)
- ✅ Dokumentation vollständig

---

## Daily Standup Template

**Datum:** YYYY-MM-DD  
**Sprint:** Sprint X, Day Y

**Was wurde gestern gemacht?**
- Task 1.X.Y: [Status]

**Was wird heute gemacht?**
- Task 1.X.Y: [Geplant]

**Blockers?**
- [Keine / Beschreibung]

**Notes:**
- [Wichtige Erkenntnisse]

---

## Review & Retro Template

**Sprint:** Sprint X  
**Datum:** YYYY-MM-DD

**Was wurde erreicht?**
- ✅ Task 1.X.Y: Abgeschlossen
- ⏳ Task 1.X.Y: In Progress

**Was lief gut?**
- [Positives]

**Was kann verbessert werden?**
- [Verbesserungen]

**Action Items:**
- [ ] Action 1
- [ ] Action 2

**Nächste Schritte:**
- [ ] Task 1.X.Y: Starten

---

**Letzte Aktualisierung:** 2025-01-27  
**Nächste Review:** Nach Sprint 1


