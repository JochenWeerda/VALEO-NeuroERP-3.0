import { RoutePlan } from '../../core/entities/route-plan';
import { ShipmentRepository, RoutePlanRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { LogisticsMetrics } from '../../infrastructure/observability/metrics';
import { RoutingPlanRequestDto } from '../dto/logistics-dtos';
export declare class RoutingOptimizationService {
    private readonly shipmentRepository;
    private readonly routeRepository;
    private readonly eventBus;
    private readonly metrics;
    constructor(shipmentRepository: ShipmentRepository, routeRepository: RoutePlanRepository, eventBus: LogisticsEventBus, metrics: LogisticsMetrics);
    planRoute(dto: RoutingPlanRequestDto): Promise<RoutePlan>;
    replanRoute(dto: RoutingPlanRequestDto, reason: string): Promise<RoutePlan>;
}
//# sourceMappingURL=routing-optimization-service.d.ts.map