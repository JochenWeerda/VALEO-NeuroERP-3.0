/**
 * Webhook DTOs and Validation Schemas
 */
import { z } from 'zod';
export declare const CreateWebhookRequestSchema: z.ZodObject<{
    name: z.ZodString;
    integrationId: z.ZodString;
    config: z.ZodObject<{
        url: z.ZodString;
        method: z.ZodEnum<["GET", "POST", "PUT", "PATCH", "DELETE"]>;
        headers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
        timeout: z.ZodOptional<z.ZodNumber>;
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
        authentication: z.ZodOptional<z.ZodObject<{
            type: z.ZodEnum<["bearer", "basic", "api-key"]>;
            credentials: z.ZodRecord<z.ZodString, z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        }, {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        }>>;
    }, "strip", z.ZodTypeAny, {
        url: string;
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        headers?: Record<string, string> | undefined;
        timeout?: number | undefined;
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        authentication?: {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        } | undefined;
    }, {
        url: string;
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        headers?: Record<string, string> | undefined;
        timeout?: number | undefined;
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        authentication?: {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        } | undefined;
    }>;
    events: z.ZodArray<z.ZodString, "many">;
    description: z.ZodOptional<z.ZodString>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    name: string;
    config: {
        url: string;
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        headers?: Record<string, string> | undefined;
        timeout?: number | undefined;
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        authentication?: {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        } | undefined;
    };
    tags: string[];
    integrationId: string;
    events: string[];
    description?: string | undefined;
}, {
    name: string;
    config: {
        url: string;
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        headers?: Record<string, string> | undefined;
        timeout?: number | undefined;
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        authentication?: {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        } | undefined;
    };
    integrationId: string;
    events: string[];
    description?: string | undefined;
    tags?: string[] | undefined;
}>;
export declare const UpdateWebhookRequestSchema: z.ZodObject<{
    name: z.ZodOptional<z.ZodString>;
    config: z.ZodOptional<z.ZodObject<{
        url: z.ZodString;
        method: z.ZodEnum<["GET", "POST", "PUT", "PATCH", "DELETE"]>;
        headers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
        timeout: z.ZodOptional<z.ZodNumber>;
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
        authentication: z.ZodOptional<z.ZodObject<{
            type: z.ZodEnum<["bearer", "basic", "api-key"]>;
            credentials: z.ZodRecord<z.ZodString, z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        }, {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        }>>;
    }, "strip", z.ZodTypeAny, {
        url: string;
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        headers?: Record<string, string> | undefined;
        timeout?: number | undefined;
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        authentication?: {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        } | undefined;
    }, {
        url: string;
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        headers?: Record<string, string> | undefined;
        timeout?: number | undefined;
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        authentication?: {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        } | undefined;
    }>>;
    events: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    description: z.ZodOptional<z.ZodString>;
    tags: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    status: z.ZodOptional<z.ZodEnum<["active", "inactive", "pending", "error"]>>;
    isActive: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    name?: string | undefined;
    config?: {
        url: string;
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        headers?: Record<string, string> | undefined;
        timeout?: number | undefined;
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        authentication?: {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        } | undefined;
    } | undefined;
    status?: "active" | "inactive" | "pending" | "error" | undefined;
    description?: string | undefined;
    tags?: string[] | undefined;
    isActive?: boolean | undefined;
    events?: string[] | undefined;
}, {
    name?: string | undefined;
    config?: {
        url: string;
        method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
        headers?: Record<string, string> | undefined;
        timeout?: number | undefined;
        retryPolicy?: {
            maxRetries: number;
            backoffMs: number;
        } | undefined;
        authentication?: {
            type: "bearer" | "basic" | "api-key";
            credentials: Record<string, string>;
        } | undefined;
    } | undefined;
    status?: "active" | "inactive" | "pending" | "error" | undefined;
    description?: string | undefined;
    tags?: string[] | undefined;
    isActive?: boolean | undefined;
    events?: string[] | undefined;
}>;
export declare const TriggerWebhookRequestSchema: z.ZodObject<{
    payload: z.ZodRecord<z.ZodString, z.ZodUnknown>;
    event: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    payload: Record<string, unknown>;
    event?: string | undefined;
}, {
    payload: Record<string, unknown>;
    event?: string | undefined;
}>;
export declare const WebhookQuerySchema: z.ZodObject<{
    page: z.ZodDefault<z.ZodNumber>;
    limit: z.ZodDefault<z.ZodNumber>;
    sortBy: z.ZodOptional<z.ZodString>;
    sortOrder: z.ZodDefault<z.ZodEnum<["asc", "desc"]>>;
    integrationId: z.ZodOptional<z.ZodString>;
    event: z.ZodOptional<z.ZodString>;
    status: z.ZodOptional<z.ZodEnum<["active", "inactive", "pending", "error"]>>;
    isActive: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    page: number;
    limit: number;
    sortOrder: "asc" | "desc";
    status?: "active" | "inactive" | "pending" | "error" | undefined;
    isActive?: boolean | undefined;
    sortBy?: string | undefined;
    integrationId?: string | undefined;
    event?: string | undefined;
}, {
    status?: "active" | "inactive" | "pending" | "error" | undefined;
    isActive?: boolean | undefined;
    page?: number | undefined;
    limit?: number | undefined;
    sortBy?: string | undefined;
    sortOrder?: "asc" | "desc" | undefined;
    integrationId?: string | undefined;
    event?: string | undefined;
}>;
export declare const WebhookResponseSchema: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    integrationId: z.ZodString;
    config: z.ZodRecord<z.ZodString, z.ZodUnknown>;
    events: z.ZodArray<z.ZodString, "many">;
    status: z.ZodEnum<["active", "inactive", "pending", "error"]>;
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
    status: "active" | "inactive" | "pending" | "error";
    description: string | null;
    tags: string[];
    isActive: boolean;
    id: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    updatedBy: string;
    integrationId: string;
    events: string[];
}, {
    name: string;
    config: Record<string, unknown>;
    status: "active" | "inactive" | "pending" | "error";
    description: string | null;
    tags: string[];
    isActive: boolean;
    id: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    updatedBy: string;
    integrationId: string;
    events: string[];
}>;
export declare const WebhookListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        name: z.ZodString;
        integrationId: z.ZodString;
        config: z.ZodRecord<z.ZodString, z.ZodUnknown>;
        events: z.ZodArray<z.ZodString, "many">;
        status: z.ZodEnum<["active", "inactive", "pending", "error"]>;
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
        status: "active" | "inactive" | "pending" | "error";
        description: string | null;
        tags: string[];
        isActive: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        createdBy: string;
        updatedBy: string;
        integrationId: string;
        events: string[];
    }, {
        name: string;
        config: Record<string, unknown>;
        status: "active" | "inactive" | "pending" | "error";
        description: string | null;
        tags: string[];
        isActive: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        createdBy: string;
        updatedBy: string;
        integrationId: string;
        events: string[];
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
        status: "active" | "inactive" | "pending" | "error";
        description: string | null;
        tags: string[];
        isActive: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        createdBy: string;
        updatedBy: string;
        integrationId: string;
        events: string[];
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
        status: "active" | "inactive" | "pending" | "error";
        description: string | null;
        tags: string[];
        isActive: boolean;
        id: string;
        createdAt: string;
        updatedAt: string;
        createdBy: string;
        updatedBy: string;
        integrationId: string;
        events: string[];
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
export declare const WebhookTriggerResponseSchema: z.ZodObject<{
    success: z.ZodBoolean;
    statusCode: z.ZodOptional<z.ZodNumber>;
    response: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    error: z.ZodOptional<z.ZodString>;
    executionTime: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    success: boolean;
    executionTime: number;
    error?: string | undefined;
    statusCode?: number | undefined;
    response?: Record<string, unknown> | undefined;
}, {
    success: boolean;
    executionTime: number;
    error?: string | undefined;
    statusCode?: number | undefined;
    response?: Record<string, unknown> | undefined;
}>;
export type CreateWebhookRequest = z.infer<typeof CreateWebhookRequestSchema>;
export type UpdateWebhookRequest = z.infer<typeof UpdateWebhookRequestSchema>;
export type TriggerWebhookRequest = z.infer<typeof TriggerWebhookRequestSchema>;
export type WebhookQuery = z.infer<typeof WebhookQuerySchema>;
export type WebhookResponse = z.infer<typeof WebhookResponseSchema>;
export type WebhookListResponse = z.infer<typeof WebhookListResponseSchema>;
export type WebhookTriggerResponse = z.infer<typeof WebhookTriggerResponseSchema>;
export declare function validateCreateWebhookRequest(data: unknown): CreateWebhookRequest;
export declare function validateUpdateWebhookRequest(data: unknown): UpdateWebhookRequest;
export declare function validateTriggerWebhookRequest(data: unknown): TriggerWebhookRequest;
export declare function validateWebhookQuery(data: unknown): WebhookQuery;
//# sourceMappingURL=webhook-dto.d.ts.map