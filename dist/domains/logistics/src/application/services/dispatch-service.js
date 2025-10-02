"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DispatchService = void 0;
const dispatch_assignment_1 = require("../../core/entities/dispatch-assignment");
const logistics_event_bus_1 = require("../../infrastructure/messaging/logistics-event-bus");
class DispatchService {
    dispatchRepository;
    routeRepository;
    eventBus;
    metrics;
    constructor(dispatchRepository, routeRepository, eventBus, metrics) {
        this.dispatchRepository = dispatchRepository;
        this.routeRepository = routeRepository;
        this.eventBus = eventBus;
        this.metrics = metrics;
    }
    async assign(dto) {
        const route = await this.routeRepository.findRoutePlanById(dto.tenantId, dto.routeId);
        if (!route) {
            throw new Error(Route, not, found);
            for (tenant;;)
                ;
        }
        const assignment = dispatch_assignment_1.DispatchAssignment.create({
            tenantId: dto.tenantId,
            routeId: dto.routeId,
            driverId: dto.driverId,
            vehicleId: dto.vehicleId,
            trailerId: dto.trailerId,
        });
        await this.dispatchRepository.saveAssignment(assignment);
        this.metrics.dispatchGauge.inc({ tenant: dto.tenantId }, 1);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.dispatch.assigned', dto.tenantId, { assignment });
        this.eventBus.publish(event);
        route.updateStatus('in_progress');
        await this.routeRepository.saveRoutePlan(route);
        return assignment;
    }
    async reassign(dto, previousDriverId) {
        const assignment = await this.assign(dto);
        assignment.updateStatus('reassigned');
        await this.dispatchRepository.saveAssignment(assignment);
        const event = (0, logistics_event_bus_1.buildEvent)('logistics.dispatch.changed', dto.tenantId, { assignment, previousDriverId });
        this.eventBus.publish(event);
        return assignment;
    }
}
exports.DispatchService = DispatchService;
