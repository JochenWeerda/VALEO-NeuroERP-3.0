"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReturnsService = void 0;
const return_order_1 = require("../../core/entities/return-order");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class ReturnsService {
    constructor(repository, eventBus) {
        this.repository = repository;
        this.eventBus = eventBus;
    }
    async create(dto) {
        const order = return_order_1.ReturnOrder.create({
            tenantId: dto.tenantId,
            originalShipmentId: dto.originalShipmentId,
            pickupAddress: dto.pickupAddress,
            returnReason: dto.returnReason,
        });
        await this.repository.saveReturnOrder(order);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.return.created', dto.tenantId, { returnOrder: order });
        this.eventBus.publish(event);
        return order;
    }
    async receive(tenantId, returnId) {
        const order = await this.repository.findReturnOrderById(tenantId, returnId);
        if (order === undefined || order === null) {
            throw new Error(`Return order ${returnId} not found for tenant ${tenantId}`);
        }
        order.updateStatus('received');
        await this.repository.saveReturnOrder(order);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.return.received', tenantId, { returnOrder: order });
        this.eventBus.publish(event);
        return order;
    }
}
exports.ReturnsService = ReturnsService;
//# sourceMappingURL=returns-service.js.map