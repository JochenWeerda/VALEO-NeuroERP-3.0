export type ForecastModel = 'ARIMA' | 'ExponentialSmoothing' | 'LinearRegression' | 'RandomForest' | 'NeuralNetwork' | 'RuleBased' | 'External';
export type ForecastHorizon = 'days' | 'weeks' | 'months' | 'quarters' | 'years';
export interface ForecastValue {
    timestamp: Date;
    value: number;
    lowerBound?: number;
    upperBound?: number;
    confidence?: number;
}
export interface ForecastMetadata {
    trainingDataPoints?: number;
    modelParameters?: Record<string, any>;
    accuracyMetrics?: {
        mse?: number;
        rmse?: number;
        mae?: number;
        mape?: number;
        r2?: number;
    };
    lastTrainedAt?: Date;
    dataSource?: string;
}
export declare class Forecast {
    readonly id: string;
    readonly tenantId: string;
    readonly metricName: string;
    readonly horizon: number;
    readonly horizonUnit: ForecastHorizon;
    readonly model: ForecastModel;
    readonly forecastValues: ForecastValue[];
    readonly confidenceInterval?: number | undefined;
    readonly createdAt: Date;
    readonly metadata?: ForecastMetadata | undefined;
    readonly version: number;
    constructor(id: string, tenantId: string, metricName: string, horizon: number, horizonUnit: ForecastHorizon, model: ForecastModel, forecastValues: ForecastValue[], confidenceInterval?: number | undefined, createdAt?: Date, metadata?: ForecastMetadata | undefined, version?: number);
    static create(params: {
        id: string;
        tenantId: string;
        metricName: string;
        horizon: number;
        horizonUnit: ForecastHorizon;
        model: ForecastModel;
        forecastValues: ForecastValue[];
        confidenceInterval?: number;
        metadata?: ForecastMetadata;
    }): Forecast;
    updateValues(newValues: ForecastValue[]): Forecast;
    isExpired(maxAgeHours?: number): boolean;
    getForecastForDate(targetDate: Date): ForecastValue | null;
    getAccuracyScore(): number | null;
    toJSON(): {
        id: string;
        tenantId: string;
        metricName: string;
        horizon: number;
        horizonUnit: ForecastHorizon;
        model: ForecastModel;
        forecastValues: {
            timestamp: string;
            value: number;
            lowerBound: number | undefined;
            upperBound: number | undefined;
            confidence: number | undefined;
        }[];
        confidenceInterval: number | undefined;
        createdAt: string;
        metadata: ForecastMetadata | undefined;
        version: number;
    };
}
//# sourceMappingURL=forecast.d.ts.map