import { InvoiceEntity, CreateInvoiceInput, UpdateInvoiceInput, InvoiceStatusType } from '../entities';
import { InvoiceRepository } from '../../infra/repo';
export interface InvoiceServiceDependencies {
    invoiceRepo: InvoiceRepository;
}
export interface CreateInvoiceData extends CreateInvoiceInput {
    tenantId: string;
    invoiceNumber: string;
    lines: any[];
}
export interface UpdateInvoiceData extends UpdateInvoiceInput {
    tenantId: string;
}
export declare class InvoiceService {
    private deps;
    constructor(deps: InvoiceServiceDependencies);
    createInvoice(data: CreateInvoiceData): Promise<InvoiceEntity>;
    getInvoice(id: string, tenantId: string): Promise<InvoiceEntity | null>;
    updateInvoice(id: string, data: UpdateInvoiceData): Promise<InvoiceEntity>;
    markInvoiceAsPaid(id: string, tenantId: string): Promise<InvoiceEntity>;
    markInvoiceAsOverdue(id: string, tenantId: string): Promise<InvoiceEntity>;
    cancelInvoice(id: string, tenantId: string): Promise<InvoiceEntity>;
    searchInvoices(tenantId: string, filters?: {
        customerId?: string;
        orderId?: string;
        status?: InvoiceStatusType;
        search?: string;
        dueDateFrom?: Date;
        dueDateTo?: Date;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/invoice-repository").PaginatedResult<InvoiceEntity>>;
    getInvoicesByCustomer(customerId: string, tenantId: string, filters?: {
        orderId?: string;
        status?: InvoiceStatusType;
        search?: string;
        dueDateFrom?: Date;
        dueDateTo?: Date;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/invoice-repository").PaginatedResult<InvoiceEntity>>;
    getOverdueInvoices(tenantId: string): Promise<InvoiceEntity[]>;
}
//# sourceMappingURL=invoice-service.d.ts.map