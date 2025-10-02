"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SlotDockYardService = void 0;
const yard_visit_1 = require("../../core/entities/yard-visit");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class SlotDockYardService {
    constructor(yardRepository, eventBus) {
        this.yardRepository = yardRepository;
        this.eventBus = eventBus;
    }
    async bookSlot(dto) {
        const yardVisit = yard_visit_1.YardVisit.create({
            tenantId: dto.tenantId,
            shipmentId: dto.shipmentId,
            gate: dto.gate,
            dock: dto.dock,
            scheduledWindow: dto.window
                ? { from: new Date(dto.window.from), to: new Date(dto.window.to) }
                : undefined,
        });
        await this.yardRepository.saveYardVisit(yardVisit);
        this.publish('logistics.slot.booked', dto.tenantId, { yardVisit });
        if (dto.dock) {
            this.publish('logistics.dock.assigned', dto.tenantId, { yardVisit });
        }
        return yardVisit;
    }
    async checkIn(tenantId, shipmentId) {
        return this.updateStatus(tenantId, shipmentId, 'checked_in');
    }
    async checkOut(tenantId, shipmentId) {
        return this.updateStatus(tenantId, shipmentId, 'checked_out');
    }
    async updateStatus(tenantId, shipmentId, status) {
        const yardVisit = await this.yardRepository.findYardVisitByShipmentId(tenantId, shipmentId);
        if (!yardVisit) {
            throw new Error(`Yard visit not found for shipment ${shipmentId}`);
        }
        yardVisit.updateStatus(status);
        await this.yardRepository.saveYardVisit(yardVisit);
        this.publish('logistics.yard.statusChanged', tenantId, { yardVisit });
        return yardVisit;
    }
    publish(eventType, tenantId, payload) {
        const event = (0, logistics_event_bus_1.buildEvent)(eventType, tenantId, payload);
        this.eventBus.publish(event);
    }
}
exports.SlotDockYardService = SlotDockYardService;
//# sourceMappingURL=slot-dock-yard-service.js.map