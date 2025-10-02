"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CostingBillingService = void 0;
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class CostingBillingService {
    eventBus;
    constructor(eventBus) {
        this.eventBus = eventBus;
    }
    allocate(dto) {
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.costs.allocated', dto.tenantId, {
            shipmentId: dto.shipmentId,
            total: dto.total,
            currency: dto.currency,
            breakdown: dto.breakdown,
        });
        this.eventBus.publish(event);
    }
    approveFreightBill(tenantId, shipmentId, carrierId, amount, currency) {
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.freight.billApproved', tenantId, {
            shipmentId,
            carrierId,
            amount,
            currency,
        });
        this.eventBus.publish(event);
    }
}
exports.CostingBillingService = CostingBillingService;
