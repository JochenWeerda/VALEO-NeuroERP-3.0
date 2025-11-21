"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.QuoteService = void 0;
class QuoteService {
    deps;
    constructor(deps) {
        this.deps = deps;
    }
    async createQuote(data) {
        // Business validation
        if (data.lines.length === 0) {
            throw new Error('Quote must have at least one line item');
        }
        // Check if quote number already exists
        const existingQuote = await this.deps.quoteRepo.findByNumber(data.quoteNumber, data.tenantId);
        if (existingQuote) {
            throw new Error(`Quote number ${data.quoteNumber} already exists`);
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
        const quote = await this.deps.quoteRepo.create(data);
        return quote;
    }
    async getQuote(id, tenantId) {
        return this.deps.quoteRepo.findById(id, tenantId);
    }
    async getQuoteByNumber(quoteNumber, tenantId) {
        return this.deps.quoteRepo.findByNumber(quoteNumber, tenantId);
    }
    async updateQuote(id, data) {
        const existingQuote = await this.deps.quoteRepo.findById(id, data.tenantId);
        if (existingQuote === undefined || existingQuote === null) {
            throw new Error(`Quote ${id} not found`);
        }
        // Business validation
        if (data.lines) {
            if (data.lines.length === 0) {
                throw new Error('Quote must have at least one line item');
            }
            for (const line of data.lines) {
                if (line.quantity <= 0) {
                    throw new Error('Line item quantity must be positive');
                }
                if (line.unitPrice < 0) {
                    throw new Error('Line item unit price cannot be negative');
                }
            }
        }
        const updatedQuote = await this.deps.quoteRepo.update(id, data.tenantId, data);
        if (updatedQuote === undefined || updatedQuote === null) {
            throw new Error(`Failed to update quote ${id}`);
        }
        return updatedQuote;
    }
    async deleteQuote(id, tenantId) {
        const quote = await this.deps.quoteRepo.findById(id, tenantId);
        if (quote === undefined || quote === null) {
            throw new Error(`Quote ${id} not found`);
        }
        // Business rule: only draft quotes can be deleted
        if (quote.status !== 'Draft') {
            throw new Error('Only draft quotes can be deleted');
        }
        return this.deps.quoteRepo.delete(id, tenantId);
    }
    async sendQuote(id, tenantId) {
        const quote = await this.deps.quoteRepo.findById(id, tenantId);
        if (quote === undefined || quote === null) {
            throw new Error(`Quote ${id} not found`);
        }
        if (!quote.canBeSent()) {
            throw new Error('Quote cannot be sent in its current state');
        }
        const updatedQuote = await this.deps.quoteRepo.updateStatus(id, tenantId, 'Sent');
        if (updatedQuote === undefined || updatedQuote === null) {
            throw new Error(`Failed to send quote`);
        }
        return updatedQuote;
    }
    async acceptQuote(id, tenantId) {
        const quote = await this.deps.quoteRepo.findById(id, tenantId);
        if (quote === undefined || quote === null) {
            throw new Error(`Quote ${id} not found`);
        }
        if (!quote.canBeAccepted()) {
            throw new Error('Quote cannot be accepted in its current state');
        }
        const updatedQuote = await this.deps.quoteRepo.updateStatus(id, tenantId, 'Accepted');
        if (updatedQuote === undefined || updatedQuote === null) {
            throw new Error(`Failed to accept quote`);
        }
        return updatedQuote;
    }
    async rejectQuote(id, tenantId) {
        const quote = await this.deps.quoteRepo.findById(id, tenantId);
        if (quote === undefined || quote === null) {
            throw new Error(`Quote ${id} not found`);
        }
        if (quote.status !== 'Sent') {
            throw new Error('Only sent quotes can be rejected');
        }
        const updatedQuote = await this.deps.quoteRepo.updateStatus(id, tenantId, 'Rejected');
        if (updatedQuote === undefined || updatedQuote === null) {
            throw new Error(`Failed to reject quote`);
        }
        return updatedQuote;
    }
    async expireQuote(id, tenantId) {
        const quote = await this.deps.quoteRepo.findById(id, tenantId);
        if (quote === undefined || quote === null) {
            throw new Error(`Quote ${id} not found`);
        }
        if (quote.status === 'Expired' || quote.status === 'Rejected' || quote.status === 'Accepted') {
            return quote; // Already in terminal state
        }
        const updatedQuote = await this.deps.quoteRepo.updateStatus(id, tenantId, 'Expired');
        if (updatedQuote === undefined || updatedQuote === null) {
            throw new Error(`Failed to expire quote`);
        }
        return updatedQuote;
    }
    async searchQuotes(tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.quoteRepo.findAll(tenantId, filters, pagination);
    }
    async getQuotesByCustomer(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.quoteRepo.findByCustomerId(customerId, tenantId, filters, pagination);
    }
    async getExpiringSoon(tenantId, daysAhead = 7) {
        return this.deps.quoteRepo.getExpiringSoon(tenantId, daysAhead);
    }
    async getExpiredQuotes(tenantId) {
        return this.deps.quoteRepo.getExpired(tenantId);
    }
}
exports.QuoteService = QuoteService;
//# sourceMappingURL=quote-service.js.map