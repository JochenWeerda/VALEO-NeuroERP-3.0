***REMOVED*** Phase 1.2 - Consent-Management (DSGVO)

**Status:** 🚀 In Progress  
**Priorität:** 🔴 Hoch  
**Capability:** CRM-CNS-01  
**Prioritäts-Score:** 25.0  
**Lösungstyp:** C (New Module)  
**Owner:** Compliance-Team  
**Aufwand:** 2-3 Wochen

***REMOVED******REMOVED*** Mission Overview

Implementierung eines vollständigen Consent-Management-Systems für DSGVO-Konformität mit:
- Double-Opt-In für alle Kommunikationskanäle
- Consent-Historie (revisionssicher)
- Kanal-spezifische Opt-ins (Email, SMS, Telefon, Post)
- Automatische Consent-Prüfung vor Kommunikation

***REMOVED******REMOVED*** Backend Tasks

***REMOVED******REMOVED******REMOVED*** 1. Service erstellen: `services/crm-consent/`
- [ ] Projektstruktur anlegen
- [ ] FastAPI-App mit Router
- [ ] Database-Models (SQLAlchemy)
- [ ] Pydantic-Schemas
- [ ] Alembic-Migrationen

***REMOVED******REMOVED******REMOVED*** 2. Database Models
- [ ] `Consent` Entity:
  - `id`, `tenant_id`
  - `contact_id` (FK zu Contact/Customer)
  - `channel` (email, sms, phone, postal)
  - `consent_type` (marketing, service, required)
  - `status` (pending, granted, denied, revoked)
  - `granted_at`, `denied_at`, `revoked_at`
  - `ip_address`, `user_agent`
  - `source` (web_form, api, import, manual)
  - `double_opt_in_token` (UUID)
  - `double_opt_in_confirmed_at`
  - `created_at`, `updated_at`
  - `created_by`, `updated_by`

- [ ] `ConsentHistory` Entity:
  - `id`, `consent_id` (FK)
  - `action` (granted, denied, revoked, updated)
  - `old_status`, `new_status`
  - `changed_by`, `changed_at`
  - `reason` (optional)
  - `ip_address`, `user_agent`

***REMOVED******REMOVED******REMOVED*** 3. API Endpoints
- [ ] `POST /consents` - Consent erstellen (mit Double-Opt-In Token)
- [ ] `GET /consents` - Liste mit Filtern
- [ ] `GET /consents/{id}` - Detail
- [ ] `PUT /consents/{id}` - Update
- [ ] `DELETE /consents/{id}` - Löschen
- [ ] `POST /consents/{id}/confirm` - Double-Opt-In bestätigen
- [ ] `POST /consents/{id}/revoke` - Consent widerrufen
- [ ] `GET /consents/contact/{contact_id}` - Alle Consents eines Kontakts
- [ ] `GET /consents/{id}/history` - Consent-Historie
- [ ] `POST /consents/check` - Consent-Prüfung (für Kommunikation)

***REMOVED******REMOVED******REMOVED*** 4. Business Logic
- [ ] Double-Opt-In Flow:
  - Token generieren
  - Email mit Bestätigungs-Link senden
  - Token validieren bei Bestätigung
  - Status auf "granted" setzen
- [ ] Consent-Prüfung:
  - Prüfe aktiven Consent für Kanal
  - Prüfe Consent-Typ (marketing vs. service)
  - Prüfe Ablaufdatum (falls vorhanden)
- [ ] Automatische Historie:
  - Jede Änderung wird protokolliert
  - Revisionssicher

***REMOVED******REMOVED******REMOVED*** 5. Events
- [ ] `crm.consent.created`
- [ ] `crm.consent.confirmed` (Double-Opt-In)
- [ ] `crm.consent.revoked`
- [ ] `crm.consent.updated`

***REMOVED******REMOVED*** Frontend Tasks

