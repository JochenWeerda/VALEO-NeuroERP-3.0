***REMOVED*** Phase 1.5 - Kampagnenmanagement

**Status:** 🚀 In Progress  
**Priorität:** 🟡 Mittel  
**Capability:** MKT-CAM-01  
**Prioritäts-Score:** 15.0  
**Lösungstyp:** C (New Module)  
**Owner:** Marketing-Team  
**Aufwand:** 3-4 Wochen

***REMOVED******REMOVED*** Mission Overview

Implementierung eines vollständigen Kampagnenmanagement-Systems mit:
- Email-Kampagnen mit Templates
- Campaign-Tracking (Opens, Clicks, Conversions)
- Segment-basierte Kampagnen-Zuweisung
- A/B-Testing
- Marketing-ROI Measurement
- Campaign-Performance-Dashboard

***REMOVED******REMOVED*** Backend Tasks

***REMOVED******REMOVED******REMOVED*** 1. Service erweitern: `services/crm-marketing/`
- [ ] Campaign-Models (SQLAlchemy)
- [ ] Campaign-Template-Models
- [ ] Campaign-Recipient-Models
- [ ] Campaign-Event-Models (Tracking)
- [ ] Pydantic-Schemas
- [ ] Alembic-Migrationen

***REMOVED******REMOVED******REMOVED*** 2. Database Models
- [ ] `Campaign` Entity:
  - `id`, `tenant_id`
  - `name`, `description`
  - `type` (email, sms, push, other)
  - `status` (draft, scheduled, running, paused, completed, cancelled)
  - `segment_id` (FK zu Segment)
  - `template_id` (FK zu CampaignTemplate)
  - `scheduled_at`, `started_at`, `completed_at`
  - `sender_name`, `sender_email`
  - `subject` (für Email)
  - `settings` (JSON - A/B-Test, etc.)
  - `created_at`, `updated_at`

- [ ] `CampaignTemplate` Entity:
  - `id`, `tenant_id`
  - `name`, `description`
  - `type` (email, sms, push)
  - `subject_template` (für Email)
  - `body_template` (HTML/Text)
  - `variables` (JSON - verfügbare Variablen)
  - `is_active`
  - `created_at`, `updated_at`

- [ ] `CampaignRecipient` Entity:
  - `id`, `campaign_id` (FK)
  - `contact_id` (FK)
  - `email` (cached)
  - `status` (pending, sent, delivered, bounced, failed)
  - `sent_at`, `delivered_at`
  - `bounce_reason`
  - `variant` (für A/B-Test)

- [ ] `CampaignEvent` Entity:
  - `id`, `campaign_id` (FK)
  - `recipient_id` (FK)
  - `event_type` (sent, delivered, opened, clicked, converted, bounced, unsubscribed)
  - `timestamp`
  - `details` (JSON - z.B. clicked_link, user_agent)
  - `ip_address`

- [ ] `CampaignABTest` Entity:
  - `id`, `campaign_id` (FK)
  - `variant_name` (A, B, C, etc.)
  - `subject` (für Email-Varianten)
  - `body_template` (für Email-Varianten)
  - `recipient_count`
  - `open_rate`, `click_rate`, `conversion_rate`

***REMOVED******REMOVED******REMOVED*** 3. API Endpoints
- [ ] `POST /campaigns` - Campaign erstellen
- [ ] `GET /campaigns` - Liste mit Filtern
- [ ] `GET /campaigns/{id}` - Detail
- [ ] `PUT /campaigns/{id}` - Update
- [ ] `DELETE /campaigns/{id}` - Löschen
- [ ] `POST /campaigns/{id}/schedule` - Campaign planen
- [ ] `POST /campaigns/{id}/start` - Campaign starten
- [ ] `POST /campaigns/{id}/pause` - Campaign pausieren
- [ ] `POST /campaigns/{id}/resume` - Campaign fortsetzen
- [ ] `POST /campaigns/{id}/cancel` - Campaign abbrechen
- [ ] `GET /campaigns/{id}/recipients` - Empfänger-Liste
- [ ] `GET /campaigns/{id}/events` - Event-Liste
- [ ] `GET /campaigns/{id}/performance` - Performance-Daten
- [ ] `POST /campaigns/{id}/test-send` - Test-Versand
- [ ] `GET /campaigns/templates` - Template-Liste
- [ ] `POST /campaigns/templates` - Template erstellen
- [ ] `GET /campaigns/templates/{id}` - Template-Detail
- [ ] `PUT /campaigns/templates/{id}` - Template aktualisieren
- [ ] `DELETE /campaigns/templates/{id}` - Template löschen

***REMOVED******REMOVED******REMOVED*** 4. Business Logic
- [ ] **Campaign-Scheduler**:
  - Scheduled Campaigns automatisch starten
  - Background-Job für Versand
  - Rate-Limiting (z.B. 1000 Emails/Stunde)
  
- [ ] **Email-Sender**:
  - Integration mit Email-Service (SMTP/SendGrid/etc.)
  - Template-Rendering (Variablen ersetzen)
  - Personalisierung pro Empfänger
  
- [ ] **Event-Tracking**:
  - Open-Tracking (Tracking-Pixel)
  - Click-Tracking (Link-Wrapping)
  - Conversion-Tracking
  - Bounce-Handling
  
