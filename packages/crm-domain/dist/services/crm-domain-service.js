"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CRMDomainService = void 0;
const customer_1 = require("../core/entities/customer");
const noopLogger = {
    debug() { },
    info() { },
    warn() { },
    error() { },
};
class CRMDomainService {
    customers;
    logger;
    metrics;
    constructor(customers, options = {}) {
        this.customers = customers;
        this.logger = options.logger ?? noopLogger;
        this.metrics = options.metrics ?? undefined;
    }
    async createCustomer(input) {
        this.logger.info('crm.customer.create.start', { name: input.name, type: input.type });
        const customer = (0, customer_1.createCustomer)(input);
        const saved = await this.customers.create(customer);
        this.metrics?.incrementCounter('crm.customer.created', { type: saved.type });
        return saved;
    }
    async updateCustomer(id, updates) {
        const existing = await this.customers.findById(id);
        if (!existing) {
            throw new Error(`Customer ${String(id)} not found`);
        }
        const next = (0, customer_1.applyCustomerUpdate)(existing, updates);
        const updated = await this.customers.update(id, next);
        this.metrics?.incrementCounter('crm.customer.updated', { type: updated.type });
        return updated;
    }
    async listCustomers(filters) {
        return this.customers.list(filters);
    }
    async getCustomer(id) {
        return this.customers.findById(id);
    }
    async deleteCustomer(id) {
        const existing = await this.customers.findById(id);
        if (!existing) {
            throw new Error(`Customer ${String(id)} not found`);
        }
        await this.customers.delete(id);
        this.metrics?.incrementCounter('crm.customer.deleted', { type: existing.type });
    }
}
exports.CRMDomainService = CRMDomainService;
//# sourceMappingURL=crm-domain-service.js.map