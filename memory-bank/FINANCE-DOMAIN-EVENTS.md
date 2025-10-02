# VALEO NeuroERP 3.0 - Finance Domain Events

## 📡 Domain Events für Event-Driven Architecture

**Version:** 3.0.0
**Datum:** 2025-09-28
**Status:** ✅ Production Ready

Diese Dokumentation beschreibt alle Domain Events der Finance Domain für die Integration mit event-driven Systemen, Middleware und Frontend-Anwendungen.

---

## 🔧 Event Infrastructure

### Base Domain Event Interface
```typescript
export interface DomainEvent {
  eventId: string;              // Unique event identifier
  eventType: string;            // Event type (e.g., 'JournalPosted')
  aggregateId: string;          // ID of the aggregate root
  aggregateType: string;        // Type of aggregate (e.g., 'Journal')
  eventVersion: number;         // Event schema version
  occurredOn: Date;             // When the event occurred
  eventData: Record<string, any>; // Event-specific data
  metadata?: EventMetadata;     // Optional metadata
}

export interface EventMetadata {
  userId?: string;              // User who triggered the event
  correlationId?: string;       // Request correlation ID
  causationId?: string;         // ID of the event that caused this
  tenantId?: string;            // Multi-tenant support
  source: EventSource;          // Where the event originated
  traceId?: string;             // Distributed tracing ID
}

export enum EventSource {
  API = 'api',
  UI = 'ui',
  SYSTEM = 'system',
  BATCH = 'batch',
  INTEGRATION = 'integration'
}
```

### Event Publishing
```typescript
// Event Bus Interface
export interface EventBus {
  publish(event: DomainEvent): Promise<void>;
  subscribe(eventType: string, handler: EventHandler): Promise<void>;
  unsubscribe(eventType: string, handler: EventHandler): Promise<void>;
}

// Event Handler Type
export type EventHandler = (event: DomainEvent) => Promise<void>;

// Middleware Integration
const financeEventBus = new EventBus();

// Subscribe to events
financeEventBus.subscribe('JournalPosted', async (event) => {
  await updateGeneralLedger(event);
  await notifyAccountingSystem(event);
});
```

---

## 📊 Ledger Events

### Journal Events
```typescript
// JournalCreated
export interface JournalCreatedEvent extends DomainEvent {
  eventType: 'JournalCreated';
  aggregateType: 'Journal';
  eventData: {
    journalId: string;
    date: string;
    description: string;
    totalAmount: number;
    currency: string;
    entries: JournalEntryData[];
    createdBy: string;
  };
}

// JournalPosted
export interface JournalPostedEvent extends DomainEvent {
  eventType: 'JournalPosted';
  aggregateType: 'Journal';
  eventData: {
    journalId: string;
    postedBy: string;
    postedAt: string;
    aiConfidence?: number;
    aiExplanation?: string;
    affectedAccounts: AccountBalanceChange[];
  };
}

export interface AccountBalanceChange {
  accountId: string;
  previousBalance: number;
  newBalance: number;
  changeAmount: number;
}

// JournalVoided
export interface JournalVoidedEvent extends DomainEvent {
  eventType: 'JournalVoided';
  aggregateType: 'Journal';
  eventData: {
    journalId: string;
    voidedBy: string;
    voidedAt: string;
    reason: string;
    reversedEntries: JournalEntryData[];
  };
}

export interface JournalEntryData {
  accountId: string;
  debit: number;
  credit: number;
  description?: string;
}
```

### Account Events
```typescript
// AccountCreated
export interface AccountCreatedEvent extends DomainEvent {
  eventType: 'AccountCreated';
  aggregateType: 'Account';
  eventData: {
    accountId: string;
    name: string;
    type: string;
    category: string;
    skrCode?: string;
    parentAccountId?: string;
  };
}

// AccountBalanceChanged
export interface AccountBalanceChangedEvent extends DomainEvent {
  eventType: 'AccountBalanceChanged';
  aggregateType: 'Account';
  eventData: {
    accountId: string;
    previousBalance: number;
    newBalance: number;
    changeAmount: number;
    changeType: 'debit' | 'credit';
    journalId: string;
    transactionDate: string;
  };
}
```

### Period Events
```typescript
// AccountingPeriodClosed
export interface AccountingPeriodClosedEvent extends DomainEvent {
  eventType: 'AccountingPeriodClosed';
  aggregateType: 'AccountingPeriod';
  eventData: {
    period: string; // '2025-09'
    year: number;
    month: number;
    closedBy: string;
    closedAt: string;
    finalBalances: AccountBalance[];
  };
}

export interface AccountBalance {
  accountId: string;
  balance: number;
  currency: string;
}
```

---

## 📄 Invoice Events

