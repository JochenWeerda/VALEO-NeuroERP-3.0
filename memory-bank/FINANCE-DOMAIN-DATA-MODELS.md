# VALEO NeuroERP 3.0 - Finance Domain Data Models

## 📋 Datenmodelle für Frontend und Middleware Integration

**Version:** 3.0.0
**Datum:** 2025-09-28
**Status:** ✅ Production Ready

Diese Dokumentation beschreibt alle Datenmodelle, Entitäten und TypeScript-Interfaces der Finance Domain für die Integration mit Frontend und Middleware.

---

## 🔧 Core TypeScript Types

### Branded Types für Type Safety
```typescript
// Branded Types für Domain Safety
export type AccountId = string & { readonly __brand: 'AccountId' };
export type JournalId = string & { readonly __brand: 'JournalId' };
export type InvoiceId = string & { readonly __brand: 'InvoiceId' };
export type CustomerId = string & { readonly __brand: 'CustomerId' };
export type SupplierId = string & { readonly __brand: 'SupplierId' };
export type UserId = string & { readonly __brand: 'UserId' };
export type TenantId = string & { readonly __brand: 'TenantId' };

// Money Type mit Currency
export interface Money {
  amount: number;
  currency: Currency;
}

export enum Currency {
  EUR = 'EUR',
  USD = 'USD',
  GBP = 'GBP',
  CHF = 'CHF'
}

// Result Type für Error Handling
export interface Result<T, E = Error> {
  success: boolean;
  data?: T;
  error?: E;
}
```

---

## 📊 Ledger Domain Models

### Account Entity
```typescript
export interface Account {
  id: AccountId;
  accountId: string; // Human-readable ID like "1200"
  name: string;
  type: AccountType;
  category: AccountCategory;
  isActive: boolean;
  parentAccountId?: AccountId;
  skrCode?: string; // SKR04 code for German accounting
  balance: Money;
  createdAt: Date;
  updatedAt: Date;
}

export enum AccountType {
  ASSET = 'asset',
  LIABILITY = 'liability',
  EQUITY = 'equity',
  REVENUE = 'revenue',
  EXPENSE = 'expense'
}

export enum AccountCategory {
  // Assets
  CURRENT_ASSETS = 'current_assets',
  FIXED_ASSETS = 'fixed_assets',
  INTANGIBLE_ASSETS = 'intangible_assets',

  // Liabilities
  CURRENT_LIABILITIES = 'current_liabilities',
  LONG_TERM_LIABILITIES = 'long_term_liabilities',

  // Equity
  CAPITAL = 'capital',
  RETAINED_EARNINGS = 'retained_earnings',

  // Revenue
  SALES_REVENUE = 'sales_revenue',
  OTHER_REVENUE = 'other_revenue',

  // Expenses
  COST_OF_GOODS_SOLD = 'cost_of_goods_sold',
  OPERATING_EXPENSES = 'operating_expenses',
  FINANCIAL_EXPENSES = 'financial_expenses'
}
```

### Journal Entity
```typescript
export interface Journal {
  id: JournalId;
  journalId: string;
  date: Date;
  description: string;
  status: JournalStatus;
  entries: JournalEntry[];
  totalDebit: Money;
  totalCredit: Money;
  isBalanced: boolean;
  postedBy?: UserId;
  postedAt?: Date;
  approvedBy?: UserId;
  approvedAt?: Date;
  aiConfidence?: number;
  aiExplanation?: string;
  metadata?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export enum JournalStatus {
  DRAFT = 'draft',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  POSTED = 'posted',
  REJECTED = 'rejected',
  VOIDED = 'voided'
}

export interface JournalEntry {
  id: string;
  accountId: AccountId;
  debit: Money;
  credit: Money;
  description?: string;
  reference?: string;
  taxCode?: string;
  costCenter?: string;
  projectId?: string;
}
```

