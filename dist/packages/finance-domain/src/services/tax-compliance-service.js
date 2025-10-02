"use strict";
/**
 * VALEO NeuroERP 3.0 - Tax Compliance Service
 *
 * Handles VAT calculation, tax validation, and German tax export formats
 * Supports DATEV, ELSTER, and EU tax compliance requirements
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.GermanTaxProfile = exports.TaxComplianceApplicationService = void 0;
const ar_invoice_1 = require("../core/entities/ar-invoice");
// ===== SERVICE =====
class TaxComplianceApplicationService {
    taxCalculationRepo;
    taxReturnRepo;
    taxValidationRepo;
    eventPublisher;
    countryProfiles;
    constructor(taxCalculationRepo, taxReturnRepo, taxValidationRepo, eventPublisher, countryProfiles) {
        this.taxCalculationRepo = taxCalculationRepo;
        this.taxReturnRepo = taxReturnRepo;
        this.taxValidationRepo = taxValidationRepo;
        this.eventPublisher = eventPublisher;
        this.countryProfiles = countryProfiles;
    }
    /**
     * Calculate VAT for a period
     */
    async calculateVAT(command) {
        try {
            const calculations = [];
            const countryProfile = this.countryProfiles.get(command.countryCode);
            if (!countryProfile) {
                return (0, ar_invoice_1.err)(`No tax profile found for country: ${command.countryCode}`);
            }
            for (const transaction of command.transactions) {
                const taxRate = await this.getEffectiveTaxRate(transaction.taxCode, command.countryCode, countryProfile);
                const taxAmount = transaction.amount * (taxRate / 100);
                const calculation = {
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
            return (0, ar_invoice_1.ok)(calculations);
        }
        catch (error) {
            return (0, ar_invoice_1.err)(error instanceof Error ? error.message : 'Tax calculation failed');
        }
    }
    /**
     * Generate DATEV export
     */
    async generateDATEVExport(command) {
        try {
            // Get all tax calculations for the period
            const calculations = await this.taxCalculationRepo.findByPeriod(command.tenantId, command.period);
            if (calculations.length === 0) {
                return (0, ar_invoice_1.err)(`No tax calculations found for period: ${command.period}`);
            }
            // Convert to DATEV format
            const currentDate = new Date();
            const dateString = currentDate.toISOString().split('T')[0];
            const datevData = calculations.map(calc => ({
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
            const datevContent = this.generateDATEVContent(command, datevData, calculations);
            const exportData = {
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
            return (0, ar_invoice_1.ok)(exportData);
        }
        catch (error) {
            return (0, ar_invoice_1.err)(error instanceof Error ? error.message : 'DATEV export failed');
        }
    }
    /**
     * Generate ELSTER export
     */
    async generateELSTERExport(command) {
        try {
            // Get tax return for the period
            const taxReturn = await this.taxReturnRepo.findByPeriod(command.tenantId, command.period);
            if (!taxReturn) {
                return (0, ar_invoice_1.err)(`No tax return found for period: ${command.period}`);
            }
            // Generate ELSTER XML
            const elsterXml = this.generateELSTERXml(command, taxReturn);
            const exportData = {
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
            return (0, ar_invoice_1.ok)(exportData);
        }
        catch (error) {
            return (0, ar_invoice_1.err)(error instanceof Error ? error.message : 'ELSTER export failed');
        }
    }
    /**
     * Validate tax compliance
     */
    async validateTaxCompliance(command) {
        try {
            const rules = await this.taxValidationRepo.findActiveRules(command.countryCode);
            const calculations = await this.taxCalculationRepo.findByPeriod(command.tenantId, command.period);
            const errors = [];
            const warnings = [];
            const info = [];
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
                }
                else {
                    const issues = ruleResult.getValue();
                    errors.push(...issues.filter(i => i.severity === 'ERROR'));
                    warnings.push(...issues.filter(i => i.severity === 'WARNING'));
                    info.push(...issues.filter(i => i.severity === 'INFO'));
                }
            }
            const result = {
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
            return (0, ar_invoice_1.ok)(result);
        }
        catch (error) {
            return (0, ar_invoice_1.err)(error instanceof Error ? error.message : 'Tax validation failed');
        }
    }
    /**
     * Get effective tax rate for tax code and country
     */
    async getEffectiveTaxRate(taxCode, countryCode, countryProfile) {
        // Get rate from country profile
        const rate = countryProfile.taxRates[taxCode];
        if (rate !== undefined) {
            return rate;
        }
        // Fallback to default rates
        const defaultRates = {
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
    generateDATEVContent(command, data, calculations) {
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
    generateELSTERXml(command, taxReturn) {
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
    async applyValidationRule(rule, calculations, command) {
        const issues = [];
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
                    const invalidCodes = calculations.filter(calc => !this.isValidTaxCode(calc.taxCode, command.countryCode));
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
            return (0, ar_invoice_1.ok)(issues);
        }
        catch (error) {
            return (0, ar_invoice_1.err)(error instanceof Error ? error.message : 'Rule evaluation failed');
        }
    }
    /**
     * Validate tax code for country
     */
    isValidTaxCode(taxCode, countryCode) {
        const validCodes = {
            'DE': ['DE-19', 'DE-7', 'DE-0'],
            'AT': ['AT-20', 'AT-10', 'AT-0'],
            'CH': ['CH-8.1', 'CH-3.8', 'CH-2.6', 'CH-0']
        };
        return validCodes[countryCode]?.includes(taxCode) || false;
    }
    /**
     * Get account name from number
     */
    getAccountName(accountNumber) {
        const accountNames = {
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
    calculateHash(content) {
        // Simple hash for demo - in production use crypto.subtle
        return Buffer.from(content).toString('base64').substring(0, 32);
    }
}
exports.TaxComplianceApplicationService = TaxComplianceApplicationService;
class GermanTaxProfile {
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
exports.GermanTaxProfile = GermanTaxProfile;
