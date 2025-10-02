import { Logger, MetricsRecorder } from '@valero-neuroerp/utilities';
import { Customer, CustomerFilters, CreateCustomerInput, UpdateCustomerInput, CustomerId } from "../core/entities/customer";
import { CustomerRepository } from "../core/repositories/customer-repository";
export interface CRMDomainServiceOptions {
    logger?: Logger;
    metrics?: MetricsRecorder;
}
export declare class CRMDomainService {
    private readonly customers;
    private readonly logger;
    private readonly metrics?;
    constructor(customers: CustomerRepository, options?: CRMDomainServiceOptions);
    createCustomer(input: CreateCustomerInput): Promise<Customer>;
    updateCustomer(id: CustomerId, updates: UpdateCustomerInput): Promise<Customer>;
    listCustomers(filters?: CustomerFilters): Promise<Customer[]>;
    getCustomer(id: CustomerId): Promise<Customer | null>;
    deleteCustomer(id: CustomerId): Promise<void>;
}
//# sourceMappingURL=crm-domain-service.d.ts.map