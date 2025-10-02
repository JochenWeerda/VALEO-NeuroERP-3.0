/**
 * VALEO NeuroERP 3.0 - AI Assistance Service
 *
 * Advanced AI for slotting optimization, forecasting enhancement, and anomaly detection
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
export interface SlottingRecommendation {
    recommendationId: string;
    sku: string;
    currentLocation: string;
    recommendedLocation: string;
    confidence: number;
    reasoning: string[];
    expectedBenefits: {
        travelTimeReduction: number;
        pickingEfficiency: number;
        inventoryAccuracy: number;
        costSavings: number;
    };
    implementation: {
        priority: 'low' | 'medium' | 'high' | 'urgent';
        estimatedEffort: number;
        dependencies: string[];
        riskLevel: 'low' | 'medium' | 'high';
    };
    generatedAt: Date;
    expiresAt: Date;
}
export interface ForecastingModel {
    modelId: string;
    sku: string;
    modelType: 'arima' | 'prophet' | 'neural_network' | 'ensemble' | 'hybrid';
    parameters: Record<string, any>;
    performance: {
        accuracy: number;
        meanAbsoluteError: number;
        meanSquaredError: number;
        trainingDataSize: number;
        lastTrained: Date;
        nextRetraining: Date;
    };
    features: string[];
    hyperparameters: Record<string, any>;
    active: boolean;
    createdAt: Date;
    updatedAt: Date;
}
export interface AnomalyPattern {
    patternId: string;
    type: 'point_anomaly' | 'contextual_anomaly' | 'collective_anomaly';
    severity: 'low' | 'medium' | 'high' | 'critical';
    affectedEntities: {
        type: 'sku' | 'location' | 'zone' | 'robot' | 'process';
        id: string;
        name: string;
    }[];
    detection: {
        algorithm: 'isolation_forest' | 'autoencoder' | 'statistical' | 'machine_learning';
        confidence: number;
        threshold: number;
        detectedAt: Date;
        detectionWindow: {
            start: Date;
            end: Date;
        };
    };
    analysis: {
        rootCause: string;
        contributingFactors: Array<{
            factor: string;
            impact: number;
            evidence: string;
        }>;
        similarIncidents: string[];
        recommendedActions: Array<{
            action: string;
            priority: 'low' | 'medium' | 'high' | 'urgent';
            expectedImpact: string;
            timeline: string;
        }>;
    };
    status: 'detected' | 'investigating' | 'resolved' | 'false_positive';
    resolution?: {
        resolvedAt: Date;
        resolvedBy: string;
        actionsTaken: string[];
        effectiveness: number;
    };
    createdAt: Date;
    updatedAt: Date;
}
export interface PredictiveInsight {
    insightId: string;
    type: 'trend' | 'seasonality' | 'correlation' | 'causality' | 'anomaly_prediction';
    title: string;
    description: string;
    confidence: number;
    impact: {
        level: 'low' | 'medium' | 'high' | 'critical';
        affected: string[];
        potentialValue: number;
    };
    data: {
        timeRange: {
            start: Date;
            end: Date;
        };
        metrics: Record<string, any>;
        visualization: {
            type: 'line' | 'bar' | 'scatter' | 'heatmap';
            data: any;
            config: Record<string, any>;
        };
    };
    recommendations: Array<{
        action: string;
        rationale: string;
        expectedOutcome: string;
        implementation: {
            complexity: 'low' | 'medium' | 'high';
            timeline: string;
            resources: string[];
        };
    }>;
    generatedAt: Date;
    expiresAt: Date;
}
export declare class AIAssistanceService {
    private readonly eventBus;
    private readonly metrics;
    private slottingRecommendations;
    private forecastingModels;
    private anomalyPatterns;
    private predictiveInsights;
    constructor(eventBus: EventBus);
    /**
     * Generate AI-powered slotting recommendations
     */
    generateSlottingRecommendations(warehouseLayout: any, inventoryData: any, pickingHistory: any): Promise<SlottingRecommendation[]>;
    /**
     * Enhance forecasting with advanced AI models
     */
    enhanceForecasting(sku: string, historicalData: any[], externalFactors: any): Promise<{
        enhancedForecast: any[];
        modelPerformance: any;
        confidence: number;
        insights: string[];
    }>;
    /**
     * Advanced anomaly detection with AI
     */
    detectAnomalies(dataStreams: any[], detectionConfig: any): Promise<AnomalyPattern[]>;
    /**
     * Generate predictive insights
     */
    generatePredictiveInsights(data: any, context: any): Promise<PredictiveInsight[]>;
    /**
     * Train and update AI models
     */
    trainModels(modelType: 'slotting' | 'forecasting' | 'anomaly_detection', trainingData: any): Promise<{
        modelId: string;
        performance: any;
        improvements: string[];
    }>;
    /**
     * Get AI assistance recommendations
     */
    getAssistanceRecommendations(context: {
        user: string;
        currentTask?: string;
        location?: string;
        timeOfDay: number;
        recentActions: string[];
    }): Promise<Array<{
        type: 'suggestion' | 'warning' | 'optimization' | 'alert';
        title: string;
        description: string;
        confidence: number;
        action?: {
            type: string;
            parameters: any;
        };
    }>>;
    private analyzeCurrentSlottingEfficiency;
    private identifySlottingOpportunities;
    private generateSlottingRecommendation;
    private predictOptimalLocation;
    private calculateExpectedBenefits;
    private createForecastingModel;
    private enhanceDataWithExternalFactors;
    private generateEnhancedForecast;
    private calculateForecastConfidence;
    private generateForecastInsights;
    private detectWithIsolationForest;
    private detectWithAutoencoder;
    private detectWithStatisticalMethods;
    private deduplicateAnomalies;
    private enrichAnomaly;
    private analyzeTrends;
    private detectSeasonality;
    private analyzeCorrelations;
    private generatePredictions;
    private trainSlottingModel;
    private trainForecastingModel;
    private trainAnomalyModel;
    private getPickingAssistance;
    private getReceivingAssistance;
    private getLocationAssistance;
    private getTimeBasedAssistance;
    private getProactiveAssistance;
    private initializeAIModels;
    private startContinuousLearning;
    private retrainModels;
    private publishSlottingOptimizedEvent;
    private publishForecastEnhancedEvent;
    private publishAnomalyDetectedEvent;
    private publishModelTrainedEvent;
}
//# sourceMappingURL=ai-assistance-service.d.ts.map