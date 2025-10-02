"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ForecastingService = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const schema_1 = require("../../infra/db/schema");
const forecast_1 = require("../entities/forecast");
const event_factories_1 = require("../events/event-factories");
const publisher_1 = require("../../infra/messaging/publisher");
class ForecastingService {
    db;
    config;
    constructor(db, config = {}) {
        this.db = db;
        this.config = config;
        this.config.defaultModel = config.defaultModel || 'ARIMA';
        this.config.defaultConfidenceInterval = config.defaultConfidenceInterval || 0.95;
        this.config.maxForecastHorizon = config.maxForecastHorizon || 365;
        this.config.enableExternalModels = config.enableExternalModels || false;
    }
    async generateForecast(request) {
        const startTime = Date.now();
        try {
            this.validateForecastRequest(request);
            const model = request.model || this.config.defaultModel;
            const confidenceInterval = request.confidenceInterval || this.config.defaultConfidenceInterval;
            let forecastValues = [];
            let accuracy;
            let modelParameters = {};
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
                    }
                    else {
                        throw new Error('External ML models are not enabled');
                    }
                    break;
                default:
                    ({ forecastValues, accuracy, modelParameters } = await this.generateRuleBasedForecast(request));
            }
            const forecast = forecast_1.Forecast.create({
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
            await this.saveForecast(forecast);
            const event = (0, event_factories_1.createForecastCreatedEvent)(forecast);
            await (0, publisher_1.getEventPublisher)().publish(event);
            const executionTimeMs = Date.now() - startTime;
            return {
                forecast,
                success: true,
                executionTimeMs,
                modelUsed: model,
                accuracy,
            };
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                forecast: forecast_1.Forecast.create({
                    id: `forecast-error-${request.tenantId}-${Date.now()}`,
                    tenantId: request.tenantId,
                    metricName: request.metricName,
                    horizon: request.horizon,
                    horizonUnit: request.horizonUnit,
                    model: request.model || this.config.defaultModel,
                    forecastValues: [],
                }),
                success: false,
                executionTimeMs,
                modelUsed: request.model || this.config.defaultModel,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }
    async generateARIMAForecast(request) {
        const { historicalData, horizon, horizonUnit } = request;
        const values = historicalData.map(d => d.value);
        const movingAverage = values.reduce((sum, val) => sum + val, 0) / values.length;
        const trend = this.calculateTrend(values);
        const forecastValues = [];
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
                value: Math.max(0, forecastValue),
                confidence: 0.8,
            });
        }
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
    async generateExponentialSmoothingForecast(request) {
        const { historicalData, horizon, horizonUnit } = request;
        const values = historicalData.map(d => d.value);
        const alpha = 0.3;
        if (values.length === 0 || values[0] === undefined) {
            throw new Error('Historical data is empty');
        }
        let smoothedValue = values[0];
        for (let i = 1; i < values.length; i++) {
            const currentValue = values[i];
            if (currentValue !== undefined) {
                smoothedValue = alpha * currentValue + (1 - alpha) * smoothedValue;
            }
        }
        const forecastValues = [];
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
    async generateLinearRegressionForecast(request) {
        const { historicalData, horizon, horizonUnit } = request;
        const values = historicalData.map(d => d.value);
        const n = values.length;
        const { slope, intercept, r2 } = this.calculateLinearRegression(values);
        const forecastValues = [];
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
    async generateRuleBasedForecast(request) {
        const { historicalData, horizon, horizonUnit } = request;
        const values = historicalData.map(d => d.value);
        const average = values.reduce((sum, val) => sum + val, 0) / values.length;
        const forecastValues = [];
        const lastDataPoint = historicalData[historicalData.length - 1];
        if (!lastDataPoint) {
            throw new Error('Historical data is empty');
        }
        const lastTimestamp = lastDataPoint.timestamp;
        for (let i = 1; i <= horizon; i++) {
            const forecastTimestamp = this.addTimeToDate(lastTimestamp, i, horizonUnit);
            const variation = (Math.random() - 0.5) * 0.2;
            const forecastValue = average * (1 + variation);
            forecastValues.push({
                timestamp: forecastTimestamp,
                value: Math.max(0, forecastValue),
                confidence: 0.6,
            });
        }
        return {
            forecastValues,
            accuracy: 0.5,
            modelParameters: {
                method: 'rule_based',
                average,
                variation: 0.2,
                dataPoints: values.length,
            },
        };
    }
    async generateExternalForecast(request) {
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
            const result = await response.json();
            const forecastValues = result.forecastValues.map(fv => ({
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
        }
        catch (error) {
            throw new Error(`External ML service error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    async getForecasts(tenantId, filters = {}) {
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.forecasts.tenantId, tenantId)];
        if (filters.metricName) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.forecasts.metricName, filters.metricName));
        }
        if (filters.model) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.forecasts.model, filters.model));
        }
        if (filters.fromDate) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.forecasts.createdAt, filters.fromDate));
        }
        if (filters.toDate) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.forecasts.createdAt, filters.toDate));
        }
        const results = await this.db
            .select()
            .from(schema_1.forecasts)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy((0, drizzle_orm_1.desc)(schema_1.forecasts.createdAt))
            .limit(filters.limit || 100)
            .offset(filters.offset || 0);
        return results.map(row => forecast_1.Forecast.create({
            id: row.id,
            tenantId: row.tenantId,
            metricName: row.metricName,
            horizon: Number(row.horizon),
            horizonUnit: row.horizonUnit,
            model: row.model,
            forecastValues: row.forecastValues,
            confidenceInterval: row.confidenceInterval ? Number(row.confidenceInterval) : undefined,
            metadata: row.metadata ?? undefined,
        }));
    }
    async cleanupOldForecasts(tenantId, olderThanDays = 90) {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);
        const result = await this.db
            .delete(schema_1.forecasts)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.forecasts.tenantId, tenantId), (0, drizzle_orm_1.sql) `${schema_1.forecasts.createdAt} < ${cutoffDate}`));
        return result.rowCount || 0;
    }
    validateForecastRequest(request) {
        if (request.horizon <= 0 || request.horizon > this.config.maxForecastHorizon) {
            throw new Error(`Forecast horizon must be between 1 and ${this.config.maxForecastHorizon}`);
        }
        if (request.historicalData.length < 3) {
            throw new Error('At least 3 historical data points are required for forecasting');
        }
        if (request.confidenceInterval && (request.confidenceInterval <= 0 || request.confidenceInterval >= 1)) {
            throw new Error('Confidence interval must be between 0 and 1');
        }
    }
    calculateTrend(values) {
        const n = values.length;
        if (n < 2)
            return 0;
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
    calculateLinearRegression(values) {
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
    calculateSimpleAccuracy(values) {
        if (values.length < 2)
            return 0;
        const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
        const stdDev = Math.sqrt(variance);
        const cv = mean !== 0 ? stdDev / mean : 1;
        return Math.max(0, Math.min(1, 1 - cv));
    }
    addTimeToDate(date, amount, unit) {
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
    async saveForecast(forecast) {
        await this.db.insert(schema_1.forecasts).values({
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
exports.ForecastingService = ForecastingService;
//# sourceMappingURL=forecasting-service.js.map