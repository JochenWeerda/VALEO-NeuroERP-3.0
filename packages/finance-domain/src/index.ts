// ===== VALEO NeuroERP 3.0 - FINANCE DOMAIN PACKAGE =====
// Central exports for all finance domain functionality

// Core entities and value objects - specific exports to avoid conflicts
export { APInvoice, InvoiceId, APInvoiceEntity } from './core/entities/ap-invoice';
export { ArInvoice, ArInvoiceId, ArInvoiceStatus, ArInvoiceEntity } from './core/entities/ar-invoice';
export { Journal, JournalId, Account, AccountId, JournalEntry, EntryId } from './core/entities/ledger';

// Domain events
export * from './core/domain-events/finance-domain-events';

// Application services
export * from './application/services/ai-bookkeeper-service';
export * from './application/services/finance-domain-service';
export * from './application/services/ledger-service';

// Infrastructure
export * from './infrastructure/cache/cache-service';
export * from './infrastructure/event-bus/event-bus';
export * from './infrastructure/observability/metrics-service';
export * from './infrastructure/repositories/einvoice-repository';
// export * from './infrastructure/repositories/postgres-ledger-repository'; // Commented out due to PostgresConnection conflict
export * from './infrastructure/security/auth-service';

// Presentation
export * from './presentation/controllers/finance-api-controller';

// Services - specific exports to avoid conflicts
export { ArInvoiceApplicationService } from './services/ar-invoice-service';
export { AuditAssistApplicationService } from './services/audit-assist-service';
export { ForecastingApplicationService } from './services/forecasting-service';
export { TaxComplianceApplicationService } from './services/tax-compliance-service';

// Bootstrap
export * from './bootstrap';