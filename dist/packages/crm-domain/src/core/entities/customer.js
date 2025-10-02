"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_PAGE_SIZE = void 0;
exports.createCustomer = createCustomer;
exports.applyCustomerUpdate = applyCustomerUpdate;
const branded_types_1 = require("../../types/branded-types");
exports.DEFAULT_PAGE_SIZE = 25;
function createCustomer(input) {
    if (!input.name?.trim()) {
        throw new Error('Customer name is required');
    }
    if (!input.type) {
        throw new Error('Customer type is required');
    }
    const now = new Date();
    return {
        id: (0, branded_types_1.createId)('CustomerId'),
        createdAt: now,
        updatedAt: now,
        customerNumber: input.customerNumber ?? generateCustomerNumber(),
        name: input.name.trim(),
        type: input.type,
        status: input.status ?? 'active',
        email: input.email,
        phone: input.phone,
        website: input.website?.trim(),
        address: input.address ? { ...input.address } : undefined,
        industry: input.industry,
        companySize: input.companySize,
        annualRevenue: input.annualRevenue,
        taxId: input.taxId,
        vatNumber: input.vatNumber,
        salesRepId: input.salesRepId,
        leadSource: input.leadSource,
        leadScore: input.leadScore,
        notes: input.notes,
        tags: normalizeTags(input.tags),
    };
}
function applyCustomerUpdate(customer, updates) {
    return {
        ...customer,
        customerNumber: updates.customerNumber ?? customer.customerNumber,
        name: updates.name ? updates.name.trim() : customer.name,
        type: updates.type ?? customer.type,
        status: updates.status ?? customer.status,
        email: updates.email ?? customer.email,
        phone: updates.phone ?? customer.phone,
        website: updates.website?.trim() ?? customer.website,
        address: updates.address ? { ...updates.address } : customer.address,
        industry: updates.industry ?? customer.industry,
        companySize: updates.companySize ?? customer.companySize,
        annualRevenue: updates.annualRevenue ?? customer.annualRevenue,
        taxId: updates.taxId ?? customer.taxId,
        vatNumber: updates.vatNumber ?? customer.vatNumber,
        salesRepId: updates.salesRepId ?? customer.salesRepId,
        leadSource: updates.leadSource ?? customer.leadSource,
        leadScore: updates.leadScore ?? customer.leadScore,
        notes: updates.notes ?? customer.notes,
        tags: updates.tags ? normalizeTags(updates.tags) : customer.tags,
        updatedAt: new Date(),
    };
}
function generateCustomerNumber() {
    return `C-${Date.now().toString(36).toUpperCase()}`;
}
function normalizeTags(tags) {
    if (!tags) {
        return [];
    }
    return Array.from(new Set(tags.map((tag) => tag.trim()).filter(Boolean)));
}
