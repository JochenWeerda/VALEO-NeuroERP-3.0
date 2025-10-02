/**
 * VALEO NeuroERP 3.0 - Finance Domain Events
 *
 * Domain events for the Finance domain following Domain-Driven Design principles.
 */
import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';
export interface FinanceDomainEvent extends DomainEvent {
    aggregateId: string;
    aggregateVersion: number;
    tenantId: string;
}
export declare class InvoiceCreatedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        invoiceNumber: string;
        amount: number;
        currency: string;
        supplierId: string;
        dueDate: Date;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "InvoiceCreated";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        invoiceNumber: string;
        amount: number;
        currency: string;
        supplierId: string;
        dueDate: Date;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class InvoiceProcessedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        invoiceId: string;
        status: string;
        processedBy: string;
        confidence?: number;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "InvoiceProcessed";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        invoiceId: string;
        status: string;
        processedBy: string;
        confidence?: number;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class InvoicePaidEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        invoiceId: string;
        paymentAmount: number;
        paymentDate: Date;
        paymentReference: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "InvoicePaid";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        invoiceId: string;
        paymentAmount: number;
        paymentDate: Date;
        paymentReference: string;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class JournalEntryCreatedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        journalId: string;
        entryDate: Date;
        description: string;
        totalAmount: number;
        lineItems: Array<{
            accountId: string;
            debitAmount?: number;
            creditAmount?: number;
            description?: string;
        }>;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "JournalEntryCreated";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        journalId: string;
        entryDate: Date;
        description: string;
        totalAmount: number;
        lineItems: Array<{
            accountId: string;
            debitAmount?: number;
            creditAmount?: number;
            description?: string;
        }>;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class JournalEntryPostedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        journalId: string;
        postedBy: string;
        postedAt: Date;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "JournalEntryPosted";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        journalId: string;
        postedBy: string;
        postedAt: Date;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class LedgerBalanceUpdatedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        accountId: string;
        previousBalance: number;
        newBalance: number;
        transactionId: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "LedgerBalanceUpdated";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        accountId: string;
        previousBalance: number;
        newBalance: number;
        transactionId: string;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class PaymentProcessedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        paymentId: string;
        amount: number;
        currency: string;
        paymentMethod: string;
        status: string;
        reference?: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "PaymentProcessed";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        paymentId: string;
        amount: number;
        currency: string;
        paymentMethod: string;
        status: string;
        reference?: string;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class AuditTrailCreatedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        entityType: string;
        entityId: string;
        action: string;
        userId: string;
        changes?: Record<string, any>;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "AuditTrailCreated";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        entityType: string;
        entityId: string;
        action: string;
        userId: string;
        changes?: Record<string, any>;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class TaxCalculatedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        documentId: string;
        documentType: string;
        taxAmount: number;
        taxRate: number;
        taxCode: string;
        netAmount: number;
        grossAmount: number;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "TaxCalculated";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        documentId: string;
        documentType: string;
        taxAmount: number;
        taxRate: number;
        taxCode: string;
        netAmount: number;
        grossAmount: number;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class BudgetExceededEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        budgetId: string;
        categoryId: string;
        budgetAmount: number;
        actualAmount: number;
        exceedAmount: number;
        period: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "BudgetExceeded";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        budgetId: string;
        categoryId: string;
        budgetAmount: number;
        actualAmount: number;
        exceedAmount: number;
        period: string;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class ReconciliationCompletedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        accountId: string;
        reconciliationId: string;
        period: string;
        reconciledAmount: number;
        unreconciledItems: number;
        completedBy: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly type = "ReconciliationCompleted";
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        accountId: string;
        reconciliationId: string;
        period: string;
        reconciledAmount: number;
        unreconciledItems: number;
        completedBy: string;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export type AllFinanceDomainEvents = InvoiceCreatedEvent | InvoiceProcessedEvent | InvoicePaidEvent | JournalEntryCreatedEvent | JournalEntryPostedEvent | LedgerBalanceUpdatedEvent | PaymentProcessedEvent | AuditTrailCreatedEvent | TaxCalculatedEvent | BudgetExceededEvent | ReconciliationCompletedEvent;
//# sourceMappingURL=finance-domain-events.d.ts.map