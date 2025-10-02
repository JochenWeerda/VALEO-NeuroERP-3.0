import { TelemetryRecord } from '../../core/entities/telemetry-record';
import { TelemetryRepository, RoutePlanRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { TelemetryPushDto } from '../dto/logistics-dtos';
export declare class TelematicsGatewayService {
    private readonly telemetryRepository;
    private readonly routeRepository;
    private readonly eventBus;
    constructor(telemetryRepository: TelemetryRepository, routeRepository: RoutePlanRepository, eventBus: LogisticsEventBus);
    ingest(dto: TelemetryPushDto): Promise<TelemetryRecord>;
    calculateEta(tenantId: string, shipmentId: string, referenceTime?: Date): Promise<number | undefined>;
}
//# sourceMappingURL=telematics-gateway-service.d.ts.map