import { SafetyAlert } from '../../core/entities/safety-alert';
import { SafetyAlertRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { SafetyValidationDto } from '../dto/logistics-dtos';
export declare class DangerousColdchainService {
    private readonly repository;
    private readonly eventBus;
    constructor(repository: SafetyAlertRepository, eventBus: LogisticsEventBus);
    raiseAlert(dto: SafetyValidationDto): Promise<SafetyAlert>;
    raiseColdChainAlert(tenantId: string, referenceId: string, shipmentId: string | undefined, temperatureC: number, message: string): Promise<SafetyAlert>;
}
//# sourceMappingURL=dangerous-coldchain-service.d.ts.map