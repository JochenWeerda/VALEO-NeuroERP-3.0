"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ForecastComparisonSchema = exports.ForecastAccuracySchema = exports.ForecastListResponseSchema = exports.ForecastQuerySchema = exports.ForecastResponseSchema = exports.CreateForecastRequestSchema = exports.ForecastMetadataSchema = exports.ForecastValueSchema = exports.ForecastHorizonSchema = exports.ForecastModelSchema = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.ForecastModelSchema = zod_1.z.enum([
    'ARIMA',
    'ExponentialSmoothing',
    'LinearRegression',
    'RandomForest',
    'NeuralNetwork',
    'RuleBased',
    'External'
]).openapi({
    title: 'Forecast Model',
    description: 'Machine learning or statistical model for forecasting',
});
exports.ForecastHorizonSchema = zod_1.z.enum([
    'days',
    'weeks',
    'months',
    'quarters',
    'years'
]).openapi({
    title: 'Forecast Horizon',
    description: 'Time unit for forecast horizon',
});
exports.ForecastValueSchema = zod_1.z.object({
    timestamp: zod_1.z.date(),
    value: zod_1.z.number(),
    lowerBound: zod_1.z.number().optional(),
    upperBound: zod_1.z.number().optional(),
    confidence: zod_1.z.number().min(0).max(1).optional(),
}).openapi({
    title: 'Forecast Value',
    description: 'Individual forecast data point',
});
exports.ForecastMetadataSchema = zod_1.z.object({
    trainingDataPoints: zod_1.z.number().optional(),
    modelParameters: zod_1.z.record(zod_1.z.any()).optional(),
    accuracyMetrics: zod_1.z.object({
        mse: zod_1.z.number().optional(),
        rmse: zod_1.z.number().optional(),
        mae: zod_1.z.number().optional(),
        mape: zod_1.z.number().optional(),
        r2: zod_1.z.number().optional(),
    }).optional(),
    lastTrainedAt: zod_1.z.date().optional(),
    dataSource: zod_1.z.string().optional(),
}).openapi({
    title: 'Forecast Metadata',
    description: 'Metadata about forecast model and training',
});
exports.CreateForecastRequestSchema = zod_1.z.object({
    metricName: zod_1.z.string().min(1).max(100),
    horizon: zod_1.z.number().int().min(1).max(365),
    horizonUnit: exports.ForecastHorizonSchema,
    model: exports.ForecastModelSchema,
    confidenceInterval: zod_1.z.number().min(0).max(1).optional(),
}).openapi({
    title: 'Create Forecast Request',
    description: 'Request payload for creating a forecast',
});
exports.ForecastResponseSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    metricName: zod_1.z.string(),
    horizon: zod_1.z.number(),
    horizonUnit: exports.ForecastHorizonSchema,
    model: exports.ForecastModelSchema,
    forecastValues: zod_1.z.array(zod_1.z.object({
        timestamp: zod_1.z.string().datetime(),
        value: zod_1.z.number(),
        lowerBound: zod_1.z.number().optional(),
        upperBound: zod_1.z.number().optional(),
        confidence: zod_1.z.number().min(0).max(1).optional(),
    })),
    confidenceInterval: zod_1.z.number().min(0).max(1).optional(),
    createdAt: zod_1.z.string().datetime(),
    metadata: exports.ForecastMetadataSchema.optional(),
    version: zod_1.z.number(),
}).openapi({
    title: 'Forecast Response',
    description: 'Forecast data response',
});
exports.ForecastQuerySchema = zod_1.z.object({
    metricName: zod_1.z.string().optional(),
    model: exports.ForecastModelSchema.optional(),
    from: zod_1.z.string().datetime().optional(),
    to: zod_1.z.string().datetime().optional(),
    page: zod_1.z.coerce.number().int().min(1).default(1),
    pageSize: zod_1.z.coerce.number().int().min(1).max(100).default(20),
}).openapi({
    title: 'Forecast Query Parameters',
    description: 'Query parameters for forecast filtering and pagination',
});
exports.ForecastListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.ForecastResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
}).openapi({
    title: 'Forecast List Response',
    description: 'Paginated list of forecasts',
});
exports.ForecastAccuracySchema = zod_1.z.object({
    forecastId: zod_1.z.string().uuid(),
    metricName: zod_1.z.string(),
    accuracy: zod_1.z.number().min(0).max(1),
    mse: zod_1.z.number().optional(),
    rmse: zod_1.z.number().optional(),
    mae: zod_1.z.number().optional(),
    mape: zod_1.z.number().optional(),
    r2: zod_1.z.number().optional(),
}).openapi({
    title: 'Forecast Accuracy',
    description: 'Accuracy metrics for a forecast',
});
exports.ForecastComparisonSchema = zod_1.z.object({
    actualValues: zod_1.z.array(zod_1.z.object({
        timestamp: zod_1.z.string().datetime(),
        value: zod_1.z.number(),
    })),
    forecastValues: zod_1.z.array(zod_1.z.object({
        timestamp: zod_1.z.string().datetime(),
        value: zod_1.z.number(),
        lowerBound: zod_1.z.number().optional(),
        upperBound: zod_1.z.number().optional(),
    })),
    accuracy: exports.ForecastAccuracySchema,
}).openapi({
    title: 'Forecast Comparison',
    description: 'Comparison between actual and forecast values',
});
//# sourceMappingURL=forecast-contracts.js.map