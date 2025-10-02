/**
 * Integration DTOs and Validation Schemas
 */
import { z } from 'zod';
// Base schemas
const IntegrationTypeSchema = z.enum(['api', 'webhook', 'file', 'database', 'message-queue']);
const EntityStatusSchema = z.enum(['active', 'inactive', 'pending', 'error']);
// Request DTOs
export const CreateIntegrationRequestSchema = z.object({
    name: z.string().min(1).max(255),
    type: IntegrationTypeSchema,
    config: z.record(z.unknown()),
    description: z.string().optional(),
    tags: z.array(z.string()).default([])
});
export const UpdateIntegrationRequestSchema = z.object({
    name: z.string().min(1).max(255).optional(),
    config: z.record(z.unknown()).optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).optional(),
    status: EntityStatusSchema.optional(),
    isActive: z.boolean().optional()
});
export const IntegrationQuerySchema = z.object({
    page: z.number().min(1).default(1),
    limit: z.number().min(1).max(100).default(10),
    sortBy: z.string().optional(),
    sortOrder: z.enum(['asc', 'desc']).default('desc'),
    type: IntegrationTypeSchema.optional(),
    status: EntityStatusSchema.optional(),
    tags: z.array(z.string()).optional(),
    isActive: z.boolean().optional()
});
// Response DTOs
export const IntegrationResponseSchema = z.object({
    id: z.string(),
    name: z.string(),
    type: IntegrationTypeSchema,
    status: EntityStatusSchema,
    config: z.record(z.unknown()),
    description: z.string().nullable(),
    tags: z.array(z.string()),
    isActive: z.boolean(),
    createdAt: z.string(),
    updatedAt: z.string(),
    createdBy: z.string(),
    updatedBy: z.string()
});
export const IntegrationListResponseSchema = z.object({
    data: z.array(IntegrationResponseSchema),
    pagination: z.object({
        page: z.number(),
        limit: z.number(),
        total: z.number(),
        totalPages: z.number(),
        hasNext: z.boolean(),
        hasPrev: z.boolean()
    })
});
// Validation functions
export function validateCreateIntegrationRequest(data) {
    return CreateIntegrationRequestSchema.parse(data);
}
export function validateUpdateIntegrationRequest(data) {
    return UpdateIntegrationRequestSchema.parse(data);
}
export function validateIntegrationQuery(data) {
    return IntegrationQuerySchema.parse(data);
}
//# sourceMappingURL=integration-dto.js.map