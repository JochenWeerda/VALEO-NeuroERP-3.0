# 🔗 BFF ↔ Domain API Matrix

## Übersicht

Diese Matrix definiert klar, welche BFFs (web/mobile/back-office) welche Domains konsumieren, inkl. Priorität (P1–P3), Kern-Use-Cases und exemplarische API-Endpunkte.

## BFF-Architektur

### 1. Web BFF (`bff-web`)
**Zielgruppe**: Management & Operative Cockpits (Desktop/Web-User)
**Technologie**: React + TypeScript, Fastify BFF
**Auth-Level**: Vollständige RBAC/ABAC

### 2. Mobile BFF (`bff-mobile`)
**Zielgruppe**: Fahrer & Außendienst (Offline-Capable)
**Technologie**: React Native + TypeScript, Fastify BFF
**Auth-Level**: Rollenbasiert, Offline-Sync

### 3. Back-Office BFF (`bff-back-office`)
**Zielgruppe**: Compliance, Governance, Serienläufe (Administratoren)
**Technologie**: React + TypeScript, Fastify BFF
**Auth-Level**: Strenge RBAC, Audit-Trails

---

## 📊 Domain-API Mapping Matrix

### Legende
- **P1** = sofort nötig (MVP) · **P2** = wichtig (Folge-Release) · **P3** = nice-to-have
- **R/W** = Read/Write Scope · **R** = Read-Only · **W** = Write-Only

---

## 1. bff-web (Management & Operative Cockpits)

| Domain | Priorität | Scope (R/W) | Kern-Use-Cases | Beispiel-Endpunkte |
|--------|-----------|-------------|----------------|-------------------|
| **analytics** | P1 | R | Dashboards, KPIs, Forecasts | `GET /analytics/api/v1/kpis`, `GET /cubes/contract-positions` |
| **contracts** | P1 | R/W | Contract 360, Fixings, Call-offs | `GET /contracts/:id`, `POST /contracts/:id/fixing` |
| **pricing** | P1 | R | Quote-Simulation, Preislisten-Ansicht | `POST /pricing/api/v1/quotes/calc`, `GET /pricelists?status=Active` |
| **inventory** | P1 | R | Lagerstände, Bewegungen, Los-Detail | `GET /inventory/api/v1/lots/:id`, `GET /movements?from&to` |
| **weighing** | P1 | R | Ticket-Übersicht, Toleranzen, Slot-Auslastung | `GET /weighing/api/v1/tickets?from&to`, `GET /tolerances` |
| **sales** | P1 | R | Auftrags-/Rechnungslisten, Status | `GET /sales/api/v1/orders?from&to`, `GET /invoices?status=` |
| **document** | P1 | R | PDF-Download, Vorschau | `GET /document/api/v1/documents/:id/file?role=render` |
| **quality** | P2 | R/W | Prüfpläne, NC/CAPA-Boards | `GET /quality/api/v1/ncs?status=Open`, `POST /capas` |
| **regulatory** | P2 | R | Label-Status, Evidenzen | `POST /regulatory/api/v1/labels/evaluate`, `GET /evidence?ref=` |
| **finance** | P2 | R | AR/AP-Status, Overdues | `GET /finance/api/v1/ar/invoices?overdue=1` |
| **notifications** | P2 | R/W | Versand von Sammeldokumenten | `POST /notifications/api/v1/messages/send` |
| **crm** | P3 | R | Kundenakte, Kommunikationsverlauf | `GET /crm/api/v1/customers/:id` |
| **scheduler** | P3 | R/W | Ad-hoc Trigger, Backfills | `POST /scheduler/api/v1/schedules/:id/trigger` |
| **audit** | P3 | R | Audit-Logs, Exporte | `GET /audit/api/v1/events?from&to` |

---

## 2. bff-mobile (Fahrer & Außendienst)

