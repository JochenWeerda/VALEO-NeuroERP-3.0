/**
 * VALEO NeuroERP 3.0 - Finance Domain - E-Invoice Repository Interfaces
 *
 * Repository interfaces for e-invoice document management
 * Following Repository pattern and Clean Architecture
 */
import { TenantId } from '../../core/entities/ledger';
export interface EInvoiceDocument {
    readonly id: string;
    readonly tenantId: TenantId;
    readonly documentId: string;
    readonly filename: string;
    readonly content: Buffer;
    readonly kind: 'PDFA3' | 'XML' | 'UBL' | 'CII';
    readonly mimetype: string;
    readonly profile?: string;
    readonly schemaVersion?: string;
    readonly validationStatus: 'PENDING' | 'VALID' | 'INVALID' | 'ERROR';
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
}
export interface EInvoiceValidation {
    readonly id: string;
    readonly tenantId: TenantId;
    readonly documentId: string;
    readonly validatorName: string;
    readonly validatorVersion: string;
    readonly validationResult: {
        valid: boolean;
        profile: string;
        schemaVersion: string;
        errors: ValidationError[];
        warnings: ValidationWarning[];
    };
    readonly passed: boolean;
    readonly errorCount: number;
    readonly warningCount: number;
    readonly executionTimeMs?: number;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
}
export interface EInvoiceProfile {
    readonly id: string;
    readonly tenantId: TenantId;
    readonly profileName: string;
    readonly standard: 'ZUGFeRD' | 'XRECHNUNG' | 'PEPPOL';
    readonly version: string;
    readonly isActive: boolean;
    readonly configuration: {
        schema: 'CII' | 'UBL';
        conformance: string;
        validation: {
            xml: boolean;
            schematron: boolean;
            en16931?: boolean;
            xrechnung?: boolean;
            peppol?: boolean;
        };
    };
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
export interface EInvoiceNormalized {
    readonly id: string;
    readonly tenantId: TenantId;
    readonly invoiceId: string;
    readonly invoiceType: 'AP' | 'AR';
    readonly normalizedData: any;
    readonly normalizationVersion: string;
    readonly confidenceScore?: number;
    readonly normalizationMetadata: Record<string, any>;
    readonly createdAt: Date;
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
export interface EInvoiceDocumentRepository {
    save(document: Omit<EInvoiceDocument, 'id' | 'createdAt'>): Promise<EInvoiceDocument>;
    findById(id: string): Promise<EInvoiceDocument | null>;
    findByDocumentId(tenantId: TenantId, documentId: string): Promise<EInvoiceDocument | null>;
    findByProfile(tenantId: TenantId, profile: string): Promise<EInvoiceDocument[]>;
    findByValidationStatus(tenantId: TenantId, status: EInvoiceDocument['validationStatus']): Promise<EInvoiceDocument[]>;
    delete(id: string): Promise<void>;
}
export interface EInvoiceValidationRepository {
    save(validation: Omit<EInvoiceValidation, 'id' | 'createdAt'>): Promise<EInvoiceValidation>;
    findById(id: string): Promise<EInvoiceValidation | null>;
    findByDocumentId(documentId: string): Promise<EInvoiceValidation[]>;
    findLatestByDocumentId(documentId: string): Promise<EInvoiceValidation | null>;
    findByValidator(tenantId: TenantId, validatorName: string): Promise<EInvoiceValidation[]>;
    findFailedValidations(tenantId: TenantId): Promise<EInvoiceValidation[]>;
}
export interface EInvoiceProfileRepository {
    save(profile: Omit<EInvoiceProfile, 'id' | 'createdAt' | 'updatedAt'>): Promise<EInvoiceProfile>;
    findById(id: string): Promise<EInvoiceProfile | null>;
    findByName(tenantId: TenantId, profileName: string): Promise<EInvoiceProfile | null>;
    findActiveProfiles(tenantId: TenantId): Promise<EInvoiceProfile[]>;
    findByStandard(tenantId: TenantId, standard: EInvoiceProfile['standard']): Promise<EInvoiceProfile[]>;
    update(id: string, profile: Partial<EInvoiceProfile>): Promise<EInvoiceProfile>;
}
export interface EInvoiceNormalizedRepository {
    save(normalized: Omit<EInvoiceNormalized, 'id' | 'createdAt'>): Promise<EInvoiceNormalized>;
    findById(id: string): Promise<EInvoiceNormalized | null>;
    findByInvoiceId(tenantId: TenantId, invoiceId: string, invoiceType: 'AP' | 'AR'): Promise<EInvoiceNormalized | null>;
    findByConfidence(threshold: number): Promise<EInvoiceNormalized[]>;
    update(id: string, normalized: Partial<EInvoiceNormalized>): Promise<EInvoiceNormalized>;
}
//# sourceMappingURL=einvoice-repository.d.ts.map