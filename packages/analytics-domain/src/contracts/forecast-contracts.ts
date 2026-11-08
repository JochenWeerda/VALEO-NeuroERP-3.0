import { z } from 'zod';

// Forecast Model Enum
export const ForecastModelSchema = z.enum([
  'ARIMA',
  'ExponentialSmoothing',
  'LinearRegression',
  'RandomForest',
  'NeuralNetwork',
  'RuleBased',
  'External'
]).meta({
  title: 'Forecast Model',
  description: 'Machine learning or statistical model for forecasting',
});

// Forecast Horizon Enum
export const ForecastHorizonSchema = z.enum([
  'days',
  'weeks',
  'months',
  'quarters',
  'years'
]).meta({
  title: 'Forecast Horizon',
  description: 'Time unit for forecast horizon',
});

// Forecast Value Schema
export const ForecastValueSchema = z.object({
  timestamp: z.date(),
  value: z.number(),
  lowerBound: z.number().optional(),
  upperBound: z.number().optional(),
  confidence: z.number().min(0).max(1).optional(),
}).meta({
  title: 'Forecast Value',
  description: 'Individual forecast data point',
});

// Forecast Metadata Schema
export const ForecastMetadataSchema = z.object({
  trainingDataPoints: z.number().optional(),
  modelParameters: z.record(z.string(), z.any()).optional(),
  accuracyMetrics: z.object({
    mse: z.number().optional(),
    rmse: z.number().optional(),
    mae: z.number().optional(),
    mape: z.number().optional(),
    r2: z.number().optional(),
  }).optional(),
  lastTrainedAt: z.date().optional(),
  dataSource: z.string().optional(),
}).meta({
  title: 'Forecast Metadata',
  description: 'Metadata about forecast model and training',
});

// Create Forecast Request Schema
export const CreateForecastRequestSchema = z.object({
  metricName: z.string().min(1).max(100),
  horizon: z.number().int().min(1).max(365),
  horizonUnit: ForecastHorizonSchema,
  model: ForecastModelSchema,
  confidenceInterval: z.number().min(0).max(1).optional(),
}).meta({
  title: 'Create Forecast Request',
  description: 'Request payload for creating a forecast',
});

// Forecast Response Schema
export const ForecastResponseSchema = z.object({
  id: z.string().guid(),
  tenantId: z.string(),
  metricName: z.string(),
  horizon: z.number(),
  horizonUnit: ForecastHorizonSchema,
  model: ForecastModelSchema,
  forecastValues: z.array(z.object({
    timestamp: z.string().datetime(),
    value: z.number(),
    lowerBound: z.number().optional(),
    upperBound: z.number().optional(),
    confidence: z.number().min(0).max(1).optional(),
  })),
  confidenceInterval: z.number().min(0).max(1).optional(),
  createdAt: z.string().datetime(),
  metadata: ForecastMetadataSchema.optional(),
  version: z.number(),
}).meta({
  title: 'Forecast Response',
  description: 'Forecast data response',
});

// Forecast Query Parameters Schema
export const ForecastQuerySchema = z.object({
  metricName: z.string().optional(),
  model: ForecastModelSchema.optional(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
}).meta({
  title: 'Forecast Query Parameters',
  description: 'Query parameters for forecast filtering and pagination',
});

// Forecast List Response Schema
export const ForecastListResponseSchema = z.object({
  data: z.array(ForecastResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
}).meta({
  title: 'Forecast List Response',
  description: 'Paginated list of forecasts',
});

// Forecast Accuracy Schema
export const ForecastAccuracySchema = z.object({
  forecastId: z.string().guid(),
  metricName: z.string(),
  accuracy: z.number().min(0).max(1),
  mse: z.number().optional(),
  rmse: z.number().optional(),
  mae: z.number().optional(),
  mape: z.number().optional(),
  r2: z.number().optional(),
}).meta({
  title: 'Forecast Accuracy',
  description: 'Accuracy metrics for a forecast',
});

// Forecast Comparison Schema
export const ForecastComparisonSchema = z.object({
  actualValues: z.array(z.object({
    timestamp: z.string().datetime(),
    value: z.number(),
  })),
  forecastValues: z.array(z.object({
    timestamp: z.string().datetime(),
    value: z.number(),
    lowerBound: z.number().optional(),
    upperBound: z.number().optional(),
  })),
  accuracy: ForecastAccuracySchema,
}).meta({
  title: 'Forecast Comparison',
  description: 'Comparison between actual and forecast values',
});