| Domain | Priorität | Scope (R/W) | Kern-Use-Cases | Beispiel-Endpunkte |
|--------|-----------|-------------|----------------|-------------------|
| **weighing** | P1 | R/W | Wiegevorgang, Ticket-Abschluss, Offline-Modus | `POST /weighing/api/v1/sessions`, `POST /sessions/:id/complete` |
| **logistics** | P1 | R | Routen/Stops, Slot-Zeiten | `GET /logistics/api/v1/shipments?driverId=` |
| **sales** | P1 | R | Kundenaufträge einsehen | `GET /sales/api/v1/orders?customerId=` |
| **crm** | P1 | R/W | Besuchsnotizen, Kontakte, Termine | `GET /crm/api/v1/customers/:id`, `POST /crm/api/v1/notes` |
| **notifications** | P1 | W | WhatsApp/Push an Kunden | `POST /notifications/api/v1/messages/send` |
| **contracts** | P2 | R | Kundenkontrakte & offene Mengen | `GET /contracts/api/v1/contracts?customerId=&openOnly=1` |
| **document** | P2 | R | Lieferschein/Wiegeschein anzeigen | `GET /document/api/v1/documents/:id/file?role=render` |
| **quality** | P2 | W | Proben erfassen (Fotos), NC-Meldung | `POST /quality/api/v1/samples`, `POST /ncs` |
| **scheduler** | P3 | R/W | Tour-Reminder, persönliche Tasks | `POST /scheduler/api/v1/schedules` |
| **audit** | P3 | R | Eigene Aktionshistorie | `GET /audit/api/v1/events?actor.userId=` |

---

## 3. bff-back-office (Compliance, Governance, Serienläufe)

| Domain | Priorität | Scope (R/W) | Kern-Use-Cases | Beispiel-Endpunkte |
|--------|-----------|-------------|----------------|-------------------|
| **document** | P1 | R/W | Serienläufe, Archiv, Retention/Legal Hold | `POST /document/api/v1/documents`, `POST /documents/:id/legal-hold` |
| **audit** | P1 | R | Prüfer-Exports, Integritätscheck | `GET /audit/api/v1/integrity/check`, `POST /exports` |
| **scheduler** | P1 | R/W | Jobs verwalten, Backfills, Workflows | `POST /scheduler/api/v1/schedules`, `POST /runs/:id/retry` |
| **regulatory** | P1 | R/W | Policy- & Labelpflege, Evidenzen | `POST /regulatory/api/v1/policies`, `POST /evidence` |
| **finance** | P1 | R | Periodenabschluss, Overdues | `GET /finance/api/v1/ar/invoices?overdue=1` |
| **analytics** | P1 | R | Monatsreports, KPI-Exports | `POST /analytics/api/v1/reports`, `GET /kpis?from&to` |
| **pricing** | P2 | R/W | Preislistenpflege, Simulationen | `PATCH /pricing/api/v1/pricelists/:id`, `POST /quotes/calc` |
| **quality** | P2 | R/W | CAPA-Boards, Laborimport | `POST /quality/api/v1/samples/:id/results`, `PATCH /capas/:id` |
| **contracts** | P2 | R/W | Amendments, Fulfilment-Korrektur (governed) | `PATCH /contracts/api/v1/contracts/:id` |
| **weighing** | P2 | R | Prüf-/Toleranz-Reporting, Geräteverwaltung | `GET /weighing/api/v1/devices`, `GET /tolerance-violations` |
| **fleet** | P2 | R/W | UVV/TÜV-Planung, Tankkartenimport | `POST /fleet/api/v1/inspections`, `POST /fuel-logs` |
| **notifications** | P2 | R/W | Massenversand, Kampagnen | `POST /notifications/api/v1/messages/send` |

---

## 4. Inventory Domain

| BFF Type | SKU API | Location API | Lot API | Movement API | Notes |
|----------|---------|--------------|---------|--------------|-------|
| **Web BFF** | ✅ Full CRUD<br/>- Product Management<br/>- Stock Levels<br/>- Reorder Points<br/>- ABC Analysis | ✅ Full CRUD<br/>- Warehouse Layout<br/>- Zone Management<br/>- Capacity Planning | ✅ Full CRUD<br/>- Lot Tracking<br/>- Expiration Dates<br/>- Quality Control | ✅ Full CRUD<br/>- Stock Movements<br/>- Picking/Putaway<br/>- Cycle Counting | Vollständiges WMS |
| **Mobile BFF** | 🔄 Read-Only<br/>- Product Lookup<br/>- Stock Check<br/>- Barcode Scan | 🔄 Read + Update<br/>- Location Updates<br/>- Stock Counts | 🔄 Read + Update<br/>- Lot Information<br/>- Quality Checks | ✅ Create + Update<br/>- Movement Logging<br/>- Picking Confirmation<br/>- Putaway Recording | Warehouse Mobile Operations |
| **Back-Office BFF** | 🔄 Read-Only<br/>- Inventory Reports<br/>- Audit Trails<br/>- Compliance Logs | 🔄 Read-Only<br/>- Layout Audit<br/>- Safety Compliance | 🔄 Read-Only<br/>- Lot History<br/>- Recall Management | 🔄 Read-Only<br/>- Movement Audit<br/>- Performance Metrics | Compliance & Audit |

