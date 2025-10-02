import { z } from 'zod';
export declare const ForecastModelSchema: z.ZodEnum<["ARIMA", "ExponentialSmoothing", "LinearRegression", "RandomForest", "NeuralNetwork", "RuleBased", "External"]>;
export declare const ForecastHorizonSchema: z.ZodEnum<["days", "weeks", "months", "quarters", "years"]>;
export declare const ForecastValueSchema: z.ZodObject<{
    timestamp: z.ZodDate;
    value: z.ZodNumber;
    lowerBound: z.ZodOptional<z.ZodNumber>;
    upperBound: z.ZodOptional<z.ZodNumber>;
    confidence: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    value: number;
    timestamp: Date;
    lowerBound?: number | undefined;
    upperBound?: number | undefined;
    confidence?: number | undefined;
}, {
    value: number;
    timestamp: Date;
    lowerBound?: number | undefined;
    upperBound?: number | undefined;
    confidence?: number | undefined;
}>;
export declare const ForecastMetadataSchema: z.ZodObject<{
    trainingDataPoints: z.ZodOptional<z.ZodNumber>;
    modelParameters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    accuracyMetrics: z.ZodOptional<z.ZodObject<{
        mse: z.ZodOptional<z.ZodNumber>;
        rmse: z.ZodOptional<z.ZodNumber>;
        mae: z.ZodOptional<z.ZodNumber>;
        mape: z.ZodOptional<z.ZodNumber>;
        r2: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        mse?: number | undefined;
        rmse?: number | undefined;
        mae?: number | undefined;
        mape?: number | undefined;
        r2?: number | undefined;
    }, {
        mse?: number | undefined;
        rmse?: number | undefined;
        mae?: number | undefined;
        mape?: number | undefined;
        r2?: number | undefined;
    }>>;
    lastTrainedAt: z.ZodOptional<z.ZodDate>;
    dataSource: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    trainingDataPoints?: number | undefined;
    modelParameters?: Record<string, any> | undefined;
    accuracyMetrics?: {
        mse?: number | undefined;
        rmse?: number | undefined;
        mae?: number | undefined;
        mape?: number | undefined;
        r2?: number | undefined;
    } | undefined;
    lastTrainedAt?: Date | undefined;
    dataSource?: string | undefined;
}, {
    trainingDataPoints?: number | undefined;
    modelParameters?: Record<string, any> | undefined;
    accuracyMetrics?: {
        mse?: number | undefined;
        rmse?: number | undefined;
        mae?: number | undefined;
        mape?: number | undefined;
        r2?: number | undefined;
    } | undefined;
    lastTrainedAt?: Date | undefined;
    dataSource?: string | undefined;
}>;
export declare const CreateForecastRequestSchema: z.ZodObject<{
    metricName: z.ZodString;
    horizon: z.ZodNumber;
    horizonUnit: z.ZodEnum<["days", "weeks", "months", "quarters", "years"]>;
    model: z.ZodEnum<["ARIMA", "ExponentialSmoothing", "LinearRegression", "RandomForest", "NeuralNetwork", "RuleBased", "External"]>;
    confidenceInterval: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    metricName: string;
    horizon: number;
    horizonUnit: "days" | "weeks" | "months" | "quarters" | "years";
    model: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External";
    confidenceInterval?: number | undefined;
}, {
    metricName: string;
    horizon: number;
    horizonUnit: "days" | "weeks" | "months" | "quarters" | "years";
    model: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External";
    confidenceInterval?: number | undefined;
}>;
export declare const ForecastResponseSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    metricName: z.ZodString;
    horizon: z.ZodNumber;
    horizonUnit: z.ZodEnum<["days", "weeks", "months", "quarters", "years"]>;
    model: z.ZodEnum<["ARIMA", "ExponentialSmoothing", "LinearRegression", "RandomForest", "NeuralNetwork", "RuleBased", "External"]>;
    forecastValues: z.ZodArray<z.ZodObject<{
        timestamp: z.ZodString;
        value: z.ZodNumber;
        lowerBound: z.ZodOptional<z.ZodNumber>;
        upperBound: z.ZodOptional<z.ZodNumber>;
        confidence: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        value: number;
        timestamp: string;
        lowerBound?: number | undefined;
        upperBound?: number | undefined;
        confidence?: number | undefined;
    }, {
        value: number;
        timestamp: string;
        lowerBound?: number | undefined;
        upperBound?: number | undefined;
        confidence?: number | undefined;
    }>, "many">;
    confidenceInterval: z.ZodOptional<z.ZodNumber>;
    createdAt: z.ZodString;
    metadata: z.ZodOptional<z.ZodObject<{
        trainingDataPoints: z.ZodOptional<z.ZodNumber>;
        modelParameters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
        accuracyMetrics: z.ZodOptional<z.ZodObject<{
            mse: z.ZodOptional<z.ZodNumber>;
            rmse: z.ZodOptional<z.ZodNumber>;
            mae: z.ZodOptional<z.ZodNumber>;
            mape: z.ZodOptional<z.ZodNumber>;
            r2: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            mse?: number | undefined;
            rmse?: number | undefined;
            mae?: number | undefined;
            mape?: number | undefined;
            r2?: number | undefined;
        }, {
            mse?: number | undefined;
            rmse?: number | undefined;
            mae?: number | undefined;
            mape?: number | undefined;
            r2?: number | undefined;
        }>>;
        lastTrainedAt: z.ZodOptional<z.ZodDate>;
        dataSource: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        trainingDataPoints?: number | undefined;
        modelParameters?: Record<string, any> | undefined;
        accuracyMetrics?: {
            mse?: number | undefined;
            rmse?: number | undefined;
            mae?: number | undefined;
            mape?: number | undefined;
            r2?: number | undefined;
        } | undefined;
        lastTrainedAt?: Date | undefined;
        dataSource?: string | undefined;
    }, {
        trainingDataPoints?: number | undefined;
        modelParameters?: Record<string, any> | undefined;
        accuracyMetrics?: {
            mse?: number | undefined;
            rmse?: number | undefined;
            mae?: number | undefined;
            mape?: number | undefined;
            r2?: number | undefined;
        } | undefined;
        lastTrainedAt?: Date | undefined;
        dataSource?: string | undefined;
    }>>;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    createdAt: string;
    version: number;
    metricName: string;
    horizon: number;
    horizonUnit: "days" | "weeks" | "months" | "quarters" | "years";
    model: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External";
    forecastValues: {
        value: number;
        timestamp: string;
        lowerBound?: number | undefined;
        upperBound?: number | undefined;
        confidence?: number | undefined;
    }[];
    metadata?: {
        trainingDataPoints?: number | undefined;
        modelParameters?: Record<string, any> | undefined;
        accuracyMetrics?: {
            mse?: number | undefined;
            rmse?: number | undefined;
            mae?: number | undefined;
            mape?: number | undefined;
            r2?: number | undefined;
        } | undefined;
        lastTrainedAt?: Date | undefined;
        dataSource?: string | undefined;
    } | undefined;
    confidenceInterval?: number | undefined;
}, {
    id: string;
    tenantId: string;
    createdAt: string;
    version: number;
    metricName: string;
    horizon: number;
    horizonUnit: "days" | "weeks" | "months" | "quarters" | "years";
    model: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External";
    forecastValues: {
        value: number;
        timestamp: string;
        lowerBound?: number | undefined;
        upperBound?: number | undefined;
        confidence?: number | undefined;
    }[];
    metadata?: {
        trainingDataPoints?: number | undefined;
        modelParameters?: Record<string, any> | undefined;
        accuracyMetrics?: {
            mse?: number | undefined;
            rmse?: number | undefined;
            mae?: number | undefined;
            mape?: number | undefined;
            r2?: number | undefined;
        } | undefined;
        lastTrainedAt?: Date | undefined;
        dataSource?: string | undefined;
    } | undefined;
    confidenceInterval?: number | undefined;
}>;
export declare const ForecastQuerySchema: z.ZodObject<{
    metricName: z.ZodOptional<z.ZodString>;
    model: z.ZodOptional<z.ZodEnum<["ARIMA", "ExponentialSmoothing", "LinearRegression", "RandomForest", "NeuralNetwork", "RuleBased", "External"]>>;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    from?: string | undefined;
    to?: string | undefined;
    metricName?: string | undefined;
    model?: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External" | undefined;
}, {
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
    metricName?: string | undefined;
    model?: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External" | undefined;
}>;
export declare const ForecastListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodString;
        metricName: z.ZodString;
        horizon: z.ZodNumber;
        horizonUnit: z.ZodEnum<["days", "weeks", "months", "quarters", "years"]>;
        model: z.ZodEnum<["ARIMA", "ExponentialSmoothing", "LinearRegression", "RandomForest", "NeuralNetwork", "RuleBased", "External"]>;
        forecastValues: z.ZodArray<z.ZodObject<{
            timestamp: z.ZodString;
            value: z.ZodNumber;
            lowerBound: z.ZodOptional<z.ZodNumber>;
            upperBound: z.ZodOptional<z.ZodNumber>;
            confidence: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            value: number;
            timestamp: string;
            lowerBound?: number | undefined;
            upperBound?: number | undefined;
            confidence?: number | undefined;
        }, {
            value: number;
            timestamp: string;
            lowerBound?: number | undefined;
            upperBound?: number | undefined;
            confidence?: number | undefined;
        }>, "many">;
        confidenceInterval: z.ZodOptional<z.ZodNumber>;
        createdAt: z.ZodString;
        metadata: z.ZodOptional<z.ZodObject<{
            trainingDataPoints: z.ZodOptional<z.ZodNumber>;
            modelParameters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
            accuracyMetrics: z.ZodOptional<z.ZodObject<{
                mse: z.ZodOptional<z.ZodNumber>;
                rmse: z.ZodOptional<z.ZodNumber>;
                mae: z.ZodOptional<z.ZodNumber>;
                mape: z.ZodOptional<z.ZodNumber>;
                r2: z.ZodOptional<z.ZodNumber>;
            }, "strip", z.ZodTypeAny, {
                mse?: number | undefined;
                rmse?: number | undefined;
                mae?: number | undefined;
                mape?: number | undefined;
                r2?: number | undefined;
            }, {
                mse?: number | undefined;
                rmse?: number | undefined;
                mae?: number | undefined;
                mape?: number | undefined;
                r2?: number | undefined;
            }>>;
            lastTrainedAt: z.ZodOptional<z.ZodDate>;
            dataSource: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            trainingDataPoints?: number | undefined;
            modelParameters?: Record<string, any> | undefined;
            accuracyMetrics?: {
                mse?: number | undefined;
                rmse?: number | undefined;
                mae?: number | undefined;
                mape?: number | undefined;
                r2?: number | undefined;
            } | undefined;
            lastTrainedAt?: Date | undefined;
            dataSource?: string | undefined;
        }, {
            trainingDataPoints?: number | undefined;
            modelParameters?: Record<string, any> | undefined;
            accuracyMetrics?: {
                mse?: number | undefined;
                rmse?: number | undefined;
                mae?: number | undefined;
                mape?: number | undefined;
                r2?: number | undefined;
            } | undefined;
            lastTrainedAt?: Date | undefined;
            dataSource?: string | undefined;
        }>>;
        version: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        id: string;
        tenantId: string;
        createdAt: string;
        version: number;
        metricName: string;
        horizon: number;
        horizonUnit: "days" | "weeks" | "months" | "quarters" | "years";
        model: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External";
        forecastValues: {
            value: number;
            timestamp: string;
            lowerBound?: number | undefined;
            upperBound?: number | undefined;
            confidence?: number | undefined;
        }[];
        metadata?: {
            trainingDataPoints?: number | undefined;
            modelParameters?: Record<string, any> | undefined;
            accuracyMetrics?: {
                mse?: number | undefined;
                rmse?: number | undefined;
                mae?: number | undefined;
                mape?: number | undefined;
                r2?: number | undefined;
            } | undefined;
            lastTrainedAt?: Date | undefined;
            dataSource?: string | undefined;
        } | undefined;
        confidenceInterval?: number | undefined;
    }, {
        id: string;
        tenantId: string;
        createdAt: string;
        version: number;
        metricName: string;
        horizon: number;
        horizonUnit: "days" | "weeks" | "months" | "quarters" | "years";
        model: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External";
        forecastValues: {
            value: number;
            timestamp: string;
            lowerBound?: number | undefined;
            upperBound?: number | undefined;
            confidence?: number | undefined;
        }[];
        metadata?: {
            trainingDataPoints?: number | undefined;
            modelParameters?: Record<string, any> | undefined;
            accuracyMetrics?: {
                mse?: number | undefined;
                rmse?: number | undefined;
                mae?: number | undefined;
                mape?: number | undefined;
                r2?: number | undefined;
            } | undefined;
            lastTrainedAt?: Date | undefined;
            dataSource?: string | undefined;
        } | undefined;
        confidenceInterval?: number | undefined;
    }>, "many">;
    pagination: z.ZodObject<{
        page: z.ZodNumber;
        pageSize: z.ZodNumber;
        total: z.ZodNumber;
        totalPages: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    }, {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    }>;
}, "strip", z.ZodTypeAny, {
    data: {
        id: string;
        tenantId: string;
        createdAt: string;
        version: number;
        metricName: string;
        horizon: number;
        horizonUnit: "days" | "weeks" | "months" | "quarters" | "years";
        model: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External";
        forecastValues: {
            value: number;
            timestamp: string;
            lowerBound?: number | undefined;
            upperBound?: number | undefined;
            confidence?: number | undefined;
        }[];
        metadata?: {
            trainingDataPoints?: number | undefined;
            modelParameters?: Record<string, any> | undefined;
            accuracyMetrics?: {
                mse?: number | undefined;
                rmse?: number | undefined;
                mae?: number | undefined;
                mape?: number | undefined;
                r2?: number | undefined;
            } | undefined;
            lastTrainedAt?: Date | undefined;
            dataSource?: string | undefined;
        } | undefined;
        confidenceInterval?: number | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}, {
    data: {
        id: string;
        tenantId: string;
        createdAt: string;
        version: number;
        metricName: string;
        horizon: number;
        horizonUnit: "days" | "weeks" | "months" | "quarters" | "years";
        model: "ARIMA" | "ExponentialSmoothing" | "LinearRegression" | "RandomForest" | "NeuralNetwork" | "RuleBased" | "External";
        forecastValues: {
            value: number;
            timestamp: string;
            lowerBound?: number | undefined;
            upperBound?: number | undefined;
            confidence?: number | undefined;
        }[];
        metadata?: {
            trainingDataPoints?: number | undefined;
            modelParameters?: Record<string, any> | undefined;
            accuracyMetrics?: {
                mse?: number | undefined;
                rmse?: number | undefined;
                mae?: number | undefined;
                mape?: number | undefined;
                r2?: number | undefined;
            } | undefined;
            lastTrainedAt?: Date | undefined;
            dataSource?: string | undefined;
        } | undefined;
        confidenceInterval?: number | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
export declare const ForecastAccuracySchema: z.ZodObject<{
    forecastId: z.ZodString;
    metricName: z.ZodString;
    accuracy: z.ZodNumber;
    mse: z.ZodOptional<z.ZodNumber>;
    rmse: z.ZodOptional<z.ZodNumber>;
    mae: z.ZodOptional<z.ZodNumber>;
    mape: z.ZodOptional<z.ZodNumber>;
    r2: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    metricName: string;
    forecastId: string;
    accuracy: number;
    mse?: number | undefined;
    rmse?: number | undefined;
    mae?: number | undefined;
    mape?: number | undefined;
    r2?: number | undefined;
}, {
    metricName: string;
    forecastId: string;
    accuracy: number;
    mse?: number | undefined;
    rmse?: number | undefined;
    mae?: number | undefined;
    mape?: number | undefined;
    r2?: number | undefined;
}>;
export declare const ForecastComparisonSchema: z.ZodObject<{
    actualValues: z.ZodArray<z.ZodObject<{
        timestamp: z.ZodString;
        value: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        value: number;
        timestamp: string;
    }, {
        value: number;
        timestamp: string;
    }>, "many">;
    forecastValues: z.ZodArray<z.ZodObject<{
        timestamp: z.ZodString;
        value: z.ZodNumber;
        lowerBound: z.ZodOptional<z.ZodNumber>;
        upperBound: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        value: number;
        timestamp: string;
        lowerBound?: number | undefined;
        upperBound?: number | undefined;
    }, {
        value: number;
        timestamp: string;
        lowerBound?: number | undefined;
        upperBound?: number | undefined;
    }>, "many">;
    accuracy: z.ZodObject<{
        forecastId: z.ZodString;
        metricName: z.ZodString;
        accuracy: z.ZodNumber;
        mse: z.ZodOptional<z.ZodNumber>;
        rmse: z.ZodOptional<z.ZodNumber>;
        mae: z.ZodOptional<z.ZodNumber>;
        mape: z.ZodOptional<z.ZodNumber>;
        r2: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        metricName: string;
        forecastId: string;
        accuracy: number;
        mse?: number | undefined;
        rmse?: number | undefined;
        mae?: number | undefined;
        mape?: number | undefined;
        r2?: number | undefined;
    }, {
        metricName: string;
        forecastId: string;
        accuracy: number;
        mse?: number | undefined;
        rmse?: number | undefined;
        mae?: number | undefined;
        mape?: number | undefined;
        r2?: number | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    forecastValues: {
        value: number;
        timestamp: string;
        lowerBound?: number | undefined;
        upperBound?: number | undefined;
    }[];
    accuracy: {
        metricName: string;
        forecastId: string;
        accuracy: number;
        mse?: number | undefined;
        rmse?: number | undefined;
        mae?: number | undefined;
        mape?: number | undefined;
        r2?: number | undefined;
    };
    actualValues: {
        value: number;
        timestamp: string;
    }[];
}, {
    forecastValues: {
        value: number;
        timestamp: string;
        lowerBound?: number | undefined;
        upperBound?: number | undefined;
    }[];
    accuracy: {
        metricName: string;
        forecastId: string;
        accuracy: number;
        mse?: number | undefined;
        rmse?: number | undefined;
        mae?: number | undefined;
        mape?: number | undefined;
        r2?: number | undefined;
    };
    actualValues: {
        value: number;
        timestamp: string;
    }[];
}>;
//# sourceMappingURL=forecast-contracts.d.ts.map