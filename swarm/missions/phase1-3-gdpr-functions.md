# Phase 1.3 - DSGVO-Funktionen

**Status:** 🚀 In Progress  
**Priorität:** 🔴 Hoch  
**Capability:** CRM-CNS-02  
**Prioritäts-Score:** 25.0  
**Lösungstyp:** C (New Module)  
**Owner:** Compliance-Team  
**Aufwand:** 2-3 Wochen

## Mission Overview

Implementierung eines vollständigen DSGVO-Compliance-Systems mit:
- Auskunftsanfragen (Art. 15 DSGVO)
- Datenexport (Art. 20 DSGVO - Recht auf Datenübertragbarkeit)
- Löschung/Anonymisierung (Art. 17 DSGVO - Recht auf Löschung)
- Widerspruchs-Verwaltung (Art. 21 DSGVO - Widerspruchsrecht)
- Vollständige Protokollierung aller Requests

## Backend Tasks

### 1. Service erstellen: `services/crm-gdpr/`
- [ ] Projektstruktur anlegen
- [ ] FastAPI-App mit Router
- [ ] Database-Models (SQLAlchemy)
- [ ] Pydantic-Schemas
- [ ] Alembic-Migrationen

### 2. Database Models
- [ ] `GDPRRequest` Entity:
  - `id`, `tenant_id`
  - `request_type` (access, deletion, portability, objection)
  - `contact_id` (FK zu Contact/Customer)
  - `status` (pending, in_progress, completed, rejected, cancelled)
  - `requested_at`, `completed_at`, `rejected_at`
  - `requested_by` (User ID oder Contact selbst)
  - `verified_at` (Identitätsprüfung)
  - `verification_method` (email, id_card, other)
  - `response_data` (JSON - für Export-Daten)
  - `response_file_path` (Pfad zu Export-Datei)
  - `rejection_reason` (optional)
  - `notes` (interne Notizen)
  - `created_at`, `updated_at`
  - `created_by`, `updated_by`

- [ ] `GDPRRequestHistory` Entity:
  - `id`, `request_id` (FK)
  - `action` (created, status_changed, data_exported, data_deleted, rejected)
  - `old_status`, `new_status`
  - `changed_by`, `changed_at`
  - `notes` (optional)

### 3. API Endpoints
- [ ] `POST /gdpr/requests` - Request erstellen
- [ ] `GET /gdpr/requests` - Liste mit Filtern
- [ ] `GET /gdpr/requests/{id}` - Detail
- [ ] `PUT /gdpr/requests/{id}` - Update (Status ändern)
- [ ] `POST /gdpr/requests/{id}/verify` - Identität verifizieren
- [ ] `POST /gdpr/requests/{id}/export` - Datenexport generieren
- [ ] `POST /gdpr/requests/{id}/delete` - Daten löschen/anonymisieren
- [ ] `POST /gdpr/requests/{id}/reject` - Request ablehnen
- [ ] `GET /gdpr/requests/{id}/history` - Request-Historie
- [ ] `GET /gdpr/requests/{id}/download` - Export-Datei herunterladen
- [ ] `POST /gdpr/check` - Prüfen ob Request für Contact existiert

### 4. Business Logic
- [ ] **Datenexport (Art. 20)**:
  - Sammle alle Daten eines Kontakts aus allen CRM-Modulen
  - Formate: JSON, CSV, PDF
  - Strukturierte, maschinenlesbare Daten
  - Verschlüsselung für Download
  
- [ ] **Datenlöschung (Art. 17)**:
  - Anonymisierung statt vollständiger Löschung (GoBD-Konformität)
  - Cascade-Logik für abhängige Datensätze
  - Pseudonymisierung für Logs
  - Audit-Trail für Löschungen
  
- [ ] **Widerspruch (Art. 21)**:
  - Widerspruch gegen Verarbeitung speichern
  - Automatische Einstellung der Verarbeitung
  - Verknüpfung mit Consent-Management

- [ ] **Identitätsprüfung**:
  - Email-Verifizierung
  - ID-Karte Upload (optional)
  - Manuelle Verifizierung durch Compliance-Officer

