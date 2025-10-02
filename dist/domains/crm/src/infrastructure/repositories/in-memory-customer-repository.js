"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryCustomerRepository = void 0;
const branded_types_1 = require("../../../../../packages/data-models/src/branded-types");
const customer_1 = require("../../core/entities/customer");
function matchesSearch(customer, term) {
    const value = term.toLowerCase();
    return [customer.name, customer.customerNumber, customer.email, customer.phone]
        .filter(Boolean)
        .some((field) => field.toString().toLowerCase().includes(value));
}
class InMemoryCustomerRepository {
    constructor(seed = []) {
        this.store = new Map();
        seed.forEach((customer) => {
            const id = (0, branded_types_1.createId)('CustomerId');
            const now = new Date();
            this.store.set(id, {
                id,
                customerNumber: customer.customerNumber ?? id,
                name: customer.name,
                type: customer.type,
                status: customer.status ?? 'active',
                email: customer.email,
                phone: customer.phone,
                website: customer.website,
                address: customer.address,
                industry: customer.industry,
                companySize: customer.companySize,
                annualRevenue: customer.annualRevenue,
                taxId: customer.taxId,
                vatNumber: customer.vatNumber,
                salesRepId: customer.salesRepId,
                leadSource: customer.leadSource,
                leadScore: customer.leadScore,
                notes: customer.notes,
                tags: customer.tags,
                createdAt: now,
                updatedAt: now,
            });
        });
    }
    async list(filters = {}) {
        const values = Array.from(this.store.values());
        let filtered = values;
        if (filters.status) {
            filtered = filtered.filter((customer) => customer.status === filters.status);
        }
        if (filters.type) {
            filtered = filtered.filter((customer) => customer.type === filters.type);
        }
        if (filters.search) {
            filtered = filtered.filter((customer) => matchesSearch(customer, filters.search));
        }
        const offset = filters.offset ?? 0;
        const limit = filters.limit ?? customer_1.DEFAULT_PAGE_SIZE;
        return filtered.slice(offset, offset + limit);
    }
    async findById(id) {
        return this.store.get(id) ?? null;
    }
    async create(payload) {
        const id = (0, branded_types_1.createId)('CustomerId');
        const now = new Date();
        const record = {
            id,
            customerNumber: payload.customerNumber ?? id,
            name: payload.name,
            type: payload.type,
            status: payload.status ?? 'active',
            email: payload.email,
            phone: payload.phone,
            website: payload.website,
            address: payload.address,
            industry: payload.industry,
            companySize: payload.companySize,
            annualRevenue: payload.annualRevenue,
            taxId: payload.taxId,
            vatNumber: payload.vatNumber,
            salesRepId: payload.salesRepId,
            leadSource: payload.leadSource,
            leadScore: payload.leadScore,
            notes: payload.notes,
            tags: payload.tags,
            createdAt: now,
            updatedAt: now,
        };
        this.store.set(id, record);
        return record;
    }
    async update(id, updates) {
        const current = this.store.get(id);
        if (!current) {
            throw new Error(`Customer ${id} not found.`);
        }
        const next = {
            ...current,
            ...updates,
            email: updates.email === undefined ? current.email : updates.email ?? undefined,
            phone: updates.phone === undefined ? current.phone : updates.phone ?? undefined,
            website: updates.website === undefined ? current.website : updates.website ?? undefined,
            address: updates.address === undefined ? current.address : updates.address,
            updatedAt: new Date(),
        };
        this.store.set(id, next);
        return next;
    }
    async delete(id) {
        this.store.delete(id);
    }
}
exports.InMemoryCustomerRepository = InMemoryCustomerRepository;
