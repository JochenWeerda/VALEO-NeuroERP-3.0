"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TelematicsGatewayService = void 0;
const telemetry_record_1 = require("../../core/entities/telemetry-record");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class TelematicsGatewayService {
    constructor(telemetryRepository, routeRepository, eventBus) {
        this.telemetryRepository = telemetryRepository;
        this.routeRepository = routeRepository;
        this.eventBus = eventBus;
    }
    async ingest(dto) {
        const record = telemetry_record_1.TelemetryRecord.create({
            tenantId: dto.tenantId,
            vehicleId: dto.vehicleId,
            recordedAt: new Date(dto.recordedAt),
            lat: dto.lat,
            lon: dto.lon,
            speedKph: dto.speedKph,
            temperatureC: dto.temperatureC,
            fuelLevelPercent: dto.fuelLevelPercent,
            meta: dto.meta,
        });
        await this.telemetryRepository.saveTelemetry(record);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.position.updated', dto.tenantId, { telemetry: record });
        this.eventBus.publish(event);
        return record;
    }
    async calculateEta(tenantId, shipmentId, referenceTime = new Date()) {
        const route = await this.routeRepository.findRoutePlanByShipmentId(tenantId, shipmentId);
        if (!route) {
            return undefined;
        }
        const remainingLegs = route.legs.filter((leg) => leg.eta.to.getTime() >= referenceTime.getTime());
        if (remainingLegs.length === 0) {
            return 0;
        }
        const lastLeg = remainingLegs[remainingLegs.length - 1];
        const etaMinutes = Math.round((lastLeg.eta.to.getTime() - referenceTime.getTime()) / 60000);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.eta.updated', tenantId, {
            shipmentId,
            stopId: lastLeg.toStopId,
            eta: lastLeg.eta.to.toISOString(),
            confidence: 0.8,
        });
        this.eventBus.publish(event);
        return etaMinutes;
    }
}
exports.TelematicsGatewayService = TelematicsGatewayService;
//# sourceMappingURL=telematics-gateway-service.js.map