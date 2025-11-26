# Phase 1.5 - Kampagnenmanagement

**Status:** 🚀 In Progress  
**Priorität:** 🟡 Mittel  
**Capability:** MKT-CAM-01  
**Prioritäts-Score:** 15.0  
**Lösungstyp:** C (New Module)  
**Owner:** Marketing-Team  
**Aufwand:** 3-4 Wochen

## Mission Overview

Implementierung eines vollständigen Kampagnenmanagement-Systems mit:
- Email-Kampagnen mit Templates
- Campaign-Tracking (Opens, Clicks, Conversions)
- Segment-basierte Kampagnen
- A/B-Testing
- Marketing-ROI Measurement
- Campaign-Performance-Dashboard

## Backend Tasks

### 1. Service erweitern: `services/crm-marketing/`
- [ ] Campaign-Models (SQLAlchemy)
- [ ] Campaign-Templates
- [ ] Campaign-Tracking
- [ ] A/B-Testing
- [ ] Pydantic-Schemas
- [ ] Alembic-Migrationen

### 2. Database Models
- [ ] `Campaign` Entity:
  - `id`, `tenant_id`
  - `name`, `description`
  - `type` (email, sms, push, social)
  - `status` (draft, scheduled, running, paused, completed, cancelled)
  - `segment_id` (FK)
  - `template_id` (FK)
  - `scheduled_at`, `started_at`, `completed_at`
  - `budget`, `spent`
  - `target_count`, `sent_count`, `delivered_count`
  - `open_count`, `click_count`, `conversion_count`
  - `created_at`, `updated_at`

- [ ] `CampaignTemplate` Entity:
  - `id`, `tenant_id`
  - `name`, `description`
  - `type` (email, sms, push)
  - `subject` (für Email)
  - `body_html`, `body_text`
  - `variables` (JSON - für Personalisierung)
  - `is_active`
  - `created_at`, `updated_at`

- [ ] `CampaignVariant` Entity (für A/B-Testing):
  - `id`, `campaign_id` (FK)
  - `name`, `description`
  - `variant_type` (A, B, C, etc.)
  - `template_id` (FK)
  - `target_percentage` (z.B. 50% für A/B)
  - `sent_count`, `open_count`, `click_count`, `conversion_count`
  - `winner` (boolean - für A/B-Test-Ergebnis)

- [ ] `CampaignRecipient` Entity:
  - `id`, `campaign_id` (FK)
  - `contact_id` (FK)
  - `variant_id` (FK, optional - für A/B-Testing)
  - `email`, `phone` (cached)
  - `status` (pending, sent, delivered, bounced, failed)
  - `sent_at`, `delivered_at`
  - `opened_at`, `clicked_at`, `converted_at`
  - `open_count`, `click_count`
  - `bounce_reason`, `failure_reason`

- [ ] `CampaignEvent` Entity (für Tracking):
  - `id`, `campaign_id` (FK)
  - `recipient_id` (FK)
  - `event_type` (sent, delivered, opened, clicked, bounced, converted)
  - `timestamp`
  - `metadata` (JSON - z.B. IP, User-Agent, Link-URL)

- [ ] `CampaignPerformance` Entity:
  - `id`, `campaign_id` (FK)
  - `date`
  - `sent_count`, `delivered_count`
  - `open_count`, `click_count`, `conversion_count`
  - `open_rate`, `click_rate`, `conversion_rate`
  - `revenue`, `roi`

### 3. API Endpoints
- [ ] `POST /campaigns` - Campaign erstellen
- [ ] `GET /campaigns` - Liste mit Filtern
- [ ] `GET /campaigns/{id}` - Detail
- [ ] `PUT /campaigns/{id}` - Update
- [ ] `DELETE /campaigns/{id}` - Löschen
- [ ] `POST /campaigns/{id}/schedule` - Campaign planen
- [ ] `POST /campaigns/{id}/start` - Campaign starten
- [ ] `POST /campaigns/{id}/pause` - Campaign pausieren
- [ ] `POST /campaigns/{id}/cancel` - Campaign abbrechen
- [ ] `GET /campaigns/{id}/recipients` - Empfänger-Liste
- [ ] `GET /campaigns/{id}/performance` - Performance-Daten
- [ ] `GET /campaigns/{id}/events` - Event-Log
- [ ] `POST /campaigns/{id}/test` - Test-Versand
- [ ] `GET /campaigns/{id}/ab-test-results` - A/B-Test-Ergebnisse

- [ ] `POST /campaigns/templates` - Template erstellen
- [ ] `GET /campaigns/templates` - Template-Liste
- [ ] `GET /campaigns/templates/{id}` - Template-Detail
- [ ] `PUT /campaigns/templates/{id}` - Template aktualisieren
- [ ] `DELETE /campaigns/templates/{id}` - Template löschen

- [ ] `POST /campaigns/tracking/open` - Open-Tracking (public)
- [ ] `POST /campaigns/tracking/click` - Click-Tracking (public)

