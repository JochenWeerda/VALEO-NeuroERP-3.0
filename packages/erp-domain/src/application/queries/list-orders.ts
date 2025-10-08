import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { OrderDTO } from '../dto/order-dto';
import { toOrderDTO } from '../mappers/order-mapper';
import type { OrderFilters } from '../../core/entities/order';

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

export class ListOrdersQuery {
  constructor(private readonly service: OrderDomainService) {}

  async execute(options: ListOrdersOptions = {}): Promise<OrderDTO[]> {
    const filters: OrderFilters = {
      status: options.status as OrderFilters['status'],
      documentType: options.documentType as OrderFilters['documentType'],
      customerNumber: options.customerNumber,
      debtorNumber: options.debtorNumber,
      from: options.from != null ? new Date(options.from) : undefined,
      to: options.to != null ? new Date(options.to) : undefined,
      limit: options.limit,
      offset: options.offset,
    };

    const orders = await this.service.listOrders(filters);
    return orders.map(toOrderDTO);
  }
}
