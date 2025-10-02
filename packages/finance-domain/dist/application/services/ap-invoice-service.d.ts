/**
 * VALEO NeuroERP 3.0 - Finance Domain - AP Invoice Application Service
 *
 * Application Service for Accounts Payable invoice processing
 * Sprint 2 Implementation: OCR processing and AI booking
 */
import { AIBookingService, APInvoice, APInvoiceRepository, APInvoiceService, ApproveAPInvoiceCommand, CreateAPInvoiceCommand, InvoiceId, OCRService, ProcessPaymentCommand, TenantId } from '../../core/entities/ap-invoice';
import { ZUGFeRDAdapterApplicationService } from './zugferd-adapter-service';
export interface EventPublisher {
    publish(event: any): Promise<void>;
}
export interface APInvoiceServiceDependencies {
    apInvoiceRepository: APInvoiceRepository;
    ocrService: OCRService;
    aiBookingService: AIBookingService;
    zugferdAdapter?: ZUGFeRDAdapterApplicationService;
    eventPublisher: EventPublisher;
}
export declare class APInvoiceApplicationService implements APInvoiceService {
    private readonly dependencies;
    constructor(dependencies: APInvoiceServiceDependencies);
    /**
     * Create AP invoice from document
     */
    createInvoice(command: CreateAPInvoiceCommand): Promise<InvoiceId>;
    /**
     * Approve invoice with booking entries
     */
    approveInvoice(command: ApproveAPInvoiceCommand): Promise<void>;
    /**
     * Process payment for invoice
     */
    processPayment(command: ProcessPaymentCommand): Promise<void>;
    /**
     * Get invoice by ID
     */
    getInvoice(invoiceId: InvoiceId): Promise<APInvoice | null>;
    /**
     * List invoices for tenant
     */
    listInvoices(tenantId: TenantId, status?: APInvoice['status']): Promise<APInvoice[]>;
    /**
     * Get overdue invoices
     */
    getOverdueInvoices(tenantId: TenantId): Promise<APInvoice[]>;
    /**
     * Get invoices pending approval
     */
    getPendingApprovalInvoices(tenantId: TenantId): Promise<APInvoice[]>;
    /**
     * Process e-invoice document with ZUGFeRD adapter
     */
    processEInvoiceDocument(file: Buffer, filename: string, tenantId: TenantId, supplierId?: string): Promise<InvoiceId>;
    /**
     * Create AP invoice from normalized e-invoice data
     */
    private createInvoiceFromEInvoice;
    /**
     * Process invoice document (auto-detects e-invoice vs OCR)
     */
    processInvoiceDocument(documentPath: string, tenantId: TenantId, supplierId?: string): Promise<InvoiceId>;
    /**
     * Check if document is an e-invoice
     */
    private isEInvoiceDocument;
    /**
     * Process invoice document with OCR (legacy method)
     */
    private processInvoiceDocumentOCR;
}
export declare function createAPInvoiceService(dependencies: APInvoiceServiceDependencies): APInvoiceService;
//# sourceMappingURL=ap-invoice-service.d.ts.map