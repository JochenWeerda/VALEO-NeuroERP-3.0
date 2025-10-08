import { DispatchAssignment } from '../../core/entities/dispatch-assignment';
import { DispatchRepository, RoutePlanRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { LogisticsMetrics } from '../../infrastructure/observability/metrics';
import { DispatchAssignDto } from '../dto/logistics-dtos';

export class DispatchService {
  constructor(
    private readonly dispatchRepository: DispatchRepository,
    private readonly routeRepository: RoutePlanRepository,
    private readonly eventBus: LogisticsEventBus,
    private readonly metrics: LogisticsMetrics,
  ) {}

  async assign(dto: DispatchAssignDto): Promise<DispatchAssignment> {
    const route = await this.routeRepository.findRoutePlanById(dto.tenantId, dto.routeId);
    if (route === undefined || route === null) {
      throw new Error(`Route ${dto.routeId} not found for tenant ${dto.tenantId}`);
    }

    const assignment = DispatchAssignment.create({
      tenantId: dto.tenantId,
      routeId: dto.routeId,
      driverId: dto.driverId,
      vehicleId: dto.vehicleId,
      trailerId: dto.trailerId,
    });

    await this.dispatchRepository.saveAssignment(assignment);
    this.metrics.dispatchGauge.inc({ tenant: dto.tenantId }, 1);

    const event = buildEvent('logistics.dispatch.assigned', dto.tenantId, { assignment });
    this.eventBus.publish(event);

    route.updateStatus('in_progress');
    await this.routeRepository.saveRoutePlan(route);

    return assignment;
  }

  async reassign(dto: DispatchAssignDto, previousDriverId: string): Promise<DispatchAssignment> {
    const assignment = await this.assign(dto);
    assignment.updateStatus('reassigned');
    await this.dispatchRepository.saveAssignment(assignment);
    const event = buildEvent('logistics.dispatch.changed', dto.tenantId, { assignment, previousDriverId });
    this.eventBus.publish(event);
    return assignment;
  }
}

