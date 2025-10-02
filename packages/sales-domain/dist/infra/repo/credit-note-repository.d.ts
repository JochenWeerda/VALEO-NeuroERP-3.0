import { CreditNoteEntity, CreateCreditNoteInput, UpdateCreditNoteInput, CreditNoteStatusType } from '../../domain/entities';
export interface CreditNoteFilters {
    customerId?: string;
    invoiceId?: string;
    status?: CreditNoteStatusType;
    search?: string;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: 'creditNumber' | 'totalNet' | 'createdAt' | 'updatedAt';
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
export declare class CreditNoteRepository {
    findById(id: string, tenantId: string): Promise<CreditNoteEntity | null>;
    findByNumber(creditNumber: string, tenantId: string): Promise<CreditNoteEntity | null>;
    findByInvoiceId(invoiceId: string, tenantId: string): Promise<CreditNoteEntity[]>;
    findByCustomerId(customerId: string, tenantId: string, filters?: CreditNoteFilters, pagination?: PaginationOptions): Promise<PaginatedResult<CreditNoteEntity>>;
    findAll(tenantId: string, filters?: CreditNoteFilters, pagination?: PaginationOptions): Promise<PaginatedResult<CreditNoteEntity>>;
    create(input: CreateCreditNoteInput & {
        tenantId: string;
    }): Promise<CreditNoteEntity>;
    update(id: string, tenantId: string, input: UpdateCreditNoteInput): Promise<CreditNoteEntity | null>;
    delete(id: string, tenantId: string): Promise<boolean>;
    exists(id: string, tenantId: string): Promise<boolean>;
    updateStatus(id: string, tenantId: string, status: CreditNoteStatusType): Promise<CreditNoteEntity | null>;
}
//# sourceMappingURL=credit-note-repository.d.ts.map