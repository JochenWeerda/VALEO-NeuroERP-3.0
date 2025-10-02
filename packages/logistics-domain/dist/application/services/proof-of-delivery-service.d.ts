import { ProofOfDelivery } from '../../core/entities/proof-of-delivery';
import { ProofOfDeliveryRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { CapturePodDto } from '../dto/logistics-dtos';
export declare class ProofOfDeliveryService {
    private readonly repository;
    private readonly eventBus;
    constructor(repository: ProofOfDeliveryRepository, eventBus: LogisticsEventBus);
    capture(dto: CapturePodDto): Promise<ProofOfDelivery>;
}
//# sourceMappingURL=proof-of-delivery-service.d.ts.map