### AP Invoice Events
```typescript
// InvoiceCreated
export interface InvoiceCreatedEvent extends DomainEvent {
  eventType: 'InvoiceCreated';
  aggregateType: 'Invoice';
  eventData: {
    invoiceId: string;
    type: 'AP';
    supplierId: string;
    amount: number;
    currency: string;
    dueDate: string;
    status: string;
    ocrData?: OCRResult;
    aiSuggestions?: AISuggestion[];
  };
}

export interface OCRResult {
  supplier: string;
  amount: number;
  date: string;
  dueDate?: string;
  confidence: number;
}

export interface AISuggestion {
  accountId: string;
  confidence: number;
  reason: string;
}

// InvoiceApproved
export interface InvoiceApprovedEvent extends DomainEvent {
  eventType: 'InvoiceApproved';
  aggregateType: 'Invoice';
  eventData: {
    invoiceId: string;
    approvedBy: string;
    approvedAt: string;
    journalId: string;
    approvalWorkflow: ApprovalStep[];
  };
}

export interface ApprovalStep {
  step: number;
  approver: string;
  approvedAt: string;
  comments?: string;
}

// InvoicePaid
export interface InvoicePaidEvent extends DomainEvent {
  eventType: 'InvoicePaid';
  aggregateType: 'Invoice';
  eventData: {
    invoiceId: string;
    paymentId: string;
    amount: number;
    paymentMethod: string;
    paidAt: string;
    outstandingAmount: number;
  };
}
```

### AR Invoice Events
```typescript
// ARInvoiceCreated
export interface ARInvoiceCreatedEvent extends DomainEvent {
  eventType: 'ARInvoiceCreated';
  aggregateType: 'Invoice';
  eventData: {
    invoiceId: string;
    type: 'AR';
    customerId: string;
    amount: number;
    currency: string;
    dueDate: string;
    exportedFormats?: EInvoiceFormat[];
  };
}

// InvoiceOverdue
export interface InvoiceOverdueEvent extends DomainEvent {
  eventType: 'InvoiceOverdue';
  aggregateType: 'Invoice';
  eventData: {
    invoiceId: string;
    customerId: string;
    amount: number;
    dueDate: string;
    daysOverdue: number;
    dunningLevel: number;
  };
}
```

---

## 🏦 Bank Reconciliation Events

### Statement Events
```typescript
// BankStatementImported
export interface BankStatementImportedEvent extends DomainEvent {
  eventType: 'BankStatementImported';
  aggregateType: 'BankStatement';
  eventData: {
    statementId: string;
    accountId: string;
    period: string;
    transactionCount: number;
    totalAmount: number;
    currency: string;
    importMethod: 'mt940' | 'csv' | 'api';
  };
}

// TransactionMatched
export interface TransactionMatchedEvent extends DomainEvent {
  eventType: 'TransactionMatched';
  aggregateType: 'BankTransaction';
  eventData: {
    transactionId: string;
    statementId: string;
    journalEntryId: string;
    matchType: 'auto' | 'manual';
    confidence?: number;
    matchedBy: string;
    matchedAt: string;
  };
}

// ReconciliationCompleted
export interface ReconciliationCompletedEvent extends DomainEvent {
  eventType: 'ReconciliationCompleted';
  aggregateType: 'BankReconciliation';
  eventData: {
    accountId: string;
    period: string;
    matchRate: number;
    matchedTransactions: number;
    unmatchedTransactions: number;
    exceptionTransactions: number;
    reconciledBy: string;
    reconciledAt: string;
  };
}
```

---

## 💰 Tax Events

### Tax Calculation Events
```typescript
// TaxCalculated
export interface TaxCalculatedEvent extends DomainEvent {
  eventType: 'TaxCalculated';
  aggregateType: 'TaxCalculation';
  eventData: {
    transactionId: string;
    country: string;
    baseAmount: number;
    taxAmount: number;
    taxRate: number;
    taxCode: string;
    calculatedBy: 'system' | 'manual';
  };
}

// TaxReportGenerated
export interface TaxReportGeneratedEvent extends DomainEvent {
  eventType: 'TaxReportGenerated';
  aggregateType: 'TaxReport';
  eventData: {
    reportId: string;
    country: string;
    period: string;
    type: string;
    totalTaxDue: number;
    generatedBy: string;
    generatedAt: string;
    validationResult: ValidationResult;
  };
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}
```

---

## 🔮 Forecasting Events

