"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ERPApiController = void 0;
class ERPApiController {
    constructor(listOrders, getOrder, createOrder, updateOrderStatus, deleteOrder) {
        this.listOrders = listOrders;
        this.getOrder = getOrder;
        this.createOrder = createOrder;
        this.updateOrderStatus = updateOrderStatus;
        this.deleteOrder = deleteOrder;
    }
    register(router) {
        router.get('/erp/orders', (request) => this.handleListOrders(request));
        router.get('/erp/orders/:id', (request) => this.handleGetOrder(request));
        router.post('/erp/orders', (request) => this.handleCreateOrder(request));
        router.patch('/erp/orders/:id/status', (request) => this.handleUpdateStatus(request));
        router.delete('/erp/orders/:id', (request) => this.handleDeleteOrder(request));
    }
    async handleListOrders(request) {
        const payload = await this.listOrders.execute({
            status: pickString(request.query.status),
            documentType: pickString(request.query.documentType),
            customerNumber: pickString(request.query.customerNumber),
            debtorNumber: pickString(request.query.debtorNumber),
            from: pickString(request.query.from),
            to: pickString(request.query.to),
            limit: pickNumber(request.query.limit),
            offset: pickNumber(request.query.offset),
        });
        return { status: 200, body: payload };
    }
    async handleGetOrder(request) {
        const id = request.params.id;
        if (id === undefined || id === null) {
            return { status: 400, body: { message: 'Order id missing.' } };
        }
        const order = await this.getOrder.execute(id);
        if (order === undefined || order === null) {
            return { status: 404, body: { message: 'Order not found.' } };
        }
        return { status: 200, body: order };
    }
    async handleCreateOrder(request) {
        const body = request.body;
        if (body === undefined || body === null) {
            return { status: 400, body: { message: 'Request body is required.' } };
        }
        const created = await this.createOrder.execute(body);
        return { status: 201, body: created };
    }
    async handleUpdateStatus(request) {
        const id = request.params.id;
        if (id === undefined || id === null) {
            return { status: 400, body: { message: 'Order id missing.' } };
        }
        const body = request.body;
        if (body?.status == null) {
            return { status: 400, body: { message: 'Status is required.' } };
        }
        const updated = await this.updateOrderStatus.execute(id, body);
        return { status: 200, body: updated };
    }
    async handleDeleteOrder(request) {
        const id = request.params.id;
        if (id === undefined || id === null) {
            return { status: 400, body: { message: 'Order id missing.' } };
        }
        await this.deleteOrder.execute(id);
        return { status: 204 };
    }
}
exports.ERPApiController = ERPApiController;
function pickString(value) {
    if (Array.isArray(value)) {
        return value[0];
    }
    return value;
}
function pickNumber(value) {
    const raw = pickString(value);
    if (raw === undefined || raw === null)
        return undefined;
    const parsed = Number(raw);
    return Number.isFinite(parsed) ? parsed : undefined;
}
//# sourceMappingURL=erp-api-controller.js.map