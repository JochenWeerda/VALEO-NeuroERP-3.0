"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - AP Invoice Entities
 *
 * Accounts Payable entities with OCR processing and AI booking
 * Following Domain-Driven Design and Event Sourcing patterns
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.APInvoiceEntity = exports.AIBookingProposedEvent = exports.APInvoicePaidEvent = exports.APInvoiceApprovedEvent = exports.APInvoiceReceivedEvent = void 0;
exports.calculateTaxAmount = calculateTaxAmount;
exports.calculateTotalAmount = calculateTotalAmount;
exports.validateTaxRate = validateTaxRate;
exports.extractSupplierFromOCR = extractSupplierFromOCR;
// ===== DOMAIN EVENTS =====
class APInvoiceReceivedEvent {
    invoice;
    type = 'finance.ap-invoice.received';
    occurredAt;
    aggregateId;
    tenantId;
    constructor(invoice) {
        this.invoice = invoice;
        this.occurredAt = new Date();
        this.aggregateId = invoice.id;
        this.tenantId = invoice.tenantId;
    }
}
exports.APInvoiceReceivedEvent = APInvoiceReceivedEvent;
class APInvoiceApprovedEvent {
    invoiceId;
    tenantId;
    approvedBy;
    approvedEntries;
    totalAmount;
    type = 'finance.ap-invoice.approved';
    occurredAt;
    aggregateId;
    constructor(invoiceId, tenantId, approvedBy, approvedEntries, totalAmount) {
        this.invoiceId = invoiceId;
        this.tenantId = tenantId;
        this.approvedBy = approvedBy;
        this.approvedEntries = approvedEntries;
        this.totalAmount = totalAmount;
        this.occurredAt = new Date();
        this.aggregateId = invoiceId;
    }
}
exports.APInvoiceApprovedEvent = APInvoiceApprovedEvent;
class APInvoicePaidEvent {
    invoiceId;
    tenantId;
    paymentDate;
    paymentMethod;
    amount;
    paidBy;
    type = 'finance.ap-invoice.paid';
    occurredAt;
    aggregateId;
    constructor(invoiceId, tenantId, paymentDate, paymentMethod, amount, paidBy) {
        this.invoiceId = invoiceId;
        this.tenantId = tenantId;
        this.paymentDate = paymentDate;
        this.paymentMethod = paymentMethod;
        this.amount = amount;
        this.paidBy = paidBy;
        this.occurredAt = new Date();
        this.aggregateId = invoiceId;
    }
}
exports.APInvoicePaidEvent = APInvoicePaidEvent;
class AIBookingProposedEvent {
    invoiceId;
    tenantId;
    proposal;
    confidence;
    explanation;
    type = 'finance.ai-booking.proposed';
    occurredAt;
    aggregateId;
    constructor(invoiceId, tenantId, proposal, confidence, explanation) {
        this.invoiceId = invoiceId;
        this.tenantId = tenantId;
        this.proposal = proposal;
        this.confidence = confidence;
        this.explanation = explanation;
        this.occurredAt = new Date();
        this.aggregateId = invoiceId;
    }
}
exports.AIBookingProposedEvent = AIBookingProposedEvent;
// ===== BUSINESS LOGIC =====
/**
 * AP Invoice Entity with business logic
 */