**API Endpoints (Web BFF):**
```
GET    /inventory/api/v1/skus
POST   /inventory/api/v1/skus
GET    /inventory/api/v1/skus/:id
PATCH  /inventory/api/v1/skus/:id
GET    /inventory/api/v1/locations
POST   /inventory/api/v1/locations
GET    /inventory/api/v1/lots
POST   /inventory/api/v1/lots
POST   /inventory/api/v1/movements
GET    /inventory/api/v1/movements
```

---

## 5. Finance Domain

| BFF Type | Ledger API | Invoice API | Tax API | Audit API | Notes |
|----------|------------|-------------|---------|-----------|-------|
| **Web BFF** | ✅ Read + Journal<br/>- Account Balances<br/>- Journal Entries<br/>- Financial Reports<br/>- Budget Tracking | ✅ Full CRUD<br/>- AR/AP Management<br/>- Payment Processing<br/>- Dunning Procedures | 🔄 Read-Only<br/>- Tax Calculations<br/>- Compliance Reports | 🔄 Read-Only<br/>- Audit Trails<br/>- Financial Controls | Financial Operations |
| **Mobile BFF** | ❌ No Access | ❌ No Access | ❌ No Access | ❌ No Access | Nicht relevant für Mobile |
| **Back-Office BFF** | ✅ Full Access<br/>- Complete Ledger<br/>- System Controls<br/>- Financial Audit<br/>- Regulatory Reporting | ✅ Full Access<br/>- All Invoices<br/>- Payment Audit<br/>- Tax Compliance | ✅ Full Access<br/>- Tax Configuration<br/>- Compliance Monitoring<br/>- Regulatory Filing | ✅ Full Access<br/>- System Audit<br/>- Security Logs<br/>- Compliance Reports | Administrative Financial Control |

**API Endpoints (Web BFF):**
```
GET    /finance/api/v1/accounts
GET    /finance/api/v1/accounts/:id/balance
POST   /finance/api/v1/journal-entries
GET    /finance/api/v1/invoices
POST   /finance/api/v1/invoices
GET    /finance/api/v1/invoices/:id
PATCH  /finance/api/v1/invoices/:id
```

---

## 6. Analytics Domain

| BFF Type | Report API | Dashboard API | KPI API | Alert API | Notes |
|----------|------------|----------------|---------|-----------|-------|
| **Web BFF** | ✅ Full Access<br/>- Custom Reports<br/>- Scheduled Reports<br/>- Export Functions<br/>- Data Visualization | ✅ Full Access<br/>- Dashboard Builder<br/>- Widget Management<br/>- Real-time Updates | ✅ Full Access<br/>- KPI Configuration<br/>- Alert Rules<br/>- Performance Tracking | ✅ Full Access<br/>- Alert Management<br/>- Notification Rules<br/>- Escalation Paths | Business Intelligence |
| **Mobile BFF** | 🔄 Read-Only<br/>- Key Metrics<br/>- Status Dashboards<br/>- Basic Reports | 🔄 Read-Only<br/>- Mobile Dashboards<br/>- KPI Overview | ⚡ Push Alerts<br/>- Critical Alerts<br/>- Status Updates | ⚡ Push Notifications<br/>- Real-time Alerts | Mobile BI Overview |
| **Back-Office BFF** | ✅ Full Access<br/>- System Analytics<br/>- Performance Monitoring<br/>- Audit Reports<br/>- Compliance Metrics | ✅ Full Access<br/>- Executive Dashboards<br/>- System Health<br/>- SLA Monitoring | ✅ Full Access<br/>- All KPIs<br/>- Custom Metrics<br/>- Alert Configuration | ✅ Full Access<br/>- System Alerts<br/>- Security Monitoring<br/>- Compliance Alerts | System Governance |

