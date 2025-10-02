import { drizzle } from 'drizzle-orm/node-postgres';
import { Forecast, ForecastModel, ForecastHorizon } from '../entities/forecast';
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
export declare class ForecastingService {
    private db;
    private config;
    constructor(db: ReturnType<typeof drizzle>, config?: ForecastingConfig);
    generateForecast(request: ForecastRequest): Promise<ForecastResult>;
    private generateARIMAForecast;
    private generateExponentialSmoothingForecast;
    private generateLinearRegressionForecast;
    private generateRuleBasedForecast;
    private generateExternalForecast;
    getForecasts(tenantId: string, filters?: {
        metricName?: string;
        model?: ForecastModel;
        fromDate?: Date;
        toDate?: Date;
        limit?: number;
        offset?: number;
    }): Promise<Forecast[]>;
    cleanupOldForecasts(tenantId: string, olderThanDays?: number): Promise<number>;
    private validateForecastRequest;
    private calculateTrend;
    private calculateLinearRegression;
    private calculateSimpleAccuracy;
    private addTimeToDate;
    private saveForecast;
}
//# sourceMappingURL=forecasting-service.d.ts.map