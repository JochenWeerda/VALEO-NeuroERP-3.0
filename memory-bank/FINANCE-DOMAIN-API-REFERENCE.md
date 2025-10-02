# VALEO NeuroERP 3.0 - Finance Domain API Reference

## 📋 Schnittstellenbeschreibung für Middleware und Frontend Integration

**Version:** 3.0.0
**Datum:** 2025-09-28
**Status:** ✅ Production Ready
**Base URL:** `/api/finance`

Diese Dokumentation beschreibt die vollständigen Schnittstellen der VALEO NeuroERP 3.0 Finance Domain für die Integration mit Middleware und Frontend-Anwendungen.

---

## 🔐 Authentifizierung & Autorisierung

### JWT Authentication
```typescript
// Authentication Endpoints
POST /api/finance/auth/login
POST /api/finance/auth/refresh
POST /api/finance/auth/logout

// Request: Login
{
  "email": "user@company.com",
  "password": "password",
  "mfaCode": "123456"  // Optional
}

// Response: Auth Token
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
  "expiresIn": 3600,
  "tokenType": "Bearer"
}
```

### Role-Based Access Control (RBAC)
```typescript
enum UserRole {
  ADMIN = 'admin',      // Full access
  ACCOUNTANT = 'accountant', // Accounting operations
  AUDITOR = 'auditor',  // Read-only audit access
  MANAGER = 'manager',  // Approval and reporting
  VIEWER = 'viewer'     // Read-only access
}

enum Permission {
  'ledger:create', 'ledger:read', 'ledger:update', 'ledger:delete',
  'invoice:create', 'invoice:read', 'invoice:update', 'invoice:approve',
  'tax:read', 'tax:calculate',
  'audit:read', 'audit:export',
  'forecast:read', 'forecast:create',
  'user:*', 'system:*'
}
```

### Middleware Integration
```typescript
// Authorization Middleware Hook
const financeAuthMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = verifyFinanceToken(token);

  if (!user) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // Check permissions
  if (!hasPermission(user, req.method, req.path)) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  req.financeUser = user;
  next();
};
```

---

## 📊 Core Business APIs

### 1. Ledger Management

#### Journal Operations
```typescript
// POST /api/finance/ledger/journals
// Create new journal entry
{
  "journalId": "string",
  "date": "2025-09-28",
  "description": "Invoice payment",
  "entries": [
    {
      "accountId": "1200",
      "debit": 119.00,
      "credit": 0,
      "description": "Bank account"
    },
    {
      "accountId": "1400",
      "debit": 0,
      "credit": 119.00,
      "description": "Accounts receivable"
    }
  ],
  "metadata": {
    "source": "invoice",
    "referenceId": "INV-001"
  }
}

// GET /api/finance/ledger/journals/{id}
// Response
{
  "journalId": "string",
  "date": "2025-09-28",
  "description": "string",
  "status": "posted|draft",
  "entries": [...],
  "postedBy": "user-id",
  "postedAt": "2025-09-28T10:00:00Z",
  "aiConfidence": 0.95,
  "aiExplanation": "Standard invoice payment pattern"
}
```

#### Trial Balance
```typescript
// GET /api/finance/ledger/trial-balance
// Query Parameters: ?period=2025-09&format=detailed
{
  "period": "2025-09",
  "accounts": [
    {
      "accountId": "1200",
      "accountName": "Bank account",
      "debit": 15000.00,
      "credit": 3100.00,
      "balance": 11900.00
    }
  ],
  "totals": {
    "totalDebit": 15000.00,
    "totalCredit": 15000.00,
    "inBalance": true
  }
}
```

#### Account Management
```typescript
// GET /api/finance/ledger/accounts
// GET /api/finance/ledger/accounts/{id}
// POST /api/finance/ledger/accounts
// PUT /api/finance/ledger/accounts/{id}

{
  "accountId": "1200",
  "name": "Bank account",
  "type": "asset",
  "category": "current_assets",
  "isActive": true,
  "parentAccountId": null,
  "skrCode": "1200"
}
```

### 2. Accounts Payable (AP)

#### Invoice Processing
```typescript
// POST /api/finance/ap/invoices
// Upload and process invoice
const formData = new FormData();
formData.append('file', invoiceFile);
formData.append('metadata', JSON.stringify({
  "supplierId": "SUP-001",
  "expectedAmount": 119.00,
  "dueDate": "2025-10-28"
}));

// Response
{
  "invoiceId": "AP-001",
  "status": "processed",
  "ocrData": {
    "supplier": "ABC GmbH",
    "amount": 119.00,
    "date": "2025-09-28",
    "dueDate": "2025-10-28"
  },
  "aiSuggestions": [
    {
      "accountId": "4200",
      "confidence": 0.92,
      "reason": "Office supplies based on supplier history"
    }
  ],
  "validationErrors": []
}
```