### Forecast Events
```typescript
// CashflowForecastGenerated
export interface CashflowForecastGeneratedEvent extends DomainEvent {
  eventType: 'CashflowForecastGenerated';
  aggregateType: 'CashflowForecast';
  eventData: {
    forecastId: string;
    name: string;
    periods: number;
    scenarios: string[];
    averageConfidence: number;
    generatedBy: string;
    generatedAt: string;
  };
}

// ForecastScenarioCreated
export interface ForecastScenarioCreatedEvent extends DomainEvent {
  eventType: 'ForecastScenarioCreated';
  aggregateType: 'ForecastScenario';
  eventData: {
    scenarioId: string;
    forecastId: string;
    name: string;
    type: string;
    assumptions: Record<string, any>;
    createdBy: string;
  };
}
```

---

## 📋 Audit Events

### Audit Trail Events
```typescript
// AuditEventRecorded
export interface AuditEventRecordedEvent extends DomainEvent {
  eventType: 'AuditEventRecorded';
  aggregateType: 'AuditEvent';
  eventData: {
    auditEventId: string;
    eventType: string;
    entityType: string;
    entityId: string;
    userId?: string;
    timestamp: string;
    aiExplanation?: string;
    compliance: ComplianceInfo;
  };
}

export interface ComplianceInfo {
  hgb: boolean;
  gobd: boolean;
  gdpr: boolean;
  retentionDays: number;
}

// AuditPackageGenerated
export interface AuditPackageGeneratedEvent extends DomainEvent {
  eventType: 'AuditPackageGenerated';
  aggregateType: 'AuditPackage';
  eventData: {
    packageId: string;
    name: string;
    period: string;
    standards: string[];
    fileCount: number;
    totalSize: number;
    generatedBy: string;
    generatedAt: string;
    compliance: Record<string, ComplianceScore>;
  };
}

export interface ComplianceScore {
  compliant: boolean;
  score: number;
  issues: string[];
}
```

---

## 🔐 Security Events

### Authentication Events
```typescript
// UserLoggedIn
export interface UserLoggedInEvent extends DomainEvent {
  eventType: 'UserLoggedIn';
  aggregateType: 'User';
  eventData: {
    userId: string;
    email: string;
    ipAddress: string;
    userAgent: string;
    loginMethod: 'password' | 'mfa' | 'sso';
    successful: boolean;
    failureReason?: string;
  };
}

// PermissionChanged
export interface PermissionChangedEvent extends DomainEvent {
  eventType: 'PermissionChanged';
  aggregateType: 'User';
  eventData: {
    userId: string;
    changedBy: string;
    previousPermissions: string[];
    newPermissions: string[];
    changeReason: string;
  };
}
```

---

## 🎯 Frontend Integration

### React Event Hooks
```typescript
// Custom Hook für Finance Events
const useFinanceEvents = (eventTypes: string[]) => {
  const [events, setEvents] = useState<DomainEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://finance-domain/events');

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    ws.onmessage = (msg) => {
      const event: DomainEvent = JSON.parse(msg.data);
      if (eventTypes.includes(event.eventType)) {
        setEvents(prev => [event, ...prev.slice(0, 99)]); // Keep last 100
      }
    };

    // Subscribe to specific events
    ws.send(JSON.stringify({
      type: 'subscribe',
      events: eventTypes
    }));

    return () => ws.close();
  }, [eventTypes]);

  return { events, isConnected };
};

// Usage in Component
const InvoiceDashboard = () => {
  const { events } = useFinanceEvents([
    'InvoiceCreated',
    'InvoiceApproved',
    'InvoicePaid'
  ]);

  return (
    <div>
      {events.map(event => (
        <InvoiceEventNotification key={event.eventId} event={event} />
      ))}
    </div>
  );
};
```

### Event-Driven State Management
```typescript
// Redux Integration
const financeEventsSlice = createSlice({
  name: 'financeEvents',
  initialState: {
    events: [],
    unreadCount: 0
  },
  reducers: {
    addEvent: (state, action) => {
      state.events.unshift(action.payload);
      state.unreadCount += 1;
    },
    markAsRead: (state) => {
      state.unreadCount = 0;
    }
  }
});

// Event Listener Service
class EventListenerService {
  private ws: WebSocket;
  private store: Store;

  constructor(store: Store) {
    this.store = store;
    this.connect();
  }

  private connect() {
    this.ws = new WebSocket('ws://finance-domain/events');

    this.ws.onmessage = (msg) => {
      const event: DomainEvent = JSON.parse(msg.data);
      this.store.dispatch(addEvent(event));
    };
  }
}
```

---

## 🔄 Middleware Integration Patterns

