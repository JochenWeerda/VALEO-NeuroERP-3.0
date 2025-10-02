"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const strict_1 = __importDefault(require("node:assert/strict"));
const crm_domain_service_1 = require("../../src/services/crm-domain-service");
const in_memory_customer_repository_1 = require("../../src/infrastructure/repositories/in-memory-customer-repository");
(0, node_test_1.describe)('CRMDomainService', () => {
    let repository;
    let service;
    (0, node_test_1.beforeEach)(() => {
        const seed = [
            {
                customerNumber: 'C-001',
                name: 'Acme Corporation',
                type: 'company',
                status: 'active',
                email: 'sales@acme.example',
                address: {
                    city: 'Berlin',
                    country: 'DE',
                },
                industry: 'Automotive',
                notes: 'Key account',
            },
        ];
        repository = new in_memory_customer_repository_1.InMemoryCustomerRepository(seed);
        service = new crm_domain_service_1.CRMDomainService(repository);
    });
    (0, node_test_1.it)('lists seeded customers', async () => {
        const customers = await service.listCustomers();
        strict_1.default.equal(customers.length, 1);
        strict_1.default.equal(customers[0]?.name, 'Acme Corporation');
    });
    (0, node_test_1.it)('creates a new customer', async () => {
        const created = await service.createCustomer({
            customerNumber: 'C-002',
            name: 'Beta GmbH',
            type: 'company',
            status: 'active',
            email: 'hello@beta.example',
        });
        strict_1.default.equal(created.name, 'Beta GmbH');
        const all = await service.listCustomers({ limit: 10 });
        strict_1.default.equal(all.length, 2);
    });
    (0, node_test_1.it)('updates an existing customer', async () => {
        const [existing] = await service.listCustomers();
        strict_1.default.ok(existing);
        const updated = await service.updateCustomer(existing.id, { name: 'Updated Corp' });
        strict_1.default.equal(updated.name, 'Updated Corp');
    });
    (0, node_test_1.it)('deletes customers', async () => {
        const [existing] = await service.listCustomers();
        strict_1.default.ok(existing);
        await service.deleteCustomer(existing.id);
        const remaining = await service.listCustomers();
        strict_1.default.equal(remaining.length, 0);
    });
});
