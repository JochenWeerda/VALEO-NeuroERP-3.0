import { DispatchAssignment } from '../../core/entities/dispatch-assignment';
import { DispatchRepository, RoutePlanRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { LogisticsMetrics } from '../../infrastructure/observability/metrics';
import { DispatchAssignDto } from '../dto/logistics-dtos';
export declare class DispatchService {
    private readonly dispatchRepository;
    private readonly routeRepository;
    private readonly eventBus;
    private readonly metrics;
    constructor(dispatchRepository: DispatchRepository, routeRepository: RoutePlanRepository, eventBus: LogisticsEventBus, metrics: LogisticsMetrics);
    assign(dto: DispatchAssignDto): Promise<DispatchAssignment>;
    reassign(dto: DispatchAssignDto, previousDriverId: string): Promise<DispatchAssignment>;
}
//# sourceMappingURL=dispatch-service.d.ts.map