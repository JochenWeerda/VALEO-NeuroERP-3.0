/**
 * VALEO NeuroERP 3.0 - AR Invoice Entity
 *
 * Domain entity for Accounts Receivable (AR) invoices
 * Handles outgoing invoices, dunning process, and payment tracking
 */

export interface Entity<T> {
  readonly id: T;
  equals(other: Entity<T>): boolean;
}

export interface Result<T> {
  isSuccess: boolean;
  isFailure: boolean;
  getValue(): T;
  error?: string;
}

export const ok = <T>(value: T): Result<T> => ({
  isSuccess: true,
  isFailure: false,
  getValue: () => value
});

export const err = <T>(error: string | Error): Result<T> => ({
  isSuccess: false,
  isFailure: true,
  getValue: () => { throw new Error(typeof error === 'string' ? error : error.message); },
  error: typeof error === 'string' ? error : error.message
});

export interface DomainEvent {
  type: string;
  occurredAt: Date;
  aggregateId: string;
  payload?: unknown;
  metadata?: Record<string, unknown>;
}

// ===== VALUE OBJECTS =====

export type ArInvoiceId = string;

export const createArInvoiceId = (value: string): ArInvoiceId => value;

// ===== INTERFACES =====

export interface ArInvoice {
  readonly id: ArInvoiceId;
  readonly tenantId: string;
  readonly customerId: string;
  readonly invoiceNumber: string;
  readonly issueDate: Date;
  readonly dueDate: Date;
  readonly currency: string;
  readonly lines: ArInvoiceLine[];
  readonly subtotal: number;
  readonly taxAmount: number;
  readonly total: number;
  status: ArInvoiceStatus;
  readonly dunningLevel: number;
  readonly lastDunningDate?: Date;
  readonly nextDunningDate?: Date;
  readonly paidAt?: Date;
  readonly paidAmount: number;
  readonly outstandingAmount: number;
  readonly paymentTerms: string;
  readonly notes?: string;
  readonly metadata: Record<string, any>;
  readonly createdAt: Date;
  readonly updatedAt: Date;

  // Business logic interface methods
  isOverdue(): boolean;
  isPaid(): boolean;
  getDaysOverdue(): number;
}

export interface ArInvoiceLine {
  readonly id: string;
  readonly description: string;
  readonly quantity: number;
  readonly unitPrice: number;
  readonly taxRate: number;
  readonly taxCode: string;
  readonly total: number;
  readonly metadata: Record<string, any>;
}

export type ArInvoiceStatus =
  | 'DRAFT'
  | 'ISSUED'
  | 'SENT'
  | 'PARTIALLY_PAID'
  | 'PAID'
  | 'OVERDUE'
  | 'CANCELLED'
  | 'CREDITED';

export interface CreateArInvoiceCommand {
  readonly tenantId: string;
  readonly customerId: string;
  readonly invoiceNumber: string;
  readonly issueDate: Date;
  readonly dueDate: Date;
  readonly currency: string;
  readonly lines: Omit<ArInvoiceLine, 'id' | 'total'>[];
  readonly paymentTerms: string;
  readonly notes?: string;
  readonly metadata?: Record<string, any>;
}

export interface UpdateArInvoiceCommand {
  readonly id: ArInvoiceId;
  readonly lines?: ArInvoiceLine[];
  readonly dueDate?: Date;
  readonly paymentTerms?: string;
  readonly notes?: string;
  readonly metadata?: Record<string, any>;
}

export interface RecordPaymentCommand {
  readonly id: ArInvoiceId;
  readonly amount: number;
  readonly paymentDate: Date;
  readonly paymentMethod: string;
  readonly reference?: string;
  readonly metadata?: Record<string, any>;
}

export interface ProcessDunningCommand {
  readonly tenantId: string;
  readonly customerId?: string;
  readonly invoiceIds?: ArInvoiceId[];
  readonly dunningLevel: number;
  readonly processedBy: string;
}

// ===== DOMAIN EVENTS =====

export class ArInvoiceCreatedEvent implements DomainEvent {
  readonly type = 'ArInvoiceCreated';
  readonly aggregateId: ArInvoiceId;
  readonly occurredAt: Date;

  constructor(
    public readonly invoice: ArInvoice
  ) {
    this.aggregateId = invoice.id;
    this.occurredAt = new Date();
  }
}

export class ArInvoiceIssuedEvent implements DomainEvent {
  readonly type = 'ArInvoiceIssued';
  readonly aggregateId: ArInvoiceId;
  readonly occurredAt: Date;

  constructor(
    public readonly invoice: ArInvoice
  ) {
    this.aggregateId = invoice.id;
    this.occurredAt = new Date();
  }
}

export class ArInvoicePaymentReceivedEvent implements DomainEvent {
  readonly type = 'ArInvoicePaymentReceived';
  readonly aggregateId: ArInvoiceId;
  readonly occurredAt: Date;

