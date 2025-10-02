"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DangerousColdchainService = void 0;
const safety_alert_1 = require("../../core/entities/safety-alert");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class DangerousColdchainService {
    constructor(repository, eventBus) {
        this.repository = repository;
        this.eventBus = eventBus;
    }
    async raiseAlert(dto) {
        const alert = safety_alert_1.SafetyAlert.create({
            tenantId: dto.tenantId,
            referenceId: dto.referenceId,
            shipmentId: dto.shipmentId,
            type: dto.type,
            severity: dto.severity,
            message: dto.message,
        });
        await this.repository.saveSafetyAlert(alert);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.safety.violation', dto.tenantId, { alert });
        this.eventBus.publish(event);
        return alert;
    }
    async raiseColdChainAlert(tenantId, referenceId, shipmentId, temperatureC, message) {
        const alert = safety_alert_1.SafetyAlert.create({
            tenantId,
            referenceId,
            shipmentId,
            type: 'temperature',
            severity: temperatureC > 8 || temperatureC < 2 ? 'critical' : 'warning',
            message,
        });
        await this.repository.saveSafetyAlert(alert);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.coldchain.alert', tenantId, { alert, temperatureC });
        this.eventBus.publish(event);
        return alert;
    }
}
exports.DangerousColdchainService = DangerousColdchainService;
//# sourceMappingURL=dangerous-coldchain-service.js.map