### Trial Balance
```typescript
export interface TrialBalance {
  period: AccountingPeriod;
  accounts: TrialBalanceEntry[];
  totals: {
    totalDebit: Money;
    totalCredit: Money;
    inBalance: boolean;
    difference: Money;
  };
  generatedAt: Date;
  generatedBy: UserId;
}

export interface TrialBalanceEntry {
  accountId: AccountId;
  accountName: string;
  debit: Money;
  credit: Money;
  balance: Money;
  balanceType: 'debit' | 'credit';
}

export interface AccountingPeriod {
  year: number;
  month: number;
  startDate: Date;
  endDate: Date;
  status: PeriodStatus;
  closedBy?: UserId;
  closedAt?: Date;
}

export enum PeriodStatus {
  OPEN = 'open',
  CLOSING = 'closing',
  CLOSED = 'closed',
  AUDITED = 'audited'
}
```

---

## 📄 Invoice Domain Models

### Base Invoice Entity
```typescript
export interface Invoice {
  id: InvoiceId;
  invoiceNumber: string;
  type: InvoiceType;
  status: InvoiceStatus;
  customerId?: CustomerId;
  supplierId?: SupplierId;
  issueDate: Date;
  dueDate: Date;
  currency: Currency;
  subtotal: Money;
  taxAmount: Money;
  totalAmount: Money;
  paidAmount: Money;
  outstandingAmount: Money;
  items: InvoiceItem[];
  payments: Payment[];
  attachments: Attachment[];
  notes?: string;
  reference?: string;
  paymentTerms?: string;
  createdBy: UserId;
  approvedBy?: UserId;
  approvedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export enum InvoiceType {
  AP = 'accounts_payable',    // Supplier invoice
  AR = 'accounts_receivable'  // Customer invoice
}

export enum InvoiceStatus {
  DRAFT = 'draft',
  SENT = 'sent',
  APPROVED = 'approved',
  PARTIALLY_PAID = 'partially_paid',
  PAID = 'paid',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled'
}

export interface InvoiceItem {
  id: string;
  description: string;
  quantity: number;
  unitPrice: Money;
  discount?: Money;
  taxRate: number;
  taxAmount: Money;
  totalAmount: Money;
  accountId?: AccountId;
  projectId?: string;
  costCenter?: string;
}
```

### E-Invoice Models
```typescript
export interface EInvoiceData {
  format: EInvoiceFormat;
  version: string;
  data: any; // XML or JSON data
  validation: ValidationResult;
  attachments: Attachment[];
}

export enum EInvoiceFormat {
  ZUGFERD = 'zugferd',
  XRECHNUNG = 'xrechnung',
  PEPPOL = 'peppol',
  FACTUR_X = 'factur-x'
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  compliance: ComplianceCheck[];
}

export interface ValidationError {
  code: string;
  message: string;
  field?: string;
  value?: any;
}

export interface ValidationWarning {
  code: string;
  message: string;
  field?: string;
}

export interface ComplianceCheck {
  standard: string; // 'EN16931', 'XRechnung', etc.
  version: string;
  compliant: boolean;
  score: number; // 0.0 to 1.0
  issues: string[];
}
```

### Payment Models
```typescript
export interface Payment {
  id: string;
  invoiceId: InvoiceId;
  amount: Money;
  paymentDate: Date;
  paymentMethod: PaymentMethod;
  reference?: string;
  bankTransactionId?: string;
  status: PaymentStatus;
  processedBy?: UserId;
  processedAt?: Date;
  notes?: string;
}

export enum PaymentMethod {
  BANK_TRANSFER = 'bank_transfer',
  CREDIT_CARD = 'credit_card',
  DEBIT_CARD = 'debit_card',
  CASH = 'cash',
  CHECK = 'check',
  DIRECT_DEBIT = 'direct_debit'
}

export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSED = 'processed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded'
}
```

---

## 🏦 Bank Reconciliation Models

