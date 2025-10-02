import { QuoteEntity, CreateQuoteInput, UpdateQuoteInput, QuoteStatusType } from '../../domain/entities';
export interface QuoteFilters {
    customerId?: string;
    status?: QuoteStatusType;
    search?: string;
    validUntilFrom?: Date;
    validUntilTo?: Date;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: 'quoteNumber' | 'validUntil' | 'totalNet' | 'createdAt' | 'updatedAt';
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
export declare class QuoteRepository {
    findById(id: string, tenantId: string): Promise<QuoteEntity | null>;
    findByNumber(quoteNumber: string, tenantId: string): Promise<QuoteEntity | null>;
    findByCustomerId(customerId: string, tenantId: string, filters?: QuoteFilters, pagination?: PaginationOptions): Promise<PaginatedResult<QuoteEntity>>;
    findAll(tenantId: string, filters?: QuoteFilters, pagination?: PaginationOptions): Promise<PaginatedResult<QuoteEntity>>;
    create(input: CreateQuoteInput & {
        tenantId: string;
    }): Promise<QuoteEntity>;
    update(id: string, tenantId: string, input: UpdateQuoteInput): Promise<QuoteEntity | null>;
    delete(id: string, tenantId: string): Promise<boolean>;
    exists(id: string, tenantId: string): Promise<boolean>;
    updateStatus(id: string, tenantId: string, status: QuoteStatusType): Promise<QuoteEntity | null>;
    getExpiringSoon(tenantId: string, daysAhead?: number): Promise<QuoteEntity[]>;
    getExpired(tenantId: string): Promise<QuoteEntity[]>;
}
//# sourceMappingURL=quote-repository.d.ts.map