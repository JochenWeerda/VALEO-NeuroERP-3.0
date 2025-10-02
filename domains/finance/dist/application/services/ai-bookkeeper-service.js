"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - AI Bookkeeper Service
 *
 * AI-powered accounting service for automated booking proposals
 * Sprint 2 Implementation: Machine learning for account classification
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AIBookkeeperApplicationService = exports.RuleEngine = void 0;
exports.createAIBookkeeperService = createAIBookkeeperService;
exports.createDefaultBookingRules = createDefaultBookingRules;
const finance_constants_1 = require("../../core/constants/finance-constants");
// ===== RULE ENGINE =====
class RuleEngine {
    constructor() {
        this.rules = [];
    }
    addRule(rule) {
        this.rules.push(rule);
        this.rules.sort((a, b) => b.priority - a.priority);
    }
    evaluate(invoice, line) {
        const actions = [];
        for (const rule of this.rules) {
            if (!rule.isActive)
                continue;
            let ruleMatches = true;
            for (const condition of rule.conditions) {
                if (!this.evaluateCondition(condition, invoice, line)) {
                    ruleMatches = false;
                    break;
                }
            }
            if (ruleMatches) {
                actions.push(...rule.actions);
            }
        }
        return actions;
    }
    evaluateCondition(condition, invoice, line) {
        let fieldValue;
        // Extract field value based on condition field
        switch (condition.field) {
            case 'supplier_id':
                fieldValue = invoice.supplierId;
                break;
            case 'description':
                fieldValue = line.description;
                break;
            case 'amount':
                fieldValue = line.lineTotal;
                break;
            case 'tax_rate':
                fieldValue = line.taxRate;
                break;
            default:
                fieldValue = '';
        }
        switch (condition.operator) {
            case 'EQUALS':
                return fieldValue === condition.value;
            case 'CONTAINS':
                return String(fieldValue).toLowerCase().includes(String(condition.value).toLowerCase());
            case 'GREATER_THAN':
                return Number(fieldValue) > Number(condition.value);
            case 'LESS_THAN':
                return Number(fieldValue) < Number(condition.value);
            case 'REGEX':
                return new RegExp(String(condition.value)).test(String(fieldValue));
            default:
                return false;
        }
    }
}
exports.RuleEngine = RuleEngine;
// ===== AI SERVICE IMPLEMENTATION =====
class AIBookkeeperApplicationService {
    constructor(dependencies) {
        this.dependencies = dependencies;
        this.initializeDefaultRules();
    }
    /**
     * Propose booking for invoice using AI
     */
    async proposeBooking(invoice) {
        const proposalId = crypto.randomUUID();
        const suggestedEntries = [];
        for (const line of invoice.lines) {
            const entry = await this.proposeBookingForLine(invoice, line);
            suggestedEntries.push(entry);
        }
        // Calculate overall confidence
        const confidence = this.calculateOverallConfidence(suggestedEntries);
        // Generate explanation
        const explanation = await this.generateExplanation(invoice, suggestedEntries);
        return {
            proposalId,
            createdAt: new Date(),
            confidence,
            suggestedEntries,
            explanation,
            rules: this.getAppliedRules(invoice, suggestedEntries),
            features: this.extractFeatures(invoice, suggestedEntries)
        };
    }
    /**
     * Validate AI booking proposal
     */
    async validateProposal(proposal) {
        // Validate each entry
        for (const entry of proposal.suggestedEntries) {
            const account = await this.dependencies.accountRepository.findById(entry.accountId);
            if (!account) {
                return false;
            }
            if (!account.isActive) {
                return false;
            }
        }
        // Validate totals balance
        const totalDebit = proposal.suggestedEntries.reduce((sum, entry) => sum + entry.debit, 0);
        const totalCredit = proposal.suggestedEntries.reduce((sum, entry) => sum + entry.credit, 0);
        return Math.abs(totalDebit - totalCredit) < finance_constants_1.TAX_RATES.TOLERANCE;
    }
    /**
     * Explain AI booking proposal
     */
    async explainProposal(proposal) {
        const explanations = proposal.suggestedEntries.map(entry => `${entry.description}: ${entry.reasoning} (Confidence: ${Math.round(entry.confidence * finance_constants_1.PERCENTAGES.HUNDRED)}%)`);
        return `AI Booking Proposal Explanation:\n${explanations.join('\n')}\n\nOverall Confidence: ${Math.round(proposal.confidence * finance_constants_1.PERCENTAGES.HUNDRED)}%`;
    }
    /**
     * Propose booking for individual line item
     */
    async proposeBookingForLine(invoice, line) {
        // Extract features for ML model
        const features = this.extractLineFeatures(invoice, line);
        // Get rule-based suggestions
        const ruleActions = this.dependencies.ruleEngine.evaluate(invoice, line);
        // Get AI prediction
        const aiPrediction = await this.dependencies.mlModel.predict(features);
        // Combine rule and AI suggestions
        const suggestedAccount = this.selectBestAccount(ruleActions, aiPrediction);
        // Create journal entry proposal
        return {
            accountId: suggestedAccount.accountId,
            accountNumber: suggestedAccount.accountNumber,
            accountName: suggestedAccount.accountName,
            debit: this.determineDebitAmount(invoice, line, suggestedAccount),
            credit: this.determineCreditAmount(invoice, line, suggestedAccount),
            description: this.generateEntryDescription(invoice, line),
            taxCode: this.determineTaxCode(invoice, line, suggestedAccount),
            costCenter: this.determineCostCenter(invoice, line),
            confidence: aiPrediction.confidence,
            reasoning: `${aiPrediction.explanation} | Rule-based: ${ruleActions.length > 0 ? 'Applied' : 'None'}`
        };
    }
    /**
     * Initialize default booking rules
     */
    initializeDefaultRules() {
        // Office supplies rule
        this.dependencies.ruleEngine.addRule({
            id: 'office-supplies',
            name: 'Office Supplies to Expense Account',
            conditions: [
                { field: 'description', operator: 'CONTAINS', value: 'office' },
                { field: 'description', operator: 'CONTAINS', value: 'supplies' }
            ],
            actions: [
                { type: 'SET_ACCOUNT', value: '6000' }, // Office expense account
                { type: 'SET_TAX_CODE', value: 'DE-19' }
            ],
            priority: 10,
            isActive: true
        });
        // Travel expenses rule
        this.dependencies.ruleEngine.addRule({
            id: 'travel-expenses',
            name: 'Travel Expenses',
            conditions: [
                { field: 'description', operator: 'CONTAINS', value: 'hotel' },
                { field: 'description', operator: 'CONTAINS', value: 'travel' }
            ],
            actions: [
                { type: 'SET_ACCOUNT', value: '6200' }, // Travel expense account
                { type: 'SET_TAX_CODE', value: 'DE-19' }
            ],
            priority: 10,
            isActive: true
        });
        // Software licenses rule
        this.dependencies.ruleEngine.addRule({
            id: 'software-licenses',
            name: 'Software Licenses',
            conditions: [
                { field: 'description', operator: 'CONTAINS', value: 'software' },
                { field: 'description', operator: 'CONTAINS', value: 'license' }
            ],
            actions: [
                { type: 'SET_ACCOUNT', value: '6100' }, // Software expense account
                { type: 'SET_TAX_CODE', value: 'DE-19' }
            ],
            priority: 10,
            isActive: true
        });
    }
    /**
     * Extract features for ML model
     */
    extractFeatures(invoice, entries) {
        const features = {};
        // Invoice-level features
        features.invoice_amount = invoice.totalAmount;
        features.invoice_tax_rate = invoice.taxRate;
        features.supplier_id_encoded = this.encodeString(invoice.supplierId);
        features.currency_encoded = this.encodeString(invoice.currency);
        // Line-level features (aggregated)
        const totalLineAmount = entries.reduce((sum, entry) => sum + Math.max(entry.debit, entry.credit), 0);
        features.avg_line_amount = totalLineAmount / entries.length;
        features.line_count = entries.length;
        return features;
    }
    /**
     * Extract features for individual line
     */
    extractLineFeatures(invoice, line) {
        return {
            line_amount: line.lineTotal,
            line_tax_rate: line.taxRate,
            quantity: line.quantity,
            unit_price: line.unitPrice,
            description_length: line.description.length,
            supplier_encoded: this.encodeString(invoice.supplierId),
            has_sku: line.sku ? 1 : 0,
            tax_rate_category: this.categorizeTaxRate(line.taxRate)
        };
    }
    /**
     * Select best account from rules and AI
     */
    selectBestAccount(ruleActions, aiPrediction) {
        // If rules provide account, use it
        const ruleAccount = ruleActions.find(action => action.type === 'SET_ACCOUNT');
        if (ruleAccount) {
            return {
                accountId: ruleAccount.value,
                accountNumber: ruleAccount.value,
                accountName: `Account ${ruleAccount.value}`
            };
        }
        // Otherwise use AI prediction
        if (aiPrediction && aiPrediction.prediction) {
            return {
                accountId: aiPrediction.prediction,
                accountNumber: aiPrediction.prediction,
                accountName: `AI Suggested Account ${aiPrediction.prediction}`
            };
        }
        // Fallback
        return {
            accountId: '6000',
            accountNumber: '6000',
            accountName: 'Default Expense Account'
        };
    }
    /**
     * Determine debit amount for entry
     */
    determineDebitAmount(invoice, line, account) {
        // For AP invoices, debit expense accounts, credit liability accounts
        if (account && account.accountNumber && account.accountNumber.startsWith('6')) { // Expense account
            return line.lineTotal;
        }
        return 0;
    }
    /**
     * Determine credit amount for entry
     */
    determineCreditAmount(invoice, line, account) {
        // For AP invoices, credit accounts payable
        if (account.accountNumber === '1600') { // Accounts payable
            return line.lineTotal;
        }
        return 0;
    }
    /**
     * Generate entry description
     */
    generateEntryDescription(invoice, line) {
        return `${invoice.supplierId} - ${line.description} (${invoice.invoiceNumber})`;
    }
    /**
     * Determine tax code for entry
     */
    determineTaxCode(invoice, line, account) {
        const ruleActions = this.dependencies.ruleEngine.evaluate(invoice, line);
        const taxAction = ruleActions.find(action => action.type === 'SET_TAX_CODE');
        if (taxAction) {
            return taxAction.value;
        }
        // Default based on invoice tax rate
        return invoice.taxRate === finance_constants_1.TAX_RATES.STANDARD ? 'DE-19' : 'DE-7';
    }
    /**
     * Determine cost center for entry
     */
    determineCostCenter(invoice, line) {
        // Extract cost center from description or metadata
        const costCenterMatch = line.description.match(/CC[0-9]+|CostCenter[0-9]+/i);
        return costCenterMatch ? costCenterMatch[0] : 'CC-01'; // Default cost center
    }
    /**
     * Calculate overall confidence
     */
    calculateOverallConfidence(entries) {
        if (entries.length === 0)
            return 0;
        const totalConfidence = entries.reduce((sum, entry) => sum + entry.confidence, 0);
        return totalConfidence / entries.length;
    }
    /**
     * Generate explanation for proposal
     */
    async generateExplanation(invoice, entries) {
        const explanations = entries.map(entry => `${entry.accountNumber} (${entry.accountName}): ${entry.reasoning}`);
        return `AI Booking Proposal for Invoice ${invoice.invoiceNumber}:\n${explanations.join('\n')}`;
    }
    /**
     * Get applied rules for proposal
     */
    getAppliedRules(invoice, entries) {
        const appliedRules = new Set();
        for (const entry of entries) {
            if (entry.reasoning.includes('Rule-based')) {
                appliedRules.add('BUSINESS_RULES');
            }
            if (entry.reasoning.includes('AI')) {
                appliedRules.add('MACHINE_LEARNING');
            }
        }
        return Array.from(appliedRules);
    }
    /**
     * Encode string to numeric value for ML
     */
    encodeString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i += finance_constants_1.COLLECTION.FIVE) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash) / finance_constants_1.TIME.HASH_NORMALIZATION_FACTOR; // Normalize
    }
    /**
     * Categorize tax rate for ML features
     */
    categorizeTaxRate(taxRate) {
        if (taxRate === finance_constants_1.TAX_RATES.ZERO)
            return 0;
        if (taxRate === finance_constants_1.TAX_RATES.REDUCED)
            return 1;
        if (taxRate === finance_constants_1.TAX_RATES.STANDARD)
            return finance_constants_1.COLLECTION.TWO;
        return finance_constants_1.COLLECTION.THREE; // Other
    }
}
exports.AIBookkeeperApplicationService = AIBookkeeperApplicationService;
// ===== FACTORY FUNCTION =====
function createAIBookkeeperService(dependencies) {
    return new AIBookkeeperApplicationService(dependencies);
}
// ===== DEFAULT RULES SETUP =====
function createDefaultBookingRules() {
    return [
        {
            id: 'office-supplies',
            name: 'Office Supplies to Administrative Expenses',
            conditions: [
                { field: 'description', operator: 'CONTAINS', value: 'office' },
                { field: 'description', operator: 'CONTAINS', value: 'supplies' }
            ],
            actions: [
                { type: 'SET_ACCOUNT', value: '6400' }, // Administrative expenses
                { type: 'SET_TAX_CODE', value: 'DE-19' }
            ],
            priority: 10,
            isActive: true
        },
        {
            id: 'software-licenses',
            name: 'Software Licenses to IT Expenses',
            conditions: [
                { field: 'description', operator: 'CONTAINS', value: 'software' },
                { field: 'description', operator: 'CONTAINS', value: 'license' }
            ],
            actions: [
                { type: 'SET_ACCOUNT', value: '6100' }, // IT expenses
                { type: 'SET_TAX_CODE', value: 'DE-19' }
            ],
            priority: 10,
            isActive: true
        },
        {
            id: 'travel-expenses',
            name: 'Travel Expenses',
            conditions: [
                { field: 'description', operator: 'CONTAINS', value: 'hotel' },
                { field: 'description', operator: 'CONTAINS', value: 'travel' }
            ],
            actions: [
                { type: 'SET_ACCOUNT', value: '6200' }, // Travel expenses
                { type: 'SET_TAX_CODE', value: 'DE-19' }
            ],
            priority: 10,
            isActive: true
        },
        {
            id: 'marketing-expenses',
            name: 'Marketing and Advertising',
            conditions: [
                { field: 'description', operator: 'CONTAINS', value: 'marketing' },
                { field: 'description', operator: 'CONTAINS', value: 'advertising' }
            ],
            actions: [
                { type: 'SET_ACCOUNT', value: '6300' }, // Marketing expenses
                { type: 'SET_TAX_CODE', value: 'DE-19' }
            ],
            priority: 10,
            isActive: true
        }
    ];
}
//# sourceMappingURL=ai-bookkeeper-service.js.map