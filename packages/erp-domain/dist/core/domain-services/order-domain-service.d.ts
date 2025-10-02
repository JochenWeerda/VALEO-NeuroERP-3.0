import type { OrderId } from '@valero-neuroerp/data-models';
import { Order, OrderFilters, OrderStatus, CreateOrderInput } from '../entities/order';
import { OrderRepository } from '../repositories/order-repository';
export declare class OrderDomainService {
    private readonly repository;
    constructor(repository: OrderRepository);
    listOrders(filters?: OrderFilters): Promise<Order[]>;
    getOrder(id: OrderId): Promise<Order | null>;
    createOrder(input: CreateOrderInput): Promise<Order>;
    updateOrderStatus(id: OrderId, status: OrderStatus): Promise<Order>;
    deleteOrder(id: OrderId): Promise<void>;
    private assertStatus;
    private assertCurrency;
    private assertAmountConsistency;
}
//# sourceMappingURL=order-domain-service.d.ts.map