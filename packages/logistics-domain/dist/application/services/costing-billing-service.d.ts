import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { CostingApplyDto } from '../dto/logistics-dtos';
export declare class CostingBillingService {
    private readonly eventBus;
    constructor(eventBus: LogisticsEventBus);
    allocate(dto: CostingApplyDto): void;
    approveFreightBill(tenantId: string, shipmentId: string, carrierId: string, amount: number, currency: string): void;
}
//# sourceMappingURL=costing-billing-service.d.ts.map