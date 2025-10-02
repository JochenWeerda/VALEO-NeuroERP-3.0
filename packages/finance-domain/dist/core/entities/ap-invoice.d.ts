/**
 * VALEO NeuroERP 3.0 - Finance Domain - AP Invoice Entities
 *
 * Accounts Payable entities with OCR processing and AI booking
 * Following Domain-Driven Design and Event Sourcing patterns
 */
export interface DomainEvent {
    type: string;
    occurredAt: Date;
    aggregateId: string;
    payload?: unknown;
    metadata?: Record<string, unknown>;
}
export type InvoiceId = string;
export type SupplierId = string;
export type DocumentId = string;
export type TenantId = string;
/**
 * AP Invoice Entity
 * Represents an accounts payable invoice with OCR data and AI processing
 */
export interface APInvoice {
    readonly id: InvoiceId;
    readonly tenantId: TenantId;
    readonly supplierId: SupplierId;
    readonly invoiceNumber: string;
    readonly issueDate: Date;
    readonly dueDate: Date;
    readonly status: 'DRAFT' | 'PROCESSING' | 'APPROVED' | 'PAID' | 'CANCELLED';
    readonly currency: string;
    readonly subtotal: number;
    readonly taxAmount: number;
    readonly totalAmount: number;
    readonly taxRate: number;
    readonly paymentTerms: string;
    readonly lines: APInvoiceLine[];
    readonly documentRef: string;
    readonly ocrData?: OCRData;
    readonly aiBooking?: AIBookingProposal;
    readonly approvedAt?: Date;
    readonly approvedBy?: string;
    readonly paidAt?: Date;
    readonly paidBy?: string;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
/**
 * AP Invoice Line Item
 * Individual line items from the invoice
 */
export interface APInvoiceLine {
    readonly id: string;
    readonly invoiceId: InvoiceId;
    readonly lineNumber: number;
    readonly description: string;
    readonly quantity: number;
    readonly unitPrice: number;
    readonly lineTotal: number;
    readonly taxRate: number;
    readonly taxAmount: number;
    readonly accountId?: string;
    readonly costCenter?: string;
    readonly ocrConfidence: number;
    readonly metadata: Record<string, any>;
}
/**
 * OCR Processing Data
 * Data extracted from document by OCR service
 */
export interface OCRData {
    readonly documentId: DocumentId;
    readonly extractedAt: Date;
    readonly confidence: number;
    readonly fields: OCRField[];
    readonly rawText: string;
    readonly processingMetadata: Record<string, any>;
}
/**
 * Individual OCR Field
 */
export interface OCRField {
    readonly fieldName: string;
    readonly value: string;
    readonly confidence: number;
    readonly bbox?: number[];
    readonly pageNumber: number;
}
/**
 * AI Booking Proposal
 * Suggested accounting treatment by AI
 */
export interface AIBookingProposal {
    readonly proposalId: string;
    readonly createdAt: Date;
    readonly confidence: number;
    readonly suggestedEntries: JournalEntryProposal[];
    readonly explanation: string;
    readonly rules: string[];
    readonly features: Record<string, number>;
    readonly acceptedAt?: Date;
    readonly acceptedBy?: string;
    readonly rejectedAt?: Date;
    readonly rejectedBy?: string;
    readonly rejectionReason?: string;
}
/**
 * Journal Entry Proposal from AI
 */
export interface JournalEntryProposal {
    readonly accountId: string;
    readonly accountNumber: string;
    readonly accountName: string;
    readonly debit: number;
    readonly credit: number;
    readonly description: string;
    readonly taxCode?: string;
    readonly costCenter?: string;
    readonly confidence: number;
    readonly reasoning: string;
}
export interface CreateAPInvoiceCommand {
    tenantId: TenantId;
    supplierId: SupplierId;
    invoiceNumber: string;
    issueDate: Date;
    dueDate: Date;
    currency: string;
    subtotal: number;
    taxAmount: number;
    totalAmount: number;
    taxRate: number;
    paymentTerms: string;
    lines: Omit<APInvoiceLine, 'id' | 'invoiceId' | 'metadata' | 'ocrConfidence'>[];
    documentRef: string;
    ocrData?: OCRData;
    metadata?: Record<string, any>;
}
export interface ApproveAPInvoiceCommand {
    invoiceId: InvoiceId;
    approvedBy: string;
    approvedEntries: JournalEntryProposal[];
}
export interface ProcessPaymentCommand {
    invoiceId: InvoiceId;
    paymentDate: Date;
    paymentMethod: string;
    paymentReference?: string;
    paidBy: string;
}
export declare class APInvoiceReceivedEvent implements DomainEvent {
    readonly invoice: APInvoice;
    readonly type = "finance.ap-invoice.received";
    readonly occurredAt: Date;
    readonly aggregateId: InvoiceId;
    readonly tenantId: TenantId;
    constructor(invoice: APInvoice);
}
export declare class APInvoiceApprovedEvent implements DomainEvent {
    readonly invoiceId: InvoiceId;
    readonly tenantId: TenantId;
    readonly approvedBy: string;
    readonly approvedEntries: JournalEntryProposal[];
    readonly totalAmount: number;
    readonly type = "finance.ap-invoice.approved";
    readonly occurredAt: Date;
    readonly aggregateId: InvoiceId;
    constructor(invoiceId: InvoiceId, tenantId: TenantId, approvedBy: string, approvedEntries: JournalEntryProposal[], totalAmount: number);
}
export declare class APInvoicePaidEvent implements DomainEvent {
    readonly invoiceId: InvoiceId;
    readonly tenantId: TenantId;
    readonly paymentDate: Date;
    readonly paymentMethod: string;
    readonly amount: number;
    readonly paidBy: string;
    readonly type = "finance.ap-invoice.paid";
    readonly occurredAt: Date;
    readonly aggregateId: InvoiceId;
    constructor(invoiceId: InvoiceId, tenantId: TenantId, paymentDate: Date, paymentMethod: string, amount: number, paidBy: string);
}
export declare class AIBookingProposedEvent implements DomainEvent {
    readonly invoiceId: InvoiceId;
    readonly tenantId: TenantId;
    readonly proposal: AIBookingProposal;
    readonly confidence: number;
    readonly explanation: string;
    readonly type = "finance.ai-booking.proposed";
    readonly occurredAt: Date;
    readonly aggregateId: InvoiceId;
    constructor(invoiceId: InvoiceId, tenantId: TenantId, proposal: AIBookingProposal, confidence: number, explanation: string);
}
/**
 * AP Invoice Entity with business logic
 */
export declare class APInvoiceEntity implements APInvoice {
    readonly id: InvoiceId;
    readonly tenantId: TenantId;
    readonly supplierId: SupplierId;
    readonly invoiceNumber: string;
    readonly issueDate: Date;
    readonly dueDate: Date;
    readonly status: 'DRAFT' | 'PROCESSING' | 'APPROVED' | 'PAID' | 'CANCELLED';
    readonly currency: string;
    readonly subtotal: number;
    readonly taxAmount: number;
    readonly totalAmount: number;
    readonly taxRate: number;
    readonly paymentTerms: string;
    readonly lines: APInvoiceLine[];
    readonly documentRef: string;
    readonly ocrData?: OCRData;
    readonly aiBooking?: AIBookingProposal;
    readonly approvedAt?: Date;
    readonly approvedBy?: string;
    readonly paidAt?: Date;
    readonly paidBy?: string;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    constructor(id: InvoiceId, tenantId: TenantId, supplierId: SupplierId, invoiceNumber: string, issueDate: Date, dueDate: Date, currency: string, subtotal: number, taxAmount: number, totalAmount: number, taxRate: number, paymentTerms: string, lines: APInvoiceLine[], documentRef: string, status?: APInvoice['status'], ocrData?: OCRData, aiBooking?: AIBookingProposal, approvedAt?: Date, approvedBy?: string, paidAt?: Date, paidBy?: string, metadata?: Record<string, any>, createdAt?: Date, updatedAt?: Date);
    /**
     * Create AP Invoice from command
     */
    static create(command: CreateAPInvoiceCommand): APInvoiceEntity;
    /**
     * Approve invoice with AI booking proposal
     */
    approve(approvedBy: string, approvedEntries: JournalEntryProposal[]): APInvoiceEntity;
    /**
     * Mark invoice as paid
     */
    markAsPaid(paidBy: string, paymentDate: Date, paymentMethod: string): APInvoiceEntity;
    /**
     * Add AI booking proposal
     */
    addAIBookingProposal(proposal: AIBookingProposal): APInvoiceEntity;
    /**
     * Calculate overall confidence from entries
     */
    private calculateOverallConfidence;
    /**
     * Check if invoice is overdue
     */
    isOverdue(): boolean;
    /**
     * Get days until due
     */
    getDaysUntilDue(): number;
    /**
     * Validate invoice business rules
     */
    private validateInvoice;
}
export interface APInvoiceRepository {
    findById(id: InvoiceId): Promise<APInvoice | null>;
    findBySupplier(supplierId: SupplierId): Promise<APInvoice[]>;
    findByStatus(tenantId: TenantId, status: APInvoice['status']): Promise<APInvoice[]>;
    findOverdue(tenantId: TenantId): Promise<APInvoice[]>;
    save(invoice: APInvoice): Promise<void>;
    findPendingApproval(tenantId: TenantId): Promise<APInvoice[]>;
}
export interface OCRService {
    processDocument(documentPath: string): Promise<OCRData>;
    extractFields(ocrData: OCRData, template: string): Promise<APInvoiceLine[]>;
}
export interface AIBookingService {
    proposeBooking(invoice: APInvoice): Promise<AIBookingProposal>;
    validateProposal(proposal: AIBookingProposal): Promise<boolean>;
    explainProposal(proposal: AIBookingProposal): Promise<string>;
}
export interface APInvoiceService {
    createInvoice(command: CreateAPInvoiceCommand): Promise<InvoiceId>;
    approveInvoice(command: ApproveAPInvoiceCommand): Promise<void>;
    processPayment(command: ProcessPaymentCommand): Promise<void>;
    getInvoice(invoiceId: InvoiceId): Promise<APInvoice | null>;
    listInvoices(tenantId: TenantId, status?: APInvoice['status']): Promise<APInvoice[]>;
    getOverdueInvoices(tenantId: TenantId): Promise<APInvoice[]>;
    getPendingApprovalInvoices(tenantId: TenantId): Promise<APInvoice[]>;
    processInvoiceDocument(documentPath: string, tenantId: TenantId, supplierId?: string): Promise<InvoiceId>;
    processEInvoiceDocument(file: Buffer, filename: string, tenantId: TenantId, supplierId?: string): Promise<InvoiceId>;
}
/**
 * Calculate tax amount from subtotal and rate
 */
export declare function calculateTaxAmount(subtotal: number, taxRate: number): number;
/**
 * Calculate total amount from subtotal and tax
 */
export declare function calculateTotalAmount(subtotal: number, taxAmount: number): number;
/**
 * Validate German tax rates
 */
export declare function validateTaxRate(taxRate: number): boolean;
/**
 * Extract supplier information from OCR data
 */
export declare function extractSupplierFromOCR(ocrData: OCRData): {
    supplierId?: string;
    supplierName?: string;
};
//# sourceMappingURL=ap-invoice.d.ts.map