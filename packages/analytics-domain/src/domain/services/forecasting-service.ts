import { eq, and, sql, desc, gte, lte } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/node-postgres';
import { forecasts } from '../../infra/db/schema';
import { Forecast, ForecastModel, ForecastHorizon, ForecastValue } from '../entities/forecast';
import { createForecastCreatedEvent } from '../events/event-factories';
import { getEventPublisher } from '../../infra/messaging/publisher';

export interface ForecastingConfig {
  defaultModel?: ForecastModel;
  defaultConfidenceInterval?: number;
  maxForecastHorizon?: number;
  externalMLServiceUrl?: string;
  enableExternalModels?: boolean;
}

export interface HistoricalDataPoint {
  timestamp: Date;
  value: number;
  metadata?: Record<string, any>;
}

export interface ForecastRequest {
  tenantId: string;
  metricName: string;
  historicalData: HistoricalDataPoint[];
  horizon: number;
  horizonUnit: ForecastHorizon;
  model?: ForecastModel;
  confidenceInterval?: number;
  parameters?: Record<string, any>;
}

export interface ForecastResult {
  forecast: Forecast;
  success: boolean;
  executionTimeMs: number;
  modelUsed: ForecastModel;
  accuracy?: number;
  error?: string;
}

export interface MLModelResponse {
  forecastValues: Array<{
    timestamp: string;
    value: number;
    lowerBound?: number;
    upperBound?: number;
    confidence?: number;
  }>;
  accuracy?: number;
  modelParameters?: Record<string, any>;
}

export class ForecastingService {
  constructor(
    private db: ReturnType<typeof drizzle>,
    private config: ForecastingConfig = {}
  ) {
    this.config.defaultModel = config.defaultModel || 'ARIMA';
    this.config.defaultConfidenceInterval = config.defaultConfidenceInterval || 0.95;
    this.config.maxForecastHorizon = config.maxForecastHorizon || 365;
    this.config.enableExternalModels = config.enableExternalModels || false;
  }

