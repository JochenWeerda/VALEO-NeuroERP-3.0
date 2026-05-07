import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { OrderDTO } from '../dto/order-dto';
export interface ListOrdersOptions {
    status?: string;
    documentType?: string;
    customerNumber?: string;
    debtorNumber?: string;
    from?: string;
    to?: string;
    limit?: number;
    offset?: number;
}
export declare class ListOrdersQuery {
    private readonly service;
    constructor(service: OrderDomainService);
    execute(options?: ListOrdersOptions): Promise<OrderDTO[]>;
}
//# sourceMappingURL=list-orders.d.ts.map