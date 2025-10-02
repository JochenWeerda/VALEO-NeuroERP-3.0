import { GuidedBuyingEngine } from '../catalog-service/guided-buying-engine';
import { ThreeWayMatchEngine } from '../receiving-service/three-way-match-engine';
import { PerformanceAnalyticsService } from './performance-analytics';
export interface AIRecommendation {
    id: string;
    type: 'supplier' | 'contract' | 'spend' | 'process' | 'risk' | 'innovation';
    priority: 'low' | 'medium' | 'high' | 'critical';
    confidence: number;
    title: string;
    description: string;
    impact: {
        costSavings?: number;
        riskReduction?: number;
        efficiencyGain?: number;
        complianceImprovement?: number;
    };
    implementation: {
        effort: 'low' | 'medium' | 'high';
        timeline: string;
        requiredActions: string[];
        responsibleRoles: string[];
    };
    data: Record<string, any>;
    createdAt: Date;
    expiresAt?: Date;
}
export interface SupplierRecommendation extends AIRecommendation {
    type: 'supplier';
    supplierId: string;
    supplierName: string;
    recommendationType: 'consolidate' | 'diversify' | 'replace' | 'expand' | 'reduce';
    rationale: string;
    alternatives?: Array<{
        supplierId: string;
        supplierName: string;
        score: number;
        advantages: string[];
    }>;
}
export interface ContractRecommendation extends AIRecommendation {
    type: 'contract';
    contractId: string;
    contractNumber: string;
    recommendationType: 'renew' | 'renegotiate' | 'terminate' | 'amend' | 'expand';
    rationale: string;
    proposedChanges?: Array<{
        section: string;
        currentValue: any;
        proposedValue: any;
        impact: string;
    }>;
}
export interface SpendRecommendation extends AIRecommendation {
    type: 'spend';
    category: string;
    recommendationType: 'optimize' | 'consolidate' | 'renegotiate' | 'substitute';
    currentSpend: number;
    potentialSavings: number;
    rationale: string;
    opportunities: Array<{
        opportunity: string;
        savings: number;
        feasibility: 'high' | 'medium' | 'low';
    }>;
}
export interface ProcessRecommendation extends AIRecommendation {
    type: 'process';
    processArea: 'requisition' | 'approval' | 'ordering' | 'receiving' | 'invoicing' | 'payment';
    recommendationType: 'automate' | 'streamline' | 'digitize' | 'integrate';
    currentEfficiency: number;
    potentialImprovement: number;
    rationale: string;
    automationOpportunities: Array<{
        process: string;
        currentTime: number;
        automatedTime: number;
        savings: number;
    }>;
}
export interface RiskRecommendation extends AIRecommendation {
    type: 'risk';
    riskType: 'supplier' | 'contract' | 'compliance' | 'financial' | 'operational';
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    recommendationType: 'mitigate' | 'transfer' | 'accept' | 'monitor';
    rationale: string;
    mitigationStrategies: Array<{
        strategy: string;
        effectiveness: number;
        cost: number;
        timeline: string;
    }>;
}
export interface InnovationRecommendation extends AIRecommendation {
    type: 'innovation';
    category: 'technology' | 'process' | 'supplier' | 'market';
    recommendationType: 'adopt' | 'pilot' | 'explore' | 'monitor';
    rationale: string;
    innovationPotential: {
        marketDisruption: number;
        competitiveAdvantage: number;
        costReduction: number;
        efficiencyGain: number;
    };
    pilotOpportunities: Array<{
        pilot: string;
        scope: string;
        investment: number;
        expectedROI: number;
        timeline: string;
    }>;
}
export declare class AIRecommendationsEngine {
    private readonly guidedBuyingEngine;
    private readonly matchEngine;
    private readonly performanceAnalytics;
    constructor(guidedBuyingEngine: GuidedBuyingEngine, matchEngine: ThreeWayMatchEngine, performanceAnalytics: PerformanceAnalyticsService);
    /**
     * Generate comprehensive AI-powered recommendations
     */
    generateRecommendations(context: {
        department?: string;
        category?: string;
        evaluationPeriod: {
            from: Date;
            to: Date;
        };
        riskTolerance?: 'low' | 'medium' | 'high';
        budget?: number;
    }): Promise<AIRecommendation[]>;
    /**
     * Generate supplier-related recommendations
     */
    private generateSupplierRecommendations;
    /**
     * Generate contract-related recommendations
     */
    private generateContractRecommendations;
    /**
     * Generate spend optimization recommendations
     */
    private generateSpendRecommendations;
    /**
     * Generate process improvement recommendations
     */
    private generateProcessRecommendations;
    /**
     * Generate risk mitigation recommendations
     */
    private generateRiskRecommendations;
    /**
     * Generate innovation recommendations
     */
    private generateInnovationRecommendations;
    /**
     * Get recommendation implementation roadmap
     */
    generateImplementationRoadmap(recommendations: AIRecommendation[], constraints: {
        budget?: number;
        timeline?: number;
        resources?: string[];
    }): Promise<{
        phases: Array<{
            phase: string;
            duration: number;
            recommendations: AIRecommendation[];
            totalInvestment: number;
            expectedROI: number;
            dependencies: string[];
        }>;
        totalInvestment: number;
        totalROI: number;
        paybackPeriod: number;
    }>;
    private generateRecommendationId;
}
export default AIRecommendationsEngine;
//# sourceMappingURL=ai-recommendations-engine.d.ts.map