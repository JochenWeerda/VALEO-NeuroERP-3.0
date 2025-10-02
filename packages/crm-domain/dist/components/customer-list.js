"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.crmApiController = exports.CRMApiController = void 0;
const crm_domain_service_1 = require("../services/crm-domain-service");
class CRMApiController {
    async createCustomer(req, res) {
        try {
            const customer = await crm_domain_service_1.crmDomainService.createCustomer(req.body);
            res.status(201).json({
                success: true,
                data: customer,
                message: 'Customer created successfully'
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error.message,
                message: 'Failed to create customer'
            });
        }
    }
    async getCustomer(req, res) {
        try {
            const customerId = req.params.id;
            const customer = await crm_domain_service_1.crmDomainService.getCustomer(customerId);
            if (!customer) {
                res.status(404).json({
                    success: false,
                    message: 'Customer not found'
                });
                return;
            }
            res.status(200).json({
                success: true,
                data: customer
            });
        }
        catch (error) {
            res.status(500).json({
                success: false,
                error: error.message,
                message: 'Failed to get customer'
            });
        }
    }
    async updateCustomer(req, res) {
        try {
            const customerId = req.params.id;
            const customer = await crm_domain_service_1.crmDomainService.updateCustomer(customerId, req.body);
            res.status(200).json({
                success: true,
                data: customer,
                message: 'Customer updated successfully'
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error.message,
                message: 'Failed to update customer'
            });
        }
    }
    async deleteCustomer(req, res) {
        try {
            const customerId = req.params.id;
            await crm_domain_service_1.crmDomainService.deleteCustomer(customerId);
            res.status(200).json({
                success: true,
                message: 'Customer deleted successfully'
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error.message,
                message: 'Failed to delete customer'
            });
        }
    }
    async getCustomers(req, res) {
        try {
            const filters = req.query;
            const customers = await crm_domain_service_1.crmDomainService.getCustomers(filters);
            res.status(200).json({
                success: true,
                data: customers,
                count: customers.length
            });
        }
        catch (error) {
            res.status(500).json({
                success: false,
                error: error.message,
                message: 'Failed to get customers'
            });
        }
    }
    async updateCustomerBalance(req, res) {
        try {
            const customerId = req.params.id;
            const { amount } = req.body;
            if (typeof amount !== 'number') {
                res.status(400).json({
                    success: false,
                    message: 'Amount must be a number'
                });
                return;
            }
            const customer = await crm_domain_service_1.crmDomainService.updateCustomerBalance(customerId, amount);
            res.status(200).json({
                success: true,
                data: customer,
                message: 'Customer balance updated successfully'
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error.message,
                message: 'Failed to update customer balance'
            });
        }
    }
}
exports.CRMApiController = CRMApiController;
// Global CRM API Controller
exports.crmApiController = new CRMApiController();
//# sourceMappingURL=customer-list.js.map