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
    readonly id: string;
    readonly type = "InvoiceCreated";
    readonly aggregateType = "Invoice";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
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
        processingDate: Date;
        approvalStatus: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "InvoiceProcessed";
    readonly aggregateType = "Invoice";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        invoiceId: string;
        processingDate: Date;
        approvalStatus: string;
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
    readonly id: string;
    readonly type = "InvoicePaid";
    readonly aggregateType = "Invoice";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
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
        entryNumber: string;
        description: string;
        debitAccount: string;
        creditAccount: string;
        amount: number;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "JournalEntryCreated";
    readonly aggregateType = "JournalEntry";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        entryNumber: string;
        description: string;
        debitAccount: string;
        creditAccount: string;
        amount: number;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class JournalEntryPostedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        entryId: string;
        postingDate: Date;
        postedBy: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "JournalEntryPosted";
    readonly aggregateType = "JournalEntry";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        entryId: string;
        postingDate: Date;
        postedBy: string;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class LedgerBalanceUpdatedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        accountCode: string;
        newBalance: number;
        previousBalance: number;
        transactionId: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "LedgerBalanceUpdated";
    readonly aggregateType = "Ledger";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        accountCode: string;
        newBalance: number;
        previousBalance: number;
        transactionId: string;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class PaymentProcessedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        paymentId: string;
        amount: number;
        method: string;
        reference: string;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "PaymentProcessed";
    readonly aggregateType = "Payment";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        paymentId: string;
        amount: number;
        method: string;
        reference: string;
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
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "AuditTrailCreated";
    readonly aggregateType = "AuditTrail";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        entityType: string;
        entityId: string;
        action: string;
        userId: string;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class TaxCalculatedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        transactionId: string;
        taxType: string;
        amount: number;
        rate: number;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "TaxCalculated";
    readonly aggregateType = "Tax";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        transactionId: string;
        taxType: string;
        amount: number;
        rate: number;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class BudgetExceededEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        budgetId: string;
        category: string;
        actualAmount: number;
        budgetLimit: number;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "BudgetExceeded";
    readonly aggregateType = "Budget";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        budgetId: string;
        category: string;
        actualAmount: number;
        budgetLimit: number;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export declare class ReconciliationCompletedEvent implements FinanceDomainEvent {
    readonly aggregateId: string;
    readonly aggregateVersion: number;
    readonly payload: {
        reconciliationId: string;
        accountCode: string;
        reconciledAmount: number;
        discrepancies: number;
    };
    readonly tenantId: string;
    readonly metadata: Record<string, unknown>;
    readonly id: string;
    readonly type = "ReconciliationCompleted";
    readonly aggregateType = "Reconciliation";
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
    constructor(aggregateId: string, aggregateVersion: number, payload: {
        reconciliationId: string;
        accountCode: string;
        reconciledAmount: number;
        discrepancies: number;
    }, tenantId: string, metadata: Record<string, unknown>);
}
export type FinanceDomainEventType = InvoiceCreatedEvent | InvoiceProcessedEvent | InvoicePaidEvent | JournalEntryCreatedEvent | JournalEntryPostedEvent | LedgerBalanceUpdatedEvent | PaymentProcessedEvent | AuditTrailCreatedEvent | TaxCalculatedEvent | BudgetExceededEvent | ReconciliationCompletedEvent;
//# sourceMappingURL=finance-domain-events.d.ts.map