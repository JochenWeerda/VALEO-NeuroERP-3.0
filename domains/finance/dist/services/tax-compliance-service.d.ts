/**
 * VALEO NeuroERP 3.0 - Tax Compliance Service
 *
 * Handles VAT calculation, tax validation, and German tax export formats
 * Supports DATEV, ELSTER, and EU tax compliance requirements
 */
import { Result } from '../core/entities/ar-invoice';
export interface TaxCalculation {
    readonly id: string;
    readonly tenantId: string;
    readonly period: string;
    readonly countryCode: string;
    readonly taxType: 'VAT' | 'SALES_TAX' | 'WITHHOLDING';
    readonly baseAmount: number;
    readonly taxRate: number;
    readonly taxAmount: number;
    readonly taxCode: string;
    readonly description: string;
    readonly metadata: Record<string, any>;
    readonly calculatedAt: Date;
}
export interface TaxReturn {
    readonly id: string;
    readonly tenantId: string;
    readonly period: string;
    readonly countryCode: string;
    readonly returnType: 'VAT' | 'INCOME' | 'CORPORATE';
    readonly status: 'DRAFT' | 'SUBMITTED' | 'ACCEPTED' | 'REJECTED';
    readonly calculations: TaxCalculation[];
    readonly totalTaxPayable: number;
    readonly totalTaxReceivable: number;
    readonly netAmount: number;
    readonly submittedAt?: Date;
    readonly acceptedAt?: Date;
    readonly metadata: Record<string, any>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
export interface DATEVExport {
    readonly id: string;
    readonly tenantId: string;
    readonly period: string;
    readonly formatVersion: string;
    readonly data: DATEVExportData[];
    readonly hash: string;
    readonly generatedAt: Date;
}
export interface DATEVExportData {
    accountNumber: string;
    accountName: string;
    date: string;
    description: string;
    amount: number;
    taxCode: string;
    costCenter?: string;
    documentRef?: string;
}
export interface ELSTERExport {
    readonly id: string;
    readonly tenantId: string;
    readonly period: string;
    readonly taxNumber: string;
    readonly xmlContent: string;
    readonly hash: string;
    readonly generatedAt: Date;
}
export interface TaxValidationRule {
    readonly id: string;
    readonly name: string;
    readonly countryCode: string;
    readonly taxType: string;
    readonly rule: string;
    readonly severity: 'ERROR' | 'WARNING' | 'INFO';
    readonly description: string;
    readonly isActive: boolean;
}
export interface TaxValidationResult {
    readonly isValid: boolean;
    readonly errors: TaxValidationIssue[];
    readonly warnings: TaxValidationIssue[];
    readonly info: TaxValidationIssue[];
}
export interface TaxValidationIssue {
    readonly ruleId: string;
    readonly ruleName: string;
    readonly severity: 'ERROR' | 'WARNING' | 'INFO';
    readonly message: string;
    readonly field?: string;
    readonly value?: any;
    readonly expectedValue?: any;
}
export interface CalculateTaxCommand {
    readonly tenantId: string;
    readonly period: string;
    readonly countryCode: string;
    readonly transactions: Array<{
        amount: number;
        taxRate: number;
        taxCode: string;
        description: string;
        accountNumber: string;
    }>;
}
export interface GenerateDATEVExportCommand {
    readonly tenantId: string;
    readonly period: string;
    readonly clientNumber: string;
    readonly consultantNumber: string;
}
export interface GenerateELSTERExportCommand {
    readonly tenantId: string;
    readonly period: string;
    readonly taxNumber: string;
    readonly taxOfficeNumber: string;
}
export interface ValidateTaxComplianceCommand {
    readonly tenantId: string;
    readonly period: string;
    readonly countryCode: string;
}
export declare class TaxComplianceApplicationService {
    private taxCalculationRepo;
    private taxReturnRepo;
    private taxValidationRepo;
    private eventPublisher;
    private countryProfiles;
    constructor(taxCalculationRepo: TaxCalculationRepository, taxReturnRepo: TaxReturnRepository, taxValidationRepo: TaxValidationRepository, eventPublisher: EventPublisher, countryProfiles: Map<string, CountryTaxProfile>);
    /**
     * Calculate VAT for a period
     */
    calculateVAT(command: CalculateTaxCommand): Promise<Result<TaxCalculation[]>>;
    /**
     * Generate DATEV export
     */
    generateDATEVExport(command: GenerateDATEVExportCommand): Promise<Result<DATEVExport>>;
    /**
     * Generate ELSTER export
     */
    generateELSTERExport(command: GenerateELSTERExportCommand): Promise<Result<ELSTERExport>>;
    /**
     * Validate tax compliance
     */
    validateTaxCompliance(command: ValidateTaxComplianceCommand): Promise<Result<TaxValidationResult>>;
    /**
     * Get effective tax rate for tax code and country
     */
    private getEffectiveTaxRate;
    /**
     * Generate DATEV content
     */
    private generateDATEVContent;
    /**
     * Generate ELSTER XML
     */
    private generateELSTERXml;
    /**
     * Apply validation rule
     */
    private applyValidationRule;
    /**
     * Validate tax code for country
     */
    private isValidTaxCode;
    /**
     * Get account name from number
     */
    private getAccountName;
    /**
     * Calculate hash for content
     */
    private calculateHash;
}
export interface CountryTaxProfile {
    countryCode: string;
    countryName: string;
    currency: string;
    taxRates: Record<string, number>;
    validationRules: string[];
    exportFormats: string[];
}
export declare class GermanTaxProfile implements CountryTaxProfile {
    countryCode: string;
    countryName: string;
    currency: string;
    taxRates: {
        'DE-19': number;
        'DE-7': number;
        'DE-0': number;
    };
    validationRules: string[];
    exportFormats: string[];
}
export interface TaxCalculationRepository {
    save(calculation: TaxCalculation): Promise<void>;
    findById(id: string): Promise<TaxCalculation | null>;
    findByPeriod(tenantId: string, period: string): Promise<TaxCalculation[]>;
    findByTenant(tenantId: string): Promise<TaxCalculation[]>;
}
export interface TaxReturnRepository {
    save(taxReturn: TaxReturn): Promise<void>;
    findById(id: string): Promise<TaxReturn | null>;
    findByPeriod(tenantId: string, period: string): Promise<TaxReturn | null>;
    findByTenant(tenantId: string): Promise<TaxReturn[]>;
}
export interface TaxValidationRepository {
    saveRule(rule: TaxValidationRule): Promise<void>;
    findActiveRules(countryCode: string): Promise<TaxValidationRule[]>;
    findRuleById(id: string): Promise<TaxValidationRule | null>;
}
export interface EventPublisher {
    publish(event: any): Promise<void>;
}
export interface JournalService {
    getJournalEntries(tenantId: string, period: string): Promise<any[]>;
}
//# sourceMappingURL=tax-compliance-service.d.ts.map