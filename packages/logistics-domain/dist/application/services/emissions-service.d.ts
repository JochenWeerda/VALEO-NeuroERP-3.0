import { EmissionRecord } from '../../core/entities/emission-record';
import { EmissionRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { EmissionCalcDto } from '../dto/logistics-dtos';
export declare class EmissionsService {
    private readonly repository;
    private readonly eventBus;
    constructor(repository: EmissionRepository, eventBus: LogisticsEventBus);
    calculate(dto: EmissionCalcDto): Promise<EmissionRecord>;
}
//# sourceMappingURL=emissions-service.d.ts.map