"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CustomerDomainService = void 0;
const customer_1 = require("../entities/customer");
class CustomerDomainService {
    constructor(repository) {
        this.repository = repository;
    }
    async listCustomers(filters = {}) {
        const normalized = {
            offset: filters.offset ?? 0,
            limit: filters.limit ?? customer_1.DEFAULT_PAGE_SIZE,
            search: filters.search?.trim() || undefined,
            status: filters.status,
            type: filters.type,
        };
        if (normalized.limit <= 0) {
            normalized.limit = customer_1.DEFAULT_PAGE_SIZE;
        }
        return this.repository.list(normalized);
    }
    async getCustomer(id) {
        return this.repository.findById(id);
    }
    async createCustomer(payload) {
        this.assertName(payload.name);
        this.assertType(payload.type);
        const status = payload.status ?? 'active';
        return this.repository.create({
            ...payload,
            status,
            name: payload.name.trim(),
        });
    }
    async updateCustomer(id, updates) {
        if (updates.name !== undefined) {
            this.assertName(updates.name);
            updates = { ...updates, name: updates.name.trim() };
        }
        if (updates.type !== undefined) {
            this.assertType(updates.type);
        }
        return this.repository.update(id, updates);
    }
    async deleteCustomer(id) {
        await this.repository.delete(id);
    }
    assertName(value) {
        if (!value || !value.trim()) {
            throw new Error('Customer name must not be empty.');
        }
    }
    assertType(value) {
        if (!value || !value.trim()) {
            throw new Error('Customer type must not be empty.');
        }
    }
}
exports.CustomerDomainService = CustomerDomainService;
