import { drizzle } from 'drizzle-orm/node-postgres';
import { KPI } from '../entities/kpi';
export interface KpiCalculationContext {
    tenantId: string;
    startDate?: Date;
    endDate?: Date;
    commodity?: string;
    customerId?: string;
    siteId?: string;
}
export interface KpiCalculationResult {
    kpi: KPI;
    success: boolean;
    executionTimeMs: number;
    error?: string;
}
export declare class KpiCalculationEngine {
    private db;
    constructor(db: ReturnType<typeof drizzle>);
    calculateContractPositionKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]>;
    calculateQualityKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]>;
    calculateWeighingKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]>;
    calculateFinanceKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]>;
    calculateRegulatoryKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]>;
    private calculateHedgingRatio;
    private calculateShortPosition;
    private calculateLongPosition;
    private calculateNetExposure;
    private calculatePassRate;
    private calculateFailureRate;
    private calculateAverageMoisture;
    private calculateAverageProtein;
    private calculateTotalWeight;
    private calculateAverageWeight;
    private calculateToleranceCompliance;
    private calculateTotalRevenue;
    private calculateGrossMargin;
    private calculateOutstandingInvoices;
    private calculateOverdueInvoices;
    private calculateEligibilityRate;
    calculateAllKpis(context: KpiCalculationContext): Promise<{
        results: KpiCalculationResult[];
        summary: {
            total: number;
            successful: number;
            failed: number;
            totalExecutionTimeMs: number;
        };
    }>;
}
//# sourceMappingURL=kpi-calculation-engine.d.ts.map