import { OrderEntity, CreateOrderInput, UpdateOrderInput, OrderStatusType } from '../entities';
import { OrderRepository } from '../../infra/repo';
export interface OrderServiceDependencies {
    orderRepo: OrderRepository;
}
export interface CreateOrderData extends CreateOrderInput {
    tenantId: string;
    orderNumber: string;
    lines: any[];
}
export interface UpdateOrderData extends UpdateOrderInput {
    tenantId: string;
    lines?: any[];
}
export declare class OrderService {
    private deps;
    constructor(deps: OrderServiceDependencies);
    createOrder(data: CreateOrderData): Promise<OrderEntity>;
    getOrder(id: string, tenantId: string): Promise<OrderEntity | null>;
    updateOrder(id: string, data: UpdateOrderData): Promise<OrderEntity>;
    confirmOrder(id: string, tenantId: string): Promise<OrderEntity>;
    markOrderAsInvoiced(id: string, tenantId: string): Promise<OrderEntity>;
    cancelOrder(id: string, tenantId: string): Promise<OrderEntity>;
    searchOrders(tenantId: string, filters?: {
        customerId?: string;
        status?: OrderStatusType;
        search?: string;
        expectedDeliveryDateFrom?: Date;
        expectedDeliveryDateTo?: Date;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/order-repository").PaginatedResult<OrderEntity>>;
    getOrdersByCustomer(customerId: string, tenantId: string, filters?: {
        status?: OrderStatusType;
        search?: string;
        expectedDeliveryDateFrom?: Date;
        expectedDeliveryDateTo?: Date;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/order-repository").PaginatedResult<OrderEntity>>;
}
//# sourceMappingURL=order-service.d.ts.map