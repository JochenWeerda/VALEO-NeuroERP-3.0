/**
 * VALEO NeuroERP 3.0 - Finance Domain - AI Bookkeeper Service
 *
 * AI-powered accounting service for automated booking proposals
 * Sprint 2 Implementation: Machine learning for account classification
 */
import { AIBookingProposal, AIBookingService, APInvoice } from '../../core/entities/ap-invoice';
import { AccountRepository } from '../../core/entities/ledger';
export interface MachineLearningModel {
    predict(features: Record<string, number>): Promise<{
        prediction: string;
        confidence: number;
        explanation: string;
    }>;
    train(features: Record<string, number>[], labels: string[]): Promise<void>;
    saveModel(path: string): Promise<void>;
    loadModel(path: string): Promise<void>;
}
export interface BookingRule {
    id: string;
    name: string;
    conditions: BookingCondition[];
    actions: BookingAction[];
    priority: number;
    isActive: boolean;
}
export interface BookingCondition {
    field: string;
    operator: 'EQUALS' | 'CONTAINS' | 'GREATER_THAN' | 'LESS_THAN' | 'REGEX';
    value: string | number;
}
export interface BookingAction {
    type: 'SET_ACCOUNT' | 'SET_TAX_CODE' | 'SET_COST_CENTER';
    value: string;
}
export interface AIBookkeeperServiceDependencies {
    mlModel: MachineLearningModel;
    ruleEngine: RuleEngine;
    accountRepository: AccountRepository;
}
export declare class RuleEngine {
    private readonly rules;
    addRule(rule: BookingRule): void;
    evaluate(invoice: APInvoice, line: any): BookingAction[];
    private evaluateCondition;
}
export declare class AIBookkeeperApplicationService implements AIBookingService {
    private readonly dependencies;
    constructor(dependencies: AIBookkeeperServiceDependencies);
    /**
     * Propose booking for invoice using AI
     */
    proposeBooking(invoice: APInvoice): Promise<AIBookingProposal>;
    /**
     * Validate AI booking proposal
     */
    validateProposal(proposal: AIBookingProposal): Promise<boolean>;
    /**
     * Explain AI booking proposal
     */
    explainProposal(proposal: AIBookingProposal): Promise<string>;
    /**
     * Propose booking for individual line item
     */
    private proposeBookingForLine;
    /**
     * Initialize default booking rules
     */
    private initializeDefaultRules;
    /**
     * Extract features for ML model
     */
    private extractFeatures;
    /**
     * Extract features for individual line
     */
    private extractLineFeatures;
    /**
     * Select best account from rules and AI
     */
    private selectBestAccount;
    /**
     * Determine debit amount for entry
     */
    private determineDebitAmount;
    /**
     * Determine credit amount for entry
     */
    private determineCreditAmount;
    /**
     * Generate entry description
     */
    private generateEntryDescription;
    /**
     * Determine tax code for entry
     */
    private determineTaxCode;
    /**
     * Determine cost center for entry
     */
    private determineCostCenter;
    /**
     * Calculate overall confidence
     */
    private calculateOverallConfidence;
    /**
     * Generate explanation for proposal
     */
    private generateExplanation;
    /**
     * Get applied rules for proposal
     */
    private getAppliedRules;
    /**
     * Encode string to numeric value for ML
     */
    private encodeString;
    /**
     * Categorize tax rate for ML features
     */
    private categorizeTaxRate;
}
export declare function createAIBookkeeperService(dependencies: AIBookkeeperServiceDependencies): AIBookingService;
export declare function createDefaultBookingRules(): BookingRule[];
//# sourceMappingURL=ai-bookkeeper-service.d.ts.map