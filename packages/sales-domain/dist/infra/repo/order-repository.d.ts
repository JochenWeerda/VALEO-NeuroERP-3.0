import { OrderEntity, CreateOrderInput, UpdateOrderInput, OrderStatusType } from '../../domain/entities';
export interface OrderFilters {
    customerId?: string;
    status?: OrderStatusType;
    search?: string;
    expectedDeliveryDateFrom?: Date;
    expectedDeliveryDateTo?: Date;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: 'orderNumber' | 'expectedDeliveryDate' | 'totalNet' | 'createdAt' | 'updatedAt';
    sortOrder?: 'asc' | 'desc';
}
export interface PaginatedResult<T> {
    data: T[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}
export declare class OrderRepository {
    findById(id: string, tenantId: string): Promise<OrderEntity | null>;
    findByNumber(orderNumber: string, tenantId: string): Promise<OrderEntity | null>;
    findByCustomerId(customerId: string, tenantId: string, filters?: OrderFilters, pagination?: PaginationOptions): Promise<PaginatedResult<OrderEntity>>;
    findAll(tenantId: string, filters?: OrderFilters, pagination?: PaginationOptions): Promise<PaginatedResult<OrderEntity>>;
    create(input: CreateOrderInput & {
        tenantId: string;
    }): Promise<OrderEntity>;
    update(id: string, tenantId: string, input: UpdateOrderInput): Promise<OrderEntity | null>;
    delete(id: string, tenantId: string): Promise<boolean>;
    exists(id: string, tenantId: string): Promise<boolean>;
    updateStatus(id: string, tenantId: string, status: OrderStatusType): Promise<OrderEntity | null>;
}
//# sourceMappingURL=order-repository.d.ts.map