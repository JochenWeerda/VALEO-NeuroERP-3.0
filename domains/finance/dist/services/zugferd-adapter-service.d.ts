/**
 * VALEO NeuroERP 3.0 - ZUGFeRD Adapter Service
 *
 * E-Invoice adapter for ZUGFeRD 2.1.1 compliance
 * Handles parsing, validation, and generation of ZUGFeRD invoices
 */
import { Result } from '../core/entities/ar-invoice';
export interface EInvoiceDocument {
    id: string;
    fileName: string;
    mimeType: string;
    content: Buffer;
    size: number;
    hash: string;
}
export interface ZUGFeRDProfile {
    version: string;
    profile: 'BASIC' | 'EN16931' | 'EXTENDED';
    conformanceLevel: 'BASIC' | 'COMFORT' | 'EXTENDED';
}
export interface NormalizedInvoice {
    supplier: {
        vatId: string;
        name: string;
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
        };
        contact?: {
            email?: string;
            phone?: string;
        };
    };
    buyer: {
        vatId: string;
        name: string;
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
        };
    };
    invoice: {
        id: string;
        issueDate: string;
        dueDate: string;
        currency: string;
        lines: Array<{
            id: string;
            sku?: string;
            name: string;
            description?: string;
            quantity: number;
            unitPrice: number;
            taxPercent: number;
            taxCode: string;
            net: number;
            tax: number;
            gross: number;
        }>;
        totals: {
            net: number;
            tax: number;
            gross: number;
        };
        payment: {
            iban?: string;
            bic?: string;
            terms: string;
        };
        profile: string;
        attachments: Array<{
            filename: string;
            mimeType: string;
            content: Buffer;
        }>;
    };
}
export interface ValidationResult {
    valid: boolean;
    profile: string;
    schemaVersion: string;
    issues: Array<{
        type: 'ERROR' | 'WARNING' | 'INFO';
        code: string;
        message: string;
        field?: string;
    }>;
}
export interface EInvoiceAdapter {
    detectProfile(document: EInvoiceDocument): Promise<Result<ZUGFeRDProfile>>;
    parseToNormalized(document: EInvoiceDocument): Promise<Result<NormalizedInvoice>>;
    validate(document: EInvoiceDocument): Promise<Result<ValidationResult>>;
    renderPDFA3(invoice: NormalizedInvoice): Promise<Result<Buffer>>;
}
export declare class ZUGFeRDAdapterService {
    private adapter;
    private documentStore;
    private eventPublisher;
    constructor(adapter: EInvoiceAdapter, documentStore: DocumentStore, eventPublisher: EventPublisher);
    /**
     * Ingest and process e-invoice document
     */
    ingestEInvoice(document: EInvoiceDocument, options?: {
        detectProfile?: boolean;
    }): Promise<Result<{
        profile: ZUGFeRDProfile;
        normalizedInvoice: NormalizedInvoice;
        validation: ValidationResult;
        xmlRef?: string;
        pdfa3Ref?: string;
    }>>;
    /**
     * Validate e-invoice document
     */
    validateEInvoice(documentRef: string): Promise<Result<ValidationResult>>;
    /**
     * Render normalized invoice as PDF/A-3
     */
    renderPDFA3(invoice: NormalizedInvoice): Promise<Result<Buffer>>;
    private calculateHash;
}
export interface DocumentStore {
    store(document: EInvoiceDocument): Promise<string>;
    retrieve(ref: string): Promise<EInvoiceDocument | null>;
    delete(ref: string): Promise<void>;
}
export interface EventPublisher {
    publish(event: any): Promise<void>;
}
export declare class MockZUGFeRDAdapter implements EInvoiceAdapter {
    detectProfile(document: EInvoiceDocument): Promise<Result<ZUGFeRDProfile>>;
    parseToNormalized(document: EInvoiceDocument): Promise<Result<NormalizedInvoice>>;
    validate(document: EInvoiceDocument): Promise<Result<ValidationResult>>;
    renderPDFA3(invoice: NormalizedInvoice): Promise<Result<Buffer>>;
}
export interface EInvoiceRepository {
    saveValidation(result: ValidationResult): Promise<string>;
    findValidationByDocument(docRef: string): Promise<ValidationResult | null>;
    saveNormalized(invoice: NormalizedInvoice): Promise<string>;
    findNormalizedById(id: string): Promise<NormalizedInvoice | null>;
}
//# sourceMappingURL=zugferd-adapter-service.d.ts.map