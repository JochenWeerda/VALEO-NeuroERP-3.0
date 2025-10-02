"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CustomerPostgresRepository = void 0;
const utilities_1 = require("@valero-neuroerp/utilities");
class CustomerPostgresRepository extends utilities_1.RepositoryBase {
    customers = new Map();
    async findById(id) {
        return this.customers.get(id) ?? null;
    }
    async findMany(query) {
        if (!query) {
            return Array.from(this.customers.values());
        }
        return Array.from(this.customers.values()).filter(customer => {
            if (query.where) {
                const conditions = query.where;
                return Object.entries(conditions).every(([key, value]) => {
                    return customer[key] === value;
                });
            }
            return true;
        });
    }
    async create(entity) {
        this.customers.set(entity.id, entity);
        return entity;
    }
    async update(id, updates) {
        const existing = this.customers.get(id);
        if (!existing) {
            throw new Error(`Customer ${String(id)} not found`);
        }
        const updated = { ...existing, ...updates, updatedAt: new Date() };
        this.customers.set(id, updated);
        return updated;
    }
    async delete(id) {
        this.customers.delete(id);
    }
    async list(filters) {
        let customers = Array.from(this.customers.values());
        if (filters) {
            if (filters.search) {
                const search = filters.search.toLowerCase();
                customers = customers.filter(c => c.name.toLowerCase().includes(search) ||
                    c.customerNumber.toLowerCase().includes(search));
            }
            if (filters.status) {
                customers = customers.filter(c => c.status === filters.status);
            }
            if (filters.type) {
                customers = customers.filter(c => c.type === filters.type);
            }
            if (filters.tags && filters.tags.length > 0) {
                customers = customers.filter(c => filters.tags.some(tag => c.tags.includes(tag)));
            }
        }
        // Apply pagination
        const offset = filters?.offset ?? 0;
        const limit = filters?.limit ?? 25;
        return customers.slice(offset, offset + limit);
    }
    async findByEmail(email) {
        return Array.from(this.customers.values()).find(c => c.email === email) ?? null;
    }
    async findByCustomerNumber(customerNumber) {
        return Array.from(this.customers.values()).find(c => c.customerNumber === customerNumber) ?? null;
    }
}
exports.CustomerPostgresRepository = CustomerPostgresRepository;
//# sourceMappingURL=customer-postgres-repository.js.map