  constructor(
    public readonly invoice: ArInvoice,
    public readonly payment: {
      amount: number;
      paymentDate: Date;
      paymentMethod: string;
      reference?: string;
    }
  ) {
    this.aggregateId = invoice.id;
    this.occurredAt = new Date();
  }
}

export class ArInvoiceOverdueEvent implements DomainEvent {
  readonly type = 'ArInvoiceOverdue';
  readonly aggregateId: ArInvoiceId;
  readonly occurredAt: Date;

  constructor(
    public readonly invoice: ArInvoice,
    public readonly daysOverdue: number
  ) {
    this.aggregateId = invoice.id;
    this.occurredAt = new Date();
  }
}

export class DunningProcessedEvent implements DomainEvent {
  readonly type = 'DunningProcessed';
  readonly aggregateId: ArInvoiceId;
  readonly occurredAt: Date;

  constructor(
    public readonly invoice: ArInvoice,
    public readonly dunningLevel: number,
    public readonly processedBy: string
  ) {
    this.aggregateId = invoice.id;
    this.occurredAt = new Date();
  }
}

// ===== ENTITY =====

export class ArInvoiceEntity implements ArInvoice, Entity<ArInvoiceId> {
  public readonly id: ArInvoiceId;

  equals(other: Entity<ArInvoiceId>): boolean {
    return this.id === other.id;
  }
  public readonly tenantId: string;
  public readonly customerId: string;
  public readonly invoiceNumber: string;
  public readonly issueDate: Date;
  public readonly currency: string;
  public status: ArInvoiceStatus;
  public readonly createdAt: Date;
  public updatedAt: Date;

  // Mutable fields
  public dueDate: Date;
  public lines: ArInvoiceLine[];
  public subtotal: number;
  public taxAmount: number;
  public total: number;
  public dunningLevel: number;
  public lastDunningDate?: Date;
  public nextDunningDate?: Date;
  public paidAt?: Date;
  public paidAmount: number;
  public outstandingAmount: number;
  public paymentTerms: string;
  public notes?: string;
  public metadata: Record<string, any>;

