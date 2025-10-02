import { QuoteEntity, CreateQuoteInput, UpdateQuoteInput, QuoteStatusType } from '../entities';
import { QuoteRepository } from '../../infra/repo';
export interface QuoteServiceDependencies {
    quoteRepo: QuoteRepository;
}
export interface CreateQuoteData extends CreateQuoteInput {
    tenantId: string;
    quoteNumber: string;
    lines: any[];
}
export interface UpdateQuoteData extends UpdateQuoteInput {
    tenantId: string;
    lines?: any[];
}
export declare class QuoteService {
    private deps;
    constructor(deps: QuoteServiceDependencies);
    createQuote(data: CreateQuoteData): Promise<QuoteEntity>;
    getQuote(id: string, tenantId: string): Promise<QuoteEntity | null>;
    getQuoteByNumber(quoteNumber: string, tenantId: string): Promise<QuoteEntity | null>;
    updateQuote(id: string, data: UpdateQuoteData): Promise<QuoteEntity>;
    deleteQuote(id: string, tenantId: string): Promise<boolean>;
    sendQuote(id: string, tenantId: string): Promise<QuoteEntity>;
    acceptQuote(id: string, tenantId: string): Promise<QuoteEntity>;
    rejectQuote(id: string, tenantId: string): Promise<QuoteEntity>;
    expireQuote(id: string, tenantId: string): Promise<QuoteEntity>;
    searchQuotes(tenantId: string, filters?: {
        customerId?: string;
        status?: QuoteStatusType;
        search?: string;
        validUntilFrom?: Date;
        validUntilTo?: Date;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo").PaginatedResult<QuoteEntity>>;
    getQuotesByCustomer(customerId: string, tenantId: string, filters?: {
        status?: QuoteStatusType;
        search?: string;
        validUntilFrom?: Date;
        validUntilTo?: Date;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo").PaginatedResult<QuoteEntity>>;
    getExpiringSoon(tenantId: string, daysAhead?: number): Promise<QuoteEntity[]>;
    getExpiredQuotes(tenantId: string): Promise<QuoteEntity[]>;
}
//# sourceMappingURL=quote-service.d.ts.map