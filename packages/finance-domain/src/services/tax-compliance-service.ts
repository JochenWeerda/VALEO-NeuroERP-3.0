/**
 * VALEO NeuroERP 3.0 - Tax Compliance Service
 *
 * Handles VAT calculation, tax validation, and German tax export formats
 * Supports DATEV, ELSTER, and EU tax compliance requirements
 */

import { Result, err, ok } from '../core/entities/ar-invoice';

// ===== INTERFACES =====

export interface TaxCalculation {
  readonly id: string;
  readonly tenantId: string;
  readonly period: string; // YYYY-MM
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

// ===== COMMANDS =====

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

// ===== SERVICE =====

export class TaxComplianceApplicationService {
  constructor(
    private readonly taxCalculationRepo: TaxCalculationRepository,
    private readonly taxReturnRepo: TaxReturnRepository,
    private readonly taxValidationRepo: TaxValidationRepository,
    private readonly eventPublisher: EventPublisher,
    private readonly countryProfiles: Map<string, CountryTaxProfile>
  ) {}

  /**
   * Calculate VAT for a period
   */
  async calculateVAT(command: CalculateTaxCommand): Promise<Result<TaxCalculation[]>> {
    try {
      const calculations: TaxCalculation[] = [];
      const countryProfile = this.countryProfiles.get(command.countryCode);

      if (!countryProfile) {
        return err(`No tax profile found for country: ${command.countryCode}`);
      }

      for (const transaction of command.transactions) {
        const taxRate = await this.getEffectiveTaxRate(
          transaction.taxCode,
          command.countryCode,
          countryProfile
        );

        const taxAmount = transaction.amount * (taxRate / 100);

        const calculation: TaxCalculation = {
          id: crypto.randomUUID(),
          tenantId: command.tenantId,
          period: command.period,
          countryCode: command.countryCode,
          taxType: 'VAT',
          baseAmount: transaction.amount,
          taxRate,
          taxAmount,
          taxCode: transaction.taxCode,
          description: transaction.description,
          metadata: {
            accountNumber: transaction.accountNumber,
            originalTaxCode: transaction.taxCode
          },
          calculatedAt: new Date()
        };

        calculations.push(calculation);
        await this.taxCalculationRepo.save(calculation);
      }

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.tax.calculated',
        tenantId: command.tenantId,
        period: command.period,
        countryCode: command.countryCode,
        calculationCount: calculations.length,
        totalTaxAmount: calculations.reduce((sum, calc) => sum + calc.taxAmount, 0)
      });

