"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CRMApiController = void 0;
class CRMApiController {
    constructor(getCustomers, createCustomer, updateCustomer, deleteCustomer) {
        this.getCustomers = getCustomers;
        this.createCustomer = createCustomer;
        this.updateCustomer = updateCustomer;
        this.deleteCustomer = deleteCustomer;
    }
    register(router) {
        router.get('/crm/customers', (request) => this.handleGetCustomers(request));
        router.post('/crm/customers', (request) => this.handleCreateCustomer(request));
        router.put('/crm/customers/:id', (request) => this.handleUpdateCustomer(request));
        router.delete('/crm/customers/:id', (request) => this.handleDeleteCustomer(request));
    }
    async handleGetCustomers(request) {
        const filters = {
            search: asString(request.query.search),
            status: asString(request.query.status),
            type: asString(request.query.type),
            limit: asNumber(request.query.limit),
            offset: asNumber(request.query.offset),
        };
        const payload = await this.getCustomers.execute(filters);
        return { status: 200, body: payload };
    }
    async handleCreateCustomer(request) {
        const body = request.body;
        if (!body) {
            return { status: 400, body: { message: 'Request body is required.' } };
        }
        const created = await this.createCustomer.execute(body);
        return { status: 201, body: created };
    }
    async handleUpdateCustomer(request) {
        const id = request.params.id;
        if (!id) {
            return { status: 400, body: { message: 'Customer id missing.' } };
        }
        const body = request.body;
        if (!body) {
            return { status: 400, body: { message: 'Request body is required.' } };
        }
        const updated = await this.updateCustomer.execute(id, body);
        return { status: 200, body: updated };
    }
    async handleDeleteCustomer(request) {
        const id = request.params.id;
        if (!id) {
            return { status: 400, body: { message: 'Customer id missing.' } };
        }
        await this.deleteCustomer.execute(id);
        return { status: 204 };
    }
}
exports.CRMApiController = CRMApiController;
function asString(value) {
    if (Array.isArray(value)) {
        return value[0];
    }
    return value;
}
function asNumber(value) {
    const str = asString(value);
    if (!str)
        return undefined;
    const parsed = Number(str);
    return Number.isFinite(parsed) ? parsed : undefined;
}
