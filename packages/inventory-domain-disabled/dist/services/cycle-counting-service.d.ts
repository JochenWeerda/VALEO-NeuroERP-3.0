/**
 * VALEO NeuroERP 3.0 - Cycle Counting Service
 *
 * ABC/XYZ policies, automated scheduling, and accuracy tracking
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
export interface CycleCountPolicy {
    policyId: string;
    policyName: string;
    classification: 'ABC' | 'XYZ';
    frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    coverage: number;
    priority: 'A' | 'B' | 'C' | 'X' | 'Y' | 'Z';
    method: 'full_count' | 'sample_count' | 'zero_count';
    tolerance: {
        quantity: number;
        value: number;
    };
    autoAdjust: boolean;
    requiresApproval: boolean;
    active: boolean;
}
export interface CycleCount {
    countId: string;
    countNumber: string;
    policyId: string;
    status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
    type: 'ABC' | 'XYZ' | 'manual' | 'emergency';
    priority: number;
    assignedTo?: string;
    location?: string;
    zone?: string;
    items: Array<{
        sku: string;
        location: string;
        lot?: string;
        serial?: string;
        expectedQty: number;
        expectedValue: number;
        countedQty?: number;
        countedValue?: number;
        varianceQty?: number;
        varianceValue?: number;
        variancePercent?: number;
        status: 'pending' | 'counted' | 'variance' | 'adjusted';
        notes?: string;
    }>;
    schedule: {
        plannedStart: Date;
        plannedEnd: Date;
        actualStart?: Date;
        actualEnd?: Date;
    };
    results: {
        totalItems: number;
        countedItems: number;
        variancesFound: number;
        accuracy: number;
        totalVarianceValue: number;
        adjustmentsMade: number;
    };
    createdAt: Date;
    completedAt?: Date;
}
export interface ABCClassification {
    sku: string;
    classification: 'A' | 'B' | 'C';
    annualUsage: number;
    annualValue: number;
    percentageOfTotal: number;
    cumulativePercentage: number;
    countFrequency: number;
    lastCount?: Date;
    nextCountDue?: Date;
}
export interface XYZClassification {
    sku: string;
    classification: 'X' | 'Y' | 'Z';
    demandVariability: number;
    forecastAccuracy: number;
    demandPattern: 'stable' | 'seasonal' | 'erratic';
    safetyStock: number;
    reorderPoint: number;
    countFrequency: number;
    lastCount?: Date;
    nextCountDue?: Date;
}
export interface CycleCountSchedule {
    scheduleId: string;
    policyId: string;
    scheduledDate: Date;
    dueDate: Date;
    items: Array<{
        sku: string;
        location: string;
        priority: number;
    }>;
    status: 'pending' | 'executing' | 'completed' | 'overdue';
    assignedTo?: string;
    createdAt: Date;
}
export interface CycleCountPerformance {
    period: string;
    metrics: {
        totalCounts: number;
        completedCounts: number;
        accuracy: number;
        averageVariance: number;
        totalVarianceValue: number;
        timePerCount: number;
        itemsPerHour: number;
    };
    byLocation: Array<{
        location: string;
        accuracy: number;
        varianceRate: number;
        countFrequency: number;
    }>;
    bySKU: Array<{
        sku: string;
        accuracy: number;
        varianceRate: number;
        countFrequency: number;
    }>;
    trends: {
        accuracy: number[];
        varianceRate: number[];
        productivity: number[];
    };
}
export declare class CycleCountingService {
    private readonly eventBus;
    private readonly metrics;
    private policies;
    private activeCounts;
    constructor(eventBus: EventBus);
    /**
     * Create ABC classification for items
     */
    createABCClassification(skus: string[]): Promise<ABCClassification[]>;
    /**
     * Create XYZ classification for items
     */
    createXYZClassification(skus: string[]): Promise<XYZClassification[]>;
    /**
     * Create cycle count policy
     */
    createCycleCountPolicy(policy: Omit<CycleCountPolicy, 'policyId'>): Promise<CycleCountPolicy>;
    /**
     * Generate cycle count schedule
     */
    generateCycleCountSchedule(policyId: string, startDate: Date, endDate: Date): Promise<CycleCountSchedule[]>;
    /**
     * Create cycle count from schedule
     */
    createCycleCount(scheduleId: string, assignedTo?: string): Promise<CycleCount>;
    /**
     * Record count result for an item
     */
    recordCountResult(countId: string, sku: string, location: string, countedQty: number, notes?: string): Promise<void>;
    /**
     * Complete cycle count
     */
    completeCycleCount(countId: string): Promise<CycleCount>;
    /**
     * Get cycle count performance metrics
     */
    getCycleCountPerformance(period?: 'day' | 'week' | 'month'): Promise<CycleCountPerformance>;
    /**
     * Get overdue counts
     */
    getOverdueCounts(): Promise<CycleCountSchedule[]>;
    private initializeDefaultPolicies;
    private getSKUUsageData;
    private getSKUDemandData;
    private calculateDemandVariability;
    private getForecastAccuracy;
    private analyzeDemandPattern;
    private calculateSafetyStock;
    private getReorderPoint;
    private calculateNextCountDue;
    private getNextCountDate;
    private selectItemsForCounting;
    private getItemsDueForCounting;
    private getPriorityValue;
    private getSchedule;
    private getCurrentInventory;
    private isVariance;
    private processAutoAdjustments;
    private createInventoryAdjustment;
    private getScheduleByCount;
    private getCompletedCounts;
    private calculatePerformanceMetrics;
    private getAllSchedules;
    private publishCycleCountCreatedEvent;
    private publishCycleCountCompletedEvent;
}
//# sourceMappingURL=cycle-counting-service.d.ts.map