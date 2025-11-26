# Phase 1.4 - Segmente & Zielgruppen

**Status:** 🚀 In Progress  
**Priorität:** 🟡 Mittel  
**Capability:** MKT-SEG-01  
**Prioritäts-Score:** 10.0  
**Lösungstyp:** C (New Module)  
**Owner:** Marketing-Team  
**Aufwand:** 2-3 Wochen

## Mission Overview

Implementierung eines vollständigen Segmentierungs-Systems mit:
- Regelbasierte Segmente (dynamisch)
- Statische Segmente (manuell)
- Segment-Performance-Tracking
- Segment-basierte Kampagnen-Zuweisung
- Automatische Segment-Aktualisierung

## Backend Tasks

### 1. Service erstellen: `services/crm-marketing/`
- [ ] Projektstruktur anlegen
- [ ] FastAPI-App mit Router
- [ ] Database-Models (SQLAlchemy)
- [ ] Pydantic-Schemas
- [ ] Alembic-Migrationen

### 2. Database Models
- [ ] `Segment` Entity:
  - `id`, `tenant_id`
  - `name`, `description`
  - `type` (dynamic, static, hybrid)
  - `status` (active, inactive, archived)
  - `rules` (JSON - für dynamische Segmente)
  - `member_count` (cached)
  - `last_updated_at`
  - `created_at`, `updated_at`
  - `created_by`, `updated_by`

- [ ] `SegmentRule` Entity:
  - `id`, `segment_id` (FK)
  - `field` (z.B. "customer.category", "contact.email_domain")
  - `operator` (equals, contains, greater_than, in, etc.)
  - `value` (JSON - kann Array sein)
  - `logical_operator` (AND, OR) - für Kombinationen
  - `order` (für Reihenfolge der Regeln)

- [ ] `SegmentMember` Entity:
  - `id`, `segment_id` (FK)
  - `contact_id` (FK)
  - `added_at` (für statische Segmente)
  - `added_by` (für manuelle Hinzufügung)
  - `removed_at` (für manuelle Entfernung)
  - `removed_by`

- [ ] `SegmentPerformance` Entity:
  - `id`, `segment_id` (FK)
  - `date` (für tägliche/wöchentliche/monatliche Aggregation)
  - `member_count`
  - `active_members`
  - `campaign_count`
  - `conversion_rate`
  - `revenue` (optional)

### 3. API Endpoints
- [ ] `POST /segments` - Segment erstellen
- [ ] `GET /segments` - Liste mit Filtern
- [ ] `GET /segments/{id}` - Detail
- [ ] `PUT /segments/{id}` - Update
- [ ] `DELETE /segments/{id}` - Löschen
- [ ] `POST /segments/{id}/rules` - Regel hinzufügen
- [ ] `PUT /segments/{id}/rules/{rule_id}` - Regel aktualisieren
- [ ] `DELETE /segments/{id}/rules/{rule_id}` - Regel löschen
- [ ] `POST /segments/{id}/members` - Mitglied manuell hinzufügen (statisch)
- [ ] `DELETE /segments/{id}/members/{member_id}` - Mitglied entfernen
- [ ] `POST /segments/{id}/calculate` - Segment neu berechnen (dynamisch)
- [ ] `GET /segments/{id}/members` - Mitglieder-Liste
- [ ] `GET /segments/{id}/performance` - Performance-Daten
- [ ] `GET /segments/{id}/export` - Segment exportieren

### 4. Business Logic
- [ ] **Segment-Berechnung (dynamisch)**:
  - Regel-Engine: Evaluierung von Segment-Regeln
  - Query-Builder: Dynamische SQL-Queries basierend auf Regeln
  - Performance-Optimierung: Caching, Batch-Processing
  - Incremental Updates: Nur geänderte Kontakte neu evaluieren
  
- [ ] **Segment-Performance**:
  - Aggregation von Mitglieder-Zahlen
  - Kampagnen-Performance pro Segment
  - Conversion-Rate Tracking
  - Revenue-Attribution (optional)

