import { CatalogItem, Catalog } from '../../core/entities/catalog';
export interface BuyingContext {
    userId: string;
    department: string;
    costCenter: string;
    project?: string;
    urgency: 'low' | 'medium' | 'high' | 'critical';
    budget?: {
        available: number;
        currency: string;
        period: 'monthly' | 'quarterly' | 'yearly';
    };
    previousPurchases?: Array<{
        category: string;
        supplier: string;
        amount: number;
        date: Date;
    }>;
}
export interface GuidedBuyingRecommendation {
    item: CatalogItem;
    recommendation: {
        score: number;
        reason: string;
        alternatives: CatalogItem[];
        compliance: {
            approved: boolean;
            violations: string[];
            warnings: string[];
        };
        budget: {
            withinBudget: boolean;
            remainingBudget?: number;
            recommendation: 'approved' | 'requires_approval' | 'not_recommended';
        };
        policy: {
            compliant: boolean;
            rules: Array<{
                rule: string;
                status: 'pass' | 'fail' | 'warning';
                message: string;
            }>;
        };
    };
}
export interface SpendAnalysis {
    category: string;
    totalSpend: number;
    transactionCount: number;
    averageOrderValue: number;
    topSuppliers: Array<{
        supplierId: string;
        supplierName: string;
        spend: number;
        percentage: number;
    }>;
    spendTrend: Array<{
        period: string;
        amount: number;
        change: number;
    }>;
    maverickSpend: {
        amount: number;
        percentage: number;
        transactions: number;
    };
    recommendations: string[];
}
export declare class GuidedBuyingEngine {
    /**
     * Get guided buying recommendations for a search query
     */
    getRecommendations(searchQuery: string, context: BuyingContext, availableItems: CatalogItem[], catalogs: Catalog[]): Promise<GuidedBuyingRecommendation[]>;
    /**
     * Analyze spend patterns for a category or department
     */
    analyzeSpend(category?: string, department?: string, dateRange?: {
        from: Date;
        to: Date;
    }): Promise<SpendAnalysis>;
    /**
     * Check if a purchase complies with company policies
     */
    checkPolicyCompliance(item: CatalogItem, quantity: number, context: BuyingContext): Promise<{
        compliant: boolean;
        violations: string[];
        warnings: string[];
        requiredApprovals: string[];
    }>;
    /**
     * Get alternative items for comparison
     */
    getAlternatives(item: CatalogItem, catalogs: Catalog[]): Promise<CatalogItem[]>;
    private filterAccessibleItems;
    private scoreItem;
    private calculateRelevanceScore;
    private analyzeBudgetFit;
    private getUserGroups;
    private getCategoryRules;
    private evaluateRule;
    /**
     * Generate ABC analysis for spend categories
     */
    generateABCAnalysis(categories: Array<{
        name: string;
        spend: number;
    }>): Promise<Array<{
        category: string;
        spend: number;
        percentage: number;
        cumulativePercentage: number;
        abcClass: 'A' | 'B' | 'C';
        recommendations: string[];
    }>>;
}
export default GuidedBuyingEngine;
//# sourceMappingURL=guided-buying-engine.d.ts.map