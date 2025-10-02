import { ContactEntity, CreateContactInput, UpdateContactInput } from '../../domain/entities';
export interface ContactFilters {
    customerId?: string;
    isPrimary?: boolean;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: 'firstName' | 'lastName' | 'createdAt' | 'updatedAt';
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
export declare class ContactRepository {
    findById(id: string, tenantId: string): Promise<ContactEntity | null>;
    findByEmail(email: string, tenantId: string): Promise<ContactEntity | null>;
    findByCustomerId(customerId: string, tenantId: string, filters?: ContactFilters, pagination?: PaginationOptions): Promise<PaginatedResult<ContactEntity>>;
    findAll(tenantId: string, filters?: ContactFilters, pagination?: PaginationOptions): Promise<PaginatedResult<ContactEntity>>;
    create(input: CreateContactInput & {
        tenantId: string;
    }): Promise<ContactEntity>;
    update(id: string, tenantId: string, input: UpdateContactInput): Promise<ContactEntity | null>;
    delete(id: string, tenantId: string): Promise<boolean>;
    exists(id: string, tenantId: string): Promise<boolean>;
    setPrimaryContact(customerId: string, contactId: string, tenantId: string): Promise<void>;
    getPrimaryContact(customerId: string, tenantId: string): Promise<ContactEntity | null>;
}
//# sourceMappingURL=contact-repository.d.ts.map