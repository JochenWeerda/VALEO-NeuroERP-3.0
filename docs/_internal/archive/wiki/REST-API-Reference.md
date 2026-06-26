# REST-API-Referenz

## Authentifizierung

Alle API-Endpunkte (ausser `/health`) erfordern:

```
Authorization: Bearer <token>
X-Tenant-ID: <uuid>
```

**Dev-Modus:** `Authorization: Bearer dev-token` umgeht OIDC.

## Basis-URL

```
http://localhost:8000/api/v1/
```

## Antwort-Formate

### Paginierte Liste (PaginatedResponse)
```json
{
  "items": [...],
  "total": 12,
  "page": 1,
  "size": 100,
  "pages": 1,
  "has_next": false,
  "has_prev": false
}
```

### Array-Liste (einige Endpunkte)
```json
[{...}, {...}]
```

### Fehler
```json
{
  "detail": "Fehlerbeschreibung",
  "type": "internal_error"
}
```

---

## Kern-Endpunkte

### Health Check
```
GET /health                              -- Kein Auth, fuer Docker/LB
GET /api/v1/health/health                -- Mit Auth
```
Response: `{"status": "healthy", "timestamp": "...", "service": "valeo-neuroerp", "version": "3.0"}`

---

### Artikel (Articles)
```
GET    /api/v1/articles/                 -- Liste (PaginatedResponse)
POST   /api/v1/articles/                 -- Neuen Artikel anlegen
GET    /api/v1/articles/{id}             -- Einzelartikel
PUT    /api/v1/articles/{id}             -- Artikel aktualisieren
DELETE /api/v1/articles/{id}             -- Artikel loeschen
```

**POST/PUT Body (Auszug):**
```json
{
  "article_number": "ART-001",
  "name": "Winterweizen",
  "unit": "kg",
  "article_group": "Getreide",
  "lager_zentral": true,
  "lager_silo": true,
  "is_active": true
}
```

---

### Geschaeftspartner (Business Partners)
```
GET    /api/v1/business-partners/        -- Liste
POST   /api/v1/business-partners/        -- Anlegen
GET    /api/v1/business-partners/{partner_id}  -- Einzelpartner
PUT    /api/v1/business-partners/{partner_id}  -- Aktualisieren
```

> PK ist `partner_id` (nicht `id`)

---

### Wiegescheine (Weighing Tickets)
```
GET    /api/v1/weighing-tickets/         -- Liste (PaginatedResponse)
POST   /api/v1/weighing-tickets/         -- Anlegen
GET    /api/v1/weighing-tickets/{id}     -- Einzeln
PUT    /api/v1/weighing-tickets/{id}     -- Aktualisieren
```

**POST Body:**
```json
{
  "ticket_number": "WG-2026-00001",
  "scale_id": "WAAGE-01",
  "vehicle_plate": "OL-AB 1234",
  "gross_weight": 42500.0,
  "tare_weight": 17200.0,
  "net_weight": 25300.0,
  "direction": "in",
  "article_group": "Getreide",
  "article_id": "<uuid>",
  "notes": "Bemerkung"
}
```

---

### Kontenrahmen (Accounts)
```
GET    /api/v1/accounts/                 -- Liste (PaginatedResponse)
POST   /api/v1/accounts/                 -- Anlegen
GET    /api/v1/accounts/{id}             -- Einzelkonto
PUT    /api/v1/accounts/{id}             -- Aktualisieren
```

**POST Body:**
```json
{
  "account_number": "1000",
  "account_name": "Kasse",
  "account_type": "asset",
  "category": "current_assets",
  "tenant_id": "<uuid>"
}
```

**Gueltige `account_type` Werte:** `asset`, `liability`, `equity`, `revenue`, `expense`

**Gueltige `category` Werte:** `current_assets`, `fixed_assets`, `current_liabilities`, `long_term_liabilities`, `equity`, `revenue`, `cost_of_goods_sold`, `operating_expenses`, `other_expenses`, `other_income`

---

### Buchungsjournal (Journal Entries)
```
GET    /api/v1/journal-entries/          -- Liste (PaginatedResponse)
POST   /api/v1/journal-entries/          -- Anlegen (mit Buchungszeilen)
GET    /api/v1/journal-entries/{id}      -- Einzeln
```

