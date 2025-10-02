import { ReturnOrder } from '../../core/entities/return-order';
import { ReturnOrderRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { ReturnRequestDto } from '../dto/logistics-dtos';
export declare class ReturnsService {
    private readonly repository;
    private readonly eventBus;
    constructor(repository: ReturnOrderRepository, eventBus: LogisticsEventBus);
    create(dto: ReturnRequestDto): Promise<ReturnOrder>;
    receive(tenantId: string, returnId: string): Promise<ReturnOrder>;
}
//# sourceMappingURL=returns-service.d.ts.map