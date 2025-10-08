"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RoutingOptimizationService = void 0;
const route_plan_1 = require("../../core/entities/route-plan");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class RoutingOptimizationService {
    constructor(shipmentRepository, routeRepository, eventBus, metrics) {
        this.shipmentRepository = shipmentRepository;
        this.routeRepository = routeRepository;
        this.eventBus = eventBus;
        this.metrics = metrics;
    }
    async planRoute(dto) {
        const shipment = await this.shipmentRepository.findShipmentById(dto.tenantId, dto.shipmentId);
        if (shipment === undefined || shipment === null) {
            throw new Error(`Cannot plan route: shipment ${dto.shipmentId} not found for tenant ${dto.tenantId}`);
        }
        const route = route_plan_1.RoutePlan.create({
            tenantId: dto.tenantId,
            shipmentId: dto.shipmentId,
            vehicleId: dto.vehicleId,
            driverId: dto.driverId,
            distanceKm: dto.distanceKm,
            legs: dto.legs.map((leg) => ({
                fromStopId: leg.fromStopId,
                toStopId: leg.toStopId,
                distanceKm: leg.distanceKm,
                etaFrom: new Date(leg.etaFrom),
                etaTo: new Date(leg.etaTo),
            })),
            stops: shipment.getStops(),
        });
        await this.routeRepository.saveRoutePlan(route);
        this.metrics.etaDeviationHistogram.observe({ tenant: dto.tenantId }, 0);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.route.planned', dto.tenantId, { route });
        this.eventBus.publish(event);
        return route;
    }
    async replanRoute(dto, reason) {
        const route = await this.planRoute(dto);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.route.replanned', dto.tenantId, { route, reason });
        this.eventBus.publish(event);
        return route;
    }
}
exports.RoutingOptimizationService = RoutingOptimizationService;
//# sourceMappingURL=routing-optimization-service.js.map