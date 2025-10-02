import { CarrierDocument, CarrierDocumentType } from '../../core/entities/carrier-document';
import { CarrierDocumentRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';

interface CarrierDocumentInput {
  tenantId: string;
  carrierId: string;
  reference: string;
  payload: Record<string, unknown>;
}

export class CarrierConnectService {
  constructor(private readonly repository: CarrierDocumentRepository, private readonly eventBus: LogisticsEventBus) {}

  async createLabel(dto: CarrierDocumentInput): Promise<CarrierDocument> {
    return this.persistDocument('label', 'logistics.carrier.labelCreated', dto);
  }

  async submitManifest(dto: CarrierDocumentInput): Promise<CarrierDocument> {
    return this.persistDocument('manifest', 'logistics.carrier.manifestSubmitted', dto);
  }

  async registerInvoice(dto: CarrierDocumentInput): Promise<CarrierDocument> {
    return this.persistDocument('invoice', 'logistics.carrier.invoiceReceived', dto);
  }

  private async persistDocument(
    type: CarrierDocumentType,
    eventType:
      | 'logistics.carrier.labelCreated'
      | 'logistics.carrier.manifestSubmitted'
      | 'logistics.carrier.invoiceReceived',
    dto: CarrierDocumentInput,
  ): Promise<CarrierDocument> {
    const document = CarrierDocument.create({
      tenantId: dto.tenantId,
      carrierId: dto.carrierId,
      type,
      reference: dto.reference,
      payload: dto.payload,
    });

    await this.repository.saveCarrierDocument(document);
    const event = buildEvent(eventType, dto.tenantId, { document });
    this.eventBus.publish(event);
    return document;
  }
}
