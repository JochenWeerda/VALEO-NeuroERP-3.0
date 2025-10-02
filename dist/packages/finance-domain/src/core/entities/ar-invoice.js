"use strict";
/**
 * VALEO NeuroERP 3.0 - AR Invoice Entity
 *
 * Domain entity for Accounts Receivable (AR) invoices
 * Handles outgoing invoices, dunning process, and payment tracking
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ArInvoiceEntity = exports.DunningProcessedEvent = exports.ArInvoiceOverdueEvent = exports.ArInvoicePaymentReceivedEvent = exports.ArInvoiceIssuedEvent = exports.ArInvoiceCreatedEvent = exports.createArInvoiceId = exports.err = exports.ok = void 0;
const ok = (value) => ({
    isSuccess: true,
    isFailure: false,
    getValue: () => value
});
exports.ok = ok;
const err = (error) => ({
    isSuccess: false,
    isFailure: true,
    getValue: () => { throw new Error(typeof error === 'string' ? error : error.message); },
    error: typeof error === 'string' ? error : error.message
});
exports.err = err;
const createArInvoiceId = (value) => value;
exports.createArInvoiceId = createArInvoiceId;
// ===== DOMAIN EVENTS =====
class ArInvoiceCreatedEvent {
    invoice;
    type = 'ArInvoiceCreated';
    aggregateId;
    occurredAt;
    constructor(invoice) {
        this.invoice = invoice;
        this.aggregateId = invoice.id;
        this.occurredAt = new Date();
    }
}
exports.ArInvoiceCreatedEvent = ArInvoiceCreatedEvent;
class ArInvoiceIssuedEvent {
    invoice;
    type = 'ArInvoiceIssued';
    aggregateId;
    occurredAt;
    constructor(invoice) {
        this.invoice = invoice;
        this.aggregateId = invoice.id;
        this.occurredAt = new Date();
    }
}
exports.ArInvoiceIssuedEvent = ArInvoiceIssuedEvent;
class ArInvoicePaymentReceivedEvent {
    invoice;
    payment;
    type = 'ArInvoicePaymentReceived';
    aggregateId;
    occurredAt;
    constructor(invoice, payment) {
        this.invoice = invoice;
        this.payment = payment;
        this.aggregateId = invoice.id;
        this.occurredAt = new Date();
    }
}
exports.ArInvoicePaymentReceivedEvent = ArInvoicePaymentReceivedEvent;
class ArInvoiceOverdueEvent {
    invoice;
    daysOverdue;
    type = 'ArInvoiceOverdue';
    aggregateId;
    occurredAt;
    constructor(invoice, daysOverdue) {
        this.invoice = invoice;
        this.daysOverdue = daysOverdue;
        this.aggregateId = invoice.id;
        this.occurredAt = new Date();
    }
}
exports.ArInvoiceOverdueEvent = ArInvoiceOverdueEvent;
class DunningProcessedEvent {
    invoice;
    dunningLevel;
    processedBy;
    type = 'DunningProcessed';
    aggregateId;
    occurredAt;
    constructor(invoice, dunningLevel, processedBy) {
        this.invoice = invoice;
        this.dunningLevel = dunningLevel;
        this.processedBy = processedBy;
        this.aggregateId = invoice.id;
        this.occurredAt = new Date();
    }
}
exports.DunningProcessedEvent = DunningProcessedEvent;
// ===== ENTITY =====
class ArInvoiceEntity {
    id;
    equals(other) {
        return this.id === other.id;
    }
    tenantId;
    customerId;
    invoiceNumber;
    issueDate;
    currency;
    status;
    createdAt;
    updatedAt;
    // Mutable fields
    dueDate;
    lines;
    subtotal;
    taxAmount;
    total;
    dunningLevel;
    lastDunningDate;
    nextDunningDate;
    paidAt;
    paidAmount;
    outstandingAmount;
    paymentTerms;
    notes;
    metadata;
    constructor(id, tenantId, customerId, invoiceNumber, issueDate, dueDate, currency, lines, subtotal, taxAmount, total, paymentTerms, notes, metadata) {
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
    static create(command) {
        // Validation
        if (!command.tenantId || !command.customerId || !command.invoiceNumber) {
            return (0, exports.err)(new Error('Tenant ID, customer ID, and invoice number are required'));
        }
        if (command.lines.length === 0) {
            return (0, exports.err)(new Error('Invoice must have at least one line'));
        }
        if (command.dueDate <= command.issueDate) {
            return (0, exports.err)(new Error('Due date must be after issue date'));
        }
        // Calculate totals
        const lines = command.lines.map((line, index) => ({
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
        const id = (0, exports.createArInvoiceId)(`ar-inv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
        return (0, exports.ok)(new ArInvoiceEntity(id, command.tenantId, command.customerId, command.invoiceNumber, command.issueDate, command.dueDate, command.currency, lines, subtotal, taxAmount, total, command.paymentTerms, command.notes, command.metadata));
    }
    update(command) {
        if (this.status !== 'DRAFT') {
            return (0, exports.err)(new Error('Can only update draft invoices'));
        }
        if (command.lines) {
            this.lines = command.lines;
            this.recalculateTotals();
        }
        if (command.dueDate) {
            if (command.dueDate <= this.issueDate) {
                return (0, exports.err)(new Error('Due date must be after issue date'));
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
        return (0, exports.ok)(undefined);
    }
    issue() {
        if (this.status !== 'DRAFT') {
            return (0, exports.err)(new Error('Can only issue draft invoices'));
        }
        this.status = 'ISSUED';
        this.updatedAt = new Date();
        return (0, exports.ok)(undefined);
    }
    send() {
        if (this.status !== 'ISSUED') {
            return (0, exports.err)(new Error('Can only send issued invoices'));
        }
        this.status = 'SENT';
        this.updatedAt = new Date();
        return (0, exports.ok)(undefined);
    }
    recordPayment(command) {
        if (command.amount <= 0) {
            return (0, exports.err)(new Error('Payment amount must be positive'));
        }
        if (command.amount > this.outstandingAmount) {
            return (0, exports.err)(new Error('Payment amount cannot exceed outstanding amount'));
        }
        this.paidAmount += command.amount;
        this.outstandingAmount -= command.amount;
        if (this.outstandingAmount === 0) {
            this.status = 'PAID';
            this.paidAt = command.paymentDate;
        }
        else {
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
        return (0, exports.ok)(undefined);
    }
    processDunning(processedBy) {
        if (this.status === 'PAID' || this.status === 'CANCELLED') {
            return (0, exports.err)(new Error('Cannot process dunning for paid or cancelled invoices'));
        }
        const now = new Date();
        const daysOverdue = Math.floor((now.getTime() - this.dueDate.getTime()) / (1000 * 60 * 60 * 24));
        if (daysOverdue < 0) {
            return (0, exports.err)(new Error('Invoice is not overdue'));
        }
        // Determine dunning level based on days overdue
        let newDunningLevel = 0;
        if (daysOverdue >= 60)
            newDunningLevel = 3; // Final notice
        else if (daysOverdue >= 30)
            newDunningLevel = 2; // Second notice
        else if (daysOverdue >= 14)
            newDunningLevel = 1; // First notice
        if (newDunningLevel <= this.dunningLevel) {
            return (0, exports.err)(new Error('Invoice already has equal or higher dunning level'));
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
        return (0, exports.ok)(undefined);
    }
    cancel(reason) {
        if (this.status === 'PAID') {
            return (0, exports.err)(new Error('Cannot cancel paid invoices'));
        }
        this.status = 'CANCELLED';
        this.metadata.cancellation = {
            reason,
            cancelledAt: new Date()
        };
        this.updatedAt = new Date();
        return (0, exports.ok)(undefined);
    }
    // Business logic methods
    isOverdue() {
        return this.status === 'OVERDUE' || (this.dueDate < new Date() && this.status === 'SENT');
    }
    isPaid() {
        return this.status === 'PAID';
    }
    getDaysOverdue() {
        if (!this.isOverdue())
            return 0;
        return Math.floor((new Date().getTime() - this.dueDate.getTime()) / (1000 * 60 * 60 * 24));
    }
    recalculateTotals() {
        this.subtotal = this.lines.reduce((sum, line) => sum + line.total, 0);
        this.taxAmount = this.lines.reduce((sum, line) => sum + (line.total * line.taxRate / 100), 0);
        this.total = this.subtotal + this.taxAmount;
        // Adjust outstanding amount if total changed
        if (this.paidAmount > 0) {
            this.outstandingAmount = Math.max(0, this.total - this.paidAmount);
            if (this.outstandingAmount === 0) {
                this.status = 'PAID';
                this.paidAt = new Date();
            }
            else {
                this.status = 'PARTIALLY_PAID';
            }
        }
        else {
            this.outstandingAmount = this.total;
        }
    }
}
exports.ArInvoiceEntity = ArInvoiceEntity;
