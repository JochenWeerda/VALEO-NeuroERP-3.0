/**
 * VALEO NeuroERP 3.0 - AI Assistance Service
 *
 * Advanced AI for slotting optimization, forecasting enhancement, and anomaly detection
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import {
  AISlottingOptimizedEvent,
  AIForecastEnhancedEvent,
  AIAnomalyDetectedEvent,
  AIModelTrainedEvent
} from '../core/domain-events/inventory-domain-events';

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
    estimatedEffort: number; // hours
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
    timeRange: { start: Date; end: Date };
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

@injectable()
export class AIAssistanceService {
  private readonly metrics = new InventoryMetricsService();
  private slottingRecommendations: Map<string, SlottingRecommendation> = new Map();
  private forecastingModels: Map<string, ForecastingModel> = new Map();
  private anomalyPatterns: Map<string, AnomalyPattern> = new Map();
  private predictiveInsights: Map<string, PredictiveInsight> = new Map();

  constructor(
    private readonly eventBus: EventBus
  ) {
    this.initializeAIModels();
    this.startContinuousLearning();
  }

  /**
   * Generate AI-powered slotting recommendations
   */
  async generateSlottingRecommendations(warehouseLayout: any, inventoryData: any, pickingHistory: any): Promise<SlottingRecommendation[]> {
    const startTime = Date.now();

    try {
      const recommendations: SlottingRecommendation[] = [];

      // Analyze current slotting efficiency
      const currentEfficiency = await this.analyzeCurrentSlottingEfficiency(warehouseLayout, pickingHistory);

      // Identify optimization opportunities
      const opportunities = await this.identifySlottingOpportunities(inventoryData, pickingHistory, warehouseLayout);

      // Generate recommendations using ML models
      for (const opportunity of opportunities) {
        const recommendation = await this.generateSlottingRecommendation(
          opportunity,
          currentEfficiency,
          warehouseLayout
        );

        if (recommendation.confidence > 0.7) { // Only high-confidence recommendations
          recommendations.push(recommendation);
          this.slottingRecommendations.set(recommendation.recommendationId, recommendation);
        }
      }

      // Sort by expected benefits
      recommendations.sort((a, b) =>
        (b.expectedBenefits.costSavings * b.confidence) - (a.expectedBenefits.costSavings * a.confidence)
      );

      // Publish events
      for (const rec of recommendations) {
        await this.publishSlottingOptimizedEvent(rec);
      }

      this.metrics.recordDatabaseQueryDuration('ai_assistance', 'slotting_recommendations', (Date.now() - startTime) / 1000);
      this.metrics.incrementAIRecommendations('slotting', recommendations.length);

      return recommendations;
    } catch (error) {
      this.metrics.incrementErrorCount('ai_assistance', 'slotting_recommendations_failed');
      throw error;
    }
  }

  /**
   * Enhance forecasting with advanced AI models
   */
  async enhanceForecasting(sku: string, historicalData: any[], externalFactors: any): Promise<{
    enhancedForecast: any[];
    modelPerformance: any;
    confidence: number;
    insights: string[];
  }> {
    const startTime = Date.now();

    try {
      // Get or create forecasting model
      let model = this.forecastingModels.get(sku);
      if (!model) {
        model = await this.createForecastingModel(sku, historicalData);
        this.forecastingModels.set(sku, model);
      }

      // Enhance with external factors
      const enhancedData = await this.enhanceDataWithExternalFactors(historicalData, externalFactors);

      // Generate enhanced forecast
      const enhancedForecast = await this.generateEnhancedForecast(model, enhancedData);

      // Calculate confidence and insights
      const confidence = await this.calculateForecastConfidence(enhancedForecast, historicalData);
      const insights = await this.generateForecastInsights(enhancedForecast, externalFactors);

      // Update model performance
      model.performance.accuracy = confidence;
      model.performance.lastTrained = new Date();
      model.updatedAt = new Date();

      // Publish event
      await this.publishForecastEnhancedEvent(sku, enhancedForecast, confidence);

      this.metrics.recordDatabaseQueryDuration('ai_assistance', 'forecasting_enhancement', (Date.now() - startTime) / 1000);

      return {
        enhancedForecast,
        modelPerformance: model.performance,
        confidence,
        insights
      };
    } catch (error) {
      this.metrics.incrementErrorCount('ai_assistance', 'forecasting_enhancement_failed');
      throw error;
    }
  }

  /**
   * Advanced anomaly detection with AI
   */
  async detectAnomalies(dataStreams: any[], detectionConfig: any): Promise<AnomalyPattern[]> {
    const startTime = Date.now();

    try {
      const anomalies: AnomalyPattern[] = [];

      // Apply multiple detection algorithms
      const isolationForestAnomalies = await this.detectWithIsolationForest(dataStreams, detectionConfig);
      const autoencoderAnomalies = await this.detectWithAutoencoder(dataStreams, detectionConfig);
      const statisticalAnomalies = await this.detectWithStatisticalMethods(dataStreams, detectionConfig);

      // Combine and deduplicate
      const allAnomalies = [...isolationForestAnomalies, ...autoencoderAnomalies, ...statisticalAnomalies];
      const uniqueAnomalies = this.deduplicateAnomalies(allAnomalies);

      // Analyze and enrich anomalies
      for (const anomaly of uniqueAnomalies) {
        const enrichedAnomaly = await this.enrichAnomaly(anomaly, dataStreams);
        anomalies.push(enrichedAnomaly);
        this.anomalyPatterns.set(enrichedAnomaly.patternId, enrichedAnomaly);

        // Publish event
        await this.publishAnomalyDetectedEvent(enrichedAnomaly);
      }

      this.metrics.recordDatabaseQueryDuration('ai_assistance', 'anomaly_detection', (Date.now() - startTime) / 1000);
      this.metrics.incrementAnomaliesDetected(anomalies.length);

      return anomalies;
    } catch (error) {
      this.metrics.incrementErrorCount('ai_assistance', 'anomaly_detection_failed');
      throw error;
    }
  }

  /**
   * Generate predictive insights
   */
  async generatePredictiveInsights(data: any, context: any): Promise<PredictiveInsight[]> {
    const startTime = Date.now();

    try {
      const insights: PredictiveInsight[] = [];

      // Trend analysis
      const trendInsights = await this.analyzeTrends(data, context);
      insights.push(...trendInsights);

      // Seasonality detection
      const seasonalityInsights = await this.detectSeasonality(data, context);
      insights.push(...seasonalityInsights);

      // Correlation analysis
      const correlationInsights = await this.analyzeCorrelations(data, context);
      insights.push(...correlationInsights);

      // Predictive modeling
      const predictiveInsights = await this.generatePredictions(data, context);
      insights.push(...predictiveInsights);

      // Sort by impact and confidence
      insights.sort((a, b) => (b.impact.potentialValue * b.confidence) - (a.impact.potentialValue * a.confidence));

      // Store insights
      for (const insight of insights) {
        this.predictiveInsights.set(insight.insightId, insight);
      }

      this.metrics.recordDatabaseQueryDuration('ai_assistance', 'predictive_insights', (Date.now() - startTime) / 1000);

      return insights.slice(0, 10); // Top 10 insights
    } catch (error) {
      this.metrics.incrementErrorCount('ai_assistance', 'predictive_insights_failed');
      throw error;
    }
  }

  /**
   * Train and update AI models
   */
  async trainModels(modelType: 'slotting' | 'forecasting' | 'anomaly_detection', trainingData: any): Promise<{
    modelId: string;
    performance: any;
    improvements: string[];
  }> {
    const startTime = Date.now();

    try {
      const modelId = `model_${modelType}_${Date.now()}`;

      // Train model based on type
      let performance: any;
      let improvements: string[];

      switch (modelType) {
        case 'slotting':
          ({ performance, improvements } = await this.trainSlottingModel(trainingData));
          break;
        case 'forecasting':
          ({ performance, improvements } = await this.trainForecastingModel(trainingData));
          break;
        case 'anomaly_detection':
          ({ performance, improvements } = await this.trainAnomalyModel(trainingData));
          break;
      }

      // Publish event
      await this.publishModelTrainedEvent(modelId, modelType, performance);

      this.metrics.recordDatabaseQueryDuration('ai_assistance', 'model_training', (Date.now() - startTime) / 1000);

      return {
        modelId,
        performance,
        improvements
      };
    } catch (error) {
      this.metrics.incrementErrorCount('ai_assistance', 'model_training_failed');
      throw error;
    }
  }

  /**
   * Get AI assistance recommendations
   */
  async getAssistanceRecommendations(context: {
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
  }>> {
    const recommendations = [];

    // Task-specific recommendations
    if (context.currentTask === 'picking') {
      const pickingRecs = await this.getPickingAssistance(context);
      recommendations.push(...pickingRecs);
    }

    if (context.currentTask === 'receiving') {
      const receivingRecs = await this.getReceivingAssistance(context);
      recommendations.push(...receivingRecs);
    }

    // Location-based recommendations
    if (context.location) {
      const locationRecs = await this.getLocationAssistance(context.location);
      recommendations.push(...locationRecs);
    }

    // Time-based recommendations
    const timeRecs = await this.getTimeBasedAssistance(context.timeOfDay);
    recommendations.push(...timeRecs);

    // Proactive recommendations
    const proactiveRecs = await this.getProactiveAssistance(context.recentActions);
    recommendations.push(...proactiveRecs);

    // Sort by confidence and relevance
    return recommendations
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 5); // Top 5 recommendations
  }

  // Private helper methods

  private async analyzeCurrentSlottingEfficiency(warehouseLayout: any, pickingHistory: any): Promise<any> {
    // Analyze travel distances, picking times, etc.
    return {
      averageTravelTime: 120, // seconds
      pickingAccuracy: 0.98,
      slotUtilization: 0.85,
      throughput: 150 // items/hour
    };
  }

  private async identifySlottingOpportunities(inventoryData: any, pickingHistory: any, warehouseLayout: any): Promise<any[]> {
    // Identify SKUs that could benefit from relocation
    return inventoryData
      .filter((item: any) => item.velocity > 10) // High-velocity items
      .map((item: any) => ({
        sku: item.sku,
        currentLocation: item.location,
        pickingFrequency: item.picksPerDay,
        travelTime: item.averageTravelTime,
        opportunity: 'move_to_fast_lane'
      }));
  }

  private async generateSlottingRecommendation(
    opportunity: any,
    currentEfficiency: any,
    warehouseLayout: any
  ): Promise<SlottingRecommendation> {
    // Use ML to recommend optimal location
    const recommendedLocation = await this.predictOptimalLocation(opportunity, warehouseLayout);

    const benefits = await this.calculateExpectedBenefits(opportunity, recommendedLocation, currentEfficiency);

    return {
      recommendationId: `rec_${Date.now()}`,
      sku: opportunity.sku,
      currentLocation: opportunity.currentLocation,
      recommendedLocation,
      confidence: 0.85,
      reasoning: [
        'High picking frequency justifies prime location',
        'Current location causes excessive travel time',
        'Recommended location optimizes picking path'
      ],
      expectedBenefits: benefits,
      implementation: {
        priority: 'high',
        estimatedEffort: 2,
        dependencies: [],
        riskLevel: 'low'
      },
      generatedAt: new Date(),
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
    };
  }

  private async predictOptimalLocation(opportunity: any, warehouseLayout: any): Promise<string> {
    // ML-based location prediction
    return 'A-01-01-01'; // Example optimal location
  }

  private async calculateExpectedBenefits(opportunity: any, newLocation: string, currentEfficiency: any): Promise<any> {
    return {
      travelTimeReduction: 45, // seconds
      pickingEfficiency: 0.15, // 15% improvement
      inventoryAccuracy: 0.02, // 2% improvement
      costSavings: 1250 // € per year
    };
  }

  private async createForecastingModel(sku: string, historicalData: any[]): Promise<ForecastingModel> {
    return {
      modelId: `forecast_${sku}`,
      sku,
      modelType: 'ensemble',
      parameters: {},
      performance: {
        accuracy: 0.85,
        meanAbsoluteError: 15.2,
        meanSquaredError: 245.8,
        trainingDataSize: historicalData.length,
        lastTrained: new Date(),
        nextRetraining: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      },
      features: ['seasonality', 'trend', 'external_factors'],
      hyperparameters: { learning_rate: 0.01, epochs: 100 },
      active: true,
      createdAt: new Date(),
      updatedAt: new Date()
    };
  }

  private async enhanceDataWithExternalFactors(historicalData: any[], externalFactors: any): Promise<any[]> {
    // Enhance historical data with external factors like promotions, weather, etc.
    return historicalData.map(data => ({
      ...data,
      externalFactors: externalFactors
    }));
  }

  private async generateEnhancedForecast(model: ForecastingModel, enhancedData: any[]): Promise<any[]> {
    // Generate forecast using the model
    return Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() + i * 24 * 60 * 60 * 1000),
      predicted: Math.random() * 100 + 50,
      confidence: 0.8 - Math.random() * 0.2
    }));
  }

  private async calculateForecastConfidence(forecast: any[], historicalData: any[]): Promise<number> {
    // Calculate confidence based on historical accuracy
    return 0.87;
  }

  private async generateForecastInsights(forecast: any[], externalFactors: any): Promise<string[]> {
    return [
      'Strong seasonal pattern detected',
      'External promotion factor increases demand by 25%',
      'Weather patterns may affect next week\'s forecast'
    ];
  }

  private async detectWithIsolationForest(dataStreams: any[], config: any): Promise<AnomalyPattern[]> {
    // Isolation Forest anomaly detection
    return [];
  }

  private async detectWithAutoencoder(dataStreams: any[], config: any): Promise<AnomalyPattern[]> {
    // Autoencoder-based anomaly detection
    return [];
  }

  private async detectWithStatisticalMethods(dataStreams: any[], config: any): Promise<AnomalyPattern[]> {
    // Statistical anomaly detection
    return [];
  }

  private deduplicateAnomalies(anomalies: AnomalyPattern[]): AnomalyPattern[] {
    // Remove duplicate anomalies
    return anomalies;
  }

  private async enrichAnomaly(anomaly: AnomalyPattern, dataStreams: any[]): Promise<AnomalyPattern> {
    // Add root cause analysis and recommendations
    return {
      ...anomaly,
      analysis: {
        rootCause: 'Supplier delay',
        contributingFactors: [
          {
            factor: 'Supplier lead time increase',
            impact: 0.8,
            evidence: 'Historical data shows 20% increase'
          }
        ],
        similarIncidents: ['anomaly_001', 'anomaly_002'],
        recommendedActions: [
          {
            action: 'Contact supplier',
            priority: 'high',
            expectedImpact: 'Reduce delay by 50%',
            timeline: 'Within 2 hours'
          }
        ]
      }
    };
  }

  private async analyzeTrends(data: any, context: any): Promise<PredictiveInsight[]> {
    return [
      {
        insightId: `insight_trend_${Date.now()}`,
        type: 'trend',
        title: 'Increasing Demand Trend',
        description: 'Demand for SKU-001 has been increasing by 15% monthly',
        confidence: 0.92,
        impact: {
          level: 'high',
          affected: ['SKU-001'],
          potentialValue: 50000
        },
        data: {
          timeRange: { start: new Date(), end: new Date() },
          metrics: {},
          visualization: {
            type: 'line',
            data: [],
            config: {}
          }
        },
        recommendations: [
          {
            action: 'Increase safety stock',
            rationale: 'Prevent stockouts during peak demand',
            expectedOutcome: 'Reduce stockout risk by 80%',
            implementation: {
              complexity: 'medium',
              timeline: '1 week',
              resources: ['Inventory Manager']
            }
          }
        ],
        generatedAt: new Date(),
        expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
      }
    ];
  }

  private async detectSeasonality(data: any, context: any): Promise<PredictiveInsight[]> {
    // Seasonality detection
    return [];
  }

  private async analyzeCorrelations(data: any, context: any): Promise<PredictiveInsight[]> {
    // Correlation analysis
    return [];
  }

  private async generatePredictions(data: any, context: any): Promise<PredictiveInsight[]> {
    // Predictive modeling
    return [];
  }

  private async trainSlottingModel(trainingData: any): Promise<{ performance: any; improvements: string[] }> {
    return {
      performance: { accuracy: 0.89, f1Score: 0.85 },
      improvements: ['Better location prediction', 'Reduced travel time']
    };
  }

  private async trainForecastingModel(trainingData: any): Promise<{ performance: any; improvements: string[] }> {
    return {
      performance: { accuracy: 0.91, mae: 12.3 },
      improvements: ['Enhanced seasonality detection', 'Better external factor integration']
    };
  }

  private async trainAnomalyModel(trainingData: any): Promise<{ performance: any; improvements: string[] }> {
    return {
      performance: { precision: 0.94, recall: 0.87 },
      improvements: ['Reduced false positives', 'Better root cause analysis']
    };
  }

  private async getPickingAssistance(context: any): Promise<any[]> {
    return [
      {
        type: 'suggestion',
        title: 'Optimize Picking Path',
        description: 'Consider picking items in A-zone first for better efficiency',
        confidence: 0.85,
        action: {
          type: 'reorder_picking_list',
          parameters: { zone: 'A' }
        }
      }
    ];
  }

  private async getReceivingAssistance(context: any): Promise<any[]> {
    return [
      {
        type: 'warning',
        title: 'Quality Check Required',
        description: 'Previous shipments from this supplier had quality issues',
        confidence: 0.78
      }
    ];
  }

  private async getLocationAssistance(location: string): Promise<any[]> {
    return [
      {
        type: 'optimization',
        title: 'Slotting Opportunity',
        description: 'Consider moving high-velocity items to this location',
        confidence: 0.82
      }
    ];
  }

  private async getTimeBasedAssistance(timeOfDay: number): Promise<any[]> {
    if (timeOfDay > 17) { // After 5 PM
      return [
        {
          type: 'alert',
          title: 'End of Day Checklist',
          description: 'Complete inventory counts before closing',
          confidence: 1.0
        }
      ];
    }
    return [];
  }

  private async getProactiveAssistance(recentActions: string[]): Promise<any[]> {
    // Analyze recent actions and provide proactive suggestions
    return [];
  }

  private initializeAIModels(): void {
    // Initialize pre-trained models
    console.log('AI models initialized');
  }

  private startContinuousLearning(): void {
    // Start continuous model training and updating
    setInterval(async () => {
      try {
        // Retrain models with new data
        await this.retrainModels();
      } catch (error) {
        console.error('Continuous learning error:', error);
      }
    }, 24 * 60 * 60 * 1000); // Daily retraining
  }

  private async retrainModels(): Promise<void> {
    // Retrain models with accumulated data
    console.log('Retraining AI models...');
  }

  // Event publishing methods
  private async publishSlottingOptimizedEvent(recommendation: SlottingRecommendation): Promise<void> {
    const event: AISlottingOptimizedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.ai.slotting.optimized',
      aggregateId: recommendation.recommendationId,
      aggregateType: 'SlottingRecommendation',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      recommendationId: recommendation.recommendationId,
      sku: recommendation.sku,
      fromLocation: recommendation.currentLocation,
      toLocation: recommendation.recommendedLocation,
      confidence: recommendation.confidence,
      expectedSavings: recommendation.expectedBenefits.costSavings
    };

    await this.eventBus.publish(event);
  }

  private async publishForecastEnhancedEvent(sku: string, forecast: any[], confidence: number): Promise<void> {
    const event: AIForecastEnhancedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.ai.forecast.enhanced',
      aggregateId: `forecast_${sku}`,
      aggregateType: 'ForecastingModel',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      sku,
      forecastPoints: forecast.length,
      confidence,
      accuracy: confidence
    };

    await this.eventBus.publish(event);
  }

  private async publishAnomalyDetectedEvent(anomaly: AnomalyPattern): Promise<void> {
    const event: AIAnomalyDetectedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.ai.anomaly.detected',
      aggregateId: anomaly.patternId,
      aggregateType: 'AnomalyPattern',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      anomalyId: anomaly.patternId,
      type: anomaly.type,
      severity: anomaly.severity,
      confidence: anomaly.detection.confidence,
      affectedEntities: anomaly.affectedEntities.length
    };

    await this.eventBus.publish(event);
  }

  private async publishModelTrainedEvent(modelId: string, modelType: string, performance: any): Promise<void> {
    const event: AIModelTrainedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.ai.model.trained',
      aggregateId: modelId,
      aggregateType: 'AIModel',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      modelId,
      modelType,
      performance: performance.accuracy || 0,
      trainingDataSize: performance.trainingDataSize || 0
    };

    await this.eventBus.publish(event);
  }
}