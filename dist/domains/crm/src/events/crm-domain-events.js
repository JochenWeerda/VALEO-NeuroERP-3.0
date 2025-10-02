"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.crmRepository = exports.CRMRepository = void 0;
// domains/crm/src/repositories/crm-repository.ts
const repository_1 = require("@packages/utilities/repository");
class CRMRepository extends repository_1.Repository {
    constructor() {
        super('customers');
    }
    async findByEmail(email) {
        const customers = await this.find({ email });
        return customers.length > 0 ? customers[0] : null;
    }
    async findByPhone(phone) {
        const customers = await this.find({ phone });
        return customers.length > 0 ? customers[0] : null;
    }
    async findByStatus(status) {
        return this.find({ status });
    }
    async findByName(name) {
        return this.find({ name: { $regex: name, $options: 'i' } });
    }
    async findActiveCustomers() {
        return this.findByStatus('active');
    }
    async findInactiveCustomers() {
        return this.findByStatus('inactive');
    }
    async findSuspendedCustomers() {
        return this.findByStatus('suspended');
    }
    async findCustomersByCreditLimit(minLimit, maxLimit) {
        return this.find({
            creditLimit: { $gte: minLimit, $lte: maxLimit }
        });
    }
    async findCustomersByBalance(minBalance, maxBalance) {
        return this.find({
            currentBalance: { $gte: minBalance, $lte: maxBalance }
        });
    }
    async findHighValueCustomers(threshold = 10000) {
        return this.find({
            creditLimit: { $gte: threshold }
        });
    }
    async findCustomersNearCreditLimit(threshold = 0.8) {
        const customers = await this.findActiveCustomers();
        return customers.filter(customer => {
            const utilizationRatio = customer.currentBalance / customer.creditLimit;
            return utilizationRatio >= threshold;
        });
    }
    async getCustomerStatistics() {
        const allCustomers = await this.findAll();
        const activeCustomers = await this.findActiveCustomers();
        const inactiveCustomers = await this.findInactiveCustomers();
        const suspendedCustomers = await this.findSuspendedCustomers();
        const totalCreditLimit = allCustomers.reduce((sum, customer) => sum + customer.creditLimit, 0);
        const totalCurrentBalance = allCustomers.reduce((sum, customer) => sum + customer.currentBalance, 0);
        const averageCreditLimit = allCustomers.length > 0 ? totalCreditLimit / allCustomers.length : 0;
        return {
            totalCustomers: allCustomers.length,
            activeCustomers: activeCustomers.length,
            inactiveCustomers: inactiveCustomers.length,
            suspendedCustomers: suspendedCustomers.length,
            averageCreditLimit,
            totalCreditLimit,
            totalCurrentBalance
        };
    }
    async searchCustomers(query) {
        const customers = await this.findAll();
        return customers.filter(customer => customer.name.toLowerCase().includes(query.toLowerCase()) ||
            customer.email.toLowerCase().includes(query.toLowerCase()) ||
            customer.phone.includes(query));
    }
    async getCustomersByDateRange(startDate, endDate) {
        return this.find({
            createdAt: { $gte: startDate, $lte: endDate }
        });
    }
    async getRecentlyUpdatedCustomers(days = 7) {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);
        return this.find({
            updatedAt: { $gte: cutoffDate }
        });
    }
}
exports.CRMRepository = CRMRepository;
// Global CRM Repository
exports.crmRepository = new CRMRepository();
