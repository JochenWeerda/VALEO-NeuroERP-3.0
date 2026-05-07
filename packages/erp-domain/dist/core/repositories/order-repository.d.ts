import type { OrderId } from '@valero-neuroerp/data-models';
import { Repository, RepositoryQuery } from '@valero-neuroerp/utilities';
import { Order, OrderFilters, OrderStatus } from '../entities/order';
export interface OrderRepository extends Repository<Order, OrderId> {
    list(filters?: OrderFilters): Promise<Order[]>;
    updateStatus(id: OrderId, status: OrderStatus): Promise<Order>;
}
export declare const buildOrderQuery: (filters?: OrderFilters) => RepositoryQuery<Order>;
//# sourceMappingURL=order-repository.d.ts.map