- [ ] **A/B-Testing**:
  - Varianten-Generierung
  - Zufällige Verteilung
  - Performance-Vergleich
  - Winner-Auswahl

- [ ] **Performance-Aggregation**:
  - Open-Rate, Click-Rate, Conversion-Rate
  - Revenue-Attribution
  - ROI-Berechnung

***REMOVED******REMOVED******REMOVED*** 5. Events
- [ ] `crm.campaign.created`
- [ ] `crm.campaign.started`
- [ ] `crm.campaign.completed`
- [ ] `crm.campaign.email.sent`
- [ ] `crm.campaign.email.opened`
- [ ] `crm.campaign.email.clicked`
- [ ] `crm.campaign.converted`

***REMOVED******REMOVED*** Frontend Tasks

***REMOVED******REMOVED******REMOVED*** 1. Campaigns Liste
- [ ] `packages/frontend-web/src/pages/crm/campaigns.tsx`
  - ListReport mit Filtern
  - Spalten: Name, Type, Status, Segment, Recipients, Open Rate, Click Rate, Created
  - Bulk-Actions: Start, Pause, Cancel, Delete
  - Export-Funktion

***REMOVED******REMOVED******REMOVED*** 2. Campaign Detail
- [ ] `packages/frontend-web/src/pages/crm/campaign-detail.tsx`
  - ObjectPage mit Tabs:
    - Grundinformationen
    - Template & Content
    - Segment & Recipients
    - A/B-Test (optional)
    - Performance (Charts & Metriken)
  - Aktionen: Save, Schedule, Start, Pause, Resume, Cancel, Test Send

***REMOVED******REMOVED******REMOVED*** 3. Campaign Template Editor
- [ ] `packages/frontend-web/src/pages/crm/campaign-template-editor.tsx`
  - WYSIWYG-Editor für Email-Templates
  - Variable-Insertion
  - Preview-Funktion
  - Template-Vorlagen

***REMOVED******REMOVED******REMOVED*** 4. Campaign Performance Dashboard
- [ ] `packages/frontend-web/src/pages/crm/campaign-performance.tsx`
  - Charts: Open Rate Over Time
  - Charts: Click Rate Over Time
  - Charts: Conversion Rate
  - Charts: Revenue Attribution
  - Metriken: Total Sent, Delivered, Opened, Clicked, Converted, Revenue, ROI

***REMOVED******REMOVED******REMOVED*** 5. Campaign Builder (Wizard)
- [ ] `packages/frontend-web/src/pages/crm/campaign-builder.tsx`
  - Multi-Step Wizard:
    1. Campaign-Typ & Name
    2. Segment-Auswahl
    3. Template-Auswahl/Erstellung
    4. A/B-Test-Konfiguration (optional)
    5. Schedule
    6. Review & Start

***REMOVED******REMOVED*** Integration Tasks

***REMOVED******REMOVED******REMOVED*** 1. Email-Service Integration
- [ ] SMTP-Konfiguration
- [ ] SendGrid/Mailgun/etc. Integration
- [ ] Template-Rendering
- [ ] Personalisierung

***REMOVED******REMOVED******REMOVED*** 2. Segment-Integration
- [ ] Segment-Auswahl in Campaign-Erstellung
- [ ] Segment-Member → Campaign-Recipients
- [ ] Segment-Performance → Campaign-Performance

***REMOVED******REMOVED******REMOVED*** 3. Tracking-Integration
- [ ] Tracking-Pixel für Opens
- [ ] Link-Wrapping für Clicks
- [ ] Conversion-Tracking
- [ ] Event-Publishing

***REMOVED******REMOVED*** Tests

***REMOVED******REMOVED******REMOVED*** 1. Unit Tests
- [ ] Campaign-Model Tests
- [ ] Template-Rendering Tests
- [ ] Event-Tracking Tests
- [ ] A/B-Test-Logic Tests

***REMOVED******REMOVED******REMOVED*** 2. Integration Tests
- [ ] API-Endpoint Tests
- [ ] Email-Sender Tests
- [ ] Event-Tracking Tests
- [ ] Performance-Aggregation Tests

***REMOVED******REMOVED******REMOVED*** 3. E2E Tests
- [ ] `tests/e2e/crm-marketing/campaigns.spec.ts`
  - Campaign erstellen
  - Template erstellen
  - Campaign planen
  - Campaign starten
  - Performance anzeigen
  - A/B-Test konfigurieren

***REMOVED******REMOVED*** Definition of Done

- ✅ Email-Kampagnen können erstellt werden
- ✅ Templates können verwaltet werden
- ✅ Campaigns können geplant und gestartet werden
- ✅ Open/Click-Tracking funktional
- ✅ A/B-Testing funktional
- ✅ Performance-Dashboard funktional
- ✅ ROI-Berechnung funktional
- ✅ Alle Tests grün

***REMOVED******REMOVED*** Nächste Schritte

1. Campaign-Models implementieren
2. Campaign-API-Endpoints implementieren
3. Email-Sender implementieren
4. Event-Tracking implementieren
5. Frontend-Seiten erstellen
6. Campaign Builder implementieren
7. Performance-Dashboard implementieren
8. Tests schreiben

---

**Referenzen:**
- Email-Marketing Best Practices
- A/B-Testing Methoden
- Campaign-Performance-Metriken

