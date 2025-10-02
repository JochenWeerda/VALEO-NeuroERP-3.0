"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderDomainService = void 0;
const node_crypto_1 = require("node:crypto");
const order_1 = require("../entities/order");
const STATUS_FLOW = {
    draft: ['confirmed', 'cancelled'],
    confirmed: ['delivered', 'invoiced', 'cancelled'],
    delivered: ['invoiced'],
    invoiced: [],
    cancelled: [],
};
const STATUS_ORDER = {
    draft: 0,
    confirmed: 1,
    delivered: 2,
    invoiced: 3,
    cancelled: 99,
};
const STATUS_WEIGHTS = STATUS_ORDER;
const CURRENCY_REGEX = /^[A-Z]{3}$/;
const MAX_TOLERANCE = 0.01;
class OrderDomainService {
    constructor(repository) {
        this.repository = repository;
    }
    async listOrders(filters = {}) {
        const normalized = {
            limit: filters.limit && filters.limit > 0 ? Math.min(filters.limit, 500) : order_1.DEFAULT_ORDER_LIMIT,
            offset: filters.offset && filters.offset >= 0 ? filters.offset : 0,
            status: filters.status,
            documentType: filters.documentType,
            customerNumber: filters.customerNumber?.trim() || undefined,
            debtorNumber: filters.debtorNumber?.trim() || undefined,
            from: filters.from,
            to: filters.to,
        };
        return this.repository.list(normalized);
    }
    async getOrder(id) {
        return this.repository.findById(id);
    }
    async createOrder(payload) {
        this.assertItems(payload.items);
        this.assertCurrency(payload.currency);
        this.assertAmountConsistency(payload);
        const draftNumber = payload.orderNumber ?? this.generateOrderNumber();
        const order = {
            ...payload,
            orderNumber: draftNumber,
            status: (payload.status ?? 'draft'),
        };
        if (!(order.status in STATUS_FLOW)) {
            throw new Error('Unsupported initial order status: ' + order.status);
        }
        return this.repository.create(order);
    }
    async updateOrderStatus(id, status) {
        if (!(status in STATUS_FLOW)) {
            throw new Error('Unsupported order status: ' + status);
        }
        const current = await this.repository.findById(id);
        if (!current) {
            throw new Error('Order ' + String(id) + ' not found');
        }
        if (current.status === status) {
            return current;
        }
        const allowedTargets = STATUS_FLOW[current.status];
        if (!allowedTargets.includes(status)) {
            throw new Error('Cannot transition order ' + current.orderNumber + ' from ' + current.status + ' to ' + status);
        }
        return this.repository.updateStatus(id, status);
    }
    async deleteOrder(id) {
        const current = await this.repository.findById(id);
        if (!current) {
            return;
        }
        if (STATUS_WEIGHTS[current.status] >= STATUS_WEIGHTS.invoiced) {
            throw new Error('Invoiced or cancelled orders cannot be deleted.');
        }
        await this.repository.delete(id);
    }
    assertItems(items) {
        if (!items.length) {
            throw new Error('An order requires at least one position.');
        }
        for (const position of items) {
            if (position.quantity <= 0) {
                throw new Error('Order item ' + position.articleNumber + ' must have a positive quantity.');
            }
            if (position.unitPrice < 0) {
                throw new Error('Order item ' + position.articleNumber + ' has an invalid unit price.');
            }
        }
    }
    assertCurrency(currency) {
        if (!currency || !CURRENCY_REGEX.test(currency)) {
            throw new Error('Invalid ISO currency provided: ' + currency);
        }
    }
    assertAmountConsistency(order) {
        const sum = order.items.reduce((acc, item) => acc + item.netPrice, 0);
        const precision = Math.abs(sum - order.netAmount);
        if (precision > MAX_TOLERANCE) {
            throw new Error('Net amount ' + order.netAmount + ' does not match item total ' + sum.toFixed(2) + '.');
        }
        const gross = Number((order.netAmount + order.vatAmount).toFixed(2));
        if (Math.abs(gross - order.totalAmount) > MAX_TOLERANCE) {
            throw new Error('Total amount ' + order.totalAmount + ' does not equal net + VAT (' + gross + ').');
        }
    }
    generateOrderNumber() {
        const id = (0, node_crypto_1.randomUUID)();
        return 'ORD-' + id.slice(0, 8).toUpperCase();
    }
}
exports.OrderDomainService = OrderDomainService;
