"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_ORDER_LIMIT = void 0;
exports.createOrder = createOrder;
exports.withOrderStatus = withOrderStatus;
exports.cloneOrder = cloneOrder;
const data_models_1 = require("@valero-neuroerp/data-models");
exports.DEFAULT_ORDER_LIMIT = 50;
function createOrder(input) {
    if (!input.customerNumber || !input.customerNumber.trim()) {
        throw new Error('customerNumber is required');
    }
    if (!input.debtorNumber || !input.debtorNumber.trim()) {
        throw new Error('debtorNumber is required');
    }
    if (!input.items.length) {
        throw new Error('order requires at least one item');
    }
    const id = (0, data_models_1.createId)('OrderId');
    const orderNumber = input.orderNumber ?? generateOrderNumber();
    const now = new Date();
    const items = input.items.map((item) => createOrderItem(item, now));
    return {
        id,
        orderNumber,
        customerNumber: input.customerNumber,
        debtorNumber: input.debtorNumber,
        contactPerson: input.contactPerson,
        documentType: input.documentType,
        status: input.status ?? 'draft',
        documentDate: new Date(input.documentDate),
        currency: input.currency,
        netAmount: input.netAmount,
        vatAmount: input.vatAmount,
        totalAmount: input.totalAmount,
        notes: input.notes,
        items,
        createdAt: now,
        updatedAt: now,
    };
}
function withOrderStatus(order, status) {
    return {
        ...order,
        status,
        updatedAt: new Date(),
    };
}
function cloneOrder(order) {
    return {
        ...order,
        items: order.items.map((item) => ({ ...item })),
    };
}
function createOrderItem(input, timestamp) {
    return {
        id: (0, data_models_1.createId)('OrderItemId'),
        articleNumber: input.articleNumber,
        description: input.description,
        quantity: input.quantity,
        unit: input.unit,
        unitPrice: input.unitPrice,
        discount: input.discount ?? 0,
        netPrice: input.netPrice,
        createdAt: timestamp,
        updatedAt: timestamp,
    };
}
function generateOrderNumber() {
    return `ORD-${Date.now().toString(36).toUpperCase()}`;
}
