import type { CustomerId } from '@valero-neuroerp/data-models';
import { Repository, RepositoryQuery } from '@valero-neuroerp/utilities';
import { Customer, CustomerFilters } from '../entities/customer';
export interface CustomerRepository extends Repository<Customer, CustomerId> {
    list(filters?: CustomerFilters): Promise<Customer[]>;
    findByEmail(email: string): Promise<Customer | null>;
    findByCustomerNumber(customerNumber: string): Promise<Customer | null>;
}
export declare const buildCustomerQuery: (filters?: CustomerFilters) => RepositoryQuery<Customer>;
//# sourceMappingURL=customer-repository.d.ts.map