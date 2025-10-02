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
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'InvoiceCreated';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.InvoiceCreatedEvent = InvoiceCreatedEvent;
class InvoiceProcessedEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'InvoiceProcessed';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.InvoiceProcessedEvent = InvoiceProcessedEvent;
class InvoicePaidEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'InvoicePaid';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.InvoicePaidEvent = InvoicePaidEvent;
// Journal Events
class JournalEntryCreatedEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'JournalEntryCreated';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.JournalEntryCreatedEvent = JournalEntryCreatedEvent;
class JournalEntryPostedEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'JournalEntryPosted';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.JournalEntryPostedEvent = JournalEntryPostedEvent;
// Ledger Events
class LedgerBalanceUpdatedEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'LedgerBalanceUpdated';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.LedgerBalanceUpdatedEvent = LedgerBalanceUpdatedEvent;
// Payment Events
class PaymentProcessedEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'PaymentProcessed';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.PaymentProcessedEvent = PaymentProcessedEvent;
// Audit Events
class AuditTrailCreatedEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'AuditTrailCreated';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.AuditTrailCreatedEvent = AuditTrailCreatedEvent;
// Tax Events
class TaxCalculatedEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'TaxCalculated';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.TaxCalculatedEvent = TaxCalculatedEvent;
// Budget Events
class BudgetExceededEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'BudgetExceeded';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.BudgetExceededEvent = BudgetExceededEvent;
// Reconciliation Events
class ReconciliationCompletedEvent {
    aggregateId;
    aggregateVersion;
    payload;
    tenantId;
    metadata;
    type = 'ReconciliationCompleted';
    occurredAt;
    constructor(aggregateId, aggregateVersion, payload, tenantId, metadata) {
        this.aggregateId = aggregateId;
        this.aggregateVersion = aggregateVersion;
        this.payload = payload;
        this.tenantId = tenantId;
        this.metadata = metadata;
        this.occurredAt = new Date();
    }
}
exports.ReconciliationCompletedEvent = ReconciliationCompletedEvent;
