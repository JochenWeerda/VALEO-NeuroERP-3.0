***REMOVED*** CRM Core Service

Responsibilities:
- Canonical customer/account master, contacts, relationships, consent.
- Exposes REST/GraphQL endpoints for customer CRUD, contact management, score updates.
- Publishes domain events: `crm.customer.created`, `crm.customer.updated`, `crm.contact.updated`, `crm.customer.status-changed`.

***REMOVED******REMOVED******REMOVED*** Stub Run
```
pip install fastapi uvicorn
uvicorn main:app --reload
```