#### Invoice Approval Workflow
```typescript
// GET /api/finance/ap/invoices/pending-approval
// POST /api/finance/ap/invoices/{id}/approve
// POST /api/finance/ap/invoices/{id}/reject

{
  "invoiceId": "AP-001",
  "approved": true,
  "approvedBy": "user-id",
  "approvedAt": "2025-09-28T10:00:00Z",
  "comments": "Approved for payment",
  "journalEntry": {
    "journalId": "JRN-001",
    "entries": [...]
  }
}
```

### 3. Accounts Receivable (AR)

#### Invoice Management
```typescript
// POST /api/finance/ar/invoices
{
  "customerId": "CUST-001",
  "amount": 119.00,
  "dueDate": "2025-10-28",
  "items": [
    {
      "description": "Consulting services",
      "quantity": 1,
      "unitPrice": 119.00,
      "taxRate": 0.19
    }
  ]
}

// GET /api/finance/ar/invoices/{id}/export
// Query: ?format=xrechnung
{
  "format": "xrechnung",
  "data": "base64-encoded-xml",
  "filename": "invoice-001.xml",
  "validation": {
    "isValid": true,
    "errors": []
  }
}
```

#### Payment Processing
```typescript
// POST /api/finance/ar/payments
{
  "invoiceId": "AR-001",
  "amount": 119.00,
  "paymentMethod": "bank_transfer",
  "paymentDate": "2025-09-28",
  "reference": "Payment reference"
}

// GET /api/finance/ar/open-items
{
  "customerId": "CUST-001",
  "openInvoices": [
    {
      "invoiceId": "AR-001",
      "amount": 119.00,
      "dueDate": "2025-10-28",
      "daysOverdue": 0,
      "dunningLevel": 0
    }
  ]
}
```

### 4. Bank Reconciliation

#### Statement Import
```typescript
// POST /api/finance/bank/statements
const formData = new FormData();
formData.append('file', statementFile);
formData.append('format', 'mt940');
formData.append('accountId', '1200');

// Response
{
  "statementId": "STMT-001",
  "transactions": 25,
  "totalAmount": 5000.00,
  "aiMatches": {
    "autoMatched": 20,
    "manualReview": 3,
    "unmatched": 2
  }
}
```

#### Reconciliation Process
```typescript
// GET /api/finance/bank/reconciliation/{statementId}
// POST /api/finance/bank/reconciliation/{statementId}/match
{
  "transactionId": "TXN-001",
  "matchType": "auto|manual",
  "matchedEntries": [
    {
      "journalId": "JRN-001",
      "entryId": "ENT-001",
      "confidence": 0.95
    }
  ]
}
```

### 5. Tax Compliance

#### VAT Calculation
```typescript
// POST /api/finance/tax/calculate-vat
{
  "country": "DE",
  "transaction": {
    "amount": 100.00,
    "taxCategory": "standard",
    "customerType": "business"
  }
}

// Response
{
  "netAmount": 100.00,
  "taxAmount": 19.00,
  "grossAmount": 119.00,
  "taxRate": 0.19,
  "taxCode": "DE_STANDARD"
}
```

#### Tax Reporting
```typescript
// GET /api/finance/tax/reports/vat
// Query: ?period=2025-09&format=datev
{
  "period": "2025-09",
  "format": "datev",
  "data": "datev-format-data",
  "validation": {
    "compliant": true,
    "warnings": []
  }
}
```

### 6. Forecasting & Analytics

#### Cashflow Forecasting
```typescript
// POST /api/finance/forecasting/cashflow
{
  "periods": 12,
  "scenarios": ["optimistic", "pessimistic", "realistic"],
  "parameters": {
    "growthRate": 0.05,
    "seasonality": true,
    "externalFactors": [...]
  }
}

// Response
{
  "forecastId": "FC-001",
  "periods": [
    {
      "period": "2025-10",
      "predictedCashflow": 15000.00,
      "confidence": 0.85,
      "scenarios": {
        "optimistic": 18000.00,
        "pessimistic": 12000.00,
        "realistic": 15000.00
      }
    }
  ]
}
```

