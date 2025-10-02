import { FreightRate } from '../../core/entities/freight-rate';
import { FreightRateRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { FreightQuoteRequestDto } from '../dto/logistics-dtos';

export class FreightRatingService {
  constructor(private readonly repository: FreightRateRepository, private readonly eventBus: LogisticsEventBus) {}

  async quote(dto: FreightQuoteRequestDto): Promise<FreightRate> {
    const rate = FreightRate.create({
      tenantId: dto.tenantId,
      shipmentId: dto.shipmentId,
      currency: dto.currency,
      baseAmount: dto.baseAmount,
      surcharges: dto.surcharges,
      explain: dto.explain,
    });

    await this.repository.saveFreightRate(rate);
    const event = buildEvent('logistics.freight.rated', dto.tenantId, { freightRate: rate });
    this.eventBus.publish(event);
    return rate;
  }
}
