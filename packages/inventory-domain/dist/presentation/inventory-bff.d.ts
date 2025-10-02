/**
 * VALEO NeuroERP 3.0 - Inventory Backend for Frontend (BFF)
 *
 * Conversational AI interface for warehouse operations
 */
import { ReceivingService } from '../services/receiving-service';
import { PutawaySlottingService } from '../services/putaway-slotting-service';
import { InventoryControlService } from '../services/inventory-control-service';
import { ReplenishmentService } from '../services/replenishment-service';
import { PickingService } from '../services/picking-service';
import { PackingShippingService } from '../services/packing-shipping-service';
import { CycleCountingService } from '../services/cycle-counting-service';
import { ReturnsDispositionService } from '../services/returns-disposition-service';
import { WCSWESAdapterService } from '../services/wcs-wes-adapter-service';
import { TraceabilityService } from '../services/traceability-service';
export interface ConversationContext {
    sessionId: string;
    userId: string;
    currentIntent?: string;
    entities: Record<string, any>;
    conversationHistory: Array<{
        role: 'user' | 'assistant';
        message: string;
        timestamp: Date;
        intent?: string;
        entities?: Record<string, any>;
    }>;
    activeWorkflow?: {
        workflowId: string;
        step: number;
        totalSteps: number;
        data: Record<string, any>;
    };
    preferences: {
        language: string;
        units: 'metric' | 'imperial';
        timezone: string;
        notifications: boolean;
    };
}
export interface AIIntent {
    intent: string;
    confidence: number;
    entities: Record<string, any>;
    response: {
        type: 'text' | 'card' | 'table' | 'chart' | 'action';
        content: any;
        actions?: Array<{
            type: 'button' | 'link' | 'command';
            label: string;
            value: string;
            style?: 'primary' | 'secondary' | 'danger';
        }>;
    };
    followUp?: {
        question: string;
        suggestions: string[];
    };
}
export interface InventoryQuery {
    type: 'status' | 'location' | 'movement' | 'forecast' | 'analytics';
    filters: {
        sku?: string;
        location?: string;
        category?: string;
        dateRange?: {
            start: Date;
            end: Date;
        };
        status?: string;
    };
    aggregation?: 'sum' | 'avg' | 'count' | 'min' | 'max';
    groupBy?: string[];
}
export declare class InventoryBFF {
    private readonly receivingService;
    private readonly putawaySlottingService;
    private readonly inventoryControlService;
    private readonly replenishmentService;
    private readonly pickingService;
    private readonly packingShippingService;
    private readonly cycleCountingService;
    private readonly returnsDispositionService;
    private readonly wcsWesAdapterService;
    private readonly traceabilityService;
    private readonly metrics;
    private conversations;
    constructor(receivingService: ReceivingService, putawaySlottingService: PutawaySlottingService, inventoryControlService: InventoryControlService, replenishmentService: ReplenishmentService, pickingService: PickingService, packingShippingService: PackingShippingService, cycleCountingService: CycleCountingService, returnsDispositionService: ReturnsDispositionService, wcsWesAdapterService: WCSWESAdapterService, traceabilityService: TraceabilityService);
    /**
     * Process natural language query
     */
    processQuery(sessionId: string, userId: string, query: string): Promise<AIIntent>;
    /**
     * Get inventory dashboard data
     */
    getDashboardData(userId: string, filters?: {
        warehouse?: string;
        dateRange?: {
            start: Date;
            end: Date;
        };
    }): Promise<{
        overview: {
            totalItems: number;
            totalValue: number;
            lowStockItems: number;
            expiringItems: number;
            activeTasks: number;
        };
        alerts: Array<{
            type: 'warning' | 'error' | 'info';
            title: string;
            message: string;
            action?: string;
        }>;
        recentActivity: Array<{
            type: string;
            description: string;
            timestamp: Date;
            user?: string;
        }>;
        performance: {
            receivingAccuracy: number;
            pickingAccuracy: number;
            inventoryAccuracy: number;
            throughput: number;
        };
    }>;
    /**
     * Execute workflow step
     */
    executeWorkflowStep(sessionId: string, stepData: Record<string, any>): Promise<{
        completed: boolean;
        nextStep?: number;
        result?: any;
        message: string;
    }>;
    /**
     * Get conversation history
     */
    getConversationHistory(sessionId: string): ConversationContext['conversationHistory'];
    /**
     * Clear conversation context
     */
    clearConversation(sessionId: string): void;
    private createConversationContext;
    private analyzeIntent;
    private handleInventoryStatusQuery;
    private handlePickingQuery;
    private handleReceivingQuery;
    private handleLocationQuery;
    private handleForecastQuery;
    private handleTraceabilityQuery;
    private handleCycleCountQuery;
    private handleAnalyticsQuery;
    private extractEntities;
    private executeActions;
    private executeWorkflowStepLogic;
    private executeReceivingWorkflowStep;
    private getOverviewData;
    private getActiveAlerts;
    private getRecentActivity;
    private getPerformanceMetrics;
}
//# sourceMappingURL=inventory-bff.d.ts.map