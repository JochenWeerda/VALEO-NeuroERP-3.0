"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GetOrderQuery = void 0;
const order_mapper_1 = require("../mappers/order-mapper");
class GetOrderQuery {
    constructor(service) {
        this.service = service;
    }
    async execute(id) {
        const order = await this.service.getOrder(id);
        return (order !== undefined && order !== null) ? (0, order_mapper_1.toOrderDTO)(order) : null;
    }
}
exports.GetOrderQuery = GetOrderQuery;
//# sourceMappingURL=get-order.js.map