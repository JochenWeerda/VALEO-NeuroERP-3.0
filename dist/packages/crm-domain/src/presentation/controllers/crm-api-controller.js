"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CRMApiController = void 0;
class CRMApiController {
    getCustomers;
    createCustomer;
    updateCustomer;
    deleteCustomer;
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
        const filters = this.parseQuery(request.query);
        const customers = await this.getCustomers.execute(filters);
        return { status: 200, body: customers };
    }
    async handleCreateCustomer(request) {
        const payload = request.body;
        if (!payload) {
            return { status: 400, body: { message: 'Request body is required' } };
        }
        try {
            const created = await this.createCustomer.execute(payload);
            return { status: 201, body: created };
        }
        catch (error) {
            return toHttpError(error);
        }
    }
    async handleUpdateCustomer(request) {
        const id = request.params.id;
        if (!id) {
            return { status: 400, body: { message: 'Customer id missing' } };
        }
        const payload = request.body;
        if (!payload) {
            return { status: 400, body: { message: 'Request body is required' } };
        }
        try {
            const updated = await this.updateCustomer.execute(id, payload);
            return { status: 200, body: updated };
        }
        catch (error) {
            return toHttpError(error);
        }
    }
    async handleDeleteCustomer(request) {
        const id = request.params.id;
        if (!id) {
            return { status: 400, body: { message: 'Customer id missing' } };
        }
        try {
            await this.deleteCustomer.execute(id);
            return { status: 204 };
        }
        catch (error) {
            return toHttpError(error);
        }
    }
    parseQuery(query) {
        const toStringValue = (value) => Array.isArray(value) ? value[0] : value;
        return {
            search: toStringValue(query.search),
            status: toStringValue(query.status),
            type: toStringValue(query.type),
            limit: toNumber(query.limit),
            offset: toNumber(query.offset),
        };
    }
}
exports.CRMApiController = CRMApiController;
function toNumber(value) {
    const raw = Array.isArray(value) ? value[0] : value;
    if (!raw) {
        return undefined;
    }
    const parsed = Number(raw);
    return Number.isFinite(parsed) ? parsed : undefined;
}
function toHttpError(error) {
    if (error instanceof Error) {
        const message = error.message;
        if (message.toLowerCase().includes('not found')) {
            return { status: 404, body: { message } };
        }
        return { status: 400, body: { message } };
    }
    return { status: 500, body: { message: 'Unknown error' } };
}
