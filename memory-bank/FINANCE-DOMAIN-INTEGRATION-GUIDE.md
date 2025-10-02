# VALEO NeuroERP 3.0 - Finance Domain Integration Guide

## 🚀 Schnellstart für Middleware und Frontend Integration

**Version:** 3.0.0
**Datum:** 2025-09-28
**Status:** ✅ Production Ready

Dieser Leitfaden bietet einen schnellen Einstieg in die Integration der Finance Domain für Middleware- und Frontend-Entwickler.

---

## 📋 Übersicht der verfügbaren Dokumentation

### 1. API Reference - Vollständige Schnittstellenbeschreibung
**Datei:** `FINANCE-DOMAIN-API-REFERENCE.md`
- ✅ **550+ Zeilen** detaillierte API-Dokumentation
- ✅ **50+ REST-Endpunkte** mit Beispielen
- ✅ **Authentifizierung & Autorisierung** (JWT, RBAC)
- ✅ **Event-Driven Integration** mit WebSockets
- ✅ **Middleware Patterns** und Best Practices
- ✅ **Frontend Integration** mit React Hooks

### 2. Data Models - TypeScript Schnittstellen
**Datei:** `FINANCE-DOMAIN-DATA-MODELS.md`
- ✅ **650+ Zeilen** vollständige Datenmodelle
- ✅ **Branded Types** für Type Safety
- ✅ **Domain Entities** (Account, Journal, Invoice, etc.)
- ✅ **Frontend Integration Types** (React Hooks, Form Data)
- ✅ **API Response Models** (Pagination, Error Handling)
- ✅ **Monitoring Models** (Metrics, Health Checks)

### 3. Domain Events - Event-Driven Architecture
**Datei:** `FINANCE-DOMAIN-EVENTS.md`
- ✅ **550+ Zeilen** Event-Katalog
- ✅ **32 Domain Events** mit vollständigen Schemas
- ✅ **Event Processing Patterns** für Middleware
- ✅ **Frontend Event Hooks** für React
- ✅ **Event Monitoring** und Health Checks
- ✅ **Real-time Integration** mit WebSockets

### 4. Complete Implementation - Technische Details
**Datei:** `FINANCE-DOMAIN-COMPLETE-IMPLEMENTATION.md`
- ✅ **400+ Zeilen** vollständige Implementierung
- ✅ **8-Sprint Entwicklung** detailliert beschrieben
- ✅ **Business Impact** und ROI-Analysen
- ✅ **Production Deployment** Anleitungen
- ✅ **Compliance Standards** (HGB, IFRS, etc.)

---

## 🎯 Schnellstart für verschiedene Integrationsszenarien

### Szenario 1: Frontend Integration (React/Vue/Angular)

#### Schritt 1: API Client Setup
```typescript
// api/finance-client.ts
import { ApiResponse, PaginatedResponse, Invoice, Journal } from './types/finance';

class FinanceApiClient {
  private baseUrl = '/api/finance';
  private token: string | null = null;

  setAuthToken(token: string) {
    this.token = token;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options?.headers
      }
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Ledger APIs
  async getTrialBalance(period: string): Promise<TrialBalance> {
    return this.request(`/ledger/trial-balance?period=${period}`);
  }

  async createJournal(data: CreateJournalData): Promise<Journal> {
    return this.request('/ledger/journals', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Invoice APIs
  async getInvoices(params?: InvoiceQuery): Promise<PaginatedResponse<Invoice>> {
    const query = new URLSearchParams(params as any);
    return this.request(`/ap/invoices?${query}`);
  }

  async uploadInvoice(file: File): Promise<Invoice> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/ap/invoices`, {
      method: 'POST',
      headers: {
        ...(this.token && { Authorization: `Bearer ${this.token}` })
      },
      body: formData
    });

    return response.json();
  }
}

export const financeApi = new FinanceApiClient();
```

#### Schritt 2: React Hooks für Finance Data
```typescript
// hooks/useFinance.ts
import { useState, useEffect } from 'react';
import { financeApi } from '../api/finance-client';
import { TrialBalance, Invoice, Journal } from '../types/finance';

export function useTrialBalance(period: string) {
  const [data, setData] = useState<TrialBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    financeApi.getTrialBalance(period)
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [period]);

  return { data, loading, error, refetch: () => setLoading(true) };
}