      return ok(calculations);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'Tax calculation failed');
    }
  }

  /**
   * Generate DATEV export
   */
  async generateDATEVExport(command: GenerateDATEVExportCommand): Promise<Result<DATEVExport>> {
    try {
      // Get all tax calculations for the period
      const calculations = await this.taxCalculationRepo.findByPeriod(
        command.tenantId,
        command.period
      );

      if (calculations.length === 0) {
        return err(`No tax calculations found for period: ${command.period}`);
      }

      // Convert to DATEV format
      const currentDate = new Date();
      const dateString = currentDate.toISOString().split('T')[0]!;

      const datevData: DATEVExportData[] = calculations.map(calc => ({
        accountNumber: calc.metadata.accountNumber || '1000',
        accountName: this.getAccountName(calc.metadata.accountNumber || '1000'),
        date: dateString,
        description: calc.description,
        amount: calc.baseAmount,
        taxCode: calc.taxCode,
        costCenter: calc.metadata.costCenter,
        documentRef: calc.metadata.documentRef
      }));

      // Generate DATEV header and content
      const datevContent = this.generateDATEVContent(
        command,
        datevData,
        calculations
      );

      const exportData: DATEVExport = {
        id: crypto.randomUUID(),
        tenantId: command.tenantId,
        period: command.period,
        formatVersion: '7.0',
        data: datevData,
        hash: this.calculateHash(datevContent),
        generatedAt: new Date()
      };

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.tax.datev.generated',
        tenantId: command.tenantId,
        period: command.period,
        recordCount: datevData.length,
        hash: exportData.hash
      });

      return ok(exportData);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'DATEV export failed');
    }
  }

  /**
   * Generate ELSTER export
   */
  async generateELSTERExport(command: GenerateELSTERExportCommand): Promise<Result<ELSTERExport>> {
    try {
      // Get tax return for the period
      const taxReturn = await this.taxReturnRepo.findByPeriod(
        command.tenantId,
        command.period
      );

      if (!taxReturn) {
        return err(`No tax return found for period: ${command.period}`);
      }

      // Generate ELSTER XML
      const elsterXml = this.generateELSTERXml(command, taxReturn);

      const exportData: ELSTERExport = {
        id: crypto.randomUUID(),
        tenantId: command.tenantId,
        period: command.period,
        taxNumber: command.taxNumber,
        xmlContent: elsterXml,
        hash: this.calculateHash(elsterXml),
        generatedAt: new Date()
      };

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.tax.elster.generated',
        tenantId: command.tenantId,
        period: command.period,
        taxNumber: command.taxNumber,
        hash: exportData.hash
      });

      return ok(exportData);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'ELSTER export failed');
    }
  }

  /**
   * Validate tax compliance
   */
  async validateTaxCompliance(command: ValidateTaxComplianceCommand): Promise<Result<TaxValidationResult>> {
    try {
      const rules = await this.taxValidationRepo.findActiveRules(
        command.countryCode
      );

      const calculations = await this.taxCalculationRepo.findByPeriod(
        command.tenantId,
        command.period
      );

      const errors: TaxValidationIssue[] = [];
      const warnings: TaxValidationIssue[] = [];
      const info: TaxValidationIssue[] = [];

      // Apply validation rules
      for (const rule of rules) {
        const ruleResult = await this.applyValidationRule(rule, calculations, command);

        if (ruleResult.isFailure) {
          errors.push({
            ruleId: rule.id,
            ruleName: rule.name,
            severity: 'ERROR',
            message: ruleResult.error || 'Validation failed'
          });
        } else {
          const issues = ruleResult.getValue();
          errors.push(...issues.filter(i => i.severity === 'ERROR'));
          warnings.push(...issues.filter(i => i.severity === 'WARNING'));
          info.push(...issues.filter(i => i.severity === 'INFO'));
        }
      }

      const result: TaxValidationResult = {
        isValid: errors.length === 0,
        errors,
        warnings,
        info
      };

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.tax.validated',
        tenantId: command.tenantId,
        period: command.period,
        countryCode: command.countryCode,
        isValid: result.isValid,
        errorCount: errors.length,
        warningCount: warnings.length
      });

      return ok(result);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'Tax validation failed');
    }
  }

  /**
   * Get effective tax rate for tax code and country
   */
  private async getEffectiveTaxRate(
    taxCode: string,
    countryCode: string,
    countryProfile: CountryTaxProfile
  ): Promise<number> {
    // Get rate from country profile
    const rate = countryProfile.taxRates[taxCode];
    if (rate !== undefined) {
      return rate;
    }

    // Fallback to default rates
    const defaultRates: Record<string, number> = {
      'DE-19': 19.0,
      'DE-7': 7.0,
      'AT-20': 20.0,
      'AT-10': 10.0,
      'CH-8.1': 8.1,
      'CH-3.8': 3.8
    };

    return defaultRates[taxCode] || 0;
  }

  /**
   * Generate DATEV content
   */
  private generateDATEVContent(
    command: GenerateDATEVExportCommand,
    data: DATEVExportData[],
    calculations: TaxCalculation[]
  ): string {
    const header = `"DATEV Export";
"Version";"7.0"
"Client";"${command.clientNumber}"
"Consultant";"${command.consultantNumber}"
"Period";"${command.period}"
"Currency";"EUR"
"Data";
`;

    const records = data.map((record, index) => {
      const calculation = calculations[index];
      return `"${record.accountNumber}";"${record.accountName}";"${record.date}";"${record.description}";"${record.amount}";"${record.taxCode}";"${record.costCenter || ''}";"${record.documentRef || ''}"`;
    }).join('\n');

    return header + records;
  }

  /**
   * Generate ELSTER XML
   */
  private generateELSTERXml(command: GenerateELSTERExportCommand, taxReturn: TaxReturn): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<Elster xmlns="http://www.elster.de">
  <TransferHeader>
    <TaxNumber>${command.taxNumber}</TaxNumber>
    <TaxOffice>${command.taxOfficeNumber}</TaxOffice>
    <Period>${taxReturn.period}</Period>
    <Year>${taxReturn.period.split('-')[0]}</Year>
  </TransferHeader>
  <VATDeclaration>
    <TaxPayable>${taxReturn.totalTaxPayable}</TaxPayable>
    <TaxReceivable>${taxReturn.totalTaxReceivable}</TaxReceivable>
    <NetAmount>${taxReturn.netAmount}</NetAmount>
  </VATDeclaration>
