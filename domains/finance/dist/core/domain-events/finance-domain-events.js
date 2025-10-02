"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain Events
 *
 * Domain events for the Finance domain following Domain-Driven Design principles.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReconciliationCompletedEvent = exports.BudgetExceededEvent = exports.TaxCalculatedEvent = exports.AuditTrailCreatedEvent = exports.PaymentProcessedEvent = exports.LedgerBalanceUpdatedEvent = exports.JournalEntryPostedEvent = exports.JournalEntryCreatedEvent = exports.InvoicePaidEvent = exports.InvoiceProcessedEvent = exports.InvoiceCreatedEvent = void 0;
// Invoice Events
class InvoiceCreatedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'InvoiceCreated';
        this.occurredAt = new Date();
    }
}
exports.InvoiceCreatedEvent = InvoiceCreatedEvent;
class InvoiceProcessedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'InvoiceProcessed';
        this.occurredAt = new Date();
    }
}
exports.InvoiceProcessedEvent = InvoiceProcessedEvent;
class InvoicePaidEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'InvoicePaid';
        this.occurredAt = new Date();
    }
}
exports.InvoicePaidEvent = InvoicePaidEvent;
// Journal Events
class JournalEntryCreatedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'JournalEntryCreated';
        this.occurredAt = new Date();
    }
}
exports.JournalEntryCreatedEvent = JournalEntryCreatedEvent;
class JournalEntryPostedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'JournalEntryPosted';
        this.occurredAt = new Date();
    }
}
exports.JournalEntryPostedEvent = JournalEntryPostedEvent;
// Ledger Events
class LedgerBalanceUpdatedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'LedgerBalanceUpdated';
        this.occurredAt = new Date();
    }
}
exports.LedgerBalanceUpdatedEvent = LedgerBalanceUpdatedEvent;
// Payment Events
class PaymentProcessedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'PaymentProcessed';
        this.occurredAt = new Date();
    }
}
exports.PaymentProcessedEvent = PaymentProcessedEvent;
// Audit Events
class AuditTrailCreatedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'AuditTrailCreated';
        this.occurredAt = new Date();
    }
}
exports.AuditTrailCreatedEvent = AuditTrailCreatedEvent;
// Tax Events
class TaxCalculatedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'TaxCalculated';
        this.occurredAt = new Date();
    }
}
exports.TaxCalculatedEvent = TaxCalculatedEvent;
// Budget Events
class BudgetExceededEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'BudgetExceeded';
        this.occurredAt = new Date();
    }
}
exports.BudgetExceededEvent = BudgetExceededEvent;
// Reconciliation Events
class ReconciliationCompletedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'ReconciliationCompleted';
        this.occurredAt = new Date();
    }
}
exports.ReconciliationCompletedEvent = ReconciliationCompletedEvent;
//# sourceMappingURL=finance-domain-events.js.map