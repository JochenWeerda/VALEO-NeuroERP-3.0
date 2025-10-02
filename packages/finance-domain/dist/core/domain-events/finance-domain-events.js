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
        this.aggregateType = 'Invoice';
        this.id = `invoice-created-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'Invoice';
        this.id = `invoice-processed-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'Invoice';
        this.id = `invoice-paid-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
    }
}
exports.InvoicePaidEvent = InvoicePaidEvent;
// Journal Entry Events
class JournalEntryCreatedEvent {
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.type = 'JournalEntryCreated';
        this.aggregateType = 'JournalEntry';
        this.id = `journal-entry-created-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'JournalEntry';
        this.id = `journal-entry-posted-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'Ledger';
        this.id = `ledger-balance-updated-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'Payment';
        this.id = `payment-processed-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'AuditTrail';
        this.id = `audit-trail-created-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'Tax';
        this.id = `tax-calculated-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'Budget';
        this.id = `budget-exceeded-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
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
        this.aggregateType = 'Reconciliation';
        this.id = `reconciliation-completed-${Date.now()}`;
        this.version = 1;
        this.occurredOn = new Date();
        this.occurredAt = new Date();
        this.data = { payload, metadata };
    }
}
exports.ReconciliationCompletedEvent = ReconciliationCompletedEvent;
//# sourceMappingURL=finance-domain-events.js.map