/**
 * VALEO NeuroERP 3.0 - Putaway & Slotting Service
 *
 * Intelligent putaway planning and slotting optimization for WMS operations
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
export interface PutawayTask {
    taskId: string;
    asnId: string;
    sku: string;
    gtin?: string;
    quantity: number;
    uom: string;
    fromLocation: string;
    toLocation: string;
    priority: number;
    strategy: PutawayStrategy;
    estimatedTime: number;
    status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
    assignedTo?: string;
    createdAt: Date;
    completedAt?: Date;
}
export interface SlottingRecommendation {
    sku: string;
    currentLocation?: string;
    recommendedLocation: string;
    confidence: number;
    reasoning: string[];
    expectedImprovement: {
        travelTime: number;
        throughput: number;
        spaceUtilization: number;
    };
    aiFeatures: Record<string, any>;
}
export type PutawayStrategy = 'velocity' | 'abc' | 'temp_zone' | 'hazmat' | 'size' | 'family' | 'manual';
export interface SlottingPolicy {
    policyId: string;
    name: string;
    description: string;
    strategy: PutawayStrategy;
    rules: SlottingRule[];
    zones: string[];
    active: boolean;
    createdAt: Date;
    updatedAt: Date;
}
export interface SlottingRule {
    ruleId: string;
    condition: {
        skuCriteria?: {
            abcClass?: 'A' | 'B' | 'C';
            velocityClass?: 'X' | 'Y' | 'Z';
            category?: string;
            tempZone?: string;
            hazmat?: boolean;
        };
        locationCriteria?: {
            zone?: string;
            type?: string;
            capacity?: {
                minUtilization?: number;
                maxUtilization?: number;
            };
        };
    };
    action: {
        priority: number;
        preferredZones: string[];
        avoidZones?: string[];
        maxDistance?: number;
    };
    weight: number;
}
export declare class PutawaySlottingService {
    private readonly eventBus;
    private readonly metrics;
    private slottingPolicies;
    constructor(eventBus: EventBus);
    /**
     * Plan putaway tasks for received goods
     */
    planPutaway(asnId: string, strategy?: PutawayStrategy): Promise<PutawayTask[]>;
    /**
     * Generate slotting recommendations using AI
     */
    generateSlottingRecommendations(skus?: string[]): Promise<SlottingRecommendation[]>;
    /**
     * Apply slotting recommendation
     */
    applySlottingRecommendation(recommendation: SlottingRecommendation): Promise<void>;
    /**
     * Get slotting analytics
     */
    getSlottingAnalytics(): Promise<{
        totalLocations: number;
        utilizedLocations: number;
        averageUtilization: number;
        slottingEfficiency: number;
        travelTimeReduction: number;
        topRecommendations: SlottingRecommendation[];
    }>;
    /**
     * Create or update slotting policy
     */
    createSlottingPolicy(policy: Omit<SlottingPolicy, 'policyId' | 'createdAt' | 'updatedAt'>): Promise<SlottingPolicy>;
    /**
     * Find optimal location for SKU
     */
    private findOptimalLocation;
    /**
     * Generate AI-powered recommendation for single SKU
     */
    private generateRecommendationForSku;
    /**
     * Velocity-based optimal location finding
     */
    private findVelocityOptimalLocation;
    /**
     * ABC-based optimal location finding
     */
    private findAbcOptimalLocation;
    /**
     * Temperature zone-based optimal location finding
     */
    private findTempZoneOptimalLocation;
    /**
     * Hazardous materials optimal location finding
     */
    private findHazmatOptimalLocation;
    /**
     * Calculate ABC score for location
     */
    private calculateAbcScore;
    /**
     * Calculate velocity score for location
     */
    private calculateVelocityScore;
    /**
     * Calculate priority for putaway task
     */
    private calculatePriority;
    /**
     * Estimate putaway time
     */
    private estimatePutawayTime;
    private getAsnDetails;
    private getSkuDetails;
    private getAvailableLocations;
    private getAllSkus;
    private getCurrentSkuLocation;
    private updateSkuLocation;
    private calculateDistanceReduction;
    private calculateThroughputIncrease;
    private createLocationFromCode;
    private initializeDefaultPolicies;
    /**
     * Publish putaway planned event
     */
    private publishPutawayPlannedEvent;
    /**
     * Publish slotting updated event
     */
    private publishSlottingUpdatedEvent;
}
//# sourceMappingURL=putaway-slotting-service.d.ts.map