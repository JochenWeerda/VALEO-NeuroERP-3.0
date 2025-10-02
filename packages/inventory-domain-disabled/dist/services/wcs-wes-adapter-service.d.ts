/**
 * VALEO NeuroERP 3.0 - WCS/WES Adapter Service
 *
 * Robotics integration, AI forecasting, and anomaly detection
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
export interface RoboticsTask {
    taskId: string;
    taskType: 'pick' | 'put' | 'move' | 'sort' | 'consolidate' | 'inventory_check';
    priority: 'low' | 'normal' | 'high' | 'urgent';
    status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
    robotId?: string;
    location: {
        from?: string;
        to: string;
        zone: string;
    };
    payload: {
        sku?: string;
        quantity?: number;
        lot?: string;
        serial?: string;
        containerId?: string;
        weight?: number;
        dimensions?: {
            length: number;
            width: number;
            height: number;
        };
    };
    constraints: {
        maxWeight?: number;
        maxDimensions?: {
            length: number;
            width: number;
            height: number;
        };
        timeWindow?: {
            start: Date;
            end: Date;
        };
        dependencies?: string[];
    };
    execution: {
        assignedAt?: Date;
        startedAt?: Date;
        completedAt?: Date;
        duration?: number;
        path?: string[];
        energyConsumed?: number;
        errors?: Array<{
            errorType: string;
            description: string;
            timestamp: Date;
            resolved: boolean;
        }>;
    };
    createdAt: Date;
    updatedAt: Date;
}
export interface Robot {
    robotId: string;
    type: 'agv' | 'arm' | 'drone' | 'conveyor' | 'sorter';
    model: string;
    capabilities: string[];
    status: 'online' | 'offline' | 'maintenance' | 'error';
    location: {
        current: string;
        zone: string;
        lastUpdated: Date;
    };
    specifications: {
        maxPayload: number;
        maxSpeed: number;
        batteryLevel?: number;
        energyEfficiency: number;
        maintenanceSchedule: {
            lastMaintenance: Date;
            nextMaintenance: Date;
            maintenanceInterval: number;
        };
    };
    performance: {
        tasksCompleted: number;
        totalDistance: number;
        totalEnergyConsumed: number;
        averageTaskTime: number;
        errorRate: number;
        uptime: number;
    };
    activeTask?: string;
    queue: RoboticsTask[];
}
export interface AnomalyDetection {
    anomalyId: string;
    type: 'inventory_discrepancy' | 'quality_issue' | 'performance_degradation' | 'demand_spike' | 'supplier_issue';
    severity: 'low' | 'medium' | 'high' | 'critical';
    confidence: number;
    detection: {
        detectedAt: Date;
        detectedBy: 'ai_model' | 'rule_engine' | 'manual';
        location?: string;
        sku?: string;
        zone?: string;
    };
    details: {
        description: string;
        metrics: Record<string, any>;
        threshold: any;
        actualValue: any;
        historicalAverage?: any;
    };
    impact: {
        affectedItems?: number;
        potentialLoss?: number;
        urgency: 'immediate' | 'high' | 'medium' | 'low';
    };
    resolution: {
        status: 'detected' | 'investigating' | 'resolved' | 'false_positive';
        actions: Array<{
            actionType: 'alert' | 'quarantine' | 'adjust_inventory' | 'maintenance' | 'investigation';
            description: string;
            assignedTo?: string;
            completedAt?: Date;
            result?: string;
        }>;
        resolvedAt?: Date;
        resolvedBy?: string;
    };
}
export interface InventoryForecast {
    forecastId: string;
    sku: string;
    location?: string;
    forecastType: 'demand' | 'supply' | 'inventory_level' | 'reorder_point';
    timeRange: {
        start: Date;
        end: Date;
        granularity: 'hour' | 'day' | 'week' | 'month';
    };
    forecast: Array<{
        timestamp: Date;
        predictedValue: number;
        confidence: number;
        upperBound: number;
        lowerBound: number;
        factors: Record<string, number>;
    }>;
    accuracy: {
        historicalAccuracy: number;
        modelUsed: string;
        lastTrained: Date;
        nextRetraining: Date;
    };
    recommendations: Array<{
        type: 'reorder' | 'safety_stock' | 'promotion' | 'discontinuation';
        description: string;
        impact: number;
        confidence: number;
    }>;
    generatedAt: Date;
    expiresAt: Date;
}
export interface WCSCommand {
    commandId: string;
    type: 'move_robot' | 'execute_task' | 'update_status' | 'emergency_stop' | 'maintenance_mode';
    target: string;
    parameters: Record<string, any>;
    priority: 'low' | 'normal' | 'high' | 'critical';
    execution: {
        sentAt: Date;
        acknowledgedAt?: Date;
        completedAt?: Date;
        status: 'sent' | 'acknowledged' | 'executing' | 'completed' | 'failed';
        response?: any;
        error?: string;
    };
}
export declare class WCSWESAdapterService {
    private readonly eventBus;
    private readonly metrics;
    private robots;
    private activeTasks;
    private anomalies;
    constructor(eventBus: EventBus);
    /**
     * Create robotics task
     */
    createRoboticsTask(task: Omit<RoboticsTask, 'taskId' | 'status' | 'createdAt' | 'updatedAt'>): Promise<RoboticsTask>;
    /**
     * Execute WCS command
     */
    executeWCSCommand(command: Omit<WCSCommand, 'commandId' | 'execution'>): Promise<WCSCommand>;
    /**
     * Generate inventory forecast
     */
    generateInventoryForecast(sku: string, forecastType: InventoryForecast['forecastType'], timeRange: InventoryForecast['timeRange']): Promise<InventoryForecast>;
    /**
     * Detect anomalies in real-time
     */
    detectAnomalies(): Promise<AnomalyDetection[]>;
    /**
     * Get robot performance analytics
     */
    getRobotPerformanceAnalytics(robotId?: string, period?: 'hour' | 'day' | 'week' | 'month'): Promise<{
        robotId: string;
        period: string;
        metrics: {
            tasksCompleted: number;
            averageTaskTime: number;
            errorRate: number;
            uptime: number;
            energyEfficiency: number;
            distanceTraveled: number;
        };
        trends: {
            taskCompletion: number[];
            errorRate: number[];
            uptime: number[];
        };
    }>;
    /**
     * Optimize robot task assignment
     */
    optimizeTaskAssignment(): Promise<{
        assignments: Array<{
            taskId: string;
            robotId: string;
            priority: number;
        }>;
        optimization: {
            totalTasks: number;
            assignedTasks: number;
            averageWaitTime: number;
            resourceUtilization: number;
        };
    }>;
    private assignOptimalRobot;
    private assignTaskToRobot;
    private isRobotSuitableForTask;
    private getPriorityValue;
    private sendCommandToWCS;
    private getHistoricalData;
    private generateForecastWithAI;
    private calculateForecastAccuracy;
    private generateRecommendations;
    private detectInventoryAnomalies;
    private detectQualityAnomalies;
    private detectPerformanceAnomalies;
    private detectDemandAnomalies;
    private initializeRobots;
    private startAnomalyDetection;
    private startForecastingEngine;
    private getHighValueItems;
    private publishRoboticsTaskCreatedEvent;
    private publishAnomalyDetectedEvent;
    private publishForecastGeneratedEvent;
}
//# sourceMappingURL=wcs-wes-adapter-service.d.ts.map