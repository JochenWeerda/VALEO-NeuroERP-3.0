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

// ===== BRANDED TYPES =====
export type InvoiceId = string;
export type SupplierId = string;
export type DocumentId = string;
export type TenantId = string;

// ===== CORE ENTITIES =====

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
  readonly accountId?: string; // Suggested by AI
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
  readonly bbox?: number[]; // Bounding box coordinates
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

// ===== COMMANDS =====

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

// ===== DOMAIN EVENTS =====

export class APInvoiceReceivedEvent implements DomainEvent {
  readonly type = 'finance.ap-invoice.received';
  readonly occurredAt: Date;
  readonly aggregateId: InvoiceId;
  readonly tenantId: TenantId;

  constructor(
    public readonly invoice: APInvoice
  ) {
    this.occurredAt = new Date();
    this.aggregateId = invoice.id;
    this.tenantId = invoice.tenantId;
  }
}

export class APInvoiceApprovedEvent implements DomainEvent {
  readonly type = 'finance.ap-invoice.approved';
  readonly occurredAt: Date;
  readonly aggregateId: InvoiceId;

  constructor(
    public readonly invoiceId: InvoiceId,
    public readonly tenantId: TenantId,
    public readonly approvedBy: string,
    public readonly approvedEntries: JournalEntryProposal[],
    public readonly totalAmount: number
  ) {
    this.occurredAt = new Date();
    this.aggregateId = invoiceId;
  }
}

export class APInvoicePaidEvent implements DomainEvent {
  readonly type = 'finance.ap-invoice.paid';
  readonly occurredAt: Date;
  readonly aggregateId: InvoiceId;

  constructor(
    public readonly invoiceId: InvoiceId,
    public readonly tenantId: TenantId,
    public readonly paymentDate: Date,
    public readonly paymentMethod: string,
    public readonly amount: number,
    public readonly paidBy: string
  ) {
    this.occurredAt = new Date();
    this.aggregateId = invoiceId;
  }
}

export class AIBookingProposedEvent implements DomainEvent {
  readonly type = 'finance.ai-booking.proposed';
  readonly occurredAt: Date;
  readonly aggregateId: InvoiceId;

  constructor(
    public readonly invoiceId: InvoiceId,
    public readonly tenantId: TenantId,
    public readonly proposal: AIBookingProposal,
    public readonly confidence: number,
    public readonly explanation: string
  ) {
    this.occurredAt = new Date();
    this.aggregateId = invoiceId;
  }
}

// ===== BUSINESS LOGIC =====

/**
 * AP Invoice Entity with business logic
 */
export class APInvoiceEntity implements APInvoice {
  public readonly id: InvoiceId;
  public readonly tenantId: TenantId;
  public readonly supplierId: SupplierId;
  public readonly invoiceNumber: string;
  public readonly issueDate: Date;
  public readonly dueDate: Date;
  public readonly status: 'DRAFT' | 'PROCESSING' | 'APPROVED' | 'PAID' | 'CANCELLED';
  public readonly currency: string;
  public readonly subtotal: number;
  public readonly taxAmount: number;
  public readonly totalAmount: number;
  public readonly taxRate: number;
  public readonly paymentTerms: string;
  public readonly lines: APInvoiceLine[];
  public readonly documentRef: string;
  public readonly ocrData?: OCRData;
  public readonly aiBooking?: AIBookingProposal;
  public readonly approvedAt?: Date;
  public readonly approvedBy?: string;
  public readonly paidAt?: Date;
  public readonly paidBy?: string;
  public readonly metadata: Record<string, any>;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;

