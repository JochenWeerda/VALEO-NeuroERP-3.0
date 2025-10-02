"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CarrierConnectService = void 0;
const carrier_document_1 = require("../../core/entities/carrier-document");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class CarrierConnectService {
    repository;
    eventBus;
    constructor(repository, eventBus) {
        this.repository = repository;
        this.eventBus = eventBus;
    }
    async createLabel(dto) {
        return this.persistDocument('label', 'logistics.carrier.labelCreated', dto);
    }
    async submitManifest(dto) {
        return this.persistDocument('manifest', 'logistics.carrier.manifestSubmitted', dto);
    }
    async registerInvoice(dto) {
        return this.persistDocument('invoice', 'logistics.carrier.invoiceReceived', dto);
    }
    async persistDocument(type, eventType, dto) {
        const document = carrier_document_1.CarrierDocument.create({
            tenantId: dto.tenantId,
            carrierId: dto.carrierId,
            type,
            reference: dto.reference,
            payload: dto.payload,
        });
        await this.repository.saveCarrierDocument(document);
        const event = (0, logistics_event_bus_1.buildEvent)(eventType, dto.tenantId, { document });
        this.eventBus.publish(event);
        return document;
    }
}
exports.CarrierConnectService = CarrierConnectService;