**POST Body:**
```json
{
  "entry_number": "BU-2026-0001",
  "entry_date": "2026-01-15T00:00:00",
  "posting_date": "2026-01-15T00:00:00",
  "description": "Wareneingang Weizen 25t",
  "reference": "WG-2026-00001",
  "source": "manual",
  "tenant_id": "<uuid>",
  "lines": [
    {"account_id": "<uuid>", "debit_amount": "6125.00", "credit_amount": "0.00", "line_number": 1},
    {"account_id": "<uuid>", "debit_amount": "0.00", "credit_amount": "6125.00", "line_number": 2}
  ]
}
```

**Gueltige `source` Werte:** `manual`, `system`, `integration`, `import`

---

### Agrar-Kontrakte (Contracts)
```
GET    /api/v1/agrar/contracts/          -- Liste (PaginatedResponse)
POST   /api/v1/agrar/contracts/          -- Anlegen
GET    /api/v1/agrar/contracts/{id}      -- Einzeln
PUT    /api/v1/agrar/contracts/{id}      -- Aktualisieren
```

---

### Ernte-Annahme (Harvest Acceptance)
```
GET    /api/v1/agrar/harvest-acceptance/ -- Liste (Array)
POST   /api/v1/agrar/harvest-acceptance/ -- Anlegen
GET    /api/v1/agrar/harvest-acceptance/{id} -- Einzeln
PUT    /api/v1/agrar/harvest-acceptance/{id} -- Aktualisieren
```

---

### Silo-Verwaltung
```
GET    /api/v1/silo/                     -- Silo-Liste
POST   /api/v1/silo/                     -- Silo anlegen
GET    /api/v1/silo/{id}                 -- Einzeln
GET    /api/v1/silo/{id}/lots            -- Silo-Partien
```

---

## Weitere Domain-Router (Auszug)

| Prefix | Domain | Tags |
|--------|--------|------|
| `/api/v1/crm/customers` | CRM | crm, customers |
| `/api/v1/crm/leads` | CRM | crm, leads |
| `/api/v1/crm/contacts` | CRM | crm, contacts |
| `/api/v1/crm/activities` | CRM | crm, activities |
| `/api/v1/crm/farm-profiles` | CRM | crm, farm-profiles |
| `/api/v1/sales/orders` | Verkauf | sales, orders |
| `/api/v1/sales/delivery-notes` | Verkauf | sales, delivery-notes |
| `/api/v1/warehouses` | Lager | inventory, warehouses |
| `/api/v1/inventory` | Lager | inventory |
| `/api/v1/agrar/psm` | Agrar | agrar, psm |
| `/api/v1/agrar/varieties` | Agrar | agrar, varieties |
| `/api/v1/agrar/daily-prices` | Agrar | agrar, pricing |
| `/api/v1/agrar/quality-protocols` | Agrar | agrar, quality |
| `/api/v1/agrar/self-billing` | Agrar | agrar, self-billing |
| `/api/v1/agrar/nawaro` | Agrar | agrar, nawaro |
| `/api/v1/finance/periods` | Finanzen | finance, periods |
| `/api/v1/finance/payments` | Finanzen | finance, payments |
| `/api/v1/finance/debtors` | Finanzen | finance, debtors |
| `/api/v1/finance/bank-statements` | Finanzen | finance, bank |
| `/api/v1/finance/reports` | Finanzen | finance, reports |
| `/api/v1/docflow` | Dokumente | docflow |
| `/api/v1/dms` | DMS | documents, dms |
| `/api/v1/audit` | Compliance | audit, gobd |
| `/api/v1/gdpr` | Compliance | GDPR |
| `/api/v1/portal` | Portal | portal, shop |
| `/api/v1/tenants` | System | tenants |
| `/api/v1/users` | System | users |
| `/api/v1/webhooks` | System | webhooks |
| `/api/v1/admin/monitoring` | Admin | monitoring |

---

## OpenAPI-Dokumentation

Automatisch generiert unter:
```
http://localhost:8000/docs      -- Swagger UI
http://localhost:8000/redoc     -- ReDoc
```