**API Endpoints (Web BFF):**
```
GET    /analytics/api/v1/dashboards
POST   /analytics/api/v1/dashboards
GET    /analytics/api/v1/reports
POST   /analytics/api/v1/reports
GET    /analytics/api/v1/kpis
POST   /analytics/api/v1/alerts
GET    /analytics/api/v1/alerts
```

---

## 7. Integration Domain

| BFF Type | Webhook API | Sync Job API | EDI API | Queue API | Notes |
|----------|-------------|--------------|---------|-----------|-------|
| **Web BFF** | 🔄 Configuration<br/>- Webhook Setup<br/>- Event Subscriptions<br/>- Retry Configuration | 🔄 Monitoring<br/>- Sync Status<br/>- Error Handling<br/>- Performance Metrics | 🔄 Configuration<br/>- Partner Setup<br/>- Message Mapping<br/>- Error Handling | 🔄 Monitoring<br/>- Queue Status<br/>- Message Flow<br/>- Error Recovery | Integration Management |
| **Mobile BFF** | ❌ No Access | ❌ No Access | ❌ No Access | ⚡ Status Updates<br/>- Sync Status<br/>- Offline Queue | Offline-Sync Status |
| **Back-Office BFF** | ✅ Full Access<br/>- Complete Configuration<br/>- Security Settings<br/>- Audit Logs<br/>- Performance Tuning | ✅ Full Access<br/>- System Integration<br/>- Error Resolution<br/>- Performance Optimization | ✅ Full Access<br/>- EDI Configuration<br/>- Partner Management<br/>- Compliance Monitoring | ✅ Full Access<br/>- Queue Management<br/>- Message Monitoring<br/>- System Health | System Integration Control |

---

## 8. Document Domain

| BFF Type | Document API | Template API | Archive API | OCR API | Notes |
|----------|--------------|--------------|-------------|---------|-------|
| **Web BFF** | ✅ Full CRUD<br/>- Document Upload<br/>- Version Control<br/>- Sharing<br/>- Search | 🔄 Read + Use<br/>- Template Selection<br/>- Document Generation<br/>- PDF Creation | 🔄 Read-Only<br/>- Document Archive<br/>- Retention Policies | ⚡ Processing<br/>- OCR Results<br/>- Data Extraction | Document Management |
| **Mobile BFF** | ✅ Upload + Read<br/>- Photo Capture<br/>- Document Upload<br/>- Signature Capture<br/>- Offline Queue | 🔄 Read-Only<br/>- Template Access<br/>- Form Generation | ❌ No Access | ⚡ Mobile OCR<br/>- Text Recognition<br/>- Form Processing | Mobile Document Handling |
| **Back-Office BFF** | ✅ Full Access<br/>- Archive Management<br/>- Retention Policies<br/>- GDPR Compliance<br/>- Audit Trails | ✅ Full Access<br/>- Template Management<br/>- Version Control<br/>- Access Control | ✅ Full Access<br/>- Archive Administration<br/>- Data Lifecycle<br/>- Compliance Reports | ✅ Full Access<br/>- OCR Configuration<br/>- Quality Monitoring<br/>- Performance Tuning | Document Governance |

---

## 9. Scheduler Domain

| BFF Type | Schedule API | Execution API | Calendar API | Notes |
|----------|--------------|---------------|--------------|-------|
| **Web BFF** | ✅ Full CRUD<br/>- Schedule Management<br/>- Trigger Configuration<br/>- Target Setup<br/>- Monitoring | 🔄 Read-Only<br/>- Execution History<br/>- Performance Metrics<br/>- Error Logs | 🔄 Configuration<br/>- Holiday Calendar<br/>- Business Hours<br/>- Timezone Settings | Job Scheduling Management |
| **Mobile BFF** | ❌ No Access | ❌ No Access | ❌ No Access | Nicht relevant für Mobile |
| **Back-Office BFF** | ✅ Full Access<br/>- System Scheduling<br/>- Maintenance Jobs<br/>- Backup Scheduling<br/>- Performance Tuning | ✅ Full Access<br/>- Execution Monitoring<br/>- Error Resolution<br/>- Performance Analysis | ✅ Full Access<br/>- System Calendar<br/>- Holiday Management<br/>- Global Settings | System Administration |

