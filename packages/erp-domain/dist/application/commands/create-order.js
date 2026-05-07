"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreateOrderCommand = void 0;
const order_mapper_1 = require("../mappers/order-mapper");
class CreateOrderCommand {
    constructor(service) {
        this.service = service;
    }
    async execute(payload) {
        const created = await this.service.createOrder((0, order_mapper_1.toCreateOrderInput)(payload));
        return (0, order_mapper_1.toOrderDTO)(created);
    }
}
exports.CreateOrderCommand = CreateOrderCommand;
//# sourceMappingURL=create-order.js.map