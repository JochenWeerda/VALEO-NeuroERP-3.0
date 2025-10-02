"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EmissionsService = void 0;
const emission_record_1 = require("../../core/entities/emission-record");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class EmissionsService {
    constructor(repository, eventBus) {
        this.repository = repository;
        this.eventBus = eventBus;
    }
    async calculate(dto) {
        const record = emission_record_1.EmissionRecord.create({
            tenantId: dto.tenantId,
            shipmentId: dto.shipmentId,
            co2eKg: dto.co2eKg,
            method: dto.method,
            factors: dto.factors,
        });
        await this.repository.saveEmission(record);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.emissions.updated', dto.tenantId, { emission: record });
        this.eventBus.publish(event);
        return record;
    }
}
exports.EmissionsService = EmissionsService;
//# sourceMappingURL=emissions-service.js.map