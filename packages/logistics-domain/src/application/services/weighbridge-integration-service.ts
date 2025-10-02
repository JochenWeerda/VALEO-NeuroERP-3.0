import { WeighingRecord } from '../../core/entities/weighing-record';
import { WeighingRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { WeighingCaptureDto } from '../dto/logistics-dtos';

export class WeighbridgeIntegrationService {
  private readonly maxNetWeightKg = 40000;

  constructor(private readonly repository: WeighingRepository, private readonly eventBus: LogisticsEventBus) {}

  async capture(dto: WeighingCaptureDto): Promise<WeighingRecord> {
    const record = WeighingRecord.create({
      tenantId: dto.tenantId,
      shipmentId: dto.shipmentId,
      grossWeightKg: dto.grossWeightKg,
      tareWeightKg: dto.tareWeightKg,
      source: dto.source,
    });

    await this.repository.saveWeighing(record);
    const measureEvent = buildEvent('logistics.weight.measured', dto.tenantId, { weighing: record });
    this.eventBus.publish(measureEvent);

    if (record.netWeightKg > this.maxNetWeightKg) {
      const toleranceEvent = buildEvent('logistics.weight.toleranceExceeded', dto.tenantId, {
        weighing: record,
        thresholdKg: this.maxNetWeightKg,
      });
      this.eventBus.publish(toleranceEvent);
    }

    return record;
  }
}
