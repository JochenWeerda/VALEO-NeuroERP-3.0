"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const strict_1 = __importDefault(require("node:assert/strict"));
const customer_domain_service_1 = require("../../src/core/domain-services/customer-domain-service");
const in_memory_customer_repository_1 = require("../../src/infrastructure/repositories/in-memory-customer-repository");
(0, node_test_1.describe)('CustomerDomainService', () => {
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
        service = new customer_domain_service_1.CustomerDomainService(repository);
    });
    (0, node_test_1.it)('returns customers using default pagination', async () => {
        const result = await service.listCustomers();
        strict_1.default.equal(result.length, 1);
        strict_1.default.equal(result[0]?.name, 'Acme Corporation');
    });
    (0, node_test_1.it)('creates a new customer and assigns identifiers', async () => {
        const created = await service.createCustomer({
            customerNumber: 'C-002',
            name: 'Beta GmbH',
            type: 'company',
            status: 'active',
            email: 'contact@beta.example',
            leadScore: 42,
        });
        strict_1.default.ok(created.id, 'id should be branded');
        strict_1.default.equal(created.name, 'Beta GmbH');
        const all = await service.listCustomers({ limit: 10 });
        strict_1.default.equal(all.length, 2);
    });
    (0, node_test_1.it)('trims and validates customer names on update', async () => {
        const [existing] = await service.listCustomers();
        strict_1.default.ok(existing, 'seed customer should exist');
        const updated = await service.updateCustomer(existing.id, { name: '  Updated Corp  ' });
        strict_1.default.equal(updated.name, 'Updated Corp');
    });
    (0, node_test_1.it)('rejects empty customer names', async () => {
        await strict_1.default.rejects(service.createCustomer({
            customerNumber: 'C-003',
            name: '  ',
            type: 'company',
        }), /must not be empty/);
    });
    (0, node_test_1.it)('deletes customers', async () => {
        const [existing] = await service.listCustomers();
        await service.deleteCustomer(existing.id);
        const remaining = await service.listCustomers({ limit: 10 });
        strict_1.default.equal(remaining.length, 0);
    });
});