### 5. Events
- [ ] `crm.gdpr.request.created`
- [ ] `crm.gdpr.request.verified`
- [ ] `crm.gdpr.request.exported`
- [ ] `crm.gdpr.request.deleted`
- [ ] `crm.gdpr.request.rejected`

## Frontend Tasks

### 1. GDPR-Requests Liste
- [ ] `packages/frontend-web/src/pages/crm/gdpr-requests.tsx`
  - ListReport mit Filtern
  - Spalten: Contact, Request Type, Status, Requested At, Completed At
  - Bulk-Actions: Export, Mark as Completed
  - Export-Funktion

### 2. GDPR-Request Detail
- [ ] `packages/frontend-web/src/pages/crm/gdpr-request-detail.tsx`
  - ObjectPage mit Tabs:
    - Grundinformationen
    - Verifizierung
    - Export-Daten (wenn exportiert)
    - Historie
  - Aktionen: Verify, Generate Export, Delete Data, Reject, Download Export

### 3. GDPR-Export Wizard
- [ ] `packages/frontend-web/src/pages/crm/gdpr-export.tsx`
  - Wizard für Datenexport
  - Schritt 1: Contact auswählen
  - Schritt 2: Datenbereiche auswählen (Contacts, Orders, Activities, etc.)
  - Schritt 3: Format wählen (JSON, CSV, PDF)
  - Schritt 4: Export generieren und Download

### 4. Public Request-Seite
- [ ] `packages/frontend-web/src/pages/crm/gdpr-request-public.tsx`
  - Public-Seite für Betroffene
  - Request erstellen
  - Status prüfen
  - Export herunterladen

### 5. Integration in Contact/Customer
- [ ] Tab "DSGVO-Requests" in `kunden-stamm.tsx`
- [ ] Quick-Actions: Request Access, Request Deletion, Object

## Integration Tasks

### 1. Datenexport aus allen Modulen
- [ ] CRM-Core: Contacts, Customers
- [ ] CRM-Sales: Opportunities, Quotes, Activities
- [ ] CRM-Marketing: Campaigns, Segments
- [ ] CRM-Communication: Emails, SMS
- [ ] Finance: Invoices, Payments
- [ ] Purchase: Orders, Offers

### 2. Anonymisierungs-Logik
- [ ] Anonymisierungs-Regeln pro Entity-Typ
- [ ] Pseudonymisierung für Logs
- [ ] Cascade-Anonymisierung

### 3. Email-Service Integration
- [ ] Verifizierungs-Email
- [ ] Export-Bereit-Email
- [ ] Löschungs-Bestätigung

## Tests

### 1. Unit Tests
- [ ] GDPR-Model Tests
- [ ] Export-Logic Tests
- [ ] Anonymisierungs-Logic Tests

### 2. Integration Tests
- [ ] API-Endpoint Tests
- [ ] Datenexport Tests
- [ ] Anonymisierungs Tests

### 3. E2E Tests
- [ ] `tests/e2e/crm-marketing/gdpr.spec.ts`
  - Request erstellen
  - Verifizierung
  - Datenexport
  - Datenlöschung
  - Widerspruch

## Definition of Done

- ✅ Auskunftsanfragen können verwaltet werden
- ✅ Datenexport funktional (Art. 20 DSGVO)
- ✅ Löschung/Anonymisierung funktional (Art. 17 DSGVO)
- ✅ Widerspruchs-Verwaltung funktional (Art. 21 DSGVO)
- ✅ Alle Requests werden protokolliert
- ✅ Identitätsprüfung funktional
- ✅ Public-Seite für Betroffene
- ✅ Integration in Contact/Customer
- ✅ Alle Tests grün
- ✅ DSGVO-konform

## Nächste Schritte

1. Backend-Service erstellen
2. Database-Models implementieren
3. API-Endpoints implementieren
4. Export-Logic implementieren
5. Anonymisierungs-Logic implementieren
6. Frontend-Seiten erstellen
7. Integration in bestehende Module
8. Tests schreiben

---

**Referenzen:**
- DSGVO Art. 15: Recht auf Auskunft
- DSGVO Art. 17: Recht auf Löschung
- DSGVO Art. 20: Recht auf Datenübertragbarkeit
- DSGVO Art. 21: Widerspruchsrecht
- GoBD-Konformität (Aufbewahrungspflichten)

