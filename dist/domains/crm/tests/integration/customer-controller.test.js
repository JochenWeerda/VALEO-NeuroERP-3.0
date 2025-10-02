"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const strict_1 = __importDefault(require("node:assert/strict"));
const service_locator_1 = require("../../../../packages/utilities/src/service-locator");
const bootstrap_1 = require("../../src/bootstrap");
class TestRouter {
    constructor() {
        this.routes = new Map();
    }
    get(path, handler) {
        this.routes.set(`GET ${path}`, handler);
    }
    post(path, handler) {
        this.routes.set(`POST ${path}`, handler);
    }
    put(path, handler) {
        this.routes.set(`PUT ${path}`, handler);
    }
    delete(path, handler) {
        this.routes.set(`DELETE ${path}`, handler);
    }
}
(0, node_test_1.describe)('CRM API controller', () => {
    let locator;
    let router;
    (0, node_test_1.beforeEach)(() => {
        locator = service_locator_1.ServiceLocator.getInstance();
        locator.reset();
        (0, bootstrap_1.registerCrmDomain)(locator, { repository: 'in-memory' });
        router = new TestRouter();
        const controller = locator.resolve(bootstrap_1.CRM_SERVICE_KEYS.controller);
        controller.register(router);
    });
    (0, node_test_1.it)('registers CRUD handlers and serves customer listings', async () => {
        const listHandler = router.routes.get('GET /crm/customers');
        strict_1.default.ok(listHandler, 'list handler should be registered');
        const response = await listHandler({ params: {}, query: {}, body: undefined });
        strict_1.default.equal(response.status, 200);
        strict_1.default.ok(Array.isArray(response.body));
    });
    (0, node_test_1.it)('creates customers through the command pipeline', async () => {
        const createHandler = router.routes.get('POST /crm/customers');
        strict_1.default.ok(createHandler, 'create handler should be registered');
        const payload = {
            customerNumber: 'C-123',
            name: 'Integration Co.',
            type: 'company',
            status: 'active',
        };
        const createResponse = await createHandler({ params: {}, query: {}, body: payload });
        strict_1.default.equal(createResponse.status, 201);
        const created = createResponse.body;
        strict_1.default.ok(created.id);
        const listHandler = router.routes.get('GET /crm/customers');
        const listResponse = await listHandler({ params: {}, query: {}, body: undefined });
        const customers = listResponse.body;
        const found = customers.find((customer) => customer.id === created.id);
        strict_1.default.ok(found);
    });
});
