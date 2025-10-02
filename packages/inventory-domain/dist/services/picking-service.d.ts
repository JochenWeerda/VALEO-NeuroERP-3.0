/**
 * VALEO NeuroERP 3.0 - Picking Service
 *
 * Advanced picking operations with wave/batch/zone picking strategies
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
export interface PickTask {
    taskId: string;
    orderId: string;
    waveId?: string;
    batchId?: string;
    sku: string;
    location: string;
    lot?: string;
    serial?: string;
    quantity: number;
    pickedQuantity: number;
    status: 'pending' | 'in_progress' | 'completed' | 'short' | 'damaged';
    assignedTo?: string;
    priority: number;
    zone: string;
    sequence: number;
    estimatedTime: number;
    actualTime?: number;
    createdAt: Date;
    startedAt?: Date;
    completedAt?: Date;
    qualityChecks?: Array<{
        checkType: 'quantity' | 'condition' | 'label';
        passed: boolean;
        notes?: string;
        checkedBy: string;
        checkedAt: Date;
    }>;
}
export interface PickingWave {
    waveId: string;
    waveNumber: string;
    status: 'planned' | 'released' | 'in_progress' | 'completed' | 'cancelled';
    strategy: 'single_order' | 'batch' | 'zone' | 'cluster';
    priority: number;
    zone: string;
    tasks: PickTask[];
    totalTasks: number;
    completedTasks: number;
    totalQuantity: number;
    pickedQuantity: number;
    assignedPickers: string[];
    estimatedDuration: number;
    actualDuration?: number;
    createdAt: Date;
    releasedAt?: Date;
    completedAt?: Date;
    productivity?: {
        picksPerHour: number;
        linesPerHour: number;
        accuracy: number;
        averageTimePerPick: number;
    };
}
export interface PickingBatch {
    batchId: string;
    batchNumber: string;
    orders: string[];
    skus: Array<{
        sku: string;
        totalQuantity: number;
        locations: Array<{
            location: string;
            quantity: number;
            lot?: string;
        }>;
    }>;
    status: 'planned' | 'active' | 'completed';
    priority: number;
    createdAt: Date;
    completedAt?: Date;
}
export interface ZoneConfiguration {
    zoneId: string;
    zoneName: string;
    type: 'forward' | 'reserve' | 'bulk' | 'hazardous' | 'ambient' | 'refrigerated' | 'frozen';
    pickers: string[];
    locations: string[];
    capacity: {
        maxConcurrentPickers: number;
        maxTasksPerHour: number;
    };
    routing: {
        entryPoint: string;
        exitPoint: string;
        optimalPath: string[];
    };
    active: boolean;
}
export interface PickerPerformance {
    pickerId: string;
    name: string;
    zone: string;
    shift: string;
    metrics: {
        totalPicks: number;
        totalLines: number;
        totalQuantity: number;
        picksPerHour: number;
        linesPerHour: number;
        accuracy: number;
        averageTimePerPick: number;
        totalTimeWorked: number;
    };
    performance: {
        score: number;
        grade: 'A' | 'B' | 'C' | 'D' | 'F';
        trends: {
            picksPerHour: number[];
            accuracy: number[];
            timePerPick: number[];
        };
    };
    currentSession: {
        startTime: Date;
        tasksCompleted: number;
        totalPicks: number;
        errors: number;
    };
}
export declare class PickingService {
    private readonly eventBus;
    private readonly metrics;
    private zones;
    private activeWaves;
    constructor(eventBus: EventBus);
    /**
     * Create picking wave from orders
     */
    createPickingWave(orders: string[], strategy?: PickingWave['strategy'], zone?: string): Promise<PickingWave>;
    /**
     * Release wave for picking
     */
    releaseWave(waveId: string): Promise<void>;
    /**
     * Start picking task
     */
    startPickTask(taskId: string, pickerId: string): Promise<void>;
    /**
     * Complete picking task
     */
    completePickTask(taskId: string, pickedQuantity: number, actualTime?: number, qualityChecks?: PickTask['qualityChecks']): Promise<void>;
    /**
     * Get picker performance metrics
     */
    getPickerPerformance(pickerId: string, period?: 'shift' | 'day' | 'week'): Promise<PickerPerformance>;
    /**
     * Get zone utilization and performance
     */
    getZonePerformance(zoneId: string): Promise<{
        zone: ZoneConfiguration;
        currentUtilization: number;
        activePickers: number;
        tasksInProgress: number;
        tasksCompleted: number;
        averageProductivity: number;
        bottlenecks: string[];
    }>;
    /**
     * Optimize picking routes within zone
     */
    optimizePickingRoute(tasks: PickTask[]): Promise<PickTask[]>;
    /**
     * Create batch picking plan
     */
    createBatchPickingPlan(orders: string[]): Promise<PickingBatch>;
    private createPickTasksFromOrders;
    private groupTasksByStrategy;
    private optimizeForBatchPicking;
    private optimizeForZonePicking;
    private optimizeForClusterPicking;
    private calculateWavePriority;
    private assignOptimalZone;
    private estimateWaveDuration;
    private assignPickersToWave;
    private estimatePickTime;
    private calculateDistance;
    private locationToNumber;
    private findPickTask;
    private updateWaveProgress;
    private calculateWaveProductivity;
    private updatePickerPerformance;
    private calculatePickerPerformance;
    private getActiveTasksInZone;
    private getCompletedTasksInZone;
    private getZoneForLocation;
    private getOrderLines;
    private getAvailableInventory;
    private getOrderDetails;
    private consolidateSkusForBatching;
    private calculateBatchPriority;
    private initializeDefaultZones;
    private publishWaveCreatedEvent;
    private publishPickTaskCreatedEvent;
    private publishPickCompletedEvent;
    private publishWaveCompletedEvent;
}
//# sourceMappingURL=picking-service.d.ts.map