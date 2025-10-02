export interface SupplierPerformanceScore {
    supplierId: string;
    supplierName: string;
    overallScore: number;
    qualityScore: number;
    deliveryScore: number;
    costScore: number;
    complianceScore: number;
    innovationScore: number;
    onTimeDeliveryRate: number;
    qualityIncidentRate: number;
    costVariance: number;
    contractCompliance: number;
    responseTime: number;
    scoreTrend: 'improving' | 'stable' | 'declining';
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    evaluationPeriod: {
        from: Date;
        to: Date;
    };
}
export interface ProcurementKPIs {
    totalSpend: number;
    spendByCategory: Array<{
        category: string;
        amount: number;
        percentage: number;
    }>;
    spendBySupplier: Array<{
        supplierId: string;
        supplierName: string;
        amount: number;
        percentage: number;
    }>;
    maverickSpend: {
        amount: number;
        percentage: number;
    };
    costSavings: number;
    savingsPercentage: number;
    contractCompliance: number;
    poCompliance: number;
    supplierPerformance: {
        averageScore: number;
        topPerformers: SupplierPerformanceScore[];
        underPerformers: SupplierPerformanceScore[];
    };
    requisitionToPOCycleTime: number;
    poToPaymentCycleTime: number;
    invoiceProcessingTime: number;
    approvalCycleTime: number;
    onTimeDeliveryRate: number;
    qualityIncidentRate: number;
    returnRate: number;
    evaluationPeriod: {
        from: Date;
        to: Date;
    };
}
export interface SpendAnalysis {
    abcClassification: Array<{
        category: string;
        spend: number;
        percentage: number;
        cumulativePercentage: number;
        abcClass: 'A' | 'B' | 'C';
        recommendations: string[];
    }>;
    contractCoverage: {
        totalSpend: number;
        contractedSpend: number;
        coveragePercentage: number;
        offContractSpend: number;
    };
    categoryAnalysis: Array<{
        category: string;
        totalSpend: number;
        supplierCount: number;
        avgOrderValue: number;
        transactionCount: number;
        priceVariance: number;
        recommendations: string[];
    }>;
    supplierConcentration: {
        herfindahlIndex: number;
        topSupplierPercentage: number;
        riskLevel: 'low' | 'medium' | 'high' | 'critical';
        diversificationRecommendations: string[];
    };
}
export interface ContractAnalytics {
    totalContracts: number;
    activeContracts: number;
    expiringContracts: number;
    totalContractValue: number;
    avgContractValue: number;
    contractUtilization: Array<{
        contractId: string;
        contractNumber: string;
        supplierName: string;
        totalValue: number;
        spentToDate: number;
        utilizationRate: number;
        status: 'under_utilized' | 'on_track' | 'over_utilized';
    }>;
    slaCompliance: {
        overallCompliance: number;
        slaViolations: number;
        topViolatedSLAs: Array<{
            sla: string;
            violationCount: number;
            affectedContracts: number;
        }>;
    };
    renewalPipeline: Array<{
        contractId: string;
        contractNumber: string;
        supplierName: string;
        expiryDate: Date;
        daysToExpiry: number;
        renewalStatus: 'not_started' | 'in_progress' | 'completed';
        estimatedValue: number;
    }>;
}
export declare class PerformanceAnalyticsService {
    /**
     * Calculate comprehensive supplier performance scores
     */
    calculateSupplierPerformance(supplierId: string, evaluationPeriod: {
        from: Date;
        to: Date;
    }): Promise<SupplierPerformanceScore>;
    /**
     * Generate comprehensive procurement KPIs
     */
    generateProcurementKPIs(evaluationPeriod: {
        from: Date;
        to: Date;
    }, filters?: {
        department?: string;
        category?: string;
    }): Promise<ProcurementKPIs>;
    /**
     * Perform detailed spend analysis with ABC classification
     */
    performSpendAnalysis(evaluationPeriod: {
        from: Date;
        to: Date;
    }, filters?: {
        department?: string;
        category?: string;
    }): Promise<SpendAnalysis>;
    /**
     * Generate contract portfolio analytics
     */
    generateContractAnalytics(evaluationPeriod: {
        from: Date;
        to: Date;
    }, filters?: {
        department?: string;
        supplier?: string;
    }): Promise<ContractAnalytics>;
    /**
     * Generate supplier scorecard
     */
    generateSupplierScorecard(supplierId: string, evaluationPeriod: {
        from: Date;
        to: Date;
    }): Promise<{
        supplierInfo: {
            id: string;
            name: string;
            category: string;
            relationshipStartDate: Date;
            totalSpend: number;
            contractCount: number;
        };
        performanceScores: SupplierPerformanceScore;
        trendAnalysis: {
            scoreHistory: Array<{
                period: string;
                score: number;
            }>;
            improvementAreas: string[];
            strengths: string[];
        };
        riskAssessment: {
            overallRisk: 'low' | 'medium' | 'high' | 'critical';
            riskFactors: string[];
            mitigationStrategies: string[];
        };
        recommendations: string[];
    }>;
    /**
     * Generate procurement savings report
     */
    generateSavingsReport(evaluationPeriod: {
        from: Date;
        to: Date;
    }, filters?: {
        department?: string;
        category?: string;
    }): Promise<{
        totalSavings: number;
        savingsPercentage: number;
        savingsByCategory: Array<{
            category: string;
            savings: number;
            percentage: number;
        }>;
        savingsByInitiative: Array<{
            initiative: string;
            savings: number;
            description: string;
        }>;
        costAvoidance: Array<{
            item: string;
            avoidedCost: number;
            description: string;
        }>;
        roi: {
            investment: number;
            returns: number;
            ratio: number;
            paybackPeriod: number;
        };
    }>;
    /**
     * Generate predictive analytics for procurement
     */
    generatePredictiveInsights(forecastPeriod: {
        months: number;
    }, filters?: {
        department?: string;
        category?: string;
    }): Promise<{
        spendForecast: Array<{
            month: string;
            predictedSpend: number;
            confidence: number;
        }>;
        supplierRiskPredictions: Array<{
            supplierId: string;
            riskLevel: 'low' | 'medium' | 'high' | 'critical';
            predictedIssues: string[];
            recommendedActions: string[];
        }>;
        categoryTrends: Array<{
            category: string;
            growthRate: number;
            predictedSpend: number;
            influencingFactors: string[];
        }>;
        costOptimizationOpportunities: Array<{
            opportunity: string;
            potentialSavings: number;
            implementationEffort: 'low' | 'medium' | 'high';
            timeline: string;
        }>;
    }>;
}
export default PerformanceAnalyticsService;
//# sourceMappingURL=performance-analytics.d.ts.map