export function useInvoices(status?: string) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    financeApi.getInvoices({ status, limit: 50 })
      .then(response => setInvoices(response.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [status]);

  return { invoices, loading };
}

export function useFinanceEvents() {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3001/events');

    ws.onmessage = (msg) => {
      const event = JSON.parse(msg.data);
      setEvents(prev => [event, ...prev.slice(0, 49)]);
    };

    return () => ws.close();
  }, []);

  return events;
}
```

#### Schritt 3: Component Integration
```typescript
// components/FinanceDashboard.tsx
import React from 'react';
import { useTrialBalance, useInvoices, useFinanceEvents } from '../hooks/useFinance';

const FinanceDashboard: React.FC = () => {
  const { data: trialBalance, loading: tbLoading } = useTrialBalance('2025-09');
  const { invoices, loading: invLoading } = useInvoices('approved');
  const events = useFinanceEvents();

  if (tbLoading || invLoading) return <div>Loading...</div>;

  return (
    <div className="finance-dashboard">
      <div className="trial-balance">
        <h3>Trial Balance - September 2025</h3>
        {trialBalance && (
          <div className="balances">
            <div>Total Debit: €{trialBalance.totals.totalDebit.amount}</div>
            <div>Total Credit: €{trialBalance.totals.totalCredit.amount}</div>
            <div className={trialBalance.totals.inBalance ? 'balanced' : 'unbalanced'}>
              Status: {trialBalance.totals.inBalance ? 'Balanced' : 'Unbalanced'}
            </div>
          </div>
        )}
      </div>

      <div className="recent-invoices">
        <h3>Recent Approved Invoices</h3>
        {invoices.slice(0, 5).map(invoice => (
          <div key={invoice.id} className="invoice-item">
            <span>{invoice.invoiceNumber}</span>
            <span>€{invoice.totalAmount.amount}</span>
            <span>{invoice.status}</span>
          </div>
        ))}
      </div>

      <div className="recent-events">
        <h3>Recent Finance Events</h3>
        {events.slice(0, 10).map(event => (
          <div key={event.eventId} className="event-item">
            <span>{event.eventType}</span>
            <span>{new Date(event.occurredOn).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FinanceDashboard;
```

### Szenario 2: Middleware Integration (Node.js/Java/Spring)

#### Schritt 1: Event Consumer Setup
```typescript
// middleware/finance-event-consumer.ts
import { EventBus } from './event-bus';
import { DomainEvent } from './types/finance';

class FinanceEventConsumer {
  private eventBus: EventBus;

  constructor(eventBus: EventBus) {
    this.eventBus = eventBus;
    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    // Journal Events
    this.eventBus.subscribe('JournalPosted', this.handleJournalPosted.bind(this));
    this.eventBus.subscribe('AccountBalanceChanged', this.handleAccountBalanceChanged.bind(this));

    // Invoice Events
    this.eventBus.subscribe('InvoiceCreated', this.handleInvoiceCreated.bind(this));
    this.eventBus.subscribe('InvoiceApproved', this.handleInvoiceApproved.bind(this));
    this.eventBus.subscribe('InvoicePaid', this.handleInvoicePaid.bind(this));

    // Bank Events
    this.eventBus.subscribe('BankStatementImported', this.handleBankStatementImported.bind(this));
    this.eventBus.subscribe('ReconciliationCompleted', this.handleReconciliationCompleted.bind(this));
  }

  private async handleJournalPosted(event: DomainEvent) {
    console.log('Processing journal posting:', event.eventData.journalId);

    // Update general ledger in ERP system
    await this.updateERPGeneralLedger(event);

    // Notify accounting team
    await this.notifyAccountingTeam(event);

    // Update data warehouse
    await this.updateDataWarehouse(event);
  }

  private async handleInvoiceApproved(event: DomainEvent) {
    console.log('Processing invoice approval:', event.eventData.invoiceId);

    // Trigger payment workflow
    await this.triggerPaymentWorkflow(event);

    // Update purchase order status
    await this.updatePurchaseOrderStatus(event);

    // Send notification to supplier
    await this.notifySupplier(event);
  }

  private async handleBankStatementImported(event: DomainEvent) {
    console.log('Processing bank statement:', event.eventData.statementId);

    // Validate transactions
    await this.validateBankTransactions(event);

    // Update cash position
    await this.updateCashPosition(event);

    // Trigger reconciliation process
    await this.triggerReconciliation(event);
  }
}

export default FinanceEventConsumer;
```

#### Schritt 2: API Integration Layer
```typescript
// middleware/finance-api-integration.ts
import axios, { AxiosInstance } from 'axios';
import { AuthService } from './auth-service';

class FinanceApiIntegration {
  private client: AxiosInstance;
  private auth: AuthService;

  constructor(baseUrl: string, auth: AuthService) {
    this.auth = auth;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for authentication
    this.client.interceptors.request.use(async (config) => {
      const token = await this.auth.getToken();
      config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          // Token expired, refresh and retry
          return this.auth.refreshToken().then(() => {
            return this.client.request(error.config);
          });
        }
        return Promise.reject(error);
      }
    );
  }

  // Ledger Integration
  async syncTrialBalance(period: string) {
    const response = await this.client.get(`/ledger/trial-balance?period=${period}`);
    return this.transformTrialBalance(response.data);
  }

  async createJournalEntry(entry: JournalEntryData) {
    const response = await this.client.post('/ledger/journals', entry);
    return response.data;
  }

  // Invoice Integration
  async processInvoice(file: Buffer, metadata: any) {
    const formData = new FormData();
    formData.append('file', file, 'invoice.pdf');
    formData.append('metadata', JSON.stringify(metadata));

    const response = await this.client.post('/ap/invoices', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    return response.data;
  }

  async getOutstandingInvoices() {
    const response = await this.client.get('/ap/invoices?status=approved&paid=false');
    return response.data.data;
  }

  // Tax Integration
  async calculateTax(transaction: TaxCalculationRequest) {
    const response = await this.client.post('/tax/calculate-vat', transaction);
    return response.data;
  }

  async submitTaxReport(report: TaxReportData) {
    const response = await this.client.post('/tax/reports', report);
    return response.data;
  }

  private transformTrialBalance(apiData: any) {
    // Transform API response to internal format
    return {
      period: apiData.period,
      accounts: apiData.accounts.map(account => ({
        id: account.accountId,
        name: account.accountName,
        balance: account.balance
      })),
      totals: apiData.totals
    };
  }
}

export default FinanceApiIntegration;
```

#### Schritt 3: Service Orchestration
```typescript
// middleware/finance-orchestrator.ts
import { FinanceApiIntegration } from './finance-api-integration';
import { FinanceEventConsumer } from './finance-event-consumer';
import { WorkflowEngine } from './workflow-engine';

class FinanceOrchestrator {
  private api: FinanceApiIntegration;
  private eventConsumer: FinanceEventConsumer;
  private workflowEngine: WorkflowEngine;

  constructor(api: FinanceApiIntegration, eventConsumer: FinanceEventConsumer) {
    this.api = api;
    this.eventConsumer = eventConsumer;
    this.workflowEngine = new WorkflowEngine();
  }

  // Invoice to Payment Workflow
  async handleInvoiceToPayment(invoiceId: string) {
    // 1. Get invoice details
    const invoice = await this.api.getInvoiceDetails(invoiceId);

    // 2. Check approval status
    if (invoice.status !== 'approved') {
      throw new Error('Invoice not approved');
    }

    // 3. Create payment workflow
    const workflowId = await this.workflowEngine.createWorkflow({
      type: 'invoice_payment',
      data: { invoiceId, amount: invoice.totalAmount }
    });

    // 4. Trigger payment process
    await this.workflowEngine.executeStep(workflowId, 'validate_payment_terms');

    return { workflowId, status: 'initiated' };
  }

  // Bank Reconciliation Workflow
  async handleBankReconciliation(statementId: string) {
    // 1. Import bank statement
    const statement = await this.api.importBankStatement(statementId);

    // 2. Auto-match transactions
    const matches = await this.api.matchTransactions(statement.transactions);

    // 3. Create reconciliation workflow for exceptions
    const exceptions = matches.filter(m => m.status === 'exception');
    if (exceptions.length > 0) {
      await this.workflowEngine.createWorkflow({
        type: 'reconciliation_review',
        data: { statementId, exceptions }
      });
    }

    // 4. Complete reconciliation
    await this.api.completeReconciliation(statementId);

    return { matched: matches.length - exceptions.length, exceptions: exceptions.length };
  }

  // Tax Compliance Workflow
  async handleTaxCompliance(period: string) {
    // 1. Generate tax report
    const report = await this.api.generateTaxReport(period);

    // 2. Validate compliance
    const validation = await this.api.validateTaxCompliance(report);

    if (!validation.isValid) {
      // Create compliance workflow
      await this.workflowEngine.createWorkflow({
        type: 'tax_compliance_review',
        data: { period, reportId: report.id, issues: validation.errors }
      });
    }

    // 3. Submit report
    await this.api.submitTaxReport(report.id);

    return { reportId: report.id, compliant: validation.isValid };
  }
}

export default FinanceOrchestrator;
```

### Szenario 3: Legacy System Integration

#### Schritt 1: ETL Pipeline Setup
```typescript
// integration/finance-etl.ts
import { FinanceApiIntegration } from '../middleware/finance-api-integration';
import { LegacySystemAdapter } from './legacy-adapter';

class FinanceETLPipeline {
  private financeApi: FinanceApiIntegration;
  private legacyAdapter: LegacySystemAdapter;

  constructor(financeApi: FinanceApiIntegration, legacyAdapter: LegacySystemAdapter) {
    this.financeApi = financeApi;
    this.legacyAdapter = legacyAdapter;
  }

  // Daily ETL Process
  async runDailyETL() {
    console.log('Starting Finance ETL Pipeline');

    try {
      // 1. Extract data from legacy system
      const legacyData = await this.extractLegacyData();

      // 2. Transform to Finance Domain format
      const transformedData = await this.transformData(legacyData);

      // 3. Load into Finance Domain
      await this.loadToFinanceDomain(transformedData);

      // 4. Validate and reconcile
      await this.validateAndReconcile();

      console.log('Finance ETL Pipeline completed successfully');
    } catch (error) {
      console.error('ETL Pipeline failed:', error);
      await this.handleETLError(error);
    }
  }

  private async extractLegacyData() {
    // Extract journals, invoices, payments from legacy system
    const [journals, invoices, payments] = await Promise.all([
      this.legacyAdapter.getJournals(),
      this.legacyAdapter.getInvoices(),
      this.legacyAdapter.getPayments()
    ]);

    return { journals, invoices, payments };
  }

  private async transformData(legacyData: any) {
    // Transform legacy format to Finance Domain format
    return {
      journals: legacyData.journals.map(this.transformJournal),
      invoices: legacyData.invoices.map(this.transformInvoice),
      payments: legacyData.payments.map(this.transformPayment)
    };
  }

  private async loadToFinanceDomain(transformedData: any) {
    // Load data into Finance Domain
    const results = await Promise.allSettled([
      ...transformedData.journals.map(j => this.financeApi.createJournal(j)),
      ...transformedData.invoices.map(i => this.financeApi.createInvoice(i)),
      ...transformedData.payments.map(p => this.financeApi.recordPayment(p))
    ]);

    return results;
  }

  private async validateAndReconcile() {
    // Validate data integrity and reconcile balances
    const trialBalance = await this.financeApi.getTrialBalance();
    const validation = this.validateTrialBalance(trialBalance);

    if (!validation.isBalanced) {
      await this.createReconciliationWorkflow(validation.discrepancies);
    }
  }
}

export default FinanceETLPipeline;
```

---

## 🔧 Setup und Konfiguration

### 1. Environment Variables
```bash
# Finance Domain Connection
FINANCE_API_URL=http://finance-domain:3001/api/finance
FINANCE_WS_URL=ws://finance-domain:3001/events

# Authentication
FINANCE_CLIENT_ID=your-client-id
FINANCE_CLIENT_SECRET=your-client-secret

# Event Processing
EVENT_BATCH_SIZE=100
EVENT_PROCESSING_TIMEOUT=30000
EVENT_RETRY_ATTEMPTS=3

# Caching
CACHE_TTL_LEDGER=300
CACHE_TTL_INVOICES=600
CACHE_TTL_REPORTS=3600
```

### 2. Dependency Installation
```json
// package.json dependencies
{
  "dependencies": {
    "axios": "^1.6.0",
    "ws": "^8.14.0",
    "form-data": "^4.0.0",
    "jsonwebtoken": "^9.0.2",
    "eventemitter3": "^5.0.1",
    "@types/node": "^20.10.0"
  }
}
```

### 3. Type Definitions
```typescript
// types/finance-integration.ts
export interface IntegrationConfig {
  apiUrl: string;
  wsUrl: string;
  auth: AuthConfig;
  events: EventConfig;
  cache: CacheConfig;
}

export interface AuthConfig {
  clientId: string;
  clientSecret: string;
  tokenEndpoint: string;
  refreshThreshold: number;
}

export interface EventConfig {
  batchSize: number;
  processingTimeout: number;
  retryAttempts: number;
  subscriptions: string[];
}

export interface CacheConfig {
  ttl: Record<string, number>;
  maxSize: number;
  strategy: 'lru' | 'lfu';
}
```

---

## 📊 Monitoring und Debugging

### Health Checks
```typescript
// middleware/health-check.ts
class FinanceHealthChecker {
  private api: FinanceApiIntegration;

  async checkHealth(): Promise<HealthStatus> {
    try {
      // API Health Check
      await this.api.getHealth();

      // Event Bus Health Check
      const eventHealth = await this.checkEventBusHealth();

      // Database Health Check
      const dbHealth = await this.checkDatabaseHealth();

      return {
        status: 'healthy',
        services: {
          api: 'healthy',
          events: eventHealth,
          database: dbHealth
        },
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
}
```

### Error Handling
```typescript
// middleware/error-handler.ts
class FinanceErrorHandler {
  handleApiError(error: any): IntegrationError {
    if (error.response) {
      // API Error
      const { status, data } = error.response;
      return new IntegrationError(
        `API Error ${status}: ${data.message}`,
        status,
        data.details
      );
    } else if (error.request) {
      // Network Error
      return new IntegrationError(
        'Network Error: Unable to reach Finance API',
        0,
        { originalError: error.message }
      );
    } else {
      // Other Error
      return new IntegrationError(
        `Integration Error: ${error.message}`,
        0,
        { originalError: error.message }
      );
    }
  }

  handleEventError(event: DomainEvent, error: any): void {
    console.error(`Event processing failed for ${event.eventType}:`, error);

    // Implement retry logic, dead letter queue, etc.
    this.sendToDeadLetterQueue(event, error);
    this.notifyMonitoringSystem(event, error);
  }
}
```

---

## 🎯 Best Practices

### 1. Error Handling
- ✅ Implement comprehensive error handling for all API calls
- ✅ Use exponential backoff for retries
- ✅ Implement circuit breakers for fault tolerance
- ✅ Log all errors with correlation IDs

### 2. Performance Optimization
- ✅ Implement caching for frequently accessed data
- ✅ Use pagination for large datasets
- ✅ Batch operations where possible
- ✅ Monitor response times and set up alerts

### 3. Security
- ✅ Store tokens securely (never in localStorage for web apps)
- ✅ Implement token refresh logic
- ✅ Validate all input data
- ✅ Use HTTPS for all communications

### 4. Event Processing
- ✅ Implement idempotent event handlers
- ✅ Use correlation IDs for request tracing
- ✅ Handle out-of-order events gracefully
- ✅ Implement event replay capabilities

### 5. Testing
- ✅ Write integration tests for all API calls
- ✅ Mock external dependencies in unit tests
- ✅ Test error scenarios and edge cases
- ✅ Implement contract tests for API compatibility

---

## 📞 Support und Ressourcen

### Dokumentation
- **API Reference**: `FINANCE-DOMAIN-API-REFERENCE.md`
- **Data Models**: `FINANCE-DOMAIN-DATA-MODELS.md`
- **Domain Events**: `FINANCE-DOMAIN-EVENTS.md`
- **Implementation Guide**: `FINANCE-DOMAIN-COMPLETE-IMPLEMENTATION.md`

### Beispielprojekte
- **Frontend Integration**: Beispiel React-Komponenten
- **Middleware Integration**: Beispiel Node.js Services
- **Legacy Integration**: ETL Pipeline Beispiele

### Support
- **Issues**: GitHub Issues für Bug Reports
- **Discussions**: GitHub Discussions für Fragen
- **Wiki**: Projekt-Wiki für erweiterte Themen

---

**Diese Integrationsanleitung bietet alles Notwendige für die erfolgreiche Integration der Finance Domain in Ihre Middleware und Frontend-Anwendungen.**

**Viel Erfolg bei der Integration!** 🚀