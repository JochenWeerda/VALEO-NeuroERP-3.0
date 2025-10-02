import { ProofOfDelivery } from '../../core/entities/proof-of-delivery';
import { ProofOfDeliveryRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { CapturePodDto } from '../dto/logistics-dtos';

export class ProofOfDeliveryService {
  constructor(private readonly repository: ProofOfDeliveryRepository, private readonly eventBus: LogisticsEventBus) {}

  async capture(dto: CapturePodDto): Promise<ProofOfDelivery> {
    const pod = ProofOfDelivery.create({
      tenantId: dto.tenantId,
      shipmentId: dto.shipmentId,
      stopId: dto.stopId,
      signedBy: dto.signedBy,
      signatureRef: dto.signatureRef,
      photoRefs: dto.photoRefs,
      scans: dto.scans,
      exceptions: dto.exceptions,
    });

    await this.repository.saveProofOfDelivery(pod);
    const event = buildEvent('logistics.pod.captured', dto.tenantId, { pod });
    this.eventBus.publish(event);
    return pod;
  }
}