  constructor(
    id: InvoiceId,
    tenantId: TenantId,
    supplierId: SupplierId,
    invoiceNumber: string,
    issueDate: Date,
    dueDate: Date,
    currency: string,
    subtotal: number,
    taxAmount: number,
    totalAmount: number,
    taxRate: number,
    paymentTerms: string,
    lines: APInvoiceLine[],
    documentRef: string,
    status: APInvoice['status'] = 'PROCESSING',
    ocrData?: OCRData,
    aiBooking?: AIBookingProposal,
    approvedAt?: Date,
    approvedBy?: string,
    paidAt?: Date,
    paidBy?: string,
    metadata: Record<string, any> = {},
    createdAt?: Date,
    updatedAt?: Date
  ) {
    this.id = id;
    this.tenantId = tenantId;
    this.supplierId = supplierId;
    this.invoiceNumber = invoiceNumber;
    this.issueDate = issueDate;
    this.dueDate = dueDate;
    this.currency = currency;
    this.subtotal = subtotal;
    this.taxAmount = taxAmount;
    this.totalAmount = totalAmount;
    this.taxRate = taxRate;
    this.paymentTerms = paymentTerms;
    this.lines = lines;
    this.documentRef = documentRef;
    this.status = status;
    if (ocrData !== undefined) this.ocrData = ocrData;
    if (aiBooking !== undefined) this.aiBooking = aiBooking;
    if (approvedAt !== undefined) this.approvedAt = approvedAt;
    if (approvedBy !== undefined) this.approvedBy = approvedBy;
    if (paidAt !== undefined) this.paidAt = paidAt;
    if (paidBy !== undefined) this.paidBy = paidBy;
    this.metadata = metadata;
    this.createdAt = createdAt ?? new Date();
    this.updatedAt = updatedAt ?? new Date();

    this.validateInvoice();
  }

  /**
   * Create AP Invoice from command
   */
  static create(command: CreateAPInvoiceCommand): APInvoiceEntity {
    const id = crypto.randomUUID() as InvoiceId;

    // Create invoice lines
    const lines: APInvoiceLine[] = command.lines.map((line, index) => ({
      id: crypto.randomUUID(),
      invoiceId: id,
      ocrConfidence: 0.95, // Default confidence
      metadata: {},
      ...line
    }));

    return new APInvoiceEntity(
      id,
      command.tenantId,
      command.supplierId,
      command.invoiceNumber,
      command.issueDate,
      command.dueDate,
      command.currency,
      command.subtotal,
      command.taxAmount,
      command.totalAmount,
      command.taxRate,
      command.paymentTerms,
      lines,
      command.documentRef,
      'PROCESSING',
      command.ocrData,
      undefined, // aiBooking
      undefined, // approvedAt
      undefined, // approvedBy
      undefined, // paidAt
      undefined, // paidBy
      command.metadata
    );
  }

  /**
   * Approve invoice with AI booking proposal
   */
  approve(approvedBy: string, approvedEntries: JournalEntryProposal[]): APInvoiceEntity {
    if (this.status !== 'PROCESSING') {
      throw new Error('Only processing invoices can be approved');
    }

    return new APInvoiceEntity(
      this.id,
      this.tenantId,
      this.supplierId,
      this.invoiceNumber,
      this.issueDate,
      this.dueDate,
      this.currency,
      this.subtotal,
      this.taxAmount,
      this.totalAmount,
      this.taxRate,
      this.paymentTerms,
      this.lines,
      this.documentRef,
      'APPROVED',
      this.ocrData,
      {
        proposalId: crypto.randomUUID(),
        createdAt: new Date(),
        confidence: this.calculateOverallConfidence(approvedEntries),
        suggestedEntries: approvedEntries,
        explanation: 'Approved by user with manual review',
        rules: ['USER_APPROVAL'],
        features: {}
      },
      new Date(),
      approvedBy,
      this.paidAt,
      this.paidBy,
      this.metadata,
      this.createdAt,
      new Date()
    );
  }

  /**
   * Mark invoice as paid
   */
  markAsPaid(paidBy: string, paymentDate: Date, paymentMethod: string): APInvoiceEntity {
    if (this.status !== 'APPROVED') {
      throw new Error('Only approved invoices can be marked as paid');
    }

    return new APInvoiceEntity(
      this.id,
      this.tenantId,
      this.supplierId,
      this.invoiceNumber,
      this.issueDate,
      this.dueDate,
      this.currency,
      this.subtotal,
      this.taxAmount,
      this.totalAmount,
      this.taxRate,
      this.paymentTerms,
      this.lines,
      this.documentRef,
      'PAID',
      this.ocrData,
      this.aiBooking,
      this.approvedAt,
      this.approvedBy,
      paymentDate,
      paidBy,
      this.metadata,
      this.createdAt,
      new Date()
    );
  }