  /**
   * Generate a forecast using the specified model
   */
  async generateForecast(request: ForecastRequest): Promise<ForecastResult> {
    const startTime = Date.now();

    try {
      // Validate request
      this.validateForecastRequest(request);

      const model = request.model || this.config.defaultModel!;
      const confidenceInterval = request.confidenceInterval || this.config.defaultConfidenceInterval!;

      let forecastValues: ForecastValue[] = [];
      let accuracy: number | undefined;
      let modelParameters: Record<string, any> = {};

      // Generate forecast based on model
      switch (model) {
        case 'ARIMA':
          ({ forecastValues, accuracy, modelParameters } = await this.generateARIMAForecast(request));
          break;
        case 'ExponentialSmoothing':
          ({ forecastValues, accuracy, modelParameters } = await this.generateExponentialSmoothingForecast(request));
          break;
        case 'LinearRegression':
          ({ forecastValues, accuracy, modelParameters } = await this.generateLinearRegressionForecast(request));
          break;
        case 'External':
          if (this.config.enableExternalModels && this.config.externalMLServiceUrl) {
            ({ forecastValues, accuracy, modelParameters } = await this.generateExternalForecast(request));
          } else {
            throw new Error('External ML models are not enabled');
          }
          break;
        default:
          ({ forecastValues, accuracy, modelParameters } = await this.generateRuleBasedForecast(request));
      }

      // Create forecast entity
      const forecast = Forecast.create({
        id: `forecast-${request.tenantId}-${request.metricName}-${Date.now()}`,
        tenantId: request.tenantId,
        metricName: request.metricName,
        horizon: request.horizon,
        horizonUnit: request.horizonUnit,
        model,
        forecastValues,
        confidenceInterval,
        metadata: {
          trainingDataPoints: request.historicalData.length,
          modelParameters,
          accuracyMetrics: accuracy ? { r2: accuracy } : undefined,
          lastTrainedAt: new Date(),
          dataSource: 'historical_data',
        },
      });

      // Save forecast to database
      await this.saveForecast(forecast);

      // Publish domain event
      const event = createForecastCreatedEvent(forecast);
      await getEventPublisher().publish(event);

      const executionTimeMs = Date.now() - startTime;

      return {
        forecast,
        success: true,
        executionTimeMs,
        modelUsed: model,
        accuracy,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        forecast: Forecast.create({
          id: `forecast-error-${request.tenantId}-${Date.now()}`,
          tenantId: request.tenantId,
          metricName: request.metricName,
          horizon: request.horizon,
          horizonUnit: request.horizonUnit,
          model: request.model || this.config.defaultModel!,
          forecastValues: [],
        }),
        success: false,
        executionTimeMs,
        modelUsed: request.model || this.config.defaultModel!,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Generate ARIMA forecast (simplified implementation)
   */
  private async generateARIMAForecast(request: ForecastRequest): Promise<{
    forecastValues: ForecastValue[];
    accuracy?: number;
    modelParameters: Record<string, any>;
  }> {
    const { historicalData, horizon, horizonUnit } = request;

    // Simple moving average as ARIMA approximation
    const values = historicalData.map(d => d.value);
    const movingAverage = values.reduce((sum, val) => sum + val, 0) / values.length;

    // Calculate trend
    const trend = this.calculateTrend(values);

    // Generate forecast values
    const forecastValues: ForecastValue[] = [];
    const lastDataPoint = historicalData[historicalData.length - 1];
    if (!lastDataPoint) {
      throw new Error('Historical data is empty');
    }
    const lastTimestamp = lastDataPoint.timestamp;

    for (let i = 1; i <= horizon; i++) {
      const forecastTimestamp = this.addTimeToDate(lastTimestamp, i, horizonUnit);
      const forecastValue = movingAverage + (trend * i);

      forecastValues.push({
        timestamp: forecastTimestamp,
        value: Math.max(0, forecastValue), // Ensure non-negative
        confidence: 0.8,
      });
    }

    // Calculate simple accuracy (R² approximation)
    const accuracy = this.calculateSimpleAccuracy(values);

    return {
      forecastValues,
      accuracy,
      modelParameters: {
        method: 'simplified_arima',
        movingAverage,
        trend,
        dataPoints: values.length,
      },
    };
  }

  /**
   * Generate Exponential Smoothing forecast
   */
  private async generateExponentialSmoothingForecast(request: ForecastRequest): Promise<{
    forecastValues: ForecastValue[];
    accuracy?: number;
    modelParameters: Record<string, any>;
  }> {
    const { historicalData, horizon, horizonUnit } = request;

    const values = historicalData.map(d => d.value);
    const alpha = 0.3; // Smoothing parameter

    // Calculate exponentially smoothed values
    if (values.length === 0 || values[0] === undefined) {
      throw new Error('Historical data is empty');
    }
    let smoothedValue: number = values[0];
    for (let i = 1; i < values.length; i++) {
      const currentValue = values[i];
      if (currentValue !== undefined) {
        smoothedValue = alpha * currentValue + (1 - alpha) * smoothedValue;
      }
    }

    // Generate forecast values
    const forecastValues: ForecastValue[] = [];
    const lastDataPoint = historicalData[historicalData.length - 1];
    if (!lastDataPoint) {
      throw new Error('Historical data is empty');
    }
    const lastTimestamp = lastDataPoint.timestamp;

    for (let i = 1; i <= horizon; i++) {
      const forecastTimestamp = this.addTimeToDate(lastTimestamp, i, horizonUnit);

      forecastValues.push({
        timestamp: forecastTimestamp,
        value: Math.max(0, smoothedValue),
        confidence: 0.75,
      });
    }

    const accuracy = this.calculateSimpleAccuracy(values);

    return {
      forecastValues,
      accuracy,
      modelParameters: {
        method: 'exponential_smoothing',
        alpha,
        finalSmoothedValue: smoothedValue,
        dataPoints: values.length,
      },
    };
  }

  /**
   * Generate Linear Regression forecast
   */
  private async generateLinearRegressionForecast(request: ForecastRequest): Promise<{
    forecastValues: ForecastValue[];
    accuracy?: number;
    modelParameters: Record<string, any>;
  }> {
    const { historicalData, horizon, horizonUnit } = request;

    const values = historicalData.map(d => d.value);
    const n = values.length;

    // Calculate linear regression
    const { slope, intercept, r2 } = this.calculateLinearRegression(values);

    // Generate forecast values
    const forecastValues: ForecastValue[] = [];
    const lastDataPoint = historicalData[historicalData.length - 1];
    if (!lastDataPoint) {
      throw new Error('Historical data is empty');
    }
    const lastTimestamp = lastDataPoint.timestamp;

    for (let i = 1; i <= horizon; i++) {
      const forecastTimestamp = this.addTimeToDate(lastTimestamp, i, horizonUnit);
      const forecastValue = intercept + slope * (n + i - 1);

      forecastValues.push({
        timestamp: forecastTimestamp,
        value: Math.max(0, forecastValue),
        confidence: 0.7,
      });
    }

    return {
      forecastValues,
      accuracy: r2,
      modelParameters: {
        method: 'linear_regression',
        slope,
        intercept,
        r2,
        dataPoints: n,
      },
    };
  }

  /**
   * Generate rule-based forecast (simple heuristics)
   */
  private async generateRuleBasedForecast(request: ForecastRequest): Promise<{
    forecastValues: ForecastValue[];
    accuracy?: number;
    modelParameters: Record<string, any>;
  }> {
    const { historicalData, horizon, horizonUnit } = request;

    const values = historicalData.map(d => d.value);
    const average = values.reduce((sum, val) => sum + val, 0) / values.length;

    // Simple rule: forecast at average with some variation
    const forecastValues: ForecastValue[] = [];
    const lastDataPoint = historicalData[historicalData.length - 1];
    if (!lastDataPoint) {
      throw new Error('Historical data is empty');
    }
    const lastTimestamp = lastDataPoint.timestamp;

    for (let i = 1; i <= horizon; i++) {
      const forecastTimestamp = this.addTimeToDate(lastTimestamp, i, horizonUnit);
      const variation = (Math.random() - 0.5) * 0.2; // ±10% variation
      const forecastValue = average * (1 + variation);

      forecastValues.push({
        timestamp: forecastTimestamp,
        value: Math.max(0, forecastValue),
        confidence: 0.6,
      });
    }

    return {
      forecastValues,
      accuracy: 0.5, // Low confidence for rule-based
      modelParameters: {
        method: 'rule_based',
        average,
        variation: 0.2,
        dataPoints: values.length,
      },
    };
  }

  /**
   * Generate forecast using external ML service
   */
  private async generateExternalForecast(request: ForecastRequest): Promise<{
    forecastValues: ForecastValue[];
    accuracy?: number;
    modelParameters: Record<string, any>;
  }> {
    if (!this.config.externalMLServiceUrl) {
      throw new Error('External ML service URL not configured');
    }

    try {
      const response = await fetch(`${this.config.externalMLServiceUrl}/forecast`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metricName: request.metricName,
          historicalData: request.historicalData.map(d => ({
            timestamp: d.timestamp.toISOString(),
            value: d.value,
            metadata: d.metadata,
          })),
          horizon: request.horizon,
          horizonUnit: request.horizonUnit,
          parameters: request.parameters,
        }),
      });

      if (!response.ok) {
        throw new Error(`External ML service returned ${response.status}`);
      }

      const result = await response.json() as MLModelResponse;

      const forecastValues: ForecastValue[] = result.forecastValues.map(fv => ({
        timestamp: new Date(fv.timestamp),
        value: fv.value,
        lowerBound: fv.lowerBound,
        upperBound: fv.upperBound,
        confidence: fv.confidence,
      }));

      return {
        forecastValues,
        accuracy: result.accuracy,
        modelParameters: result.modelParameters || {},
      };

    } catch (error) {
      throw new Error(`External ML service error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get existing forecasts for a tenant
   */
  async getForecasts(
    tenantId: string,
    filters: {
      metricName?: string;
      model?: ForecastModel;
      fromDate?: Date;
      toDate?: Date;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<Forecast[]> {
    // Build where conditions
    const conditions = [eq(forecasts.tenantId, tenantId)];

    if (filters.metricName) {
      conditions.push(eq(forecasts.metricName, filters.metricName));
    }

    if (filters.model) {
      conditions.push(eq(forecasts.model, filters.model as string));
    }

    if (filters.fromDate) {
      conditions.push(gte(forecasts.createdAt, filters.fromDate));
    }

    if (filters.toDate) {
      conditions.push(lte(forecasts.createdAt, filters.toDate));
    }

    const results = await this.db
      .select()
      .from(forecasts)
      .where(and(...conditions))
      .orderBy(desc(forecasts.createdAt))
      .limit(filters.limit || 100)
      .offset(filters.offset || 0);

    return results.map(row => Forecast.create({
      id: row.id,
      tenantId: row.tenantId,
      metricName: row.metricName,
      horizon: Number(row.horizon),
      horizonUnit: row.horizonUnit as ForecastHorizon,
      model: row.model as ForecastModel,
      forecastValues: row.forecastValues as ForecastValue[],
      confidenceInterval: row.confidenceInterval ? Number(row.confidenceInterval) : undefined,
      metadata: row.metadata ?? undefined,
    }));
  }

  /**
   * Delete old forecasts
   */
  async cleanupOldForecasts(tenantId: string, olderThanDays: number = 90): Promise<number> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);

    const result = await this.db
      .delete(forecasts)
      .where(and(
        eq(forecasts.tenantId, tenantId),
        sql`${forecasts.createdAt} < ${cutoffDate}`
      ));

    return result.rowCount || 0;
  }

  // Helper methods

  private validateForecastRequest(request: ForecastRequest): void {
    if (request.horizon <= 0 || request.horizon > this.config.maxForecastHorizon!) {
      throw new Error(`Forecast horizon must be between 1 and ${this.config.maxForecastHorizon}`);
    }

    if (request.historicalData.length < 3) {
      throw new Error('At least 3 historical data points are required for forecasting');
    }

    if (request.confidenceInterval && (request.confidenceInterval <= 0 || request.confidenceInterval >= 1)) {
      throw new Error('Confidence interval must be between 0 and 1');
    }
  }

  private calculateTrend(values: number[]): number {
    const n = values.length;
    if (n < 2) return 0;

    const xMean = (n - 1) / 2;
    const yMean = values.reduce((sum, val) => sum + val, 0) / n;

    let numerator = 0;
    let denominator = 0;

    for (let i = 0; i < n; i++) {
      const xDiff = i - xMean;
      const currentValue = values[i];
      if (currentValue !== undefined) {
        const yDiff = currentValue - yMean;
        numerator += xDiff * yDiff;
        denominator += xDiff * xDiff;
      }
    }

    return denominator !== 0 ? numerator / denominator : 0;
  }

  private calculateLinearRegression(values: number[]): { slope: number; intercept: number; r2: number } {
    const n = values.length;
    const xMean = (n - 1) / 2;
    const yMean = values.reduce((sum, val) => sum + val, 0) / n;

    let numerator = 0;
    let denominator = 0;
    let ssRes = 0;
    let ssTot = 0;

    for (let i = 0; i < n; i++) {
      const xDiff = i - xMean;
      const currentValue = values[i];
      if (currentValue !== undefined) {
        const yDiff = currentValue - yMean;
        numerator += xDiff * yDiff;
        denominator += xDiff * xDiff;
      }
    }

    const slope = denominator !== 0 ? numerator / denominator : 0;
    const intercept = yMean - slope * xMean;

    // Calculate R²
    for (let i = 0; i < n; i++) {
      const currentValue = values[i];
      if (currentValue !== undefined) {
        const predicted = intercept + slope * i;
        ssRes += Math.pow(currentValue - predicted, 2);
        ssTot += Math.pow(currentValue - yMean, 2);
      }
    }

    const r2 = ssTot !== 0 ? 1 - (ssRes / ssTot) : 0;

    return { slope, intercept, r2 };
  }

  private calculateSimpleAccuracy(values: number[]): number {
    if (values.length < 2) return 0;

    // Simple accuracy based on coefficient of variation
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);

    // Return a normalized accuracy score (0-1)
    const cv = mean !== 0 ? stdDev / mean : 1;
    return Math.max(0, Math.min(1, 1 - cv));
  }

  private addTimeToDate(date: Date, amount: number, unit: ForecastHorizon): Date {
    const result = new Date(date);

    switch (unit) {
      case 'days':
        result.setDate(result.getDate() + amount);
        break;
      case 'weeks':
        result.setDate(result.getDate() + amount * 7);
        break;
      case 'months':
        result.setMonth(result.getMonth() + amount);
        break;
      case 'quarters':
        result.setMonth(result.getMonth() + amount * 3);
        break;
      case 'years':
        result.setFullYear(result.getFullYear() + amount);
        break;
    }

    return result;
  }

  private async saveForecast(forecast: Forecast): Promise<void> {
    await this.db.insert(forecasts).values({
      tenantId: forecast.tenantId,
      metricName: forecast.metricName,
      horizon: forecast.horizon,
      horizonUnit: forecast.horizonUnit,
      model: forecast.model,
      forecastValues: JSON.parse(JSON.stringify(forecast.forecastValues)),
      confidenceInterval: forecast.confidenceInterval ? String(forecast.confidenceInterval) : null,
      metadata: forecast.metadata ? JSON.parse(JSON.stringify(forecast.metadata)) : null,
    });
  }
}