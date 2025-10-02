import { drizzle } from 'drizzle-orm/node-postgres';
export interface AggregationConfig {
    batchSize?: number;
    maxExecutionTimeMs?: number;
}
export declare class AggregationService {
    private db;
    private config;
    constructor(db: ReturnType<typeof drizzle>, config?: AggregationConfig);
    refreshContractPositions(tenantId: string): Promise<{
        success: boolean;
        recordCount: number;
        executionTimeMs: number;
        error?: string;
    }>;
    refreshQualityStats(tenantId: string): Promise<{
        success: boolean;
        recordCount: number;
        executionTimeMs: number;
        error?: string;
    }>;
    refreshRegulatoryStats(tenantId: string): Promise<{
        success: boolean;
        recordCount: number;
        executionTimeMs: number;
        error?: string;
    }>;
    refreshFinanceKpis(tenantId: string): Promise<{
        success: boolean;
        recordCount: number;
        executionTimeMs: number;
        error?: string;
    }>;
    refreshWeighingVolumes(tenantId: string): Promise<{
        success: boolean;
        recordCount: number;
        executionTimeMs: number;
        error?: string;
    }>;
    refreshAllViews(tenantId: string): Promise<{
        contractPositions: {
            success: boolean;
            recordCount: number;
            executionTimeMs: number;
            error?: string;
        };
        qualityStats: {
            success: boolean;
            recordCount: number;
            executionTimeMs: number;
            error?: string;
        };
        regulatoryStats: {
            success: boolean;
            recordCount: number;
            executionTimeMs: number;
            error?: string;
        };
        financeKpis: {
            success: boolean;
            recordCount: number;
            executionTimeMs: number;
            error?: string;
        };
        weighingVolumes: {
            success: boolean;
            recordCount: number;
            executionTimeMs: number;
            error?: string;
        };
        totalExecutionTimeMs: number;
    }>;
    getAggregationStatus(tenantId: string): Promise<{
        lastRefresh: {
            contractPositions?: Date;
            qualityStats?: Date;
            regulatoryStats?: Date;
            financeKpis?: Date;
            weighingVolumes?: Date;
        };
        recordCounts: {
            contractPositions: number;
            qualityStats: number;
            regulatoryStats: number;
            financeKpis: number;
            weighingVolumes: number;
        };
    }>;
}
//# sourceMappingURL=aggregation-service.d.ts.map