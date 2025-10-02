"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProofOfDeliveryService = void 0;
const proof_of_delivery_1 = require("../../core/entities/proof-of-delivery");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class ProofOfDeliveryService {
    constructor(repository, eventBus) {
        this.repository = repository;
        this.eventBus = eventBus;
    }
    async capture(dto) {
        const pod = proof_of_delivery_1.ProofOfDelivery.create({
            tenantId: dto.tenantId,
            shipmentId: dto.shipmentId,
            stopId: dto.stopId,
            signedBy: dto.signedBy,
            signatureRef: dto.signatureRef,
            photoRefs: dto.photoRefs,
            scans: dto.scans,
            exceptions: dto.exceptions,
        });
        await this.repository.saveProofOfDelivery(pod);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.pod.captured', dto.tenantId, { pod });
        this.eventBus.publish(event);
        return pod;
    }
}
exports.ProofOfDeliveryService = ProofOfDeliveryService;
//# sourceMappingURL=proof-of-delivery-service.js.map