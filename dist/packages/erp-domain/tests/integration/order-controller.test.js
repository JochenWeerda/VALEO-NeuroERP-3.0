"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const strict_1 = __importDefault(require("node:assert/strict"));
const utilities_1 = require("@valero-neuroerp/utilities");
const bootstrap_1 = require("../../src/bootstrap");
class TestRouter {
    routes = new Map();
    get(path, handler) {
        this.routes.set('GET ' + path, handler);
    }
    post(path, handler) {
        this.routes.set('POST ' + path, handler);
    }
    patch(path, handler) {
        this.routes.set('PATCH ' + path, handler);
    }
    delete(path, handler) {
        this.routes.set('DELETE ' + path, handler);
    }
}
(0, node_test_1.describe)('ERP API controller', () => {
    let locator;
    let router;
    (0, node_test_1.beforeEach)(() => {
        locator = utilities_1.ServiceLocator.getInstance();
        locator.reset();
        (0, bootstrap_1.registerErpDomain)(locator, { repository: 'in-memory' });
        router = new TestRouter();
        const controller = locator.resolve(bootstrap_1.ERP_SERVICE_KEYS.controller);
        controller.register(router);
    });
    (0, node_test_1.it)('registers ERP routes', () => {
        strict_1.default.ok(router.routes.has('GET /erp/orders'));
        strict_1.default.ok(router.routes.has('POST /erp/orders'));
        strict_1.default.ok(router.routes.has('PATCH /erp/orders/:id/status'));
        strict_1.default.ok(router.routes.has('DELETE /erp/orders/:id'));
    });
    (0, node_test_1.it)('creates and fetches orders through the API', async () => {
        const createHandler = router.routes.get('POST /erp/orders');
        strict_1.default.ok(createHandler);
        const payload = {
            customerNumber: 'CUST-001',
            debtorNumber: 'DEB-001',
            contactPerson: 'Max Mustermann',
            documentType: 'order',
            documentDate: '2024-01-10T00:00:00.000Z',
            currency: 'EUR',
            netAmount: 100,
            vatAmount: 19,
            totalAmount: 119,
            items: [
                {
                    articleNumber: 'ART-001',
                    description: 'Demo product',
                    quantity: 1,
                    unit: 'piece',
                    unitPrice: 100,
                    netPrice: 100,
                },
            ],
        };
        const createResponse = await createHandler({ params: {}, query: {}, body: payload });
        strict_1.default.equal(createResponse.status, 201);
        const created = createResponse.body;
        strict_1.default.ok(created.id);
        const listHandler = router.routes.get('GET /erp/orders');
        strict_1.default.ok(listHandler);
        const listResponse = await listHandler({ params: {}, query: {}, body: undefined });
        strict_1.default.equal(listResponse.status, 200);
        const orders = listResponse.body;
        strict_1.default.ok(orders.some((order) => order.id === created.id));
    });
});
