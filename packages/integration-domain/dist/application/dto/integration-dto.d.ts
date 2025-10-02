/**
 * Integration DTOs and Validation Schemas
 */
import { z } from 'zod';
export declare const CreateIntegrationRequestSchema: z.ZodObject<{
    name: z.ZodString;
    type: z.ZodEnum<["api", "webhook", "file", "database", "message-queue"]>;
    config: z.ZodRecord<z.ZodString, z.ZodUnknown>;
    description: z.ZodOptional<z.ZodString>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    name: string;
    type: "api" | "webhook" | "file" | "database" | "message-queue";
    config: Record<string, unknown>;
    tags: string[];
    description?: string | undefined;
}, {
    name: string;
    type: "api" | "webhook" | "file" | "database" | "message-queue";
    config: Record<string, unknown>;
    description?: string | undefined;
    tags?: string[] | undefined;
}>;
export declare const UpdateIntegrationRequestSchema: z.ZodObject<{
    name: z.ZodOptional<z.ZodString>;
    config: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    description: z.ZodOptional<z.ZodString>;
    tags: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    status: z.ZodOptional<z.ZodEnum<["active", "inactive", "pending", "error"]>>;
    isActive: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    name?: string | undefined;
    config?: Record<string, unknown> | undefined;
    status?: "active" | "inactive" | "pending" | "error" | undefined;
    description?: string | undefined;
    tags?: string[] | undefined;
    isActive?: boolean | undefined;
}, {
    name?: string | undefined;
    config?: Record<string, unknown> | undefined;
    status?: "active" | "inactive" | "pending" | "error" | undefined;
    description?: string | undefined;
    tags?: string[] | undefined;
    isActive?: boolean | undefined;
}>;
export declare const IntegrationQuerySchema: z.ZodObject<{
    page: z.ZodDefault<z.ZodNumber>;
    limit: z.ZodDefault<z.ZodNumber>;
    sortBy: z.ZodOptional<z.ZodString>;
    sortOrder: z.ZodDefault<z.ZodEnum<["asc", "desc"]>>;
    type: z.ZodOptional<z.ZodEnum<["api", "webhook", "file", "database", "message-queue"]>>;
    status: z.ZodOptional<z.ZodEnum<["active", "inactive", "pending", "error"]>>;
    tags: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    isActive: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    page: number;
    limit: number;
    sortOrder: "asc" | "desc";
    type?: "api" | "webhook" | "file" | "database" | "message-queue" | undefined;
    status?: "active" | "inactive" | "pending" | "error" | undefined;
    tags?: string[] | undefined;
    isActive?: boolean | undefined;
    sortBy?: string | undefined;
}, {
    type?: "api" | "webhook" | "file" | "database" | "message-queue" | undefined;
    status?: "active" | "inactive" | "pending" | "error" | undefined;
    tags?: string[] | undefined;
    isActive?: boolean | undefined;
    page?: number | undefined;
    limit?: number | undefined;
    sortBy?: string | undefined;
    sortOrder?: "asc" | "desc" | undefined;
}>;
export declare const IntegrationResponseSchema: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    type: z.ZodEnum<["api", "webhook", "file", "database", "message-queue"]>;
    status: z.ZodEnum<["active", "inactive", "pending", "error"]>;
    config: z.ZodRecord<z.ZodString, z.ZodUnknown>;
    description: z.ZodNullable<z.ZodString>;
    tags: z.ZodArray<z.ZodString, "many">;
    isActive: z.ZodBoolean;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodString;
    updatedBy: z.ZodString;
}, "strip", z.ZodTypeAny, {
    name: string;
    type: "api" | "webhook" | "file" | "database" | "message-queue";
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
}, {
    name: string;
    type: "api" | "webhook" | "file" | "database" | "message-queue";
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
}>;
export declare const IntegrationListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        name: z.ZodString;
        type: z.ZodEnum<["api", "webhook", "file", "database", "message-queue"]>;
        status: z.ZodEnum<["active", "inactive", "pending", "error"]>;
        config: z.ZodRecord<z.ZodString, z.ZodUnknown>;
        description: z.ZodNullable<z.ZodString>;
        tags: z.ZodArray<z.ZodString, "many">;
        isActive: z.ZodBoolean;
        createdAt: z.ZodString;
        updatedAt: z.ZodString;
        createdBy: z.ZodString;
        updatedBy: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        name: string;
        type: "api" | "webhook" | "file" | "database" | "message-queue";
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
    }, {
        name: string;
        type: "api" | "webhook" | "file" | "database" | "message-queue";
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
        type: "api" | "webhook" | "file" | "database" | "message-queue";
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
        type: "api" | "webhook" | "file" | "database" | "message-queue";
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
export type CreateIntegrationRequest = z.infer<typeof CreateIntegrationRequestSchema>;
export type UpdateIntegrationRequest = z.infer<typeof UpdateIntegrationRequestSchema>;
export type IntegrationQuery = z.infer<typeof IntegrationQuerySchema>;
export type IntegrationResponse = z.infer<typeof IntegrationResponseSchema>;
export type IntegrationListResponse = z.infer<typeof IntegrationListResponseSchema>;
export declare function validateCreateIntegrationRequest(data: unknown): CreateIntegrationRequest;
export declare function validateUpdateIntegrationRequest(data: unknown): UpdateIntegrationRequest;
export declare function validateIntegrationQuery(data: unknown): IntegrationQuery;
//# sourceMappingURL=integration-dto.d.ts.map