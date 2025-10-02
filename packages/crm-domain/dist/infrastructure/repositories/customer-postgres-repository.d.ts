import { RepositoryBase } from '@valero-neuroerp/utilities';
import type { CustomerId } from '@valero-neuroerp/data-models';
import { Customer, CustomerFilters } from '../../core/entities/customer';
export declare class CustomerPostgresRepository extends RepositoryBase<Customer, CustomerId> {
    private readonly customers;
    findById(id: CustomerId): Promise<Customer | null>;
    findMany(query?: any): Promise<Customer[]>;
    create(entity: Customer): Promise<Customer>;
    update(id: CustomerId, updates: Partial<Customer>): Promise<Customer>;
    delete(id: CustomerId): Promise<void>;
    list(filters?: CustomerFilters): Promise<Customer[]>;
    findByEmail(email: string): Promise<Customer | null>;
    findByCustomerNumber(customerNumber: string): Promise<Customer | null>;
}
//# sourceMappingURL=customer-postgres-repository.d.ts.map