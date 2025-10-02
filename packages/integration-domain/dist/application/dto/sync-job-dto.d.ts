/**
 * Sync Job DTOs and Validation Schemas
 */
import { z } from 'zod';
export declare const CreateSyncJobRequestSchema: z.ZodObject<{
    name: z.ZodString;
    integrationId: z.ZodString;
    config: z.ZodObject<{
        source: z.ZodObject<{
            type: z.ZodEnum<["database", "api", "file", "message-queue"]>;
            connection: z.ZodRecord<z.ZodString, z.ZodUnknown>;
            query: z.ZodOptional<z.ZodString>;
            filters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        }, "strip", z.ZodTypeAny, {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        }, {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        }>;
        target: z.ZodObject<{
            type: z.ZodEnum<["database", "api", "file", "message-queue"]>;
            connection: z.ZodRecord<z.ZodString, z.ZodUnknown>;
            mapping: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
            batchSize: z.ZodDefault<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            batchSize: number;
            mapping?: Record<string, string> | undefined;
        }, {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            mapping?: Record<string, string> | undefined;
            batchSize?: number | undefined;
        }>;
        schedule: z.ZodOptional<z.ZodObject<{
            cron: z.ZodOptional<z.ZodString>;
            interval: z.ZodOptional<z.ZodNumber>;
            timezone: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        }, {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        }>>;
        retryPolicy: z.ZodOptional<z.ZodObject<{
            maxRetries: z.ZodNumber;
            backoffMs: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            maxRetries: number;
            backoffMs: number;
        }, {
            maxRetries: number;
            backoffMs: number;
        }>>;
    }, "strip", z.ZodTypeAny, {
        source: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        };
        target: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            batchSize: number;
            mapping?: Record<string, string> | undefined;
        };
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        schedule?: {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        } | undefined;
    }, {
        source: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        };
        target: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            mapping?: Record<string, string> | undefined;
            batchSize?: number | undefined;
        };
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        schedule?: {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        } | undefined;
    }>;
    description: z.ZodOptional<z.ZodString>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    name: string;
    config: {
        source: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        };
        target: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            batchSize: number;
            mapping?: Record<string, string> | undefined;
        };
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        schedule?: {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        } | undefined;
    };
    tags: string[];
    integrationId: string;
    description?: string | undefined;
}, {
    name: string;
    config: {
        source: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        };
        target: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            mapping?: Record<string, string> | undefined;
            batchSize?: number | undefined;
        };
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        schedule?: {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        } | undefined;
    };
    integrationId: string;
    description?: string | undefined;
    tags?: string[] | undefined;
}>;
export declare const UpdateSyncJobRequestSchema: z.ZodObject<{
    name: z.ZodOptional<z.ZodString>;
    config: z.ZodOptional<z.ZodObject<{
        source: z.ZodObject<{
            type: z.ZodEnum<["database", "api", "file", "message-queue"]>;
            connection: z.ZodRecord<z.ZodString, z.ZodUnknown>;
            query: z.ZodOptional<z.ZodString>;
            filters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        }, "strip", z.ZodTypeAny, {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        }, {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        }>;
        target: z.ZodObject<{
            type: z.ZodEnum<["database", "api", "file", "message-queue"]>;
            connection: z.ZodRecord<z.ZodString, z.ZodUnknown>;
            mapping: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
            batchSize: z.ZodDefault<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            batchSize: number;
            mapping?: Record<string, string> | undefined;
        }, {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            mapping?: Record<string, string> | undefined;
            batchSize?: number | undefined;
        }>;
        schedule: z.ZodOptional<z.ZodObject<{
            cron: z.ZodOptional<z.ZodString>;
            interval: z.ZodOptional<z.ZodNumber>;
            timezone: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        }, {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        }>>;
        retryPolicy: z.ZodOptional<z.ZodObject<{
            maxRetries: z.ZodNumber;
            backoffMs: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            maxRetries: number;
            backoffMs: number;
        }, {
            maxRetries: number;
            backoffMs: number;
        }>>;
    }, "strip", z.ZodTypeAny, {
        source: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        };
        target: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            batchSize: number;
            mapping?: Record<string, string> | undefined;
        };
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        schedule?: {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        } | undefined;
    }, {
        source: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        };
        target: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            mapping?: Record<string, string> | undefined;
            batchSize?: number | undefined;
        };
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        schedule?: {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        } | undefined;
    }>>;
    description: z.ZodOptional<z.ZodString>;
    tags: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    status: z.ZodOptional<z.ZodEnum<["pending", "running", "completed", "failed", "cancelled"]>>;
    isActive: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    name?: string | undefined;
    config?: {
        source: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        };
        target: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            batchSize: number;
            mapping?: Record<string, string> | undefined;
        };
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        schedule?: {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        } | undefined;
    } | undefined;
    status?: "pending" | "running" | "completed" | "failed" | "cancelled" | undefined;
    description?: string | undefined;
    tags?: string[] | undefined;
    isActive?: boolean | undefined;
}, {
    name?: string | undefined;
    config?: {
        source: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            query?: string | undefined;
            filters?: Record<string, unknown> | undefined;
        };
        target: {
            type: "api" | "file" | "database" | "message-queue";
            connection: Record<string, unknown>;
            mapping?: Record<string, string> | undefined;
            batchSize?: number | undefined;
        };
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        schedule?: {
            cron?: string | undefined;
            interval?: number | undefined;
            timezone?: string | undefined;
        } | undefined;
    } | undefined;
    status?: "pending" | "running" | "completed" | "failed" | "cancelled" | undefined;
    description?: string | undefined;
    tags?: string[] | undefined;
    isActive?: boolean | undefined;
}>;
export declare const ExecuteSyncJobRequestSchema: z.ZodObject<{
    force: z.ZodDefault<z.ZodBoolean>;
    batchSize: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    force: boolean;
    batchSize?: number | undefined;
}, {
    batchSize?: number | undefined;
    force?: boolean | undefined;
}>;
export declare const SyncJobQuerySchema: z.ZodObject<{
    page: z.ZodDefault<z.ZodNumber>;
    limit: z.ZodDefault<z.ZodNumber>;
    sortBy: z.ZodOptional<z.ZodString>;
    sortOrder: z.ZodDefault<z.ZodEnum<["asc", "desc"]>>;
    integrationId: z.ZodOptional<z.ZodString>;
    status: z.ZodOptional<z.ZodEnum<["pending", "running", "completed", "failed", "cancelled"]>>;
    isActive: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    page: number;
    limit: number;
    sortOrder: "asc" | "desc";
    status?: "pending" | "running" | "completed" | "failed" | "cancelled" | undefined;
    isActive?: boolean | undefined;
    sortBy?: string | undefined;
    integrationId?: string | undefined;
}, {
    status?: "pending" | "running" | "completed" | "failed" | "cancelled" | undefined;
    isActive?: boolean | undefined;
    page?: number | undefined;
    limit?: number | undefined;
    sortBy?: string | undefined;
    sortOrder?: "asc" | "desc" | undefined;
    integrationId?: string | undefined;
}>;
export declare const SyncJobResponseSchema: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    integrationId: z.ZodString;
    config: z.ZodRecord<z.ZodString, z.ZodUnknown>;
    status: z.ZodEnum<["pending", "running", "completed", "failed", "cancelled"]>;
    lastRun: z.ZodNullable<z.ZodString>;
    nextRun: z.ZodNullable<z.ZodString>;
    recordsProcessed: z.ZodNumber;
    errorMessage: z.ZodNullable<z.ZodString>;
    isActive: z.ZodBoolean;
    description: z.ZodNullable<z.ZodString>;
    tags: z.ZodArray<z.ZodString, "many">;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodString;
    updatedBy: z.ZodString;
}, "strip", z.ZodTypeAny, {
    name: string;
    config: Record<string, unknown>;
    status: "pending" | "running" | "completed" | "failed" | "cancelled";
    description: string | null;
    tags: string[];
    isActive: boolean;
    id: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    updatedBy: string;
    integrationId: string;
    lastRun: string | null;
    nextRun: string | null;
    recordsProcessed: number;
    errorMessage: string | null;
}, {
    name: string;
    config: Record<string, unknown>;
    status: "pending" | "running" | "completed" | "failed" | "cancelled";
    description: string | null;
    tags: string[];
    isActive: boolean;
    id: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    updatedBy: string;
    integrationId: string;
    lastRun: string | null;
    nextRun: string | null;
    recordsProcessed: number;
    errorMessage: string | null;
}>;
export declare const SyncJobListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        name: z.ZodString;
        integrationId: z.ZodString;
        config: z.ZodRecord<z.ZodString, z.ZodUnknown>;
        status: z.ZodEnum<["pending", "running", "completed", "failed", "cancelled"]>;
        lastRun: z.ZodNullable<z.ZodString>;
        nextRun: z.ZodNullable<z.ZodString>;
        recordsProcessed: z.ZodNumber;
        errorMessage: z.ZodNullable<z.ZodString>;
        isActive: z.ZodBoolean;
        description: z.ZodNullable<z.ZodString>;
        tags: z.ZodArray<z.ZodString, "many">;
        createdAt: z.ZodString;
        updatedAt: z.ZodString;
        createdBy: z.ZodString;
        updatedBy: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        name: string;
        config: Record<string, unknown>;
        status: "pending" | "running" | "completed" | "failed" | "cancelled";
        description: string | null;
        tags: string[];
        isActive: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        createdBy: string;
        updatedBy: string;
        integrationId: string;
        lastRun: string | null;
        nextRun: string | null;
        recordsProcessed: number;
        errorMessage: string | null;
    }, {
        name: string;
        config: Record<string, unknown>;
        status: "pending" | "running" | "completed" | "failed" | "cancelled";
        description: string | null;
        tags: string[];
        isActive: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        createdBy: string;
        updatedBy: string;
        integrationId: string;
        lastRun: string | null;
        nextRun: string | null;
        recordsProcessed: number;
        errorMessage: string | null;
    }>, "many">;
    pagination: z.ZodObject<{
        page: z.ZodNumber;
        limit: z.ZodNumber;
        total: z.ZodNumber;
        totalPages: z.ZodNumber;
        hasNext: z.ZodBoolean;
        hasPrev: z.ZodBoolean;
    }, "strip", z.ZodTypeAny, {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
        hasNext: boolean;
        hasPrev: boolean;
    }, {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
        hasNext: boolean;
        hasPrev: boolean;
    }>;
}, "strip", z.ZodTypeAny, {
    data: {
        name: string;
        config: Record<string, unknown>;
        status: "pending" | "running" | "completed" | "failed" | "cancelled";
        description: string | null;
        tags: string[];
        isActive: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        createdBy: string;
        updatedBy: string;
        integrationId: string;
        lastRun: string | null;
        nextRun: string | null;
        recordsProcessed: number;
        errorMessage: string | null;
    }[];
    pagination: {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
        hasNext: boolean;
        hasPrev: boolean;
    };
}, {
    data: {
        name: string;
        config: Record<string, unknown>;
        status: "pending" | "running" | "completed" | "failed" | "cancelled";
        description: string | null;
        tags: string[];
        isActive: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        createdBy: string;
        updatedBy: string;
        integrationId: string;
        lastRun: string | null;
        nextRun: string | null;
        recordsProcessed: number;
        errorMessage: string | null;
    }[];
    pagination: {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
        hasNext: boolean;
        hasPrev: boolean;
    };
}>;
export declare const SyncJobExecutionResponseSchema: z.ZodObject<{
    success: z.ZodBoolean;
    recordsProcessed: z.ZodNumber;
    duration: z.ZodNumber;
    error: z.ZodOptional<z.ZodString>;
    nextRun: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    success: boolean;
    recordsProcessed: number;
    duration: number;
    error?: string | undefined;
    nextRun?: string | undefined;
}, {
    success: boolean;
    recordsProcessed: number;
    duration: number;
    error?: string | undefined;
    nextRun?: string | undefined;
}>;
export type CreateSyncJobRequest = z.infer<typeof CreateSyncJobRequestSchema>;
export type UpdateSyncJobRequest = z.infer<typeof UpdateSyncJobRequestSchema>;
export type ExecuteSyncJobRequest = z.infer<typeof ExecuteSyncJobRequestSchema>;
export type SyncJobQuery = z.infer<typeof SyncJobQuerySchema>;
export type SyncJobResponse = z.infer<typeof SyncJobResponseSchema>;
export type SyncJobListResponse = z.infer<typeof SyncJobListResponseSchema>;
export type SyncJobExecutionResponse = z.infer<typeof SyncJobExecutionResponseSchema>;
export declare function validateCreateSyncJobRequest(data: unknown): CreateSyncJobRequest;
export declare function validateUpdateSyncJobRequest(data: unknown): UpdateSyncJobRequest;
export declare function validateExecuteSyncJobRequest(data: unknown): ExecuteSyncJobRequest;
export declare function validateSyncJobQuery(data: unknown): SyncJobQuery;
//# sourceMappingURL=sync-job-dto.d.ts.map