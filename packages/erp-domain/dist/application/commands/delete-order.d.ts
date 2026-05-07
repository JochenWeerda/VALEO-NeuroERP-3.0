import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { OrderId } from '../../core/entities/order';
export declare class DeleteOrderCommand {
    private readonly service;
    constructor(service: OrderDomainService);
    execute(id: OrderId): Promise<void>;
}
//# sourceMappingURL=delete-order.d.ts.map