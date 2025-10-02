import { CustomerEntity, CreateCustomerInput, UpdateCustomerInput, CustomerStatusType } from '../entities';
import { CustomerRepository } from '../../infra/repo';
export interface CustomerServiceDependencies {
    customerRepo: CustomerRepository;
}
export interface CreateCustomerData extends CreateCustomerInput {
    tenantId: string;
    number: string;
    vatId?: string;
}
export interface UpdateCustomerData extends UpdateCustomerInput {
    tenantId: string;
    vatId?: string;
}
export declare class CustomerService {
    private deps;
    constructor(deps: CustomerServiceDependencies);
    createCustomer(data: CreateCustomerData): Promise<CustomerEntity>;
    getCustomer(id: string, tenantId: string): Promise<CustomerEntity | null>;
    getCustomerByNumber(number: string, tenantId: string): Promise<CustomerEntity | null>;
    updateCustomer(id: string, data: UpdateCustomerData): Promise<CustomerEntity>;
    deleteCustomer(id: string, tenantId: string): Promise<boolean>;
    changeCustomerStatus(id: string, tenantId: string, status: CustomerStatusType): Promise<CustomerEntity>;
    addTag(id: string, tenantId: string, tag: string): Promise<CustomerEntity>;
    removeTag(id: string, tenantId: string, tag: string): Promise<CustomerEntity>;
    searchCustomers(tenantId: string, filters?: {
        search?: string;
        status?: CustomerStatusType;
        tags?: string[];
        ownerUserId?: string;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo").PaginatedResult<CustomerEntity>>;
    private validateVatId;
    private validateStatusTransition;
}
//# sourceMappingURL=customer-service.d.ts.map