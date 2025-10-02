import { z } from 'zod';
declare const WorkerCapabilitiesSchema: z.ZodObject<{
    queues: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    jobKeys: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    queues: string[];
    jobKeys: string[];
}, {
    queues?: string[] | undefined;
    jobKeys?: string[] | undefined;
}>;
declare const RegisterWorkerInputSchema: z.ZodObject<{
    name: z.ZodString;
    capabilities: z.ZodObject<{
        queues: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
        jobKeys: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    }, "strip", z.ZodTypeAny, {
        queues: string[];
        jobKeys: string[];
    }, {
        queues?: string[] | undefined;
        jobKeys?: string[] | undefined;
    }>;
    maxParallel: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    name: string;
    capabilities: {
        queues: string[];
        jobKeys: string[];
    };
    maxParallel: number;
}, {
    name: string;
    capabilities: {
        queues?: string[] | undefined;
        jobKeys?: string[] | undefined;
    };
    maxParallel?: number | undefined;
}>;
declare const WorkerHeartbeatInputSchema: z.ZodObject<{
    status: z.ZodOptional<z.ZodEnum<["Online", "Offline", "Maintenance"]>>;
}, "strip", z.ZodTypeAny, {
    status?: "Online" | "Offline" | "Maintenance" | undefined;
}, {
    status?: "Online" | "Offline" | "Maintenance" | undefined;
}>;
declare const WorkerQuerySchema: z.ZodObject<{
    status: z.ZodOptional<z.ZodEnum<["Online", "Offline", "Maintenance"]>>;
    name: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
    pageSize: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    status?: "Online" | "Offline" | "Maintenance" | undefined;
    name?: string | undefined;
}, {
    status?: "Online" | "Offline" | "Maintenance" | undefined;
    name?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
}>;
declare const WorkerResponseSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodNullable<z.ZodString>;
    name: z.ZodString;
    capabilities: z.ZodObject<{
        queues: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
        jobKeys: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    }, "strip", z.ZodTypeAny, {
        queues: string[];
        jobKeys: string[];
    }, {
        queues?: string[] | undefined;
        jobKeys?: string[] | undefined;
    }>;
    heartbeatAt: z.ZodString;
    status: z.ZodEnum<["Online", "Offline", "Maintenance"]>;
    maxParallel: z.ZodNumber;
    currentJobs: z.ZodNumber;
    version: z.ZodNumber;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "Online" | "Offline" | "Maintenance";
    name: string;
    id: string;
    tenantId: string | null;
    createdAt: string;
    updatedAt: string;
    version: number;
    capabilities: {
        queues: string[];
        jobKeys: string[];
    };
    maxParallel: number;
    heartbeatAt: string;
    currentJobs: number;
}, {
    status: "Online" | "Offline" | "Maintenance";
    name: string;
    id: string;
    tenantId: string | null;
    createdAt: string;
    updatedAt: string;
    version: number;
    capabilities: {
        queues?: string[] | undefined;
        jobKeys?: string[] | undefined;
    };
    maxParallel: number;
    heartbeatAt: string;
    currentJobs: number;
}>;
declare const WorkerListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodNullable<z.ZodString>;
        name: z.ZodString;
        capabilities: z.ZodObject<{
            queues: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
            jobKeys: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
        }, "strip", z.ZodTypeAny, {
            queues: string[];
            jobKeys: string[];
        }, {
            queues?: string[] | undefined;
            jobKeys?: string[] | undefined;
        }>;
        heartbeatAt: z.ZodString;
        status: z.ZodEnum<["Online", "Offline", "Maintenance"]>;
        maxParallel: z.ZodNumber;
        currentJobs: z.ZodNumber;
        version: z.ZodNumber;
        createdAt: z.ZodString;
        updatedAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        status: "Online" | "Offline" | "Maintenance";
        name: string;
        id: string;
        tenantId: string | null;
        createdAt: string;
        updatedAt: string;
        version: number;
        capabilities: {
            queues: string[];
            jobKeys: string[];
        };
        maxParallel: number;
        heartbeatAt: string;
        currentJobs: number;
    }, {
        status: "Online" | "Offline" | "Maintenance";
        name: string;
        id: string;
        tenantId: string | null;
        createdAt: string;
        updatedAt: string;
        version: number;
        capabilities: {
            queues?: string[] | undefined;
            jobKeys?: string[] | undefined;
        };
        maxParallel: number;
        heartbeatAt: string;
        currentJobs: number;
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
        status: "Online" | "Offline" | "Maintenance";
        name: string;
        id: string;
        tenantId: string | null;
        createdAt: string;
        updatedAt: string;
        version: number;
        capabilities: {
            queues: string[];
            jobKeys: string[];
        };
        maxParallel: number;
        heartbeatAt: string;
        currentJobs: number;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}, {
    data: {
        status: "Online" | "Offline" | "Maintenance";
        name: string;
        id: string;
        tenantId: string | null;
        createdAt: string;
        updatedAt: string;
        version: number;
        capabilities: {
            queues?: string[] | undefined;
            jobKeys?: string[] | undefined;
        };
        maxParallel: number;
        heartbeatAt: string;
        currentJobs: number;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
export { RegisterWorkerInputSchema, WorkerHeartbeatInputSchema, WorkerQuerySchema, WorkerResponseSchema, WorkerListResponseSchema, WorkerCapabilitiesSchema, };
//# sourceMappingURL=worker-contracts.d.ts.map