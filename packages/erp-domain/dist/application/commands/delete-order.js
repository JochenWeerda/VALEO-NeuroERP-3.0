"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DeleteOrderCommand = void 0;
class DeleteOrderCommand {
    constructor(service) {
        this.service = service;
    }
    async execute(id) {
        await this.service.deleteOrder(id);
    }
}
exports.DeleteOrderCommand = DeleteOrderCommand;
//# sourceMappingURL=delete-order.js.map