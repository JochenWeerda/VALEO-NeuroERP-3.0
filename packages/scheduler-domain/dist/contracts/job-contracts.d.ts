import { z } from 'zod';
declare const BackoffConfigSchema: z.ZodObject<{
    strategy: z.ZodDefault<z.ZodEnum<["FIXED", "EXPONENTIAL"]>>;
    baseSec: z.ZodDefault<z.ZodNumber>;
    maxSec: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    strategy: "FIXED" | "EXPONENTIAL";
    baseSec: number;
    maxSec?: number | undefined;
}, {
    strategy?: "FIXED" | "EXPONENTIAL" | undefined;
    baseSec?: number | undefined;
    maxSec?: number | undefined;
}>;
declare const CreateJobInputSchema: z.ZodObject<{
    key: z.ZodString;
    queue: z.ZodDefault<z.ZodString>;
    priority: z.ZodDefault<z.ZodNumber>;
    maxAttempts: z.ZodDefault<z.ZodNumber>;
    backoff: z.ZodDefault<z.ZodObject<{
        strategy: z.ZodDefault<z.ZodEnum<["FIXED", "EXPONENTIAL"]>>;
        baseSec: z.ZodDefault<z.ZodNumber>;
        maxSec: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        strategy: "FIXED" | "EXPONENTIAL";
        baseSec: number;
        maxSec?: number | undefined;
    }, {
        strategy?: "FIXED" | "EXPONENTIAL" | undefined;
        baseSec?: number | undefined;
        maxSec?: number | undefined;
    }>>;
    timeoutSec: z.ZodDefault<z.ZodNumber>;
    concurrencyLimit: z.ZodOptional<z.ZodNumber>;
    slaSec: z.ZodOptional<z.ZodNumber>;
    enabled: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    enabled: boolean;
    key: string;
    queue: string;
    priority: number;
    maxAttempts: number;
    timeoutSec: number;
    backoff: {
        strategy: "FIXED" | "EXPONENTIAL";
        baseSec: number;
        maxSec?: number | undefined;
    };
    concurrencyLimit?: number | undefined;
    slaSec?: number | undefined;
}, {
    key: string;
    enabled?: boolean | undefined;
    queue?: string | undefined;
    priority?: number | undefined;
    maxAttempts?: number | undefined;
    timeoutSec?: number | undefined;
    concurrencyLimit?: number | undefined;
    slaSec?: number | undefined;
    backoff?: {
        strategy?: "FIXED" | "EXPONENTIAL" | undefined;
        baseSec?: number | undefined;
        maxSec?: number | undefined;
    } | undefined;
}>;
declare const UpdateJobInputSchema: z.ZodObject<{
    queue: z.ZodOptional<z.ZodString>;
    priority: z.ZodOptional<z.ZodNumber>;
    maxAttempts: z.ZodOptional<z.ZodNumber>;
    backoff: z.ZodOptional<z.ZodObject<{
        strategy: z.ZodDefault<z.ZodEnum<["FIXED", "EXPONENTIAL"]>>;
        baseSec: z.ZodDefault<z.ZodNumber>;
        maxSec: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        strategy: "FIXED" | "EXPONENTIAL";
        baseSec: number;
        maxSec?: number | undefined;
    }, {
        strategy?: "FIXED" | "EXPONENTIAL" | undefined;
        baseSec?: number | undefined;
        maxSec?: number | undefined;
    }>>;
    timeoutSec: z.ZodOptional<z.ZodNumber>;
    concurrencyLimit: z.ZodOptional<z.ZodNullable<z.ZodNumber>>;
    slaSec: z.ZodOptional<z.ZodNullable<z.ZodNumber>>;
    enabled: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    enabled?: boolean | undefined;
    queue?: string | undefined;
    priority?: number | undefined;
    maxAttempts?: number | undefined;
    timeoutSec?: number | undefined;
    concurrencyLimit?: number | null | undefined;
    slaSec?: number | null | undefined;
    backoff?: {
        strategy: "FIXED" | "EXPONENTIAL";
        baseSec: number;
        maxSec?: number | undefined;
    } | undefined;
}, {
    enabled?: boolean | undefined;
    queue?: string | undefined;
    priority?: number | undefined;
    maxAttempts?: number | undefined;
    timeoutSec?: number | undefined;
    concurrencyLimit?: number | null | undefined;
    slaSec?: number | null | undefined;
    backoff?: {
        strategy?: "FIXED" | "EXPONENTIAL" | undefined;
        baseSec?: number | undefined;
        maxSec?: number | undefined;
    } | undefined;
}>;
declare const JobQuerySchema: z.ZodObject<{
    enabled: z.ZodOptional<z.ZodEffects<z.ZodString, boolean, string>>;
    queue: z.ZodOptional<z.ZodString>;
    key: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
    pageSize: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    enabled?: boolean | undefined;
    key?: string | undefined;
    queue?: string | undefined;
}, {
    enabled?: string | undefined;
    key?: string | undefined;
    queue?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
}>;
declare const JobResponseSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    key: z.ZodString;
    queue: z.ZodString;
    priority: z.ZodNumber;
    maxAttempts: z.ZodNumber;
    backoff: z.ZodObject<{
        strategy: z.ZodDefault<z.ZodEnum<["FIXED", "EXPONENTIAL"]>>;
        baseSec: z.ZodDefault<z.ZodNumber>;
        maxSec: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        strategy: "FIXED" | "EXPONENTIAL";
        baseSec: number;
        maxSec?: number | undefined;
    }, {
        strategy?: "FIXED" | "EXPONENTIAL" | undefined;
        baseSec?: number | undefined;
        maxSec?: number | undefined;
    }>;
    timeoutSec: z.ZodNumber;
    concurrencyLimit: z.ZodNullable<z.ZodNumber>;
    slaSec: z.ZodNullable<z.ZodNumber>;
    enabled: z.ZodBoolean;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    version: number;
    enabled: boolean;
    id: string;
    createdAt: string;
    updatedAt: string;
    key: string;
    queue: string;
    priority: number;
    maxAttempts: number;
    timeoutSec: number;
    concurrencyLimit: number | null;
    slaSec: number | null;
    backoff: {
        strategy: "FIXED" | "EXPONENTIAL";
        baseSec: number;
        maxSec?: number | undefined;
    };
}, {
    tenantId: string;
    version: number;
    enabled: boolean;
    id: string;
    createdAt: string;
    updatedAt: string;
    key: string;
    queue: string;
    priority: number;
    maxAttempts: number;
    timeoutSec: number;
    concurrencyLimit: number | null;
    slaSec: number | null;
    backoff: {
        strategy?: "FIXED" | "EXPONENTIAL" | undefined;
        baseSec?: number | undefined;
        maxSec?: number | undefined;
    };
}>;
declare const JobListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodString;
        key: z.ZodString;
        queue: z.ZodString;
        priority: z.ZodNumber;
        maxAttempts: z.ZodNumber;
        backoff: z.ZodObject<{
            strategy: z.ZodDefault<z.ZodEnum<["FIXED", "EXPONENTIAL"]>>;
            baseSec: z.ZodDefault<z.ZodNumber>;
            maxSec: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            strategy: "FIXED" | "EXPONENTIAL";
            baseSec: number;
            maxSec?: number | undefined;
        }, {
            strategy?: "FIXED" | "EXPONENTIAL" | undefined;
            baseSec?: number | undefined;
            maxSec?: number | undefined;
        }>;
        timeoutSec: z.ZodNumber;
        concurrencyLimit: z.ZodNullable<z.ZodNumber>;
        slaSec: z.ZodNullable<z.ZodNumber>;
        enabled: z.ZodBoolean;
        createdAt: z.ZodString;
        updatedAt: z.ZodString;
        version: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        tenantId: string;
        version: number;
        enabled: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        key: string;
        queue: string;
        priority: number;
        maxAttempts: number;
        timeoutSec: number;
        concurrencyLimit: number | null;
        slaSec: number | null;
        backoff: {
            strategy: "FIXED" | "EXPONENTIAL";
            baseSec: number;
            maxSec?: number | undefined;
        };
    }, {
        tenantId: string;
        version: number;
        enabled: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        key: string;
        queue: string;
        priority: number;
        maxAttempts: number;
        timeoutSec: number;
        concurrencyLimit: number | null;
        slaSec: number | null;
        backoff: {
            strategy?: "FIXED" | "EXPONENTIAL" | undefined;
            baseSec?: number | undefined;
            maxSec?: number | undefined;
        };
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
        tenantId: string;
        version: number;
        enabled: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        key: string;
        queue: string;
        priority: number;
        maxAttempts: number;
        timeoutSec: number;
        concurrencyLimit: number | null;
        slaSec: number | null;
        backoff: {
            strategy: "FIXED" | "EXPONENTIAL";
            baseSec: number;
            maxSec?: number | undefined;
        };
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}, {
    data: {
        tenantId: string;
        version: number;
        enabled: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        key: string;
        queue: string;
        priority: number;
        maxAttempts: number;
        timeoutSec: number;
        concurrencyLimit: number | null;
        slaSec: number | null;
        backoff: {
            strategy?: "FIXED" | "EXPONENTIAL" | undefined;
            baseSec?: number | undefined;
            maxSec?: number | undefined;
        };
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
export { CreateJobInputSchema, UpdateJobInputSchema, JobQuerySchema, JobResponseSchema, JobListResponseSchema, BackoffConfigSchema, };
//# sourceMappingURL=job-contracts.d.ts.map