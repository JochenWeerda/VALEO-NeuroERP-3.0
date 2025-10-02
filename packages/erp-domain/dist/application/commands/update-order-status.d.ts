import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { UpdateOrderStatusDTO, OrderDTO } from '../dto/order-dto';
import type { OrderId } from '../../core/entities/order';
export declare class UpdateOrderStatusCommand {
    private readonly service;
    constructor(service: OrderDomainService);
    execute(id: OrderId, payload: UpdateOrderStatusDTO): Promise<OrderDTO>;
}
//# sourceMappingURL=update-order-status.d.ts.map