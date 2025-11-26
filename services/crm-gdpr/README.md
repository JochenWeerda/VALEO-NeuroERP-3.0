# CRM GDPR Service

GDPR (DSGVO) compliance service for data access, deletion, portability, and objection requests.

## Responsibilities

- Manage GDPR requests (access, deletion, portability, objection)
- Generate data exports (Art. 20 DSGVO)
- Anonymize/delete personal data (Art. 17 DSGVO)
- Handle objections (Art. 21 DSGVO)
- Identity verification
- Complete audit trail

## API Endpoints

- `POST /api/v1/gdpr/requests` - Create GDPR request
- `GET /api/v1/gdpr/requests` - List requests with filters
- `GET /api/v1/gdpr/requests/{id}` - Get request details
- `PUT /api/v1/gdpr/requests/{id}` - Update request
- `POST /api/v1/gdpr/requests/{id}/verify` - Verify identity
- `POST /api/v1/gdpr/requests/{id}/export` - Generate data export
- `POST /api/v1/gdpr/requests/{id}/delete` - Delete/anonymize data
- `POST /api/v1/gdpr/requests/{id}/reject` - Reject request
- `GET /api/v1/gdpr/requests/{id}/history` - Get request history
- `GET /api/v1/gdpr/requests/{id}/download` - Download export file
- `POST /api/v1/gdpr/check` - Check if request exists for contact

## Events

- `crm.gdpr.request.created`
- `crm.gdpr.request.verified`
- `crm.gdpr.request.exported`
- `crm.gdpr.request.deleted`
- `crm.gdpr.request.rejected`

## GDPR Articles

- **Art. 15**: Right of access
- **Art. 17**: Right to erasure (deletion)
- **Art. 20**: Right to data portability
- **Art. 21**: Right to object