### Bank Statement
```typescript
export interface BankStatement {
  id: string;
  accountId: AccountId;
  statementNumber: string;
  startDate: Date;
  endDate: Date;
  openingBalance: Money;
  closingBalance: Money;
  transactions: BankTransaction[];
  importedAt: Date;
  importedBy: UserId;
  status: StatementStatus;
}

export enum StatementStatus {
  IMPORTED = 'imported',
  PROCESSING = 'processing',
  RECONCILED = 'reconciled',
  ARCHIVED = 'archived'
}

export interface BankTransaction {
  id: string;
  statementId: string;
  transactionDate: Date;
  valueDate: Date;
  amount: Money;
  description: string;
  reference?: string;
  counterpartyName?: string;
  counterpartyAccount?: string;
  bankTransactionId: string;
  type: TransactionType;
  status: TransactionStatus;
  aiMatches: AIMatch[];
  manualMatch?: ManualMatch;
}

export enum TransactionType {
  DEBIT = 'debit',
  CREDIT = 'credit'
}

export enum TransactionStatus {
  UNMATCHED = 'unmatched',
  AUTO_MATCHED = 'auto_matched',
  MANUAL_MATCHED = 'manual_matched',
  EXCEPTION = 'exception'
}

export interface AIMatch {
  journalEntryId: string;
  confidence: number;
  matchReason: string;
  suggestedBy: 'ai' | 'rule';
  matchedFields: string[];
}

export interface ManualMatch {
  journalEntryId: string;
  matchedBy: UserId;
  matchedAt: Date;
  notes?: string;
}
```

### Reconciliation Report
```typescript
export interface ReconciliationReport {
  id: string;
  accountId: AccountId;
  period: DateRange;
  status: ReconciliationStatus;
  summary: {
    totalTransactions: number;
    matchedTransactions: number;
    unmatchedTransactions: number;
    exceptionTransactions: number;
    matchRate: number;
  };
  details: ReconciliationDetail[];
  generatedAt: Date;
  generatedBy: UserId;
}

export enum ReconciliationStatus {
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  EXCEPTIONS = 'exceptions'
}

export interface ReconciliationDetail {
  transactionId: string;
  type: 'matched' | 'unmatched' | 'exception';
  amount: Money;
  description: string;
  matchInfo?: MatchInfo;
  exceptionReason?: string;
}

export interface MatchInfo {
  journalEntryId: string;
  matchType: 'auto' | 'manual';
  confidence?: number;
  matchedAt: Date;
  matchedBy: UserId;
}
```

---

## 💰 Tax Compliance Models

### Tax Calculation
```typescript
export interface TaxCalculation {
  id: string;
  country: Country;
  transactionId: string;
  transactionType: TransactionType;
  baseAmount: Money;
  taxRate: number;
  taxAmount: Money;
  totalAmount: Money;
  taxCode: string;
  taxCategory: TaxCategory;
  exemptions?: TaxExemption[];
  calculatedAt: Date;
  calculatedBy: 'system' | 'manual';
}

export enum Country {
  DE = 'DE', // Germany
  AT = 'AT', // Austria
  CH = 'CH'  // Switzerland
}

export enum TaxCategory {
  STANDARD = 'standard',
  REDUCED = 'reduced',
  ZERO = 'zero',
  EXEMPT = 'exempt'
}

export interface TaxExemption {
  type: ExemptionType;
  reason: string;
  certificateNumber?: string;
  validFrom: Date;
  validTo?: Date;
}

export enum ExemptionType {
  REVERSE_CHARGE = 'reverse_charge',
  EXPORT = 'export',
  INTRA_COMMUNITY = 'intra_community',
  SMALL_BUSINESS = 'small_business'
}
```