</Elster>`;
  }

  /**
   * Apply validation rule
   */
  private async applyValidationRule(
    rule: TaxValidationRule,
    calculations: TaxCalculation[],
    command: ValidateTaxComplianceCommand
  ): Promise<Result<TaxValidationIssue[]>> {
    const issues: TaxValidationIssue[] = [];

    try {
      // Simple rule evaluation (in reality would use a rule engine)
      switch (rule.rule) {
        case 'TOTAL_VAT_CHECK':
          const totalVAT = calculations.reduce((sum, calc) => sum + calc.taxAmount, 0);
          if (totalVAT === 0) {
            issues.push({
              ruleId: rule.id,
              ruleName: rule.name,
              severity: 'WARNING',
              message: 'No VAT calculated for the period'
            });
          }
          break;

        case 'TAX_CODE_VALIDITY':
          const invalidCodes = calculations.filter(calc =>
            !this.isValidTaxCode(calc.taxCode, command.countryCode)
          );
          for (const calc of invalidCodes) {
            issues.push({
              ruleId: rule.id,
              ruleName: rule.name,
              severity: 'ERROR',
              message: `Invalid tax code: ${calc.taxCode}`,
              field: 'taxCode',
              value: calc.taxCode
            });
          }
          break;
      }

      return ok(issues);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'Rule evaluation failed');
    }
  }

  /**
   * Validate tax code for country
   */
  private isValidTaxCode(taxCode: string, countryCode: string): boolean {
    const validCodes: Record<string, string[]> = {
      'DE': ['DE-19', 'DE-7', 'DE-0'],
      'AT': ['AT-20', 'AT-10', 'AT-0'],
      'CH': ['CH-8.1', 'CH-3.8', 'CH-2.6', 'CH-0']
    };

    return validCodes[countryCode]?.includes(taxCode) || false;
  }

  /**
   * Get account name from number
   */
  private getAccountName(accountNumber: string): string {
    const accountNames: Record<string, string> = {
      '1000': 'Kasse',
      '1200': 'Bank',
      '1400': 'Forderungen',
      '1600': 'Verbindlichkeiten',
      '1776': 'Umsatzsteuer 19%',
      '4000': 'Umsatzerlöse',
      '6000': 'Materialaufwand'
    };

    return accountNames[accountNumber] || 'Unknown Account';
  }

  /**
   * Calculate hash for content
   */
  private calculateHash(content: string): string {
    // Simple hash for demo - in production use crypto.subtle
    return Buffer.from(content).toString('base64').substring(0, 32);
  }
}

// ===== COUNTRY PROFILES =====

export interface CountryTaxProfile {
  countryCode: string;
  countryName: string;
  currency: string;
  taxRates: Record<string, number>;
  validationRules: string[];
  exportFormats: string[];
}

export class GermanTaxProfile implements CountryTaxProfile {
  countryCode = 'DE';
  countryName = 'Deutschland';
  currency = 'EUR';
  taxRates = {
    'DE-19': 19.0,
    'DE-7': 7.0,
    'DE-0': 0.0
  };
  validationRules = [
    'EU_VAT_DIRECTIVE',
    'GERMAN_TAX_CODE_FORMAT',
    'REVERSE_CHARGE_VALIDATION'
  ];
  exportFormats = ['DATEV', 'ELSTER', 'XRECHNUNG'];
}

// ===== REPOSITORY INTERFACES =====

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

// ===== ADDITIONAL INTERFACES =====

export interface EventPublisher {
  publish(event: any): Promise<void>;
}

export interface JournalService {
  getJournalEntries(tenantId: string, period: string): Promise<any[]>;
}