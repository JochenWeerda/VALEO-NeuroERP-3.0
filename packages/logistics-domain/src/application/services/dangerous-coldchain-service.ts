import { SafetyAlert } from '../../core/entities/safety-alert';
import { SafetyAlertRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { SafetyValidationDto } from '../dto/logistics-dtos';

export class DangerousColdchainService {
  constructor(private readonly repository: SafetyAlertRepository, private readonly eventBus: LogisticsEventBus) {}

  async raiseAlert(dto: SafetyValidationDto): Promise<SafetyAlert> {
    const alert = SafetyAlert.create({
      tenantId: dto.tenantId,
      referenceId: dto.referenceId,
      shipmentId: dto.shipmentId,
      type: dto.type,
      severity: dto.severity,
      message: dto.message,
    });

    await this.repository.saveSafetyAlert(alert);
    const event = buildEvent('logistics.safety.violation', dto.tenantId, { alert });
    this.eventBus.publish(event);
    return alert;
  }

  async raiseColdChainAlert(
    tenantId: string,
    referenceId: string,
    shipmentId: string | undefined,
    temperatureC: number,
    message: string,
  ): Promise<SafetyAlert> {
    const alert = SafetyAlert.create({
      tenantId,
      referenceId,
      shipmentId,
      type: 'temperature',
      severity: temperatureC > 8 || temperatureC < 2 ? 'critical' : 'warning',
      message,
    });

    await this.repository.saveSafetyAlert(alert);
    const event = buildEvent('logistics.coldchain.alert', tenantId, { alert, temperatureC });
    this.eventBus.publish(event);
    return alert;
  }
}