### 4. Business Logic
- [ ] **Campaign-Scheduler**:
  - Scheduled Campaigns automatisch starten
  - Background-Job für Versand
  
- [ ] **Email-Sender**:
  - Integration mit Email-Service
  - Template-Rendering mit Variablen
  - Personalisierung
  
- [ ] **Campaign-Tracking**:
  - Open-Tracking (1x1 Pixel)
  - Click-Tracking (Link-Redirect)
  - Conversion-Tracking
  - Bounce-Handling
  
- [ ] **A/B-Testing**:
  - Variant-Verteilung
  - Winner-Bestimmung
  - Statistische Signifikanz
  
- [ ] **Performance-Aggregation**:
  - Tägliche/wöchentliche/monatliche Aggregation
  - ROI-Berechnung
  - Conversion-Rate-Tracking

### 5. Events
- [ ] `crm.campaign.created`
- [ ] `crm.campaign.started`
- [ ] `crm.campaign.completed`
- [ ] `crm.campaign.recipient.sent`
- [ ] `crm.campaign.recipient.opened`
- [ ] `crm.campaign.recipient.clicked`
- [ ] `crm.campaign.recipient.converted`

## Frontend Tasks

### 1. Campaigns Liste
- [ ] `packages/frontend-web/src/pages/crm/campaigns.tsx`
  - ListReport mit Filtern
  - Spalten: Name, Type, Status, Segment, Sent, Open Rate, Click Rate, Conversion Rate, ROI
  - Bulk-Actions: Start, Pause, Cancel, Export
  - Export-Funktion

### 2. Campaign Detail
- [ ] `packages/frontend-web/src/pages/crm/campaign-detail.tsx`
  - ObjectPage mit Tabs:
    - Grundinformationen
    - Template & Content
    - Segment & Targeting
    - A/B-Testing (optional)
    - Schedule
    - Recipients
    - Performance (Charts & Metriken)
    - Events (Timeline)
  - Aktionen: Save, Schedule, Start, Pause, Cancel, Test Send

### 3. Campaign Template Manager
- [ ] `packages/frontend-web/src/pages/crm/campaign-templates.tsx`
  - Template-Liste
  - Template-Editor (WYSIWYG)
  - Variable-Editor
  - Preview

### 4. Campaign Performance Dashboard
- [ ] `packages/frontend-web/src/pages/crm/campaign-performance.tsx`
  - Charts: Sent/Open/Click/Conversion Over Time
  - Charts: ROI Comparison
  - Charts: Segment Performance
  - Metriken: Total Sent, Open Rate, Click Rate, Conversion Rate, ROI

### 5. Campaign Builder (Wizard)
- [ ] `packages/frontend-web/src/pages/crm/campaign-builder.tsx`
  - Multi-Step Wizard:
    1. Campaign Type & Name
    2. Template Selection/Creation
    3. Segment Selection
    4. A/B-Testing Setup (optional)
    5. Schedule
    6. Review & Confirm

## Integration Tasks

### 1. Email-Service Integration
- [ ] SMTP/Email-Service-Integration
- [ ] Template-Rendering
- [ ] Personalisierung
- [ ] Bounce-Handling

### 2. Segment-Integration
- [ ] Segment-Auswahl in Campaign-Erstellung
- [ ] Segment-Member-Liste für Campaign
- [ ] Segment-Performance-Tracking

### 3. Tracking-Integration
- [ ] Open-Tracking-Pixel
- [ ] Click-Tracking-Links
- [ ] Conversion-Tracking

## Tests

### 1. Unit Tests
- [ ] Campaign-Model Tests
- [ ] Template-Rendering Tests
- [ ] A/B-Testing Logic Tests

### 2. Integration Tests
- [ ] API-Endpoint Tests
- [ ] Email-Sender Tests
- [ ] Tracking Tests

### 3. E2E Tests
- [ ] `tests/e2e/crm-marketing/campaigns.spec.ts`
  - Campaign erstellen
  - Campaign planen
  - Campaign starten
  - Campaign-Tracking
  - A/B-Testing
  - Performance anzeigen

## Definition of Done

- ✅ Email-Kampagnen können erstellt werden
- ✅ Campaign-Templates funktional
- ✅ Segment-basierte Kampagnen funktional
- ✅ Campaign-Tracking funktional (Opens, Clicks)
- ✅ A/B-Testing funktional
- ✅ Campaign-Performance-Dashboard funktional
- ✅ ROI-Berechnung funktional
- ✅ Alle Tests grün

## Nächste Schritte

1. Campaign-Models implementieren
2. Campaign-API-Endpoints implementieren
3. Email-Sender implementieren
4. Campaign-Tracking implementieren
5. Frontend-Seiten erstellen
6. Campaign Builder implementieren
7. Performance-Dashboard implementieren
8. Tests schreiben

---

**Referenzen:**
- Email-Marketing Best Practices
- A/B-Testing Methodologie
- Marketing-ROI Berechnung

