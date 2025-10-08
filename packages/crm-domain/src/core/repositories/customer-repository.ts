import type { CustomerId } from '@valero-neuroerp/data-models';
import { createQueryBuilder, Repository, RepositoryQuery } from '@valero-neuroerp/utilities';
import { Customer, CustomerFilters } from '../entities/customer';

export interface CustomerRepository extends Repository<Customer, CustomerId> {
  list(filters?: CustomerFilters): Promise<Customer[]>;
  findByEmail(email: string): Promise<Customer | null>;
  findByCustomerNumber(customerNumber: string): Promise<Customer | null>;
}

export const buildCustomerQuery = (filters?: CustomerFilters): RepositoryQuery<Customer> => {
  const builder = createQueryBuilder<Customer>();

  if (filters === undefined || filters === null) {
    return builder.build();
  }

  if (filters.status) {
    builder.where('status', 'eq', filters.status);
  }

  if (filters.type) {
    builder.where('type', 'eq', filters.type);
  }

  if (filters.search) {
    const pattern = `%${filters.search.trim()}%` as Customer['name'];
    builder.where('name', 'ilike', pattern);
  }

  if (typeof filters.limit === 'number') {
    builder.limitCount(filters.limit);
  }

  if (typeof filters.offset === 'number') {
    builder.offsetCount(filters.offset);
  }

  return builder.build();
};