- [ ] **Segment-Export**:
  - CSV-Export
  - JSON-Export
  - API-Integration für externe Systeme

### 5. Events
- [ ] `crm.segment.created`
- [ ] `crm.segment.updated`
- [ ] `crm.segment.member_added`
- [ ] `crm.segment.member_removed`
- [ ] `crm.segment.calculated`

## Frontend Tasks

### 1. Segmente Liste
- [ ] `packages/frontend-web/src/pages/crm/segments.tsx`
  - ListReport mit Filtern
  - Spalten: Name, Type, Status, Member Count, Last Updated, Performance
  - Bulk-Actions: Calculate, Export, Archive
  - Export-Funktion

### 2. Segment Detail
- [ ] `packages/frontend-web/src/pages/crm/segment-detail.tsx`
  - ObjectPage mit Tabs:
    - Grundinformationen
    - Regeln (für dynamische Segmente)
    - Mitglieder (Liste + manuelle Hinzufügung für statische)
    - Performance (Charts & Metriken)
  - Aktionen: Save, Calculate, Export, Archive

### 3. Segment Rule Builder
- [ ] `packages/frontend-web/src/components/crm/segment-rule-builder.tsx`
  - Visual Rule Builder
  - Drag & Drop für Regeln
  - Field-Selector
  - Operator-Selector
  - Value-Input
  - Logical Operators (AND/OR)
  - Preview: Anzahl der betroffenen Kontakte

### 4. Segment Performance Dashboard
- [ ] `packages/frontend-web/src/pages/crm/segment-performance.tsx`
  - Charts: Member Count Over Time
  - Charts: Conversion Rate
  - Charts: Campaign Performance
  - Metriken: Total Members, Active Members, Growth Rate

### 5. Integration in Campaigns
- [ ] Segment-Auswahl in Campaign-Erstellung
- [ ] Segment-Filter in Campaign-Liste

## Integration Tasks

### 1. Segment-Berechnung aus CRM-Core
- [ ] Contact-Felder abfragen
- [ ] Customer-Felder abfragen
- [ ] Activity-Daten abfragen
- [ ] Purchase-History abfragen

### 2. Segment-Performance aus Campaigns
- [ ] Campaign-Erfolg pro Segment
- [ ] Conversion-Rate pro Segment
- [ ] Revenue-Attribution

### 3. Segment-Export für Marketing-Tools
- [ ] CSV-Format für Email-Marketing
- [ ] JSON-Format für API-Integration
- [ ] Custom-Format für spezifische Tools

## Tests

### 1. Unit Tests
- [ ] Segment-Model Tests
- [ ] Rule-Engine Tests
- [ ] Query-Builder Tests

### 2. Integration Tests
- [ ] API-Endpoint Tests
- [ ] Segment-Berechnung Tests
- [ ] Performance-Aggregation Tests

### 3. E2E Tests
- [ ] `tests/e2e/crm-marketing/segments.spec.ts`
  - Segment erstellen (dynamisch)
  - Segment erstellen (statisch)
  - Regeln hinzufügen/bearbeiten
  - Segment berechnen
  - Mitglieder verwalten
  - Performance anzeigen
  - Segment exportieren

## Definition of Done

- ✅ Dynamische Segmente funktional (regelbasiert)
- ✅ Statische Segmente funktional (manuell)
- ✅ Segment-Berechnung performant (< 30 Sekunden für 10.000 Kontakte)
- ✅ Segment-Performance-Tracking funktional
- ✅ Visual Rule Builder funktional
- ✅ Segment-Export funktional
- ✅ Integration in Campaigns
- ✅ Alle Tests grün

## Nächste Schritte

1. Backend-Service erstellen
2. Database-Models implementieren
3. Rule-Engine implementieren
4. API-Endpoints implementieren
5. Frontend-Seiten erstellen
6. Rule Builder implementieren
7. Performance-Dashboard implementieren
8. Integration in Campaigns
9. Tests schreiben

---

**Referenzen:**
- Segmentierung in Marketing-Automation
- Regel-Engine Patterns
- Performance-Optimierung für große Datenmengen