### Tax Report
```typescript
export interface TaxReport {
  id: string;
  country: Country;
  period: TaxPeriod;
  type: TaxReportType;
  status: ReportStatus;
  data: TaxReportData;
  generatedAt: Date;
  generatedBy: UserId;
  submittedAt?: Date;
  submittedBy?: UserId;
  validationResult?: ValidationResult;
}

export enum TaxReportType {
  VAT_RETURN = 'vat_return',
  INTRASTAT = 'intrastat',
  ECSL = 'ecsl' // EU Control System for Liquors
}

export enum ReportStatus {
  DRAFT = 'draft',
  VALIDATED = 'validated',
  SUBMITTED = 'submitted',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected'
}

export interface TaxReportData {
  totalSales: Money;
  totalPurchases: Money;
  taxableAmount: Money;
  taxDue: Money;
  taxDeductible: Money;
  netTax: Money;
  corrections?: TaxCorrection[];
}

export interface TaxCorrection {
  period: string;
  amount: Money;
  reason: string;
}
```

---

## 🔮 Forecasting Models

### Cashflow Forecast
```typescript
export interface CashflowForecast {
  id: string;
  name: string;
  description?: string;
  period: ForecastPeriod;
  scenarios: ForecastScenario[];
  parameters: ForecastParameters;
  generatedAt: Date;
  generatedBy: UserId;
  status: ForecastStatus;
}

export enum ForecastStatus {
  GENERATING = 'generating',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface ForecastScenario {
  id: string;
  name: string;
  type: ScenarioType;
  periods: ForecastPeriodData[];
  confidence: number;
  assumptions: Record<string, any>;
}

export enum ScenarioType {
  OPTIMISTIC = 'optimistic',
  PESSIMISTIC = 'pessimistic',
  REALISTIC = 'realistic',
  CUSTOM = 'custom'
}

export interface ForecastPeriodData {
  period: string; // '2025-10'
  predictedCashflow: Money;
  inflows: Money;
  outflows: Money;
  netCashflow: Money;
  runningBalance: Money;
  confidence: number;
  factors: CashflowFactor[];
}

export interface CashflowFactor {
  type: 'revenue' | 'expense' | 'investment' | 'financing';
  category: string;
  amount: Money;
  description: string;
  confidence: number;
}

export interface ForecastParameters {
  historicalPeriods: number;
  forecastHorizon: number;
  seasonality: boolean;
  trendAnalysis: boolean;
  externalFactors: ExternalFactor[];
  confidenceLevel: number;
}

export interface ExternalFactor {
  name: string;
  type: 'economic' | 'industry' | 'company';
  impact: 'positive' | 'negative' | 'neutral';
  probability: number;
  description: string;
}
```

### P&L Forecast
```typescript
export interface PnLForecast {
  id: string;
  name: string;
  period: ForecastPeriod;
  scenarios: PnLScenario[];
  generatedAt: Date;
  generatedBy: UserId;
}

export interface PnLScenario {
  id: string;
  name: string;
  periods: PnLPeriodData[];
}

export interface PnLPeriodData {
  period: string;
  revenue: Money;
  costOfGoodsSold: Money;
  grossProfit: Money;
  operatingExpenses: Money;
  ebitda: Money;
  depreciation: Money;
  ebit: Money;
  interest: Money;
  tax: Money;
  netProfit: Money;
}
```

---

## 📋 Audit Models