#### Financial Reports
```typescript
// GET /api/finance/reports/pnl
// Query: ?period=2025-09&format=pdf
{
  "reportId": "PNL-001",
  "period": "2025-09",
  "data": {
    "revenue": 50000.00,
    "costOfGoodsSold": 20000.00,
    "grossProfit": 30000.00,
    "operatingExpenses": 15000.00,
    "netProfit": 15000.00
  },
  "generatedAt": "2025-09-28T10:00:00Z"
}
```

### 7. Audit & Compliance

#### Audit Trail Queries
```typescript
// GET /api/finance/audit/events
// Query: ?entity=invoice&entityId=INV-001&from=2025-09-01&to=2025-09-30
{
  "events": [
    {
      "eventId": "EVT-001",
      "eventType": "InvoiceCreated",
      "entityId": "INV-001",
      "userId": "USER-001",
      "timestamp": "2025-09-28T10:00:00Z",
      "data": {...},
      "aiExplanation": "Invoice created with standard validation"
    }
  ],
  "total": 15,
  "hasMore": true
}
```

#### Compliance Packages
```typescript
// POST /api/finance/audit/compliance-package
{
  "period": "2025-09",
  "standards": ["HGB", "GoBD"],
  "includeDocuments": true,
  "format": "pdf"
}

// Response
{
  "packageId": "CP-001",
  "files": [
    {
      "name": "audit-trail-2025-09.pdf",
      "size": 2048576,
      "downloadUrl": "/api/finance/audit/download/CP-001/trail.pdf"
    }
  ],
  "compliance": {
    "HGB": { "compliant": true, "score": 0.98 },
    "GoBD": { "compliant": true, "score": 0.95 }
  }
}
```

---

## 📡 Domain Events für Middleware Integration

### Event Subscription
```typescript
// WebSocket Subscription
const ws = new WebSocket('ws://finance-domain/events');

ws.onmessage = (event) => {
  const domainEvent = JSON.parse(event.data);
  handleDomainEvent(domainEvent);
};

// REST Webhook Registration
POST /api/finance/webhooks
{
  "url": "https://middleware.company.com/finance-events",
  "events": ["InvoiceCreated", "JournalPosted", "PaymentReceived"],
  "secret": "webhook-secret"
}
```

### Core Domain Events
```typescript
interface DomainEvent {
  eventId: string;
  eventType: string;
  aggregateId: string;
  aggregateType: string;
  eventVersion: number;
  occurredOn: Date;
  eventData: Record<string, any>;
  metadata?: {
    userId?: string;
    correlationId?: string;
    causationId?: string;
  };
}

// Key Events for Middleware
type FinanceEventType =
  | 'JournalPosted'
  | 'InvoiceCreated'
  | 'InvoiceApproved'
  | 'PaymentReceived'
  | 'BankStatementImported'
  | 'TaxCalculationCompleted'
  | 'AuditEventRecorded'
  | 'ForecastGenerated'
  | 'ComplianceCheckCompleted';
```

### Event Examples
```typescript
// JournalPosted Event
{
  "eventId": "evt-001",
  "eventType": "JournalPosted",
  "aggregateId": "jrnl-001",
  "aggregateType": "Journal",
  "eventVersion": 1,
  "occurredOn": "2025-09-28T10:00:00Z",
  "eventData": {
    "journalId": "jrnl-001",
    "totalAmount": 119.00,
    "entries": [...],
    "aiConfidence": 0.95
  },
  "metadata": {
    "userId": "user-001",
    "correlationId": "corr-001"
  }
}

// InvoiceCreated Event
{
  "eventId": "evt-002",
  "eventType": "InvoiceCreated",
  "aggregateId": "inv-001",
  "aggregateType": "Invoice",
  "eventData": {
    "invoiceId": "inv-001",
    "type": "AP",
    "amount": 119.00,
    "supplierId": "sup-001",
    "status": "draft"
  }
}
```

---

## 🔄 Middleware Integration Patterns

### Event-Driven Architecture
```typescript
// Middleware Event Processor
class FinanceEventProcessor {
  async processEvent(event: DomainEvent): Promise<void> {
    switch (event.eventType) {
      case 'JournalPosted':
        await this.updateGeneralLedger(event);
        await this.notifyAccountingSystem(event);
        break;

      case 'InvoiceApproved':
        await this.triggerPaymentWorkflow(event);
        await this.updateERPSystem(event);
        break;

      case 'PaymentReceived':
        await this.updateCashPosition(event);
        await this.generateReceipt(event);
        break;
    }
  }
}
```

