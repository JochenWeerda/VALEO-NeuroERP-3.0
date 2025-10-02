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

// Invoice Events
export class InvoiceCreatedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'InvoiceCreated';
  readonly aggregateType = 'Invoice';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      invoiceNumber: string;
      amount: number;
      currency: string;
      supplierId: string;
      dueDate: Date;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `invoice-created-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

export class InvoiceProcessedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'InvoiceProcessed';
  readonly aggregateType = 'Invoice';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      invoiceId: string;
      processingDate: Date;
      approvalStatus: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `invoice-processed-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

export class InvoicePaidEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'InvoicePaid';
  readonly aggregateType = 'Invoice';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      invoiceId: string;
      paymentAmount: number;
      paymentDate: Date;
      paymentReference: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `invoice-paid-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

// Journal Entry Events
export class JournalEntryCreatedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'JournalEntryCreated';
  readonly aggregateType = 'JournalEntry';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      entryNumber: string;
      description: string;
      debitAccount: string;
      creditAccount: string;
      amount: number;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `journal-entry-created-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

export class JournalEntryPostedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'JournalEntryPosted';
  readonly aggregateType = 'JournalEntry';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      entryId: string;
      postingDate: Date;
      postedBy: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `journal-entry-posted-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

// Ledger Events
export class LedgerBalanceUpdatedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'LedgerBalanceUpdated';
  readonly aggregateType = 'Ledger';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      accountCode: string;
      newBalance: number;
      previousBalance: number;
      transactionId: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `ledger-balance-updated-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

// Payment Events
export class PaymentProcessedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'PaymentProcessed';
  readonly aggregateType = 'Payment';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      paymentId: string;
      amount: number;
      method: string;
      reference: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `payment-processed-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

// Audit Events
export class AuditTrailCreatedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'AuditTrailCreated';
  readonly aggregateType = 'AuditTrail';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      entityType: string;
      entityId: string;
      action: string;
      userId: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `audit-trail-created-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

// Tax Events
export class TaxCalculatedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'TaxCalculated';
  readonly aggregateType = 'Tax';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      transactionId: string;
      taxType: string;
      amount: number;
      rate: number;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `tax-calculated-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

// Budget Events
export class BudgetExceededEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'BudgetExceeded';
  readonly aggregateType = 'Budget';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      budgetId: string;
      category: string;
      actualAmount: number;
      budgetLimit: number;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `budget-exceeded-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

// Reconciliation Events
export class ReconciliationCompletedEvent implements FinanceDomainEvent {
  readonly id: string;
  readonly type = 'ReconciliationCompleted';
  readonly aggregateType = 'Reconciliation';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      reconciliationId: string;
      accountCode: string;
      reconciledAmount: number;
      discrepancies: number;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.id = `reconciliation-completed-${Date.now()}`;
    this.version = 1;
    this.occurredOn = new Date();
    this.occurredAt = new Date();
    this.data = { payload, metadata };
  }
}

// Export all event types for type checking
export type FinanceDomainEventType = 
  | InvoiceCreatedEvent
  | InvoiceProcessedEvent
  | InvoicePaidEvent
  | JournalEntryCreatedEvent
  | JournalEntryPostedEvent
  | LedgerBalanceUpdatedEvent
  | PaymentProcessedEvent
  | AuditTrailCreatedEvent
  | TaxCalculatedEvent
  | BudgetExceededEvent
  | ReconciliationCompletedEvent;