### Audit Event
```typescript
export interface AuditEvent {
  id: string;
  eventType: AuditEventType;
  entityType: string;
  entityId: string;
  userId?: UserId;
  timestamp: Date;
  ipAddress?: string;
  userAgent?: string;
  data: Record<string, any>;
  metadata: AuditMetadata;
  aiExplanation?: string;
  compliance: ComplianceInfo;
}

export enum AuditEventType {
  // Ledger Events
  JOURNAL_CREATED = 'journal_created',
  JOURNAL_POSTED = 'journal_posted',
  JOURNAL_VOIDED = 'journal_voided',
  ACCOUNT_CREATED = 'account_created',
  ACCOUNT_MODIFIED = 'account_modified',

  // Invoice Events
  INVOICE_CREATED = 'invoice_created',
  INVOICE_APPROVED = 'invoice_approved',
  INVOICE_PAID = 'invoice_paid',
  INVOICE_CANCELLED = 'invoice_cancelled',

  // System Events
  USER_LOGIN = 'user_login',
  USER_LOGOUT = 'user_logout',
  PERMISSION_CHANGED = 'permission_changed',
  CONFIGURATION_CHANGED = 'configuration_changed'
}

export interface AuditMetadata {
  correlationId?: string;
  causationId?: string;
  sessionId?: string;
  transactionId?: string;
  source: 'api' | 'ui' | 'system' | 'batch';
}

export interface ComplianceInfo {
  hgb: boolean;
  gobd: boolean;
  gdpr: boolean;
  retention: number; // days
}
```

### Audit Package
```typescript
export interface AuditPackage {
  id: string;
  name: string;
  period: AuditPeriod;
  standards: ComplianceStandard[];
  status: PackageStatus;
  files: AuditFile[];
  summary: AuditSummary;
  generatedAt: Date;
  generatedBy: UserId;
  expiresAt?: Date;
}

export enum ComplianceStandard {
  HGB = 'hgb',
  IFRS = 'ifrs',
  GoBD = 'gobd',
  GDPdU = 'gdpdu'
}

export enum PackageStatus {
  GENERATING = 'generating',
  COMPLETED = 'completed',
  FAILED = 'failed',
  EXPIRED = 'expired'
}

export interface AuditFile {
  id: string;
  name: string;
  type: FileType;
  size: number;
  hash: string;
  downloadUrl: string;
  expiresAt: Date;
}

export enum FileType {
  PDF = 'pdf',
  XML = 'xml',
  CSV = 'csv',
  JSON = 'json'
}

export interface AuditSummary {
  totalEvents: number;
  periodStart: Date;
  periodEnd: Date;
  compliance: Record<ComplianceStandard, ComplianceScore>;
  integrity: IntegrityCheck;
}

export interface ComplianceScore {
  compliant: boolean;
  score: number;
  issues: string[];
}

export interface IntegrityCheck {
  verified: boolean;
  hashAlgorithm: string;
  rootHash: string;
  issues: string[];
}
```

---

## 🔐 Security Models

### User & Authentication
```typescript
export interface User {
  id: UserId;
  email: string;
  firstName: string;
  lastName: string;
  roles: UserRole[];
  permissions: string[];
  tenantId: TenantId;
  isActive: boolean;
  lastLogin?: Date;
  mfaEnabled: boolean;
  mfaSecret?: string;
  passwordHash?: string; // Not exposed in API
  createdAt: Date;
  updatedAt: Date;
}

export enum UserRole {
  ADMIN = 'admin',
  ACCOUNTANT = 'accountant',
  AUDITOR = 'auditor',
  MANAGER = 'manager',
  VIEWER = 'viewer'
}

export interface AuthToken {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
  user: UserProfile;
}

export interface UserProfile {
  id: UserId;
  email: string;
  firstName: string;
  lastName: string;
  roles: UserRole[];
  permissions: string[];
  tenantId: TenantId;
}
```

### Permission System
```typescript
export interface Permission {
  resource: string;
  action: PermissionAction;
  conditions?: Record<string, any>;
}

export enum PermissionAction {
  CREATE = 'create',
  READ = 'read',
  UPDATE = 'update',
  DELETE = 'delete',
  APPROVE = 'approve',
  EXPORT = 'export',
  IMPORT = 'import',
  ADMIN = 'admin'
}

// Resource Types
export type ResourceType =
  | 'ledger'
  | 'invoice'
  | 'payment'
  | 'tax'
  | 'audit'
  | 'forecast'
  | 'user'
  | 'system';
```

---

## 📡 Integration Models

