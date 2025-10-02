import { CarrierDocument } from '../../core/entities/carrier-document';
import { CarrierDocumentRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
interface CarrierDocumentInput {
    tenantId: string;
    carrierId: string;
    reference: string;
    payload: Record<string, unknown>;
}
export declare class CarrierConnectService {
    private readonly repository;
    private readonly eventBus;
    constructor(repository: CarrierDocumentRepository, eventBus: LogisticsEventBus);
    createLabel(dto: CarrierDocumentInput): Promise<CarrierDocument>;
    submitManifest(dto: CarrierDocumentInput): Promise<CarrierDocument>;
    registerInvoice(dto: CarrierDocumentInput): Promise<CarrierDocument>;
    private persistDocument;
}
export {};
//# sourceMappingURL=carrier-connect-service.d.ts.map