***REMOVED******REMOVED******REMOVED*** 1. Consent-Management Seite
- [ ] `packages/frontend-web/src/pages/crm/consent-management.tsx`
  - ListReport mit Filtern
  - Spalten: Contact, Channel, Status, Granted At, Source
  - Bulk-Actions: Revoke, Export
  - Export-Funktion

***REMOVED******REMOVED******REMOVED*** 2. Consent-Detail Seite
- [ ] `packages/frontend-web/src/pages/crm/consent-detail.tsx`
  - ObjectPage mit Tabs:
    - Grundinformationen
    - Historie (Timeline)
  - Aktionen: Revoke, Resend Confirmation Email

***REMOVED******REMOVED******REMOVED*** 3. Consent-Historie Timeline
- [ ] Timeline-Komponente
  - Chronologische Darstellung
  - Filter nach Action/Status
  - Details pro Eintrag

***REMOVED******REMOVED******REMOVED*** 4. Integration in Contact/Customer
- [ ] Tab "Consents" in `kunden-stamm.tsx`
- [ ] Consent-Status anzeigen
- [ ] Quick-Actions: Grant/Revoke

***REMOVED******REMOVED******REMOVED*** 5. Double-Opt-In Bestätigungsseite
- [ ] `packages/frontend-web/src/pages/crm/consent-confirm.tsx`
  - Public-Seite (kein Login erforderlich)
  - Token-Validierung
  - Bestätigungs-Formular
  - Success/Error-Messages

***REMOVED******REMOVED*** Integration Tasks

***REMOVED******REMOVED******REMOVED*** 1. Email-Service Integration
- [ ] Double-Opt-In Email-Template
- [ ] Bestätigungs-Link generieren
- [ ] Email-Versand bei Consent-Erstellung

***REMOVED******REMOVED******REMOVED*** 2. Marketing-Automation Integration
- [ ] Consent-Prüfung vor Email-Versand
- [ ] Consent-Prüfung vor SMS-Versand
- [ ] Consent-Prüfung vor Telefon-Kontakt
- [ ] Automatische Opt-Out bei Widerruf

***REMOVED******REMOVED******REMOVED*** 3. API-Integration
- [ ] Consent-Check-Endpoint für externe Services
- [ ] Webhook für Consent-Änderungen

***REMOVED******REMOVED*** Tests

***REMOVED******REMOVED******REMOVED*** 1. Unit Tests
- [ ] Consent-Model Tests
- [ ] Consent-Service Tests
- [ ] Double-Opt-In Flow Tests

***REMOVED******REMOVED******REMOVED*** 2. Integration Tests
- [ ] API-Endpoint Tests
- [ ] Email-Service Integration Tests
- [ ] Consent-Prüfung Tests

***REMOVED******REMOVED******REMOVED*** 3. E2E Tests
- [ ] `tests/e2e/crm-marketing/consent.spec.ts`
  - Consent erstellen
  - Double-Opt-In Flow
  - Consent widerrufen
  - Historie anzeigen
  - Consent-Prüfung

***REMOVED******REMOVED*** Definition of Done

- ✅ Double-Opt-In funktional (Email mit Token, Bestätigung)
- ✅ Consent-Historie revisionssicher (alle Änderungen protokolliert)
- ✅ Kanal-spezifische Opt-ins (Email, SMS, Telefon, Post)
- ✅ Automatische Consent-Prüfung vor Kommunikation
- ✅ Integration in Contact/Customer-Stamm
- ✅ Public Bestätigungsseite funktional
- ✅ Alle Tests grün
- ✅ DSGVO-konform (Art. 7 DSGVO: Bedingungen für die Einwilligung)

***REMOVED******REMOVED*** Nächste Schritte

1. Backend-Service erstellen
2. Database-Models implementieren
3. API-Endpoints implementieren
4. Frontend-Seiten erstellen
5. Integration in bestehende Module
6. Tests schreiben

---

**Referenzen:**
- DSGVO Art. 7: Bedingungen für die Einwilligung
- DSGVO Art. 13/14: Informationspflichten
- DSGVO Art. 17: Recht auf Löschung

