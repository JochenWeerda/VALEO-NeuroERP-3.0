"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const strict_1 = __importDefault(require("node:assert/strict"));
const order_domain_service_1 = require("../../src/core/domain-services/order-domain-service");
const in_memory_order_repository_1 = require("../../src/infrastructure/repositories/in-memory-order-repository");
function buildSampleOrder() {
    return {
        customerNumber: 'CUST-001',
        debtorNumber: 'DEB-001',
        contactPerson: 'Max Mustermann',
        documentType: 'order',
        status: 'draft',
        documentDate: new Date('2024-01-01'),
        currency: 'EUR',
        netAmount: 100,
        vatAmount: 19,
        totalAmount: 119,
        notes: 'Test order',
        items: [
            {
                articleNumber: 'ART-001',
                description: 'Demo product',
                quantity: 1,
                unit: 'piece',
                unitPrice: 100,
                discount: 0,
                netPrice: 100,
            },
        ],
    };
}
(0, node_test_1.describe)('OrderDomainService', () => {
    (0, node_test_1.it)('creates a valid order', async () => {
        const repository = new in_memory_order_repository_1.InMemoryOrderRepository();
        const service = new order_domain_service_1.OrderDomainService(repository);
        const created = await service.createOrder(buildSampleOrder());
        strict_1.default.equal(created.netAmount, 100);
        strict_1.default.equal(created.items.length, 1);
    });
    (0, node_test_1.it)('rejects inconsistent totals', async () => {
        const repository = new in_memory_order_repository_1.InMemoryOrderRepository();
        const service = new order_domain_service_1.OrderDomainService(repository);
        await strict_1.default.rejects(() => service.createOrder({
            ...buildSampleOrder(),
            netAmount: 200,
        }), /Net amount/);
    });
    (0, node_test_1.it)('enforces status transitions', async () => {
        const repository = new in_memory_order_repository_1.InMemoryOrderRepository();
        const service = new order_domain_service_1.OrderDomainService(repository);
        const created = await service.createOrder(buildSampleOrder());
        await service.updateOrderStatus(created.id, 'confirmed');
        await strict_1.default.rejects(() => service.updateOrderStatus(created.id, 'draft'), /Cannot transition/);
    });
});
