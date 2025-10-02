/**
 * VALEO NeuroERP 3.0 - Finance Domain - ZUGFeRD Adapter Service
 *
 * E-Invoice adapter for ZUGFeRD/XRechnung compliance
 * Handles document processing, validation, and format conversion
 */
import { EInvoiceDocument, EInvoiceDocumentRepository, EInvoiceNormalized, EInvoiceNormalizedRepository, EInvoiceProfileRepository, EInvoiceValidationRepository } from '../../infrastructure/repositories/einvoice-repository';
export interface EventPublisher {
    publish(event: any): Promise<void>;
}
export interface DomainEvent {
    type: string;
    occurredAt: Date;
    aggregateId: string;
    tenantId: string;
}
export interface EInvoiceAdapter {
    detectProfile(document: Buffer): Promise<string | null>;
    extractXML(document: Buffer): Promise<{
        xml: string;
        profile: string;
    } | null>;
    validateDocument(document: Buffer, profile: string): Promise<ValidationResult>;
    generatePDFA3(invoice: EInvoiceNormalized, xml: string): Promise<Buffer>;
    embedXMLInPDF(pdf: Buffer, xml: string): Promise<Buffer>;
}
export interface ValidationResult {
    valid: boolean;
    profile: string;
    schemaVersion: string;
    errors: ValidationError[];
    warnings: ValidationWarning[];
    executionTime: number;
}
export interface ValidationError {
    code: string;
    message: string;
    path: string;
    severity: 'ERROR' | 'WARNING';
}
export interface ValidationWarning {
    code: string;
    message: string;
    path: string;
}
export interface ZUGFeRDAdapterServiceDependencies {
    documentRepository: EInvoiceDocumentRepository;
    validationRepository: EInvoiceValidationRepository;
    profileRepository: EInvoiceProfileRepository;
    normalizedRepository: EInvoiceNormalizedRepository;
    adapter: EInvoiceAdapter;
    eventPublisher: EventPublisher;
}
export interface EInvoiceNormalizedDTO {
    supplier: {
        vatId: string;
        name: string;
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
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
            sku?: string;
            name: string;
            qty: number;
            price: number;
            taxPercent: number;
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
        attachments: Array<{
            filename: string;
            mimeType: string;
            data: Buffer;
        }>;
    };
    profile: string;
}
export declare class ZUGFeRDAdapterApplicationService {
    private readonly dependencies;
    constructor(dependencies: ZUGFeRDAdapterServiceDependencies);
    /**
     * Ingest e-invoice document
     */
    ingestEInvoice(file: Buffer, filename: string, tenantId: string, options?: {
        detectProfile?: boolean;
    }): Promise<{
        document: EInvoiceDocument;
        normalized: EInvoiceNormalizedDTO | undefined;
        validation: ValidationResult;
    }>;
    /**
     * Validate e-invoice document
     */
    validateEInvoice(documentId: string, tenantId: string): Promise<ValidationResult>;
    /**
     * Render PDF/A-3 with embedded XML
     */
    renderPDFA3(invoice: EInvoiceNormalizedDTO, tenantId: string): Promise<{
        pdfBuffer: Buffer;
        xmlContent: string;
        documentId: string;
    }>;
    /**
     * Detect if buffer is PDF
     */
    private isPDF;
    private isXML;
    /**
     * Parse and normalize XML to DTO
     */
    private parseAndNormalizeXML;
    /**
     * Generate ZUGFeRD XML from normalized data
     */
    private generateZUGFeRDXML;
    /**
     * Generate base PDF/A-3
     */
    private generateBasePDF;
    /**
     * Calculate normalization confidence
     */
    private calculateNormalizationConfidence;
}
export declare function createZUGFeRDAdapterService(dependencies: ZUGFeRDAdapterServiceDependencies): ZUGFeRDAdapterApplicationService;
export declare class DefaultEInvoiceAdapter implements EInvoiceAdapter {
    detectProfile(document: Buffer): Promise<string | null>;
    extractXML(document: Buffer): Promise<{
        xml: string;
        profile: string;
    } | null>;
    validateDocument(document: Buffer, profile: string): Promise<ValidationResult>;
    generatePDFA3(invoice: EInvoiceNormalized, xml: string): Promise<Buffer>;
    embedXMLInPDF(pdf: Buffer, xml: string): Promise<Buffer>;
    private isXML;
    private isPDF;
    private detectXMLProfile;
    private isPDFA3;
}
export declare class EInvoiceParsedEvent implements DomainEvent {
    readonly documentId: string;
    readonly tenantId: string;
    readonly profile: string;
    readonly normalizedData: EInvoiceNormalizedDTO;
    readonly validationResult: ValidationResult;
    readonly type = "finance.einvoice.parsed";
    readonly occurredAt: Date;
    readonly aggregateId: string;
    constructor(documentId: string, tenantId: string, profile: string, normalizedData: EInvoiceNormalizedDTO, validationResult: ValidationResult);
}
export declare class EInvoiceValidatedEvent implements DomainEvent {
    readonly documentId: string;
    readonly tenantId: string;
    readonly validationResult: ValidationResult;
    readonly type = "finance.einvoice.validated";
    readonly occurredAt: Date;
    readonly aggregateId: string;
    constructor(documentId: string, tenantId: string, validationResult: ValidationResult);
}
export declare class EInvoiceRenderedEvent implements DomainEvent {
    readonly documentId: string;
    readonly tenantId: string;
    readonly profile: string;
    readonly pdfRef: string;
    readonly xmlRef: string;
    readonly hashes: {
        pdf: string;
        xml: string;
    };
    readonly type = "finance.einvoice.rendered";
    readonly occurredAt: Date;
    readonly aggregateId: string;
    constructor(documentId: string, tenantId: string, profile: string, pdfRef: string, xmlRef: string, hashes: {
        pdf: string;
        xml: string;
    });
}
//# sourceMappingURL=zugferd-adapter-service.d.ts.map