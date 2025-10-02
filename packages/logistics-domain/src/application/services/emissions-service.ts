import { EmissionRecord } from '../../core/entities/emission-record';
import { EmissionRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { EmissionCalcDto } from '../dto/logistics-dtos';

export class EmissionsService {
  constructor(private readonly repository: EmissionRepository, private readonly eventBus: LogisticsEventBus) {}

  async calculate(dto: EmissionCalcDto): Promise<EmissionRecord> {
    const record = EmissionRecord.create({
      tenantId: dto.tenantId,
      shipmentId: dto.shipmentId,
      co2eKg: dto.co2eKg,
      method: dto.method,
      factors: dto.factors,
    });

    await this.repository.saveEmission(record);
    const event = buildEvent('logistics.emissions.updated', dto.tenantId, { emission: record });
    this.eventBus.publish(event);
    return record;
  }
}
