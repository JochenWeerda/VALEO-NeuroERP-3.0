import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { CreateOrderDTO, OrderDTO } from '../dto/order-dto';
export declare class CreateOrderCommand {
    private readonly service;
    constructor(service: OrderDomainService);
    execute(payload: CreateOrderDTO): Promise<OrderDTO>;
}
//# sourceMappingURL=create-order.d.ts.map