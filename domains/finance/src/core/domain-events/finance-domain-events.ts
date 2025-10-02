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
  readonly type = 'InvoiceCreated';
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
    this.occurredAt = new Date();
  }
}

export class InvoiceProcessedEvent implements FinanceDomainEvent {
  readonly type = 'InvoiceProcessed';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      invoiceId: string;
      status: string;
      processedBy: string;
      confidence?: number;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

export class InvoicePaidEvent implements FinanceDomainEvent {
  readonly type = 'InvoicePaid';
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
    this.occurredAt = new Date();
  }
}

// Journal Events
export class JournalEntryCreatedEvent implements FinanceDomainEvent {
  readonly type = 'JournalEntryCreated';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
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
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

export class JournalEntryPostedEvent implements FinanceDomainEvent {
  readonly type = 'JournalEntryPosted';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      journalId: string;
      postedBy: string;
      postedAt: Date;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

// Ledger Events
export class LedgerBalanceUpdatedEvent implements FinanceDomainEvent {
  readonly type = 'LedgerBalanceUpdated';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      accountId: string;
      previousBalance: number;
      newBalance: number;
      transactionId: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

// Payment Events
export class PaymentProcessedEvent implements FinanceDomainEvent {
  readonly type = 'PaymentProcessed';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      paymentId: string;
      amount: number;
      currency: string;
      paymentMethod: string;
      status: string;
      reference?: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

// Audit Events
export class AuditTrailCreatedEvent implements FinanceDomainEvent {
  readonly type = 'AuditTrailCreated';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      entityType: string;
      entityId: string;
      action: string;
      userId: string;
      changes?: Record<string, any>;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

// Tax Events
export class TaxCalculatedEvent implements FinanceDomainEvent {
  readonly type = 'TaxCalculated';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      documentId: string;
      documentType: string;
      taxAmount: number;
      taxRate: number;
      taxCode: string;
      netAmount: number;
      grossAmount: number;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

// Budget Events
export class BudgetExceededEvent implements FinanceDomainEvent {
  readonly type = 'BudgetExceeded';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      budgetId: string;
      categoryId: string;
      budgetAmount: number;
      actualAmount: number;
      exceedAmount: number;
      period: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

// Reconciliation Events
export class ReconciliationCompletedEvent implements FinanceDomainEvent {
  readonly type = 'ReconciliationCompleted';
  readonly occurredAt: Date;
  
  constructor(
    public readonly aggregateId: string,
    public readonly aggregateVersion: number,
    public readonly payload: {
      accountId: string;
      reconciliationId: string;
      period: string;
      reconciledAmount: number;
      unreconciledItems: number;
      completedBy: string;
    },
    public readonly tenantId: string,
    public readonly metadata: Record<string, unknown>
  ) {
    this.occurredAt = new Date();
  }
}

// Export all event types for easy consumption
export type AllFinanceDomainEvents = 
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
