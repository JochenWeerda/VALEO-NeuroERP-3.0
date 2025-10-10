"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ListOrdersQuery = void 0;
const order_mapper_1 = require("../mappers/order-mapper");
class ListOrdersQuery {
    constructor(service) {
        this.service = service;
    }
    async execute(options = {}) {
        const filters = {
            status: options.status,
            documentType: options.documentType,
            customerNumber: options.customerNumber,
            debtorNumber: options.debtorNumber,
            from: options.from != null ? new Date(options.from) : undefined,
            to: options.to != null ? new Date(options.to) : undefined,
            limit: options.limit,
            offset: options.offset,
        };
        const orders = await this.service.listOrders(filters);
        return orders.map(order_mapper_1.toOrderDTO);
    }
}
exports.ListOrdersQuery = ListOrdersQuery;
//# sourceMappingURL=list-orders.js.map