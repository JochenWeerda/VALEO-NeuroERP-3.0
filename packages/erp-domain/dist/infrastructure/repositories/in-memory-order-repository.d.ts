import type { OrderId } from '@valero-neuroerp/data-models';
import { InMemoryRepository } from '@valero-neuroerp/utilities';
import { Order, OrderFilters, OrderStatus, CreateOrderInput } from '../../core/entities/order';
import { OrderRepository } from '../../core/repositories/order-repository';
export declare class InMemoryOrderRepository extends InMemoryRepository<Order, 'id', OrderId> implements OrderRepository {
    constructor(seed?: CreateOrderInput[]);
    list(filters?: OrderFilters): Promise<Order[]>;
    create(order: Order): Promise<Order>;
    update(id: OrderId, order: Order): Promise<Order>;
    updateStatus(id: OrderId, status: OrderStatus): Promise<Order>;
}
//# sourceMappingURL=in-memory-order-repository.d.ts.map