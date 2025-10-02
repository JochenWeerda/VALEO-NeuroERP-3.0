"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryOrderRepository = void 0;
const node_crypto_1 = require("node:crypto");
const branded_types_1 = require("../../../../../packages/data-models/src/branded-types");
class InMemoryOrderRepository {
    constructor() {
        this.orders = new Map();
    }
    async list(filters = {}) {
        let result = Array.from(this.orders.values());
        if (filters.status) {
            result = result.filter((order) => order.status === filters.status);
        }
        if (filters.documentType) {
            result = result.filter((order) => order.documentType === filters.documentType);
        }
        if (filters.customerNumber) {
            result = result.filter((order) => order.customerNumber === filters.customerNumber);
        }
        if (filters.debtorNumber) {
            result = result.filter((order) => order.debtorNumber === filters.debtorNumber);
        }
        if (filters.from) {
            result = result.filter((order) => order.documentDate >= filters.from);
        }
        if (filters.to) {
            result = result.filter((order) => order.documentDate <= filters.to);
        }
        const offset = filters.offset ?? 0;
        const limit = filters.limit ?? result.length;
        return result.slice(offset, offset + limit);
    }
    async findById(id) {
        return this.orders.get(id) ?? null;
    }
    async create(order) {
        const id = (0, branded_types_1.brandValue)((0, node_crypto_1.randomUUID)(), 'OrderId');
        const createdAt = new Date();
        const orderEntity = {
            id,
            orderNumber: order.orderNumber ?? 'ORD-' + (0, node_crypto_1.randomUUID)().slice(0, 8).toUpperCase(),
            customerNumber: order.customerNumber,
            debtorNumber: order.debtorNumber,
            contactPerson: order.contactPerson,
            documentType: order.documentType,
            status: order.status ?? 'draft',
            documentDate: order.documentDate,
            currency: order.currency,
            netAmount: order.netAmount,
            vatAmount: order.vatAmount,
            totalAmount: order.totalAmount,
            notes: order.notes,
            items: order.items.map((item) => ({
                id: (0, node_crypto_1.randomUUID)(),
                articleNumber: item.articleNumber,
                description: item.description,
                quantity: item.quantity,
                unit: item.unit,
                unitPrice: item.unitPrice,
                discount: item.discount,
                netPrice: item.netPrice,
                createdAt,
                updatedAt: createdAt,
            })),
            createdAt,
            updatedAt: createdAt,
        };
        this.orders.set(orderEntity.id, orderEntity);
        return orderEntity;
    }
    async updateStatus(id, status) {
        const current = this.orders.get(id);
        if (!current) {
            throw new Error('Order ' + id + ' not found');
        }
        const updated = {
            ...current,
            status,
            updatedAt: new Date(),
        };
        this.orders.set(id, updated);
        return updated;
    }
    async delete(id) {
        this.orders.delete(id);
    }
}
exports.InMemoryOrderRepository = InMemoryOrderRepository;
