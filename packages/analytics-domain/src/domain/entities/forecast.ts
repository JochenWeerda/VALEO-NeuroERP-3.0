export type ForecastModel =
  | 'ARIMA'
  | 'ExponentialSmoothing'
  | 'LinearRegression'
  | 'RandomForest'
  | 'NeuralNetwork'
  | 'RuleBased'
  | 'External';

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

export class Forecast {
  constructor(
    public readonly id: string,
    public readonly tenantId: string,
    public readonly metricName: string,
    public readonly horizon: number,
    public readonly horizonUnit: ForecastHorizon,
    public readonly model: ForecastModel,
    public readonly forecastValues: ForecastValue[],
    public readonly confidenceInterval?: number,
    public readonly createdAt: Date = new Date(),
    public readonly metadata?: ForecastMetadata,
    public readonly version: number = 1
  ) {}

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
  }): Forecast {
    return new Forecast(
      params.id,
      params.tenantId,
      params.metricName,
      params.horizon,
      params.horizonUnit,
      params.model,
      params.forecastValues,
      params.confidenceInterval,
      new Date(),
      params.metadata,
      1
    );
  }

  updateValues(newValues: ForecastValue[]): Forecast {
    return new Forecast(
      this.id,
      this.tenantId,
      this.metricName,
      this.horizon,
      this.horizonUnit,
      this.model,
      newValues,
      this.confidenceInterval,
      this.createdAt,
      {
        ...this.metadata,
        lastTrainedAt: new Date(),
      },
      this.version + 1
    );
  }

  isExpired(maxAgeHours: number = 24): boolean {
    const ageMs = Date.now() - this.createdAt.getTime();
    const maxAgeMs = maxAgeHours * 60 * 60 * 1000;
    return ageMs > maxAgeMs;
  }

  getForecastForDate(targetDate: Date): ForecastValue | null {
    // Find the closest forecast value to the target date
    let closest: ForecastValue | null = null;
    let minDiff = Infinity;

    for (const value of this.forecastValues) {
      const diff = Math.abs(value.timestamp.getTime() - targetDate.getTime());
      if (diff < minDiff) {
        minDiff = diff;
        closest = value;
      }
    }

    return closest;
  }

  getAccuracyScore(): number | null {
    return this.metadata?.accuracyMetrics?.r2 || null;
  }

  toJSON() {
    return {
      id: this.id,
      tenantId: this.tenantId,
      metricName: this.metricName,
      horizon: this.horizon,
      horizonUnit: this.horizonUnit,
      model: this.model,
      forecastValues: this.forecastValues.map(v => ({
        timestamp: v.timestamp.toISOString(),
        value: v.value,
        lowerBound: v.lowerBound,
        upperBound: v.upperBound,
        confidence: v.confidence,
      })),
      confidenceInterval: this.confidenceInterval,
      createdAt: this.createdAt.toISOString(),
      metadata: this.metadata,
      version: this.version,
    };
  }
}