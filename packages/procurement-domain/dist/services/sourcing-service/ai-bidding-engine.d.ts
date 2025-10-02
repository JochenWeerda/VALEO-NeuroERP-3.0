import { Rfq, AwardRecommendation } from '../../core/entities/rfq';
export interface BidAnalysisResult {
    bidId: string;
    supplierId: string;
    overallScore: number;
    categoryScores: {
        price: number;
        quality: number;
        delivery: number;
        experience: number;
        sustainability: number;
        innovation: number;
    };
    pricePosition: 'lowest' | 'competitive' | 'high' | 'outlier';
    riskFactors: string[];
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
    confidence: number;
}
export interface AwardRecommendationResult {
    recommendations: AwardRecommendation[];
    analysis: {
        totalValue: number;
        savingsPotential: number;
        riskDistribution: Record<string, number>;
        supplierConcentration: Record<string, number>;
    };
    confidence: number;
    reasoning: string[];
}
export interface MarketIntelligence {
    category: string;
    averagePrice: number;
    priceRange: {
        min: number;
        max: number;
        median: number;
    };
    marketTrends: string[];
    competitorAnalysis: Array<{
        supplier: string;
        marketShare: number;
        pricingStrategy: string;
    }>;
    recommendations: string[];
}
export declare class AIBiddingEngine {
    /**
     * Analyze all bids for an RFQ using AI-powered algorithms
     */
    analyzeBids(rfq: Rfq, supplierData: Map<string, any>): Promise<BidAnalysisResult[]>;
    /**
     * Generate award recommendations using AI optimization
     */
    generateAwardRecommendations(rfq: Rfq, bidAnalyses: BidAnalysisResult[], constraints?: {
        maxAwardPerSupplier?: number;
        minSuppliers?: number;
        maxSuppliers?: number;
        riskTolerance?: 'low' | 'medium' | 'high';
    }): Promise<AwardRecommendationResult>;
    /**
     * Get market intelligence for category
     */
    getMarketIntelligence(category: string, region?: string): Promise<MarketIntelligence>;
    /**
     * Predict bid outcomes using machine learning
     */
    predictBidOutcomes(rfq: Rfq, historicalData?: any[]): Promise<{
        predictedWinningBid: number;
        confidenceInterval: {
            min: number;
            max: number;
        };
        factors: Array<{
            factor: string;
            impact: number;
            explanation: string;
        }>;
    }>;
    private analyzeSingleBid;
    private analyzePrice;
    private determinePricePosition;
    private analyzeQuality;
    private analyzeDelivery;
    private analyzeExperience;
    private analyzeSustainability;
    private analyzeInnovation;
    private checkSpecificationCompliance;
    private identifyRiskFactors;
    private identifyStrengthsAndWeaknesses;
    private generateBidRecommendations;
    private calculateAnalysisConfidence;
    private optimizeAwardAllocation;
    private calculateAwardAnalysis;
    private calculateRecommendationConfidence;
    private generateRecommendationReasoning;
    private calculateVariance;
    private getBasePriceForCategory;
}
export default AIBiddingEngine;
//# sourceMappingURL=ai-bidding-engine.d.ts.map