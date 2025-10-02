import type { CustomerId } from "@valero-neuroerp/data-models";
import { InMemoryRepository } from "@valero-neuroerp/utilities";
import { Customer, CustomerFilters, CreateCustomerInput } from "../../core/entities/customer";
import { CustomerRepository } from "../../core/repositories/customer-repository";
export declare class InMemoryCustomerRepository extends InMemoryRepository<Customer, 'id', CustomerId> implements CustomerRepository {
    constructor(seed?: CreateCustomerInput[]);
    list(filters?: CustomerFilters): Promise<Customer[]>;
    findByEmail(email: string): Promise<Customer | null>;
    findByCustomerNumber(customerNumber: string): Promise<Customer | null>;
}
//# sourceMappingURL=in-memory-customer-repository.d.ts.map