class APInvoiceEntity {
    id;
    tenantId;
    supplierId;
    invoiceNumber;
    issueDate;
    dueDate;
    status;
    currency;
    subtotal;
    taxAmount;
    totalAmount;
    taxRate;
    paymentTerms;
    lines;
    documentRef;
    ocrData;
    aiBooking;
    approvedAt;
    approvedBy;
    paidAt;
    paidBy;
    metadata;
    createdAt;
    updatedAt;
    constructor(id, tenantId, supplierId, invoiceNumber, issueDate, dueDate, currency, subtotal, taxAmount, totalAmount, taxRate, paymentTerms, lines, documentRef, status = 'PROCESSING', ocrData, aiBooking, approvedAt, approvedBy, paidAt, paidBy, metadata = {}, createdAt, updatedAt) {
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
        if (ocrData !== undefined)
            this.ocrData = ocrData;
        if (aiBooking !== undefined)
            this.aiBooking = aiBooking;
        if (approvedAt !== undefined)
            this.approvedAt = approvedAt;
        if (approvedBy !== undefined)
            this.approvedBy = approvedBy;
        if (paidAt !== undefined)
            this.paidAt = paidAt;
        if (paidBy !== undefined)
            this.paidBy = paidBy;
        this.metadata = metadata;
        this.createdAt = createdAt ?? new Date();
        this.updatedAt = updatedAt ?? new Date();
        this.validateInvoice();
    }
    /**
     * Create AP Invoice from command
     */
    static create(command) {
        const id = crypto.randomUUID();
        // Create invoice lines
        const lines = command.lines.map((line, index) => ({
            id: crypto.randomUUID(),
            invoiceId: id,
            ocrConfidence: 0.95, // Default confidence
            metadata: {},
            ...line
        }));
        return new APInvoiceEntity(id, command.tenantId, command.supplierId, command.invoiceNumber, command.issueDate, command.dueDate, command.currency, command.subtotal, command.taxAmount, command.totalAmount, command.taxRate, command.paymentTerms, lines, command.documentRef, 'PROCESSING', command.ocrData, undefined, // aiBooking
        undefined, // approvedAt
        undefined, // approvedBy
        undefined, // paidAt
        undefined, // paidBy
        command.metadata);
    }
    /**
     * Approve invoice with AI booking proposal
     */
    approve(approvedBy, approvedEntries) {
        if (this.status !== 'PROCESSING') {
            throw new Error('Only processing invoices can be approved');
        }
        return new APInvoiceEntity(this.id, this.tenantId, this.supplierId, this.invoiceNumber, this.issueDate, this.dueDate, this.currency, this.subtotal, this.taxAmount, this.totalAmount, this.taxRate, this.paymentTerms, this.lines, this.documentRef, 'APPROVED', this.ocrData, {
            proposalId: crypto.randomUUID(),
            createdAt: new Date(),
            confidence: this.calculateOverallConfidence(approvedEntries),
            suggestedEntries: approvedEntries,
            explanation: 'Approved by user with manual review',
            rules: ['USER_APPROVAL'],
            features: {}
        }, new Date(), approvedBy, this.paidAt, this.paidBy, this.metadata, this.createdAt, new Date());
    }
    /**
     * Mark invoice as paid
     */
    markAsPaid(paidBy, paymentDate, paymentMethod) {
        if (this.status !== 'APPROVED') {
            throw new Error('Only approved invoices can be marked as paid');
        }
        return new APInvoiceEntity(this.id, this.tenantId, this.supplierId, this.invoiceNumber, this.issueDate, this.dueDate, this.currency, this.subtotal, this.taxAmount, this.totalAmount, this.taxRate, this.paymentTerms, this.lines, this.documentRef, 'PAID', this.ocrData, this.aiBooking, this.approvedAt, this.approvedBy, paymentDate, paidBy, this.metadata, this.createdAt, new Date());
    }
    /**
     * Add AI booking proposal
     */
    addAIBookingProposal(proposal) {
        return new APInvoiceEntity(this.id, this.tenantId, this.supplierId, this.invoiceNumber, this.issueDate, this.dueDate, this.currency, this.subtotal, this.taxAmount, this.totalAmount, this.taxRate, this.paymentTerms, this.lines, this.documentRef, this.status, this.ocrData, proposal, this.approvedAt, this.approvedBy, this.paidAt, this.paidBy, this.metadata, this.createdAt, new Date());
    }
    /**
     * Calculate overall confidence from entries
     */
    calculateOverallConfidence(entries) {
        if (entries.length === 0)
            return 0;
        const totalConfidence = entries.reduce((sum, entry) => sum + entry.confidence, 0);
        return totalConfidence / entries.length;
    }
    /**
     * Check if invoice is overdue
     */
    isOverdue() {
        return this.dueDate < new Date() && this.status !== 'PAID' && this.status !== 'CANCELLED';
    }
    /**
     * Get days until due
     */
    getDaysUntilDue() {
        const today = new Date();
        const diffTime = this.dueDate.getTime() - today.getTime();
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    /**
     * Validate invoice business rules
     */
    validateInvoice() {
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
exports.APInvoiceEntity = APInvoiceEntity;
// ===== UTILITY FUNCTIONS =====
/**
 * Calculate tax amount from subtotal and rate
 */
function calculateTaxAmount(subtotal, taxRate) {
    return Math.round(subtotal * taxRate * 100) / 100;
}
/**
 * Calculate total amount from subtotal and tax
 */
function calculateTotalAmount(subtotal, taxAmount) {
    return Math.round((subtotal + taxAmount) * 100) / 100;
}
/**
 * Validate German tax rates
 */
function validateTaxRate(taxRate) {
    const validRates = [0, 0.07, 0.19]; // Standard German VAT rates
    return validRates.includes(taxRate);
}
/**
 * Extract supplier information from OCR data
 */
function extractSupplierFromOCR(ocrData) {
    const supplierFields = ocrData.fields.filter(field => field.fieldName.toLowerCase().includes('supplier') ||
        field.fieldName.toLowerCase().includes('vendor'));
    const result = {};
    const supplierName = supplierFields.find(f => f.fieldName.toLowerCase().includes('name'))?.value;
    const supplierId = supplierFields.find(f => f.fieldName.toLowerCase().includes('id'))?.value;
    if (supplierName)
        result.supplierName = supplierName;
    if (supplierId)
        result.supplierId = supplierId;
    return result;
}
