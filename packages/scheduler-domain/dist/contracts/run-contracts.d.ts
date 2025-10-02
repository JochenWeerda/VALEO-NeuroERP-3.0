import { z } from 'zod';
declare const RunMetricsSchema: z.ZodObject<{
    latencyMs: z.ZodOptional<z.ZodNumber>;
    durationMs: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    latencyMs?: number | undefined;
    durationMs?: number | undefined;
}, {
    latencyMs?: number | undefined;
    durationMs?: number | undefined;
}>;
declare const RunQuerySchema: z.ZodObject<{
    status: z.ZodOptional<z.ZodEnum<["Pending", "Running", "Succeeded", "Failed", "Missed", "Dead"]>>;
    scheduleId: z.ZodOptional<z.ZodString>;
    jobId: z.ZodOptional<z.ZodString>;
    workerId: z.ZodOptional<z.ZodString>;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
    pageSize: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    status?: "Pending" | "Running" | "Succeeded" | "Failed" | "Missed" | "Dead" | undefined;
    from?: string | undefined;
    to?: string | undefined;
    scheduleId?: string | undefined;
    jobId?: string | undefined;
    workerId?: string | undefined;
}, {
    status?: "Pending" | "Running" | "Succeeded" | "Failed" | "Missed" | "Dead" | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    scheduleId?: string | undefined;
    jobId?: string | undefined;
    workerId?: string | undefined;
}>;
declare const RunResponseSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    scheduleId: z.ZodNullable<z.ZodString>;
    jobId: z.ZodNullable<z.ZodString>;
    dedupeKey: z.ZodNullable<z.ZodString>;
    status: z.ZodEnum<["Pending", "Running", "Succeeded", "Failed", "Missed", "Dead"]>;
    startedAt: z.ZodNullable<z.ZodString>;
    finishedAt: z.ZodNullable<z.ZodString>;
    attempt: z.ZodNumber;
    error: z.ZodNullable<z.ZodString>;
    metrics: z.ZodNullable<z.ZodObject<{
        latencyMs: z.ZodNullable<z.ZodNumber>;
        durationMs: z.ZodNullable<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        latencyMs: number | null;
        durationMs: number | null;
    }, {
        latencyMs: number | null;
        durationMs: number | null;
    }>>;
    workerId: z.ZodNullable<z.ZodString>;
    payload: z.ZodNullable<z.ZodRecord<z.ZodString, z.ZodAny>>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "Pending" | "Running" | "Succeeded" | "Failed" | "Missed" | "Dead";
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    payload: Record<string, any> | null;
    scheduleId: string | null;
    jobId: string | null;
    workerId: string | null;
    dedupeKey: string | null;
    startedAt: string | null;
    finishedAt: string | null;
    attempt: number;
    error: string | null;
    metrics: {
        latencyMs: number | null;
        durationMs: number | null;
    } | null;
}, {
    status: "Pending" | "Running" | "Succeeded" | "Failed" | "Missed" | "Dead";
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    payload: Record<string, any> | null;
    scheduleId: string | null;
    jobId: string | null;
    workerId: string | null;
    dedupeKey: string | null;
    startedAt: string | null;
    finishedAt: string | null;
    attempt: number;
    error: string | null;
    metrics: {
        latencyMs: number | null;
        durationMs: number | null;
    } | null;
}>;
declare const RunListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodString;
        scheduleId: z.ZodNullable<z.ZodString>;
        jobId: z.ZodNullable<z.ZodString>;
        dedupeKey: z.ZodNullable<z.ZodString>;
        status: z.ZodEnum<["Pending", "Running", "Succeeded", "Failed", "Missed", "Dead"]>;
        startedAt: z.ZodNullable<z.ZodString>;
        finishedAt: z.ZodNullable<z.ZodString>;
        attempt: z.ZodNumber;
        error: z.ZodNullable<z.ZodString>;
        metrics: z.ZodNullable<z.ZodObject<{
            latencyMs: z.ZodNullable<z.ZodNumber>;
            durationMs: z.ZodNullable<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            latencyMs: number | null;
            durationMs: number | null;
        }, {
            latencyMs: number | null;
            durationMs: number | null;
        }>>;
        workerId: z.ZodNullable<z.ZodString>;
        payload: z.ZodNullable<z.ZodRecord<z.ZodString, z.ZodAny>>;
        createdAt: z.ZodString;
        updatedAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        status: "Pending" | "Running" | "Succeeded" | "Failed" | "Missed" | "Dead";
        id: string;
        tenantId: string;
        createdAt: string;
        updatedAt: string;
        payload: Record<string, any> | null;
        scheduleId: string | null;
        jobId: string | null;
        workerId: string | null;
        dedupeKey: string | null;
        startedAt: string | null;
        finishedAt: string | null;
        attempt: number;
        error: string | null;
        metrics: {
            latencyMs: number | null;
            durationMs: number | null;
        } | null;
    }, {
        status: "Pending" | "Running" | "Succeeded" | "Failed" | "Missed" | "Dead";
        id: string;
        tenantId: string;
        createdAt: string;
        updatedAt: string;
        payload: Record<string, any> | null;
        scheduleId: string | null;
        jobId: string | null;
        workerId: string | null;
        dedupeKey: string | null;
        startedAt: string | null;
        finishedAt: string | null;
        attempt: number;
        error: string | null;
        metrics: {
            latencyMs: number | null;
            durationMs: number | null;
        } | null;
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
        status: "Pending" | "Running" | "Succeeded" | "Failed" | "Missed" | "Dead";
        id: string;
        tenantId: string;
        createdAt: string;
        updatedAt: string;
        payload: Record<string, any> | null;
        scheduleId: string | null;
        jobId: string | null;
        workerId: string | null;
        dedupeKey: string | null;
        startedAt: string | null;
        finishedAt: string | null;
        attempt: number;
        error: string | null;
        metrics: {
            latencyMs: number | null;
            durationMs: number | null;
        } | null;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}, {
    data: {
        status: "Pending" | "Running" | "Succeeded" | "Failed" | "Missed" | "Dead";
        id: string;
        tenantId: string;
        createdAt: string;
        updatedAt: string;
        payload: Record<string, any> | null;
        scheduleId: string | null;
        jobId: string | null;
        workerId: string | null;
        dedupeKey: string | null;
        startedAt: string | null;
        finishedAt: string | null;
        attempt: number;
        error: string | null;
        metrics: {
            latencyMs: number | null;
            durationMs: number | null;
        } | null;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
declare const RetryRunInputSchema: z.ZodObject<{
    reason: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    reason?: string | undefined;
}, {
    reason?: string | undefined;
}>;
declare const CancelRunInputSchema: z.ZodObject<{
    reason: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    reason?: string | undefined;
}, {
    reason?: string | undefined;
}>;
export { RunQuerySchema, RunResponseSchema, RunListResponseSchema, RetryRunInputSchema, CancelRunInputSchema, RunMetricsSchema, };
//# sourceMappingURL=run-contracts.d.ts.map