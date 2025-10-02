import { CustomerEntity, CreateCustomerInput, UpdateCustomerInput, CustomerStatusType } from '../../domain/entities';
export interface CustomerFilters {
    search?: string;
    status?: CustomerStatusType;
    tags?: string[];
    ownerUserId?: string;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: 'name' | 'createdAt' | 'updatedAt';
    sortOrder?: 'asc' | 'desc';
}
export interface PaginatedResult<T> {
    data: T[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}
export declare class CustomerRepository {
    findById(id: string, tenantId: string): Promise<CustomerEntity | null>;
    findByNumber(number: string, tenantId: string): Promise<CustomerEntity | null>;
    findAll(tenantId: string, filters?: CustomerFilters, pagination?: PaginationOptions): Promise<PaginatedResult<CustomerEntity>>;
    create(input: CreateCustomerInput & {
        tenantId: string;
    }): Promise<CustomerEntity>;
    update(id: string, tenantId: string, input: UpdateCustomerInput): Promise<CustomerEntity | null>;
    delete(id: string, tenantId: string): Promise<boolean>;
    exists(id: string, tenantId: string): Promise<boolean>;
    updateStatus(id: string, tenantId: string, status: CustomerStatusType): Promise<CustomerEntity | null>;
    addTag(id: string, tenantId: string, tag: string): Promise<CustomerEntity | null>;
    removeTag(id: string, tenantId: string, tag: string): Promise<CustomerEntity | null>;
}
//# sourceMappingURL=customer-repository.d.ts.map