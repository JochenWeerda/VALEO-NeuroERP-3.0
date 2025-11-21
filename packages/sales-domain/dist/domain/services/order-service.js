"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderService = void 0;
class OrderService {
    deps;
    constructor(deps) {
        this.deps = deps;
    }
    async createOrder(data) {
        // Business validation
        if (data.lines.length === 0) {
            throw new Error('Order must have at least one line item');
        }
        // Check if order number already exists
        const existingOrder = await this.deps.orderRepo.findByNumber(data.orderNumber, data.tenantId);
        if (existingOrder) {
            throw new Error(`Order number ${data.orderNumber} already exists`);
        }
        // Validate line items
        for (const line of data.lines) {
            if (line.quantity <= 0) {
                throw new Error('Line item quantity must be positive');
            }
            if (line.unitPrice < 0) {
                throw new Error('Line item unit price cannot be negative');
            }
        }
        const order = await this.deps.orderRepo.create(data);
        return order;
    }
    async getOrder(id, tenantId) {
        return this.deps.orderRepo.findById(id, tenantId);
    }
    async updateOrder(id, data) {
        const existingOrder = await this.deps.orderRepo.findById(id, data.tenantId);
        if (existingOrder === undefined || existingOrder === null) {
            throw new Error(`Order ${id} not found`);
        }
        // Business validation
        if (data.lines) {
            if (data.lines.length === 0) {
                throw new Error('Order must have at least one line item');
            }
            for (const line of data.lines) {
                if (line.quantity <= 0) {
                    throw new Error('Line item quantity must be positive');
                }
                if (line.unitPrice < 0) {
                    throw new Error('Line item unit price cannot be negative');
                }
            }
        }
        const updatedOrder = await this.deps.orderRepo.update(id, data.tenantId, data);
        if (updatedOrder === undefined || updatedOrder === null) {
            throw new Error(`Failed to update order ${id}`);
        }
        return updatedOrder;
    }
    async confirmOrder(id, tenantId) {
        const order = await this.deps.orderRepo.findById(id, tenantId);
        if (order === undefined || order === null) {
            throw new Error(`Order ${id} not found`);
        }
        if (!order.canBeConfirmed()) {
            throw new Error('Order cannot be confirmed in its current state');
        }
        const updatedOrder = await this.deps.orderRepo.updateStatus(id, tenantId, 'Confirmed');
        if (updatedOrder === undefined || updatedOrder === null) {
            throw new Error(`Failed to confirm order`);
        }
        return updatedOrder;
    }
    async markOrderAsInvoiced(id, tenantId) {
        const order = await this.deps.orderRepo.findById(id, tenantId);
        if (order === undefined || order === null) {
            throw new Error(`Order ${id} not found`);
        }
        if (!order.canBeInvoiced()) {
            throw new Error('Order cannot be invoiced in its current state');
        }
        const updatedOrder = await this.deps.orderRepo.updateStatus(id, tenantId, 'Invoiced');
        if (updatedOrder === undefined || updatedOrder === null) {
            throw new Error(`Failed to mark order as invoiced`);
        }
        return updatedOrder;
    }
    async cancelOrder(id, tenantId) {
        const order = await this.deps.orderRepo.findById(id, tenantId);
        if (order === undefined || order === null) {
            throw new Error(`Order ${id} not found`);
        }
        if (!order.canBeCancelled()) {
            throw new Error('Order cannot be cancelled in its current state');
        }
        const updatedOrder = await this.deps.orderRepo.updateStatus(id, tenantId, 'Cancelled');
        if (updatedOrder === undefined || updatedOrder === null) {
            throw new Error(`Failed to cancel order`);
        }
        return updatedOrder;
    }
    async searchOrders(tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.orderRepo.findAll(tenantId, filters, pagination);
    }
    async getOrdersByCustomer(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.orderRepo.findByCustomerId(customerId, tenantId, filters, pagination);
    }
}
exports.OrderService = OrderService;
//# sourceMappingURL=order-service.js.map