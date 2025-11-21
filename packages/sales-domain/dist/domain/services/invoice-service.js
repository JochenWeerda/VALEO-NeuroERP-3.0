"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InvoiceService = void 0;
class InvoiceService {
    deps;
    constructor(deps) {
        this.deps = deps;
    }
    async createInvoice(data) {
        // Business validation
        if (data.lines.length === 0) {
            throw new Error('Invoice must have at least one line item');
        }
        // Check if invoice number already exists
        const existingInvoice = await this.deps.invoiceRepo.findByNumber(data.invoiceNumber, data.tenantId);
        if (existingInvoice) {
            throw new Error(`Invoice number ${data.invoiceNumber} already exists`);
        }
        // Validate line items
        for (const line of data.lines) {
            if (line.quantity <= 0) {
                throw new Error('Line item quantity must be positive');
            }
            if (line.unitPrice < 0) {
                throw new Error('Line item unit price cannot be negative');
            }
        }
        const invoice = await this.deps.invoiceRepo.create(data);
        return invoice;
    }
    async getInvoice(id, tenantId) {
        return this.deps.invoiceRepo.findById(id, tenantId);
    }
    async updateInvoice(id, data) {
        const existingInvoice = await this.deps.invoiceRepo.findById(id, data.tenantId);
        if (existingInvoice === undefined || existingInvoice === null) {
            throw new Error(`Invoice ${id} not found`);
        }
        const updatedInvoice = await this.deps.invoiceRepo.update(id, data.tenantId, data);
        if (updatedInvoice === undefined || updatedInvoice === null) {
            throw new Error(`Failed to update invoice ${id}`);
        }
        return updatedInvoice;
    }
    async markInvoiceAsPaid(id, tenantId) {
        const invoice = await this.deps.invoiceRepo.findById(id, tenantId);
        if (invoice === undefined || invoice === null) {
            throw new Error(`Invoice ${id} not found`);
        }
        if (!invoice.canBePaid()) {
            throw new Error('Invoice cannot be marked as paid in its current state');
        }
        const updatedInvoice = await this.deps.invoiceRepo.updateStatus(id, tenantId, 'Paid');
        if (updatedInvoice === undefined || updatedInvoice === null) {
            throw new Error(`Failed to mark invoice as paid`);
        }
        return updatedInvoice;
    }
    async markInvoiceAsOverdue(id, tenantId) {
        const invoice = await this.deps.invoiceRepo.findById(id, tenantId);
        if (invoice === undefined || invoice === null) {
            throw new Error(`Invoice ${id} not found`);
        }
        if (invoice.isOverdue()) {
            return invoice; // Already overdue
        }
        const updatedInvoice = await this.deps.invoiceRepo.updateStatus(id, tenantId, 'Overdue');
        if (updatedInvoice === undefined || updatedInvoice === null) {
            throw new Error(`Failed to mark invoice as overdue`);
        }
        return updatedInvoice;
    }
    async cancelInvoice(id, tenantId) {
        const invoice = await this.deps.invoiceRepo.findById(id, tenantId);
        if (invoice === undefined || invoice === null) {
            throw new Error(`Invoice ${id} not found`);
        }
        if (!invoice.canBeCancelled()) {
            throw new Error('Invoice cannot be cancelled in its current state');
        }
        const updatedInvoice = await this.deps.invoiceRepo.updateStatus(id, tenantId, 'Cancelled');
        if (updatedInvoice === undefined || updatedInvoice === null) {
            throw new Error(`Failed to cancel invoice`);
        }
        return updatedInvoice;
    }
    async searchInvoices(tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.invoiceRepo.findAll(tenantId, filters, pagination);
    }
    async getInvoicesByCustomer(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.invoiceRepo.findByCustomerId(customerId, tenantId, filters, pagination);
    }
    async getOverdueInvoices(tenantId) {
        return this.deps.invoiceRepo.getOverdueInvoices(tenantId);
    }
}
exports.InvoiceService = InvoiceService;
//# sourceMappingURL=invoice-service.js.map