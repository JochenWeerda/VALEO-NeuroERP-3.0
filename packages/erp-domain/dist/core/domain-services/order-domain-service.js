"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderDomainService = void 0;
const order_1 = require("../entities/order");
const STATUS_FLOW = {
    draft: ['confirmed', 'cancelled'],
    confirmed: ['processing', 'cancelled'],
    processing: ['shipped', 'cancelled'],
    shipped: ['delivered', 'cancelled'],
    delivered: ['invoiced'],
    invoiced: [],
    cancelled: [],
};
const STATUS_WEIGHTS = {
    draft: 0,
    confirmed: 1,
    processing: 2,
    shipped: 3,
    delivered: 4,
    invoiced: 5,
    cancelled: 99,
};
const DECIMAL_PRECISION = 2;
const MAX_ORDER_LIMIT_CAP = 500;
const CURRENCY_REGEX = /^[A-Z]{3}$/;
const MAX_TOLERANCE = 0.01;
class OrderDomainService {
    constructor(repository) {
        this.repository = repository;
    }
    async listOrders(filters = {}) {
        const normalized = {
            status: filters.status,
            documentType: filters.documentType,
            customerNumber: filters.customerNumber?.trim() ?? undefined,
            debtorNumber: filters.debtorNumber?.trim() ?? undefined,
            from: filters.from,
            to: filters.to,
            limit: clampLimit(filters.limit),
            offset: Math.max(filters.offset ?? 0, 0),
        };
        return this.repository.list(normalized);
    }
    async getOrder(id) {
        return this.repository.findById(id);
    }
    async createOrder(input) {
        this.assertCurrency(input.currency);
        this.assertAmountConsistency(input);
        const targetStatus = input.status ?? 'draft';
        this.assertStatus(targetStatus);
        const order = (0, order_1.createOrder)({ ...input, status: targetStatus });
        return this.repository.create(order);
    }
    async updateOrderStatus(id, status) {
        this.assertStatus(status);
        const current = await this.repository.findById(id);
        if (current === undefined || current === null) {
            throw new Error(`Order ${String(id)} not found`);
        }
        if (current.status === status) {
            return current;
        }
        const allowedTargets = STATUS_FLOW[current.status];
        if (!allowedTargets.includes(status)) {
            throw new Error(`Cannot transition order ${current.orderNumber} from ${current.status} to ${status}`);
        }
        return this.repository.updateStatus(id, status);
    }
    async deleteOrder(id) {
        const existing = await this.repository.findById(id);
        if (existing === undefined || existing === null) {
            return;
        }
        if (STATUS_WEIGHTS[existing.status] >= STATUS_WEIGHTS.invoiced) {
            throw new Error('Invoiced or cancelled orders cannot be deleted.');
        }
        await this.repository.delete(id);
    }
    assertStatus(status) {
        if (!(status in STATUS_FLOW)) {
            throw new Error(`Unsupported order status: ${status}`);
        }
    }
    assertCurrency(currency) {
        if (!currency || !CURRENCY_REGEX.test(currency)) {
            throw new Error(`Invalid ISO currency provided: ${currency}`);
        }
    }
    assertAmountConsistency(order) {
        const sum = order.items.reduce((acc, item) => acc + item.netPrice, 0);
        if (Math.abs(sum - order.netAmount) > MAX_TOLERANCE) {
            throw new Error(`Net amount ${order.netAmount} does not match item total ${sum.toFixed(DECIMAL_PRECISION)}.`);
        }
        const gross = Number((order.netAmount + order.vatAmount).toFixed(DECIMAL_PRECISION));
        if (Math.abs(gross - order.totalAmount) > MAX_TOLERANCE) {
            throw new Error(`Total amount ${order.totalAmount} does not equal net + VAT (${gross}).`);
        }
    }
}
exports.OrderDomainService = OrderDomainService;
function clampLimit(limit) {
    if (limit === undefined) {
        return order_1.DEFAULT_ORDER_LIMIT;
    }
    if (limit <= 0) {
        return order_1.DEFAULT_ORDER_LIMIT;
    }
    return Math.min(limit, MAX_ORDER_LIMIT_CAP);
}
//# sourceMappingURL=order-domain-service.js.map