"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WeighbridgeIntegrationService = void 0;
const weighing_record_1 = require("../../core/entities/weighing-record");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class WeighbridgeIntegrationService {
    repository;
    eventBus;
    maxNetWeightKg = 40000;
    constructor(repository, eventBus) {
        this.repository = repository;
        this.eventBus = eventBus;
    }
    async capture(dto) {
        const record = weighing_record_1.WeighingRecord.create({
            tenantId: dto.tenantId,
            shipmentId: dto.shipmentId,
            grossWeightKg: dto.grossWeightKg,
            tareWeightKg: dto.tareWeightKg,
            source: dto.source,
        });
        await this.repository.saveWeighing(record);
        const measureEvent = (0, logistics_event_bus_1.buildEvent)('logistics.weight.measured', dto.tenantId, { weighing: record });
        this.eventBus.publish(measureEvent);
        if (record.netWeightKg > this.maxNetWeightKg) {
            const toleranceEvent = (0, logistics_event_bus_1.buildEvent)('logistics.weight.toleranceExceeded', dto.tenantId, {
                weighing: record,
                thresholdKg: this.maxNetWeightKg,
            });
            this.eventBus.publish(toleranceEvent);
        }
        return record;
    }
}
exports.WeighbridgeIntegrationService = WeighbridgeIntegrationService;
