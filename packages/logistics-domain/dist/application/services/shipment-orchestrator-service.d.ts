import { Shipment } from '../../core/entities/shipment';
import { ShipmentRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { LogisticsMetrics } from '../../infrastructure/observability/metrics';
import { CreateShipmentDto } from '../dto/logistics-dtos';
export declare class ShipmentOrchestratorService {
    private readonly repository;
    private readonly eventBus;
    private readonly metrics;
    constructor(repository: ShipmentRepository, eventBus: LogisticsEventBus, metrics: LogisticsMetrics);
    createShipment(dto: CreateShipmentDto): Promise<Shipment>;
    cancelShipment(tenantId: string, shipmentId: string, reason: string): Promise<void>;
    listShipments(tenantId: string): Promise<Shipment[]>;
    getShipment(tenantId: string, shipmentId: string): Promise<Shipment | undefined>;
}
//# sourceMappingURL=shipment-orchestrator-service.d.ts.map