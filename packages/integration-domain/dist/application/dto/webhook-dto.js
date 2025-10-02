/**
 * Webhook DTOs and Validation Schemas
 */
import { z } from 'zod';
// Base schemas
const HttpMethodSchema = z.enum(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']);
const EntityStatusSchema = z.enum(['active', 'inactive', 'pending', 'error']);
// Request DTOs
export const CreateWebhookRequestSchema = z.object({
    name: z.string().min(1).max(255),
    integrationId: z.string().uuid(),
    config: z.object({
        url: z.string().url(),
        method: HttpMethodSchema,
        headers: z.record(z.string()).optional(),
        timeout: z.number().min(1000).max(300000).optional(),
        retryPolicy: z.object({
            maxRetries: z.number().min(0).max(10),
            backoffMs: z.number().min(100).max(60000)
        }).optional(),
        authentication: z.object({
            type: z.enum(['bearer', 'basic', 'api-key']),
            credentials: z.record(z.string())
        }).optional()
    }),
    events: z.array(z.string()).min(1),
    description: z.string().optional(),
    tags: z.array(z.string()).default([])
});
export const UpdateWebhookRequestSchema = z.object({
    name: z.string().min(1).max(255).optional(),
    config: z.object({
        url: z.string().url(),
        method: HttpMethodSchema,
        headers: z.record(z.string()).optional(),
        timeout: z.number().min(1000).max(300000).optional(),
        retryPolicy: z.object({
            maxRetries: z.number().min(0).max(10),
            backoffMs: z.number().min(100).max(60000)
        }).optional(),
        authentication: z.object({
            type: z.enum(['bearer', 'basic', 'api-key']),
            credentials: z.record(z.string())
        }).optional()
    }).optional(),
    events: z.array(z.string()).min(1).optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).optional(),
    status: EntityStatusSchema.optional(),
    isActive: z.boolean().optional()
});
export const TriggerWebhookRequestSchema = z.object({
    payload: z.record(z.unknown()),
    event: z.string().optional()
});
export const WebhookQuerySchema = z.object({
    page: z.number().min(1).default(1),
    limit: z.number().min(1).max(100).default(10),
    sortBy: z.string().optional(),
    sortOrder: z.enum(['asc', 'desc']).default('desc'),
    integrationId: z.string().uuid().optional(),
    event: z.string().optional(),
    status: EntityStatusSchema.optional(),
    isActive: z.boolean().optional()
});
// Response DTOs
export const WebhookResponseSchema = z.object({
    id: z.string(),
    name: z.string(),
    integrationId: z.string(),
    config: z.record(z.unknown()),
    events: z.array(z.string()),
    status: EntityStatusSchema,
    isActive: z.boolean(),
    description: z.string().nullable(),
    tags: z.array(z.string()),
    createdAt: z.string(),
    updatedAt: z.string(),
    createdBy: z.string(),
    updatedBy: z.string()
});
export const WebhookListResponseSchema = z.object({
    data: z.array(WebhookResponseSchema),
    pagination: z.object({
        page: z.number(),
        limit: z.number(),
        total: z.number(),
        totalPages: z.number(),
        hasNext: z.boolean(),
        hasPrev: z.boolean()
    })
});
export const WebhookTriggerResponseSchema = z.object({
    success: z.boolean(),
    statusCode: z.number().optional(),
    response: z.record(z.unknown()).optional(),
    error: z.string().optional(),
    executionTime: z.number()
});
// Validation functions
export function validateCreateWebhookRequest(data) {
    return CreateWebhookRequestSchema.parse(data);
}
export function validateUpdateWebhookRequest(data) {
    return UpdateWebhookRequestSchema.parse(data);
}
export function validateTriggerWebhookRequest(data) {
    return TriggerWebhookRequestSchema.parse(data);
}
export function validateWebhookQuery(data) {
    return WebhookQuerySchema.parse(data);
}
//# sourceMappingURL=webhook-dto.js.map