  /**
   * Add AI booking proposal
   */
  addAIBookingProposal(proposal: AIBookingProposal): APInvoiceEntity {
    return new APInvoiceEntity(
      this.id,
      this.tenantId,
      this.supplierId,
      this.invoiceNumber,
      this.issueDate,
      this.dueDate,
      this.currency,
      this.subtotal,
      this.taxAmount,
      this.totalAmount,
      this.taxRate,
      this.paymentTerms,
      this.lines,
      this.documentRef,
      this.status,
      this.ocrData,
      proposal,
      this.approvedAt,
      this.approvedBy,
      this.paidAt,
      this.paidBy,
      this.metadata,
      this.createdAt,
      new Date()
    );
  }

  /**
   * Calculate overall confidence from entries
   */
  private calculateOverallConfidence(entries: JournalEntryProposal[]): number {
    if (entries.length === 0) return 0;

    const totalConfidence = entries.reduce((sum, entry) => sum + entry.confidence, 0);
    return totalConfidence / entries.length;
  }

  /**
   * Check if invoice is overdue
   */
  isOverdue(): boolean {
    return this.dueDate < new Date() && this.status !== 'PAID' && this.status !== 'CANCELLED';
  }

  /**
   * Get days until due
   */
  getDaysUntilDue(): number {
    const today = new Date();
    const diffTime = this.dueDate.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  /**
   * Validate invoice business rules
   */
  private validateInvoice(): void {
    if (this.subtotal < 0) {
      throw new Error('Subtotal cannot be negative');
    }

    if (this.taxAmount < 0) {
      throw new Error('Tax amount cannot be negative');
    }

    if (this.totalAmount !== this.subtotal + this.taxAmount) {
      throw new Error('Total amount must equal subtotal + tax amount');
    }

    if (this.lines.length === 0) {
      throw new Error('Invoice must have at least one line item');
    }

    // Validate line totals
    const lineTotals = this.lines.reduce((sum, line) => sum + line.lineTotal, 0);
    if (Math.abs(lineTotals - this.subtotal) > 0.01) {
      throw new Error('Line item totals must match invoice subtotal');
    }
  }
}

// ===== REPOSITORY INTERFACES =====

export interface APInvoiceRepository {
  findById(id: InvoiceId): Promise<APInvoice | null>;
  findBySupplier(supplierId: SupplierId): Promise<APInvoice[]>;
  findByStatus(tenantId: TenantId, status: APInvoice['status']): Promise<APInvoice[]>;
  findOverdue(tenantId: TenantId): Promise<APInvoice[]>;
  save(invoice: APInvoice): Promise<void>;
  findPendingApproval(tenantId: TenantId): Promise<APInvoice[]>;
}

// ===== SERVICE INTERFACES =====

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

// ===== UTILITY FUNCTIONS =====

/**
 * Calculate tax amount from subtotal and rate
 */
export function calculateTaxAmount(subtotal: number, taxRate: number): number {
  return Math.round(subtotal * taxRate * 100) / 100;
}

/**
 * Calculate total amount from subtotal and tax
 */
export function calculateTotalAmount(subtotal: number, taxAmount: number): number {
  return Math.round((subtotal + taxAmount) * 100) / 100;
}

/**
 * Validate German tax rates
 */
export function validateTaxRate(taxRate: number): boolean {
  const validRates = [0, 0.07, 0.19]; // Standard German VAT rates
  return validRates.includes(taxRate);
}

/**
 * Extract supplier information from OCR data
 */
export function extractSupplierFromOCR(ocrData: OCRData): { supplierId?: string; supplierName?: string } {
  const supplierFields = ocrData.fields.filter(field =>
    field.fieldName.toLowerCase().includes('supplier') ||
    field.fieldName.toLowerCase().includes('vendor')
  );

  const result: { supplierId?: string; supplierName?: string } = {};

  const supplierName = supplierFields.find(f => f.fieldName.toLowerCase().includes('name'))?.value;
  const supplierId = supplierFields.find(f => f.fieldName.toLowerCase().includes('id'))?.value;

  if (supplierName) result.supplierName = supplierName;
  if (supplierId) result.supplierId = supplierId;

  return result;
}