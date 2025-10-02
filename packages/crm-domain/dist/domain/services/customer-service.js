"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CustomerService = void 0;
class CustomerService {
    deps;
    constructor(deps) {
        this.deps = deps;
    }
    async createCustomer(data) {
        // Business validation
        if (data.vatId) {
            await this.validateVatId(data.vatId, data.tenantId);
        }
        // Check if customer number already exists
        const existingCustomer = await this.deps.customerRepo.findByNumber(data.number, data.tenantId);
        if (existingCustomer) {
            throw new Error(`Customer number ${data.number} already exists`);
        }
        // Create customer
        const customer = await this.deps.customerRepo.create(data);
        return customer;
    }
    async getCustomer(id, tenantId) {
        return this.deps.customerRepo.findById(id, tenantId);
    }
    async getCustomerByNumber(number, tenantId) {
        return this.deps.customerRepo.findByNumber(number, tenantId);
    }
    async updateCustomer(id, data) {
        // Get existing customer
        const existingCustomer = await this.deps.customerRepo.findById(id, data.tenantId);
        if (!existingCustomer) {
            throw new Error(`Customer ${id} not found`);
        }
        // Business validation
        if (data.vatId && data.vatId !== existingCustomer.vatId) {
            await this.validateVatId(data.vatId, data.tenantId);
        }
        // Update customer
        const updatedCustomer = await this.deps.customerRepo.update(id, data.tenantId, data);
        if (!updatedCustomer) {
            throw new Error(`Failed to update customer ${id}`);
        }
        return updatedCustomer;
    }
    async deleteCustomer(id, tenantId) {
        // Check if customer exists
        const customer = await this.deps.customerRepo.findById(id, tenantId);
        if (!customer) {
            throw new Error(`Customer ${id} not found`);
        }
        // Check if customer has related records (contacts, opportunities, interactions)
        // This would typically be checked here before deletion
        return this.deps.customerRepo.delete(id, tenantId);
    }
    async changeCustomerStatus(id, tenantId, status) {
        const customer = await this.deps.customerRepo.findById(id, tenantId);
        if (!customer) {
            throw new Error(`Customer ${id} not found`);
        }
        // Business rules for status changes
        if (customer.status === status) {
            return customer; // No change needed
        }
        // Validate status transition
        this.validateStatusTransition(customer.status, status);
        const updatedCustomer = await this.deps.customerRepo.updateStatus(id, tenantId, status);
        if (!updatedCustomer) {
            throw new Error(`Failed to update customer status`);
        }
        return updatedCustomer;
    }
    async addTag(id, tenantId, tag) {
        const customer = await this.deps.customerRepo.findById(id, tenantId);
        if (!customer) {
            throw new Error(`Customer ${id} not found`);
        }
        if (customer.tags.includes(tag)) {
            return customer; // Tag already exists
        }
        const updatedCustomer = await this.deps.customerRepo.addTag(id, tenantId, tag);
        if (!updatedCustomer) {
            throw new Error(`Failed to add tag to customer`);
        }
        return updatedCustomer;
    }
    async removeTag(id, tenantId, tag) {
        const customer = await this.deps.customerRepo.findById(id, tenantId);
        if (!customer) {
            throw new Error(`Customer ${id} not found`);
        }
        if (!customer.tags.includes(tag)) {
            return customer; // Tag doesn't exist
        }
        const updatedCustomer = await this.deps.customerRepo.removeTag(id, tenantId, tag);
        if (!updatedCustomer) {
            throw new Error(`Failed to remove tag from customer`);
        }
        return updatedCustomer;
    }
    async searchCustomers(tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.customerRepo.findAll(tenantId, filters, pagination);
    }
    async validateVatId(vatId, tenantId) {
        // Basic VAT ID validation (you might want to implement more sophisticated validation)
        if (!vatId || vatId.length < 5) {
            throw new Error('Invalid VAT ID format');
        }
        // Check if VAT ID is already used by another customer
        // This would require a more complex query in a real implementation
    }
    validateStatusTransition(currentStatus, newStatus) {
        // Define valid status transitions
        const validTransitions = {
            'Prospect': ['Active', 'Blocked'],
            'Active': ['Blocked'],
            'Blocked': ['Active', 'Prospect']
        };
        const allowedStatuses = validTransitions[currentStatus];
        if (!allowedStatuses?.includes(newStatus)) {
            throw new Error(`Cannot change status from ${currentStatus} to ${newStatus}`);
        }
    }
}
exports.CustomerService = CustomerService;
//# sourceMappingURL=customer-service.js.map