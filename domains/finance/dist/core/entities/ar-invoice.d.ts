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
export declare const ok: <T>(value: T) => Result<T>;
export declare const err: <T>(error: string | Error) => Result<T>;
export interface DomainEvent {
    type: string;
    occurredAt: Date;
    aggregateId: string;
    payload?: unknown;
    metadata?: Record<string, unknown>;
}
export type ArInvoiceId = string;
export declare const createArInvoiceId: (value: string) => ArInvoiceId;
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
export type ArInvoiceStatus = 'DRAFT' | 'ISSUED' | 'SENT' | 'PARTIALLY_PAID' | 'PAID' | 'OVERDUE' | 'CANCELLED' | 'CREDITED';
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
export declare class ArInvoiceCreatedEvent implements DomainEvent {
    readonly invoice: ArInvoice;
    readonly type = "ArInvoiceCreated";
    readonly aggregateId: ArInvoiceId;
    readonly occurredAt: Date;
    constructor(invoice: ArInvoice);
}
export declare class ArInvoiceIssuedEvent implements DomainEvent {
    readonly invoice: ArInvoice;
    readonly type = "ArInvoiceIssued";
    readonly aggregateId: ArInvoiceId;
    readonly occurredAt: Date;
    constructor(invoice: ArInvoice);
}
export declare class ArInvoicePaymentReceivedEvent implements DomainEvent {
    readonly invoice: ArInvoice;
    readonly payment: {
        amount: number;
        paymentDate: Date;
        paymentMethod: string;
        reference?: string;
    };
    readonly type = "ArInvoicePaymentReceived";
    readonly aggregateId: ArInvoiceId;
    readonly occurredAt: Date;
    constructor(invoice: ArInvoice, payment: {
        amount: number;
        paymentDate: Date;
        paymentMethod: string;
        reference?: string;
    });
}
export declare class ArInvoiceOverdueEvent implements DomainEvent {
    readonly invoice: ArInvoice;
    readonly daysOverdue: number;
    readonly type = "ArInvoiceOverdue";
    readonly aggregateId: ArInvoiceId;
    readonly occurredAt: Date;
    constructor(invoice: ArInvoice, daysOverdue: number);
}
export declare class DunningProcessedEvent implements DomainEvent {
    readonly invoice: ArInvoice;
    readonly dunningLevel: number;
    readonly processedBy: string;
    readonly type = "DunningProcessed";
    readonly aggregateId: ArInvoiceId;
    readonly occurredAt: Date;
    constructor(invoice: ArInvoice, dunningLevel: number, processedBy: string);
}
export declare class ArInvoiceEntity implements ArInvoice, Entity<ArInvoiceId> {
    readonly id: ArInvoiceId;
    equals(other: Entity<ArInvoiceId>): boolean;
    readonly tenantId: string;
    readonly customerId: string;
    readonly invoiceNumber: string;
    readonly issueDate: Date;
    readonly currency: string;
    status: ArInvoiceStatus;
    readonly createdAt: Date;
    updatedAt: Date;
    dueDate: Date;
    lines: ArInvoiceLine[];
    subtotal: number;
    taxAmount: number;
    total: number;
    dunningLevel: number;
    lastDunningDate?: Date;
    nextDunningDate?: Date;
    paidAt?: Date;
    paidAmount: number;
    outstandingAmount: number;
    paymentTerms: string;
    notes?: string;
    metadata: Record<string, any>;
    private constructor();
    static create(command: CreateArInvoiceCommand): Result<ArInvoiceEntity>;
    update(command: UpdateArInvoiceCommand): Result<void>;
    issue(): Result<void>;
    send(): Result<void>;
    recordPayment(command: RecordPaymentCommand): Result<void>;
    processDunning(processedBy: string): Result<void>;
    cancel(reason: string): Result<void>;
    isOverdue(): boolean;
    isPaid(): boolean;
    getDaysOverdue(): number;
    private recalculateTotals;
}
//# sourceMappingURL=ar-invoice.d.ts.map