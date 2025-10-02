import type { CreateOrderCommand } from '../../application/commands/create-order';
import type { UpdateOrderStatusCommand } from '../../application/commands/update-order-status';
import type { DeleteOrderCommand } from '../../application/commands/delete-order';
import type { ListOrdersQuery } from '../../application/queries/list-orders';
import type { GetOrderQuery } from '../../application/queries/get-order';
export interface HttpRequest<TBody = unknown> {
    params: Record<string, string>;
    query: Record<string, string | string[] | undefined>;
    body?: TBody;
}
export interface HttpResponse<TBody = unknown> {
    status: number;
    body?: TBody;
}
export type RouteHandler = (request: HttpRequest) => Promise<HttpResponse>;
export interface RouterLike {
    get(path: string, handler: RouteHandler): void;
    post(path: string, handler: RouteHandler): void;
    patch(path: string, handler: RouteHandler): void;
    delete(path: string, handler: RouteHandler): void;
}
export declare class ERPApiController {
    private readonly listOrders;
    private readonly getOrder;
    private readonly createOrder;
    private readonly updateOrderStatus;
    private readonly deleteOrder;
    constructor(listOrders: ListOrdersQuery, getOrder: GetOrderQuery, createOrder: CreateOrderCommand, updateOrderStatus: UpdateOrderStatusCommand, deleteOrder: DeleteOrderCommand);
    register(router: RouterLike): void;
    private handleListOrders;
    private handleGetOrder;
    private handleCreateOrder;
    private handleUpdateStatus;
    private handleDeleteOrder;
}
//# sourceMappingURL=erp-api-controller.d.ts.map