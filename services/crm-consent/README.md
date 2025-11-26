# CRM Consent Service

GDPR-compliant consent management with double opt-in.

## Responsibilities

- Manage consent records for contacts/customers
- Double opt-in flow with email confirmation
- Consent history (revision-safe audit trail)
- Channel-specific opt-ins (Email, SMS, Phone, Postal)
- Automatic consent checking before communication

## API Endpoints

- `POST /api/v1/consents` - Create consent (with double opt-in token)
- `GET /api/v1/consents` - List consents with filters
- `GET /api/v1/consents/{id}` - Get consent details
- `PUT /api/v1/consents/{id}` - Update consent
- `DELETE /api/v1/consents/{id}` - Delete consent
- `POST /api/v1/consents/{id}/confirm` - Confirm double opt-in
- `POST /api/v1/consents/{id}/revoke` - Revoke consent
- `GET /api/v1/consents/contact/{contact_id}` - Get all consents for a contact
- `GET /api/v1/consents/{id}/history` - Get consent history
- `POST /api/v1/consents/check` - Check consent (for communication)

## Events

- `crm.consent.created`
- `crm.consent.confirmed` (Double opt-in)
- `crm.consent.revoked`
- `crm.consent.updated`