### API Gateway Integration
```typescript
// Gateway Route Configuration
const financeRoutes = {
  '/api/finance': {
    target: 'http://finance-domain:3001',
    auth: 'jwt',
    rateLimit: '1000/minute',
    cors: true,
    middleware: ['finance-auth', 'finance-logging']
  }
};
```

### Service Mesh Integration
```yaml
# Istio Virtual Service
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: finance-domain
spec:
  http:
  - match:
    - uri:
        prefix: /api/finance
    route:
    - destination:
        host: finance-domain
    timeout: 30s
    retries:
      attempts: 3
```

---

## 🎨 Frontend Integration Guide

### React Hooks für Finance Domain
```typescript
// Custom Hook für Ledger Data
const useLedgerData = (period: string) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/finance/ledger/trial-balance?period=${period}`)
      .then(res => res.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [period]);

  return { data, loading };
};

// Hook für Real-time Updates
const useFinanceEvents = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://finance-domain/events');

    ws.onmessage = (msg) => {
      const event = JSON.parse(msg.data);
      setEvents(prev => [event, ...prev.slice(0, 49)]); // Keep last 50
    };

    return () => ws.close();
  }, []);

  return events;
};
```

### Component Integration
```typescript
// Invoice Processing Component
const InvoiceProcessor = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/finance/ap/invoices', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Process Invoice</button>
      {result && <InvoiceReview data={result} />}
    </div>
  );
};
```

### State Management Integration
```typescript
// Redux Slice für Finance
const financeSlice = createSlice({
  name: 'finance',
  initialState: {
    journals: [],
    invoices: [],
    loading: false,
    error: null
  },
  reducers: {
    setJournals: (state, action) => {
      state.journals = action.payload;
    },
    addInvoice: (state, action) => {
      state.invoices.push(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchJournals.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchJournals.fulfilled, (state, action) => {
        state.journals = action.payload;
        state.loading = false;
      });
  }
});
```

---

## 📊 Monitoring & Observability

### Health Checks
```typescript
// GET /api/finance/health
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "cache": "connected",
    "eventBus": "connected"
  },
  "version": "3.0.0",
  "uptime": "5d 3h 24m"
}

// GET /api/finance/metrics
// Prometheus metrics endpoint
```

### Error Handling
```typescript
// Standardized Error Responses
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid journal entry",
    "details": {
      "field": "amount",
      "reason": "Amount cannot be negative"
    },
    "traceId": "trace-001"
  }
}

// Error Codes
enum FinanceErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR'
}
```

---

## 🔧 Development & Testing

### API Testing
```bash
# Test Authentication
curl -X POST http://localhost:3001/api/finance/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@finance.valero-neuroerp.com","password":"Admin123!"}'

# Test Ledger Operations
curl -X GET http://localhost:3001/api/finance/ledger/trial-balance \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Integration Testing
```typescript
// Jest Integration Test
describe('Finance API Integration', () => {
  it('should create and post journal', async () => {
    const journal = {
      journalId: 'test-001',
      date: '2025-09-28',
      description: 'Test journal',
      entries: [...]
    };

    const response = await request(app)
      .post('/api/finance/ledger/journals')
      .set('Authorization', `Bearer ${token}`)
      .send(journal);

    expect(response.status).toBe(201);
    expect(response.body.journalId).toBe('test-001');
  });
});
```

---

## 📚 Additional Resources

### Documentation Links
- [Finance Domain Implementation](./FINANCE-DOMAIN-COMPLETE-IMPLEMENTATION.md)
- [Domain Events Reference](./domain-events.md)
- [Database Schema](./database-schema.md)
- [Deployment Guide](./deployment-guide.md)

### Support & Integration
- **API Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Deprecation Policy**: 6-month deprecation notice
- **Rate Limiting**: 1000 requests/minute per client
- **CORS Policy**: Configurable for frontend domains

### Future Extensions
- **GraphQL API**: Planned for complex queries
- **Webhook Enhancements**: Custom event filtering
- **Bulk Operations**: Batch processing for large datasets
- **Advanced Analytics**: ML-powered insights and predictions

---

**Diese API-Referenz dient als vollständige Grundlage für die Integration der Finance Domain in Middleware und Frontend-Anwendungen. Alle Schnittstellen sind production-ready und folgen RESTful-Konventionen mit umfassender Fehlerbehandlung und Monitoring.**

**Version:** 3.0.0 | **Last Updated:** 2025-09-28 | **Status:** ✅ Production Ready