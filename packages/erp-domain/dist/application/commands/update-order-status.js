"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UpdateOrderStatusCommand = void 0;
const order_mapper_1 = require("../mappers/order-mapper");
class UpdateOrderStatusCommand {
    constructor(service) {
        this.service = service;
    }
    async execute(id, payload) {
        const status = payload.status;
        const updated = await this.service.updateOrderStatus(id, status);
        return (0, order_mapper_1.toOrderDTO)(updated);
    }
}
exports.UpdateOrderStatusCommand = UpdateOrderStatusCommand;
//# sourceMappingURL=update-order-status.js.map