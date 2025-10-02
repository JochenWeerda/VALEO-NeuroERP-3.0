import { CreditNoteEntity, CreateCreditNoteInput, UpdateCreditNoteInput, CreditNoteStatusType } from '../entities';
import { CreditNoteRepository } from '../../infra/repo';
export interface CreditNoteServiceDependencies {
    creditNoteRepo: CreditNoteRepository;
}
export interface CreateCreditNoteData extends CreateCreditNoteInput {
    tenantId: string;
    creditNumber: string;
    lines: any[];
}
export interface UpdateCreditNoteData extends UpdateCreditNoteInput {
    tenantId: string;
}
export declare class CreditNoteService {
    private deps;
    constructor(deps: CreditNoteServiceDependencies);
    createCreditNote(data: CreateCreditNoteData): Promise<CreditNoteEntity>;
    getCreditNote(id: string, tenantId: string): Promise<CreditNoteEntity | null>;
    updateCreditNote(id: string, data: UpdateCreditNoteData): Promise<CreditNoteEntity>;
    settleCreditNote(id: string, tenantId: string): Promise<CreditNoteEntity>;
    searchCreditNotes(tenantId: string, filters?: {
        customerId?: string;
        invoiceId?: string;
        status?: CreditNoteStatusType;
        search?: string;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/credit-note-repository").PaginatedResult<CreditNoteEntity>>;
    getCreditNotesByCustomer(customerId: string, tenantId: string, filters?: {
        invoiceId?: string;
        status?: CreditNoteStatusType;
        search?: string;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/credit-note-repository").PaginatedResult<CreditNoteEntity>>;
    getCreditNotesByInvoice(invoiceId: string, tenantId: string): Promise<CreditNoteEntity[]>;
}
//# sourceMappingURL=credit-note-service.d.ts.map