import type { OrderId } from '@valero-neuroerp/data-models';
import { createQueryBuilder, Repository, RepositoryQuery } from '@valero-neuroerp/utilities';
import { Order, OrderFilters, OrderStatus } from '../entities/order';

export interface OrderRepository extends Repository<Order, OrderId> {
  list(filters?: OrderFilters): Promise<Order[]>;
  updateStatus(id: OrderId, status: OrderStatus): Promise<Order>;
}

export const buildOrderQuery = (filters?: OrderFilters): RepositoryQuery<Order> => {
  const builder = createQueryBuilder<Order>();

  if (!filters) {
    return builder.build();
  }

  if (filters.status) {
    builder.where('status', 'eq', filters.status);
  }

  if (filters.documentType) {
    builder.where('documentType', 'eq', filters.documentType);
  }

  if (filters.customerNumber) {
    builder.where('customerNumber', 'eq', filters.customerNumber);
  }

  if (filters.debtorNumber) {
    builder.where('debtorNumber', 'eq', filters.debtorNumber);
  }

  if (typeof filters.limit === 'number') {
    builder.limitCount(filters.limit);
  }

  if (typeof filters.offset === 'number') {
    builder.offsetCount(filters.offset);
  }

  return builder.build();
};
