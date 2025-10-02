"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ShipmentOrchestratorService = void 0;
const shipment_1 = require("../../core/entities/shipment");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class ShipmentOrchestratorService {
    constructor(repository, eventBus, metrics) {
        this.repository = repository;
        this.eventBus = eventBus;
        this.metrics = metrics;
    }
    async createShipment(dto) {
        const shipment = shipment_1.Shipment.create({
            tenantId: dto.tenantId,
            reference: dto.reference,
            origin: dto.origin,
            destination: dto.destination,
            priority: dto.priority,
            incoterm: dto.incoterm,
            stops: dto.stops.map((stop) => ({
                sequence: stop.sequence,
                type: stop.type,
                address: stop.address,
                window: stop.window ? { from: new Date(stop.window.from), to: new Date(stop.window.to) } : undefined,
            })),
            payload: dto.payload,
        });
        await this.repository.saveShipment(shipment);
        this.metrics.shipmentsCounter.inc({ tenant: dto.tenantId, status: shipment.status });
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.shipment.created', dto.tenantId, { shipment: shipment.toJSON() });
        this.eventBus.publish(event);
        return shipment;
    }
    async cancelShipment(tenantId, shipmentId, reason) {
        const shipment = await this.repository.findShipmentById(tenantId, shipmentId);
        if (!shipment) {
            throw new Error(`Shipment ${shipmentId} not found for tenant ${tenantId}`);
        }
        shipment.updateStatus('canceled');
        await this.repository.saveShipment(shipment);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.shipment.canceled', tenantId, { shipmentId, reason });
        this.eventBus.publish(event);
    }
    async listShipments(tenantId) {
        return this.repository.listShipmentsByTenant(tenantId);
    }
    async getShipment(tenantId, shipmentId) {
        return this.repository.findShipmentById(tenantId, shipmentId);
    }
}
exports.ShipmentOrchestratorService = ShipmentOrchestratorService;
//# sourceMappingURL=shipment-orchestrator-service.js.map