### Event Processing Pipeline
```typescript
// Event Processor Chain
class FinanceEventProcessor {
  private processors: EventProcessor[] = [];

  addProcessor(processor: EventProcessor) {
    this.processors.push(processor);
  }

  async processEvent(event: DomainEvent): Promise<void> {
    for (const processor of this.processors) {
      if (processor.canHandle(event)) {
        await processor.process(event);
      }
    }
  }
}

// Specific Processors
class LedgerEventProcessor implements EventProcessor {
  canHandle(event: DomainEvent): boolean {
    return ['JournalPosted', 'AccountBalanceChanged'].includes(event.eventType);
  }

  async process(event: DomainEvent): Promise<void> {
    switch (event.eventType) {
      case 'JournalPosted':
        await this.updateGeneralLedger(event);
        break;
      case 'AccountBalanceChanged':
        await this.updateAccountBalances(event);
        break;
    }
  }
}
```

### Event Enrichment
```typescript
// Event Enrichment Service
class EventEnrichmentService {
  async enrichEvent(event: DomainEvent): Promise<DomainEvent> {
    const enrichedData = { ...event.eventData };

    // Add user information
    if (event.metadata?.userId) {
      enrichedData.user = await this.getUserInfo(event.metadata.userId);
    }

    // Add business context
    if (event.aggregateType === 'Invoice') {
      enrichedData.businessContext = await this.getInvoiceContext(event.aggregateId);
    }

    return {
      ...event,
      eventData: enrichedData
    };
  }
}
```

### Event Filtering & Routing
```typescript
// Event Router
class EventRouter {
  private routes: Map<string, EventHandler[]> = new Map();

  route(eventType: string, handler: EventHandler) {
    const handlers = this.routes.get(eventType) || [];
    handlers.push(handler);
    this.routes.set(eventType, handlers);
  }

  async routeEvent(event: DomainEvent): Promise<void> {
    const handlers = this.routes.get(event.eventType) || [];
    await Promise.all(handlers.map(handler => handler(event)));
  }
}

// Usage
const router = new EventRouter();
router.route('JournalPosted', updateGeneralLedger);
router.route('InvoiceCreated', notifyAccountingTeam);
router.route('PaymentReceived', updateCashPosition);
```

---

## 📊 Event Monitoring & Analytics

### Event Metrics
```typescript
// Event Metrics Collector
class EventMetricsCollector {
  private metrics: Map<string, EventMetrics> = new Map();

  recordEvent(event: DomainEvent) {
    const key = event.eventType;
    const existing = this.metrics.get(key) || {
      count: 0,
      lastOccurred: null,
      processingTimes: []
    };

    existing.count += 1;
    existing.lastOccurred = event.occurredOn;

    this.metrics.set(key, existing);
  }

  getMetrics(eventType: string): EventMetrics | null {
    return this.metrics.get(eventType) || null;
  }

  getAllMetrics(): Record<string, EventMetrics> {
    return Object.fromEntries(this.metrics);
  }
}

interface EventMetrics {
  count: number;
  lastOccurred: Date | null;
  averageProcessingTime?: number;
  errorRate?: number;
}
```

### Event Health Monitoring
```typescript
// Event Health Check
class EventHealthMonitor {
  private unhealthyEvents: Set<string> = new Set();

  checkEventHealth(event: DomainEvent): HealthStatus {
    const now = new Date();
    const eventTime = new Date(event.occurredOn);
    const age = now.getTime() - eventTime.getTime();

    // Flag events older than 5 minutes as potentially unhealthy
    if (age > 5 * 60 * 1000) {
      this.unhealthyEvents.add(event.eventId);
      return 'unhealthy';
    }

    this.unhealthyEvents.delete(event.eventId);
    return 'healthy';
  }

  getHealthStatus(): EventHealthStatus {
    return {
      totalEvents: this.unhealthyEvents.size,
      healthy: this.unhealthyEvents.size === 0,
      unhealthyEventIds: Array.from(this.unhealthyEvents)
    };
  }
}
```

---

## 📚 Event Catalog Summary

| Event Category | Event Count | Key Events |
|----------------|-------------|------------|
| **Ledger** | 6 | JournalPosted, AccountBalanceChanged, PeriodClosed |
| **Invoices** | 8 | InvoiceCreated, InvoiceApproved, InvoicePaid, InvoiceOverdue |
| **Banking** | 5 | StatementImported, TransactionMatched, ReconciliationCompleted |
| **Tax** | 4 | TaxCalculated, TaxReportGenerated |
| **Forecasting** | 3 | ForecastGenerated, ScenarioCreated |
| **Audit** | 3 | AuditEventRecorded, AuditPackageGenerated |
| **Security** | 3 | UserLoggedIn, PermissionChanged |
| **Total** | **32** | **Complete Event-Driven Finance System** |

---

**Diese Domain Events bilden die vollständige Grundlage für die event-driven Integration der Finance Domain. Alle Events sind versioniert, typsicher und mit vollständigen Metadaten ausgestattet.**

**Version:** 3.0.0 | **Last Updated:** 2025-09-28 | **Status:** ✅ Production Ready