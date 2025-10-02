import { InvoiceEntity, CreateInvoiceInput, UpdateInvoiceInput, InvoiceStatusType } from '../../domain/entities';
export interface InvoiceFilters {
    customerId?: string;
    orderId?: string;
    status?: InvoiceStatusType;
    search?: string;
    dueDateFrom?: Date;
    dueDateTo?: Date;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: 'invoiceNumber' | 'dueDate' | 'totalNet' | 'createdAt' | 'updatedAt';
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
export declare class InvoiceRepository {
    findById(id: string, tenantId: string): Promise<InvoiceEntity | null>;
    findByNumber(invoiceNumber: string, tenantId: string): Promise<InvoiceEntity | null>;
    findByOrderId(orderId: string, tenantId: string): Promise<InvoiceEntity | null>;
    findByCustomerId(customerId: string, tenantId: string, filters?: InvoiceFilters, pagination?: PaginationOptions): Promise<PaginatedResult<InvoiceEntity>>;
    findAll(tenantId: string, filters?: InvoiceFilters, pagination?: PaginationOptions): Promise<PaginatedResult<InvoiceEntity>>;
    create(input: CreateInvoiceInput & {
        tenantId: string;
    }): Promise<InvoiceEntity>;
    update(id: string, tenantId: string, input: UpdateInvoiceInput): Promise<InvoiceEntity | null>;
    delete(id: string, tenantId: string): Promise<boolean>;
    exists(id: string, tenantId: string): Promise<boolean>;
    updateStatus(id: string, tenantId: string, status: InvoiceStatusType): Promise<InvoiceEntity | null>;
    getOverdueInvoices(tenantId: string): Promise<InvoiceEntity[]>;
}
//# sourceMappingURL=invoice-repository.d.ts.map