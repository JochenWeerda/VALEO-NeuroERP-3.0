"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FreightRatingService = void 0;
const freight_rate_1 = require("../../core/entities/freight-rate");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class FreightRatingService {
    constructor(repository, eventBus) {
        this.repository = repository;
        this.eventBus = eventBus;
    }
    async quote(dto) {
        const rate = freight_rate_1.FreightRate.create({
            tenantId: dto.tenantId,
            shipmentId: dto.shipmentId,
            currency: dto.currency,
            baseAmount: dto.baseAmount,
            surcharges: dto.surcharges,
            explain: dto.explain,
        });
        await this.repository.saveFreightRate(rate);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.freight.rated', dto.tenantId, { freightRate: rate });
        this.eventBus.publish(event);
        return rate;
    }
}
exports.FreightRatingService = FreightRatingService;
//# sourceMappingURL=freight-rating-service.js.map