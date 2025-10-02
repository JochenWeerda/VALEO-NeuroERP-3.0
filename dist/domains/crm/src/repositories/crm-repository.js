"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.crmDomainService = exports.CRMDomainService = void 0;
// domains/crm/src/services/crm-domain-service.ts
const base_service_1 = require("@packages/utilities/base-service");
const business_logic_orchestrator_1 = require("@packages/business-rules/business-logic-orchestrator");
const crm_rules_1 = require("../rules/crm-rules");
class CRMDomainService extends base_service_1.BaseService {
    constructor() {
        super();
        this.initializeBusinessRules();
    }
    initializeBusinessRules() {
        // Register CRM business rules
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('CRM', new crm_rules_1.CustomerValidationRule());
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('CRM', new crm_rules_1.CustomerCreditCheckRule());
    }
    async createCustomer(request) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'CRM',
            metadata: { source: 'crm-service' }
        };
        // Execute business logic
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('CRM', request, 'create', context);
        if (!result.success) {
            throw new Error(`Customer creation failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        // Create customer entity
        const customer = {
            id: this.generateCustomerId(),
            ...result.data,
            currentBalance: 0,
            status: 'active',
            createdAt: new Date(),
            updatedAt: new Date()
        };
        // Save to repository
        await this.repository.create(customer);
        // Publish domain event
        await this.publishDomainEvent('CustomerCreated', {
            customerId: customer.id,
            customerName: customer.name,
            timestamp: new Date()
        });
        return customer;
    }
    async updateCustomer(customerId, request) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'update',
            domain: 'CRM',
            metadata: { source: 'crm-service', customerId }
        };
        // Get existing customer
        const existingCustomer = await this.repository.findById(customerId);
        if (!existingCustomer) {
            throw new Error(`Customer ${customerId} not found`);
        }
        // Merge with existing data
        const updateData = { ...existingCustomer, ...request };
        // Execute business logic
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('CRM', updateData, 'update', context);
        if (!result.success) {
            throw new Error(`Customer update failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        // Update customer entity
        const updatedCustomer = {
            ...result.data,
            updatedAt: new Date()
        };
        // Save to repository
        await this.repository.update(customerId, updatedCustomer);
        // Publish domain event
        await this.publishDomainEvent('CustomerUpdated', {
            customerId: updatedCustomer.id,
            changes: request,
            timestamp: new Date()
        });
        return updatedCustomer;
    }
    async getCustomer(customerId) {
        return this.repository.findById(customerId);
    }
    async getCustomers(filters) {
        return this.repository.find(filters);
    }
    async deleteCustomer(customerId) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'delete',
            domain: 'CRM',
            metadata: { source: 'crm-service', customerId }
        };
        // Get existing customer
        const existingCustomer = await this.repository.findById(customerId);
        if (!existingCustomer) {
            throw new Error(`Customer ${customerId} not found`);
        }
        // Execute business logic
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('CRM', existingCustomer, 'delete', context);
        if (!result.success) {
            throw new Error(`Customer deletion failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        // Delete from repository
        await this.repository.delete(customerId);
        // Publish domain event
        await this.publishDomainEvent('CustomerDeleted', {
            customerId,
            customerName: existingCustomer.name,
            timestamp: new Date()
        });
    }
    async updateCustomerBalance(customerId, amount) {
        const customer = await this.getCustomer(customerId);
        if (!customer) {
            throw new Error(`Customer ${customerId} not found`);
        }
        const newBalance = customer.currentBalance + amount;
        // Check if new balance exceeds credit limit
        if (newBalance > customer.creditLimit) {
            throw new Error(`Balance update would exceed credit limit. Current: ${customer.currentBalance}, Limit: ${customer.creditLimit}, Requested: ${amount}`);
        }
        return this.updateCustomer(customerId, { currentBalance: newBalance });
    }
    generateCustomerId() {
        return `CUST_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    getCurrentUserId() {
        // This would get the current user ID from the authentication context
        return 'system';
    }
    async publishDomainEvent(eventType, data) {
        // This would publish the domain event to the event bus
        console.log(`Publishing domain event: ${eventType}`, data);
    }
}
exports.CRMDomainService = CRMDomainService;
// Global CRM Domain Service
exports.crmDomainService = new CRMDomainService();
