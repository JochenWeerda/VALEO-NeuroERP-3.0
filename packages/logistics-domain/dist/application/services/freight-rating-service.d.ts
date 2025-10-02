import { FreightRate } from '../../core/entities/freight-rate';
import { FreightRateRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { FreightQuoteRequestDto } from '../dto/logistics-dtos';
export declare class FreightRatingService {
    private readonly repository;
    private readonly eventBus;
    constructor(repository: FreightRateRepository, eventBus: LogisticsEventBus);
    quote(dto: FreightQuoteRequestDto): Promise<FreightRate>;
}
//# sourceMappingURL=freight-rating-service.d.ts.map