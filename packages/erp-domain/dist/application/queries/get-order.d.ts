import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { OrderDTO } from '../dto/order-dto';
import type { OrderId } from '../../core/entities/order';
export declare class GetOrderQuery {
    private readonly service;
    constructor(service: OrderDomainService);
    execute(id: OrderId): Promise<OrderDTO | null>;
}
//# sourceMappingURL=get-order.d.ts.map