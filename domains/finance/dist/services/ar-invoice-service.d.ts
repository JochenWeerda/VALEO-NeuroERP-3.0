/**
 * VALEO NeuroERP 3.0 - AR Invoice Service
 *
 * Application service for Accounts Receivable (AR) invoice management
 * Handles outgoing invoices, dunning process, and payment tracking
 */
import { ArInvoiceId, CreateArInvoiceCommand, UpdateArInvoiceCommand, RecordPaymentCommand, ProcessDunningCommand, ArInvoice } from '../core/entities/ar-invoice';
interface Result<T> {
    isSuccess: boolean;
    isFailure: boolean;
    getValue(): T;
    error?: string;
}
export interface ArInvoiceServiceDependencies {
    arInvoiceRepository: ArInvoiceRepository;
    customerRepository: CustomerRepository;
    eventPublisher: EventPublisher;
    clock: Clock;
}
export interface ArInvoiceRepository {
    save(invoice: ArInvoice): Promise<void>;
    findById(id: ArInvoiceId): Promise<ArInvoice | null>;
    findByCustomer(customerId: string): Promise<ArInvoice[]>;
    findByTenant(tenantId: string): Promise<ArInvoice[]>;
    findOverdue(tenantId: string): Promise<ArInvoice[]>;
    findByStatus(tenantId: string, status: string): Promise<ArInvoice[]>;
    findByDunningLevel(tenantId: string, level: number): Promise<ArInvoice[]>;
}
export interface CustomerRepository {
    findById(id: string): Promise<any | null>;
    findByTenant(tenantId: string): Promise<any[]>;
}
export interface EventPublisher {
    publish(event: any): Promise<void>;
}
export interface Clock {
    now(): Date;
}
export declare class ArInvoiceApplicationService {
    private arInvoiceRepo;
    private customerRepo;
    private eventPublisher;
    private clock;
    constructor(arInvoiceRepo: ArInvoiceRepository, customerRepo: CustomerRepository, eventPublisher: EventPublisher, clock: Clock);
    /**
     * Create a new AR invoice
     */
    createInvoice(command: CreateArInvoiceCommand): Promise<ArInvoiceId>;
    /**
     * Update an existing AR invoice
     */
    updateInvoice(command: UpdateArInvoiceCommand): Promise<void>;
    /**
     * Issue an AR invoice (change status from DRAFT to ISSUED)
     */
    issueInvoice(invoiceId: ArInvoiceId, issuedBy: string): Promise<void>;
    /**
     * Send an AR invoice (change status from ISSUED to SENT)
     */
    sendInvoice(invoiceId: ArInvoiceId, sentBy: string): Promise<void>;
    /**
     * Record a payment against an AR invoice
     */
    recordPayment(command: RecordPaymentCommand): Promise<void>;
    /**
     * Process dunning for overdue invoices
     */
    processDunning(command: ProcessDunningCommand): Promise<void>;
    /**
     * Cancel an AR invoice
     */
    cancelInvoice(invoiceId: ArInvoiceId, reason: string, cancelledBy: string): Promise<void>;
    /**
     * Get AR invoice by ID
     */
    getInvoice(id: ArInvoiceId): Promise<ArInvoice | null>;
    /**
     * Get all invoices for a customer
     */
    getInvoicesByCustomer(customerId: string): Promise<ArInvoice[]>;
    /**
     * Get all invoices for a tenant
     */
    getInvoicesByTenant(tenantId: string): Promise<ArInvoice[]>;
    /**
     * Get overdue invoices for a tenant
     */
    getOverdueInvoices(tenantId: string): Promise<ArInvoice[]>;
    /**
     * Get open items (outstanding receivables) for a tenant
     */
    getOpenItems(tenantId: string): Promise<ArInvoice[]>;
    /**
     * Get dunning candidates for a tenant
     */
    getDunningCandidates(tenantId: string, dunningLevel?: number): Promise<ArInvoice[]>;
    /**
     * Calculate total outstanding amount for a tenant
     */
    getTotalOutstanding(tenantId: string): Promise<number>;
    /**
     * Export AR invoice as XRechnung XML
     */
    exportXRechnung(invoiceId: ArInvoiceId): Promise<Result<Buffer>>;
    /**
     * Export AR invoice as PEPPOL envelope
     */
    exportPEPPOL(invoiceId: ArInvoiceId): Promise<Result<Buffer>>;
    /**
     * Export AR invoice as ZUGFeRD PDF/A-3
     */
    exportZUGFeRD(invoiceId: ArInvoiceId): Promise<Result<Buffer>>;
    /**
     * Format date to YYYY-MM-DD string
     */
    private formatDate;
    /**
     * Generate XRechnung XML from AR invoice
     */
    private generateXRechnungXml;
    /**
     * Generate PEPPOL envelope
     */
    private generatePEPPOL;
    /**
     * Convert AR invoice to normalized format for ZUGFeRD
     */
    private convertToNormalizedFormat;
    /**
     * Get aging report for a tenant
     */
    getAgingReport(tenantId: string): Promise<{
        current: number;
        thirtyDays: number;
        sixtyDays: number;
        ninetyDays: number;
        older: number;
    }>;
}
export {};
//# sourceMappingURL=ar-invoice-service.d.ts.map