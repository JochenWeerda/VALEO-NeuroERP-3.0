import { GetCustomersQuery } from '../../application/queries/get-customers';
import { CreateCustomerCommand } from '../../application/commands/create-customer';
import { UpdateCustomerCommand } from '../../application/commands/update-customer';
import { DeleteCustomerCommand } from '../../application/commands/delete-customer';
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
    put(path: string, handler: RouteHandler): void;
    delete(path: string, handler: RouteHandler): void;
}
export declare class CRMApiController {
    private readonly getCustomers;
    private readonly createCustomer;
    private readonly updateCustomer;
    private readonly deleteCustomer;
    constructor(getCustomers: GetCustomersQuery, createCustomer: CreateCustomerCommand, updateCustomer: UpdateCustomerCommand, deleteCustomer: DeleteCustomerCommand);
    register(router: RouterLike): void;
    private handleGetCustomers;
    private handleCreateCustomer;
    private handleUpdateCustomer;
    private handleDeleteCustomer;
    private parseQuery;
}
//# sourceMappingURL=crm-api-controller.d.ts.map