  private constructor(
    id: ArInvoiceId,
    tenantId: string,
    customerId: string,
    invoiceNumber: string,
    issueDate: Date,
    dueDate: Date,
    currency: string,
    lines: ArInvoiceLine[],
    subtotal: number,
    taxAmount: number,
    total: number,
    paymentTerms: string,
    notes?: string,
    metadata?: Record<string, any>
  ) {
    this.id = id;
    this.tenantId = tenantId;
    this.customerId = customerId;
    this.invoiceNumber = invoiceNumber;
    this.issueDate = issueDate;
    this.dueDate = dueDate;
    this.currency = currency;
    this.lines = lines;
    this.subtotal = subtotal;
    this.taxAmount = taxAmount;
    this.total = total;
    this.status = 'DRAFT';
    this.dunningLevel = 0;
    this.paidAmount = 0;
    this.outstandingAmount = total;
    this.paymentTerms = paymentTerms;
    if (notes !== undefined) {
      this.notes = notes;
    }
    this.metadata = metadata || {};
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  static create(command: CreateArInvoiceCommand): Result<ArInvoiceEntity> {
    // Validation
    if (!command.tenantId || !command.customerId || !command.invoiceNumber) {
      return err(new Error('Tenant ID, customer ID, and invoice number are required'));
    }

    if (command.lines.length === 0) {
      return err(new Error('Invoice must have at least one line'));
    }

    if (command.dueDate <= command.issueDate) {
      return err(new Error('Due date must be after issue date'));
    }

    // Calculate totals
    const lines: ArInvoiceLine[] = command.lines.map((line, index) => ({
      id: `line-${index + 1}`,
      description: line.description,
      quantity: line.quantity,
      unitPrice: line.unitPrice,
      taxRate: line.taxRate,
      taxCode: line.taxCode,
      total: line.quantity * line.unitPrice,
      metadata: line.metadata || {}
    }));

    const subtotal = lines.reduce((sum, line) => sum + line.total, 0);
    const taxAmount = lines.reduce((sum, line) => sum + (line.total * line.taxRate / 100), 0);
    const total = subtotal + taxAmount;

    const id = createArInvoiceId(`ar-inv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);

    return ok(new ArInvoiceEntity(
      id,
      command.tenantId,
      command.customerId,
      command.invoiceNumber,
      command.issueDate,
      command.dueDate,
      command.currency,
      lines,
      subtotal,
      taxAmount,
      total,
      command.paymentTerms,
      command.notes,
      command.metadata
    ));
  }

  update(command: UpdateArInvoiceCommand): Result<void> {
    if (this.status !== 'DRAFT') {
      return err(new Error('Can only update draft invoices'));
    }

    if (command.lines) {
      this.lines = command.lines;
      this.recalculateTotals();
    }

    if (command.dueDate) {
      if (command.dueDate <= this.issueDate) {
        return err(new Error('Due date must be after issue date'));
      }
      this.dueDate = command.dueDate;
    }

    if (command.paymentTerms) {
      this.paymentTerms = command.paymentTerms;
    }

    if (command.notes !== undefined) {
      this.notes = command.notes;
    }

    if (command.metadata) {
      this.metadata = { ...this.metadata, ...command.metadata };
    }

    this.updatedAt = new Date();
    return ok(undefined);
  }

  issue(): Result<void> {
    if (this.status !== 'DRAFT') {
      return err(new Error('Can only issue draft invoices'));
    }

    this.status = 'ISSUED';
    this.updatedAt = new Date();
    return ok(undefined);
  }

  send(): Result<void> {
    if (this.status !== 'ISSUED') {
      return err(new Error('Can only send issued invoices'));
    }

    this.status = 'SENT';
    this.updatedAt = new Date();
    return ok(undefined);
  }

  recordPayment(command: RecordPaymentCommand): Result<void> {
    if (command.amount <= 0) {
      return err(new Error('Payment amount must be positive'));
    }

    if (command.amount > this.outstandingAmount) {
      return err(new Error('Payment amount cannot exceed outstanding amount'));
    }

    this.paidAmount += command.amount;
    this.outstandingAmount -= command.amount;

    if (this.outstandingAmount === 0) {
      this.status = 'PAID';
      this.paidAt = command.paymentDate;
    } else {
      this.status = 'PARTIALLY_PAID';
    }

    this.metadata.lastPayment = {
      amount: command.amount,
      paymentDate: command.paymentDate,
      paymentMethod: command.paymentMethod,
      reference: command.reference,
      metadata: command.metadata
    };

    this.updatedAt = new Date();
    return ok(undefined);
  }

  processDunning(processedBy: string): Result<void> {
    if (this.status === 'PAID' || this.status === 'CANCELLED') {
      return err(new Error('Cannot process dunning for paid or cancelled invoices'));
    }

    const now = new Date();
    const daysOverdue = Math.floor((now.getTime() - this.dueDate.getTime()) / (1000 * 60 * 60 * 24));

    if (daysOverdue < 0) {
      return err(new Error('Invoice is not overdue'));
    }

    // Determine dunning level based on days overdue
    let newDunningLevel = 0;
    if (daysOverdue >= 60) newDunningLevel = 3; // Final notice
    else if (daysOverdue >= 30) newDunningLevel = 2; // Second notice
    else if (daysOverdue >= 14) newDunningLevel = 1; // First notice

    if (newDunningLevel <= this.dunningLevel) {
      return err(new Error('Invoice already has equal or higher dunning level'));
    }

    this.dunningLevel = newDunningLevel;
    this.lastDunningDate = now;

    // Calculate next dunning date (escalating intervals)
    const nextDunningDays = newDunningLevel === 1 ? 14 : newDunningLevel === 2 ? 21 : 30;
    this.nextDunningDate = new Date(now.getTime() + (nextDunningDays * 24 * 60 * 60 * 1000));

    // Update status if necessary
    if (this.status === 'SENT' && daysOverdue >= 1) {
      this.status = 'OVERDUE';
    }

    this.metadata.lastDunning = {
      level: newDunningLevel,
      processedBy,
      processedAt: now
    };

    this.updatedAt = new Date();
    return ok(undefined);
  }

  cancel(reason: string): Result<void> {
    if (this.status === 'PAID') {
      return err(new Error('Cannot cancel paid invoices'));
    }

    this.status = 'CANCELLED';
    this.metadata.cancellation = {
      reason,
      cancelledAt: new Date()
    };
    this.updatedAt = new Date();
    return ok(undefined);
  }

  // Business logic methods
  isOverdue(): boolean {
    return this.status === 'OVERDUE' || (this.dueDate < new Date() && this.status === 'SENT');
  }

  isPaid(): boolean {
    return this.status === 'PAID';
  }

  getDaysOverdue(): number {
    if (!this.isOverdue()) return 0;
    return Math.floor((new Date().getTime() - this.dueDate.getTime()) / (1000 * 60 * 60 * 24));
  }


  private recalculateTotals(): void {
    this.subtotal = this.lines.reduce((sum, line) => sum + line.total, 0);
    this.taxAmount = this.lines.reduce((sum, line) => sum + (line.total * line.taxRate / 100), 0);
    this.total = this.subtotal + this.taxAmount;

    // Adjust outstanding amount if total changed
    if (this.paidAmount > 0) {
      this.outstandingAmount = Math.max(0, this.total - this.paidAmount);
      if (this.outstandingAmount === 0) {
        this.status = 'PAID';
        this.paidAt = new Date();
      } else {
        this.status = 'PARTIALLY_PAID';
      }
    } else {
      this.outstandingAmount = this.total;
    }
  }
}