---

## 🔄 Cross-Cutting (alle BFFs)

### Authentifizierung & Autorisierung
- **OIDC/JWT**: Gemeinsame Authentifizierung mit allen Domains
- **Rollen → RBAC/ABAC**: Pro Route enforced
- **Tenant-Isolation**: X-Tenant-ID Header in allen Requests

### Internationalisierung
- **Primär**: de-DE (Deutsch)
- **Optional**: en-GB (English), nl-NL (Niederländisch)

### Error UX
- **Domain-Fehler → Userfreundlich**: Automatische Übersetzung
- **Retry-Hinweise**: Bei temporären Fehlern
- **Fallback UI**: Graceful Degradation

### Caching
- **Stale-While-Revalidate**: Für read-lastige Dashboards
- **CDN**: Static Assets, Dokumente
- **Browser Cache**: Aggressive für UI Assets

### Telemetrie
- **Trace-Ids**: Durch alle BFFs durchgereicht
- **Correlation-Header**: Request-Verfolgung
- **OpenTelemetry**: Traces über alle Services

---

## 🎯 MVP-Reihenfolge (empfohlen)

### Phase 1 (P1 - Sofort nötig)
- **bff-web**: Analytics + Contracts + Inventory + Weighing
- **bff-mobile**: Weighing + Logistics + Notifications
- **bff-back-office**: Document + Audit + Scheduler

### Phase 2 (P2 - Wichtig)
- **Pricing, Quality, Regulatory, Sales-Vertiefung**
- **Real-time Features**: WebSockets, Event Streaming
- **Offline Support**: Service Workers, Sync Queues

### Phase 3 (P3 - Nice-to-have)
- **CRM-Vertiefung, Fleet, Advanced Finance**
- **KI-Assistenz**: Smart Wizards, Predictive Analytics
- **Advanced Monitoring**: Performance Tuning, Security Hardening

---

## 🧩 UI-Komponenten (Starter-Set)

### Layout
- **AppShell**: Sidebar, Header, Breadcrumbs
- **Responsive Grid**: Mobile-First Design
- **Navigation**: Breadcrumbs, Tabs, Accordions

### Daten-Anzeige
- **Tabellen**: Virtuelle Listen, Column Filters, CSV-Export
- **Charts**: Recharts (KPI Cards, Line/Bar/Pie)
- **Data Grid**: Sortierung, Filter, Pagination

### Formulare
- **react-hook-form + ZodResolver**: Type-Safe Validation
- **Async Selects**: API-backed Dropdowns
- **File Upload**: Drag & Drop, Progress Indicators

### Feedback
- **Notifications**: Toaster + Realtime Banner (WebSocket/NATS)
- **Loading States**: Skeletons, Spinners, Progress Bars
- **Error Boundaries**: Graceful Error Handling

### Dokumente
- **PDF Viewer**: Document-Domain Integration
- **Image Viewer**: Lightbox, Zoom, Rotate
- **Signature Pad**: Digital Signatures

---

## 📋 Implementierungs-Checkliste

### BFF-Web (Management Cockpits)
- [ ] Dashboard mit KPI-Übersicht
- [ ] Contract 360° View
- [ ] Inventory Management Interface
- [ ] Weighing Operations Overview
- [ ] Analytics & Reporting Portal

### BFF-Mobile (Fahrer Apps)
- [ ] Weighing Ticket App
- [ ] Route Management
- [ ] Customer Visit Logging
- [ ] Offline Document Access
- [ ] Real-time Notifications

### BFF-Back-Office (Governance)
- [ ] Document Archive Management
- [ ] Audit Trail Viewer
- [ ] System Job Scheduler
- [ ] Compliance Dashboard
- [ ] Regulatory Reporting

Diese Matrix ist der **maßgebliche Leitfaden** für die Frontend-Entwicklung und wird kontinuierlich aktualisiert basierend auf neuen Anforderungen und Domain-Erweiterungen.