### Webhook Configuration
```typescript
export interface WebhookConfig {
  id: string;
  url: string;
  events: string[];
  secret: string;
  isActive: boolean;
  retryPolicy: RetryPolicy;
  headers?: Record<string, string>;
  createdAt: Date;
  updatedAt: Date;
}

export interface RetryPolicy {
  maxRetries: number;
  backoffMultiplier: number;
  initialDelay: number;
  maxDelay: number;
}

export interface WebhookDelivery {
  id: string;
  webhookId: string;
  eventId: string;
  url: string;
  status: DeliveryStatus;
  attempts: DeliveryAttempt[];
  createdAt: Date;
  completedAt?: Date;
}

export enum DeliveryStatus {
  PENDING = 'pending',
  SUCCESS = 'success',
  FAILED = 'failed',
  RETRYING = 'retrying'
}

export interface DeliveryAttempt {
  attempt: number;
  timestamp: Date;
  statusCode?: number;
  error?: string;
  response?: any;
}
```

### API Response Models
```typescript
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: ApiMeta;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  traceId?: string;
  timestamp: Date;
}

export interface ApiMeta {
  page?: number;
  limit?: number;
  total?: number;
  hasMore?: boolean;
  timestamp: Date;
  requestId: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  meta: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}
```

---

## 🎯 Frontend Integration Types

### React Hook Types
```typescript
// Custom Hook Return Types
export interface UseLedgerDataResult {
  data: TrialBalance | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export interface UseInvoicesResult {
  invoices: Invoice[];
  loading: boolean;
  error: string | null;
  createInvoice: (data: CreateInvoiceData) => Promise<Invoice>;
  updateInvoice: (id: InvoiceId, data: UpdateInvoiceData) => Promise<Invoice>;
  deleteInvoice: (id: InvoiceId) => Promise<void>;
}

export interface UseFinanceEventsResult {
  events: DomainEvent[];
  isConnected: boolean;
  reconnect: () => void;
}
```

### Form Data Types
```typescript
export interface CreateJournalData {
  date: string;
  description: string;
  entries: CreateJournalEntryData[];
}

export interface CreateJournalEntryData {
  accountId: string;
  debit: number;
  credit: number;
  description?: string;
}

export interface CreateInvoiceData {
  type: InvoiceType;
  customerId?: string;
  supplierId?: string;
  items: CreateInvoiceItemData[];
  dueDate: string;
  notes?: string;
}

export interface CreateInvoiceItemData {
  description: string;
  quantity: number;
  unitPrice: number;
  taxRate: number;
}
```

---

## 📊 Monitoring & Metrics Models

### Performance Metrics
```typescript
export interface PerformanceMetrics {
  responseTime: HistogramData;
  throughput: CounterData;
  errorRate: RateData;
  cacheHitRate: GaugeData;
}

export interface HistogramData {
  count: number;
  sum: number;
  buckets: BucketData[];
}

export interface BucketData {
  le: number;
  count: number;
}

export interface CounterData {
  value: number;
  rate: number; // per second
}

export interface RateData {
  value: number;
  period: string;
}

export interface GaugeData {
  value: number;
  timestamp: Date;
}
```

### Health Check Models
```typescript
export interface HealthStatus {
  status: HealthState;
  services: ServiceHealth[];
  version: string;
  uptime: string;
  timestamp: Date;
}

export enum HealthState {
  HEALTHY = 'healthy',
  DEGRADED = 'degraded',
  UNHEALTHY = 'unhealthy'
}

export interface ServiceHealth {
  name: string;
  status: HealthState;
  message?: string;
  details?: Record<string, any>;
  responseTime?: number;
}
```

---

**Diese Datenmodelle bilden die vollständige Grundlage für die Integration der Finance Domain in Frontend-Anwendungen und Middleware-Systeme. Alle Modelle sind typsicher und folgen Domain-Driven Design Prinzipien.**

**Version:** 3.0.0 | **Last Updated:** 2025-09-28 | **Status:** ✅ Production Ready