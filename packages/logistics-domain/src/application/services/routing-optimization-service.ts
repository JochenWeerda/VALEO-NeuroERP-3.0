import { RoutePlan } from '../../core/entities/route-plan';
import { ShipmentRepository, RoutePlanRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { LogisticsMetrics } from '../../infrastructure/observability/metrics';
import { RoutingPlanRequestDto } from '../dto/logistics-dtos';

export class RoutingOptimizationService {
  constructor(
    private readonly shipmentRepository: ShipmentRepository,
    private readonly routeRepository: RoutePlanRepository,
    private readonly eventBus: LogisticsEventBus,
    private readonly metrics: LogisticsMetrics,
  ) {}

  async planRoute(dto: RoutingPlanRequestDto): Promise<RoutePlan> {
    const shipment = await this.shipmentRepository.findShipmentById(dto.tenantId, dto.shipmentId);
    if (!shipment) {
      throw new Error(`Cannot plan route: shipment ${dto.shipmentId} not found for tenant ${dto.tenantId}`);
    }

    const route = RoutePlan.create({
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

    const event = buildEvent('logistics.route.planned', dto.tenantId, { route });
    this.eventBus.publish(event);

    return route;
  }

  async replanRoute(dto: RoutingPlanRequestDto, reason: string): Promise<RoutePlan> {
    const route = await this.planRoute(dto);
    const event = buildEvent('logistics.route.replanned', dto.tenantId, { route, reason });
    this.eventBus.publish(event);
    return route;
  }
}
