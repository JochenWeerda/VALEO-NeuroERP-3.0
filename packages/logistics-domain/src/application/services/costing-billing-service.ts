import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { CostingApplyDto } from '../dto/logistics-dtos';

export class CostingBillingService {
  constructor(private readonly eventBus: LogisticsEventBus) {}

  allocate(dto: CostingApplyDto): void {
    const event = buildEvent('logistics.costs.allocated', dto.tenantId, {
      shipmentId: dto.shipmentId,
      total: dto.total,
      currency: dto.currency,
      breakdown: dto.breakdown,
    });
    this.eventBus.publish(event);
  }

  approveFreightBill(
    tenantId: string,
    shipmentId: string,
    carrierId: string,
    amount: number,
    currency: string,
  ): void {
    const event = buildEvent('logistics.freight.billApproved', tenantId, {
      shipmentId,
      carrierId,
      amount,
      currency,
    });
    this.eventBus.publish(event);
  }
}
