import { WeighingRecord } from '../../core/entities/weighing-record';
import { WeighingRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { WeighingCaptureDto } from '../dto/logistics-dtos';
export declare class WeighbridgeIntegrationService {
    private readonly repository;
    private readonly eventBus;
    private readonly maxNetWeightKg;
    constructor(repository: WeighingRepository, eventBus: LogisticsEventBus);
    capture(dto: WeighingCaptureDto): Promise<WeighingRecord>;
}
//# sourceMappingURL=weighbridge-integration-service.d.ts.map