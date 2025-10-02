"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InteractionListResponseContractSchema = exports.InteractionQueryContractSchema = exports.InteractionResponseContractSchema = exports.UpdateInteractionContractSchema = exports.CreateInteractionContractSchema = exports.AttachmentContractSchema = exports.InteractionTypeContractSchema = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
const entities_1 = require("../domain/entities");
// OpenAPI schema for Interaction Type
exports.InteractionTypeContractSchema = (0, zod_openapi_1.zodOpenapi)(zod_1.z.enum([
    entities_1.InteractionType.CALL,
    entities_1.InteractionType.EMAIL,
    entities_1.InteractionType.VISIT,
    entities_1.InteractionType.NOTE
]), {
    description: 'Type of customer interaction',
    example: entities_1.InteractionType.CALL
});
// OpenAPI schema for Attachment
exports.AttachmentContractSchema = (0, zod_openapi_1.zodOpenapi)(zod_1.z.object({
    id: zod_1.z.string().uuid(),
    filename: zod_1.z.string(),
    url: zod_1.z.string().url(),
    size: zod_1.z.number().nonnegative(),
    mimeType: zod_1.z.string()
}), {
    description: 'File attachment information',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440004',
        filename: 'meeting-notes.pdf',
        url: 'https://cdn.example.com/attachments/meeting-notes.pdf',
        size: 245760,
        mimeType: 'application/pdf'
    }
});
// OpenAPI schema for Create Interaction
exports.CreateInteractionContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.CreateInteractionInputSchema, {
    description: 'Interaction creation data',
    example: {
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        contactId: '550e8400-e29b-41d4-a716-446655440001',
        type: entities_1.InteractionType.CALL,
        subject: 'Follow-up on proposal',
        content: 'Discussed implementation timeline and next steps for the enterprise software project.',
        occurredAt: '2024-01-15T14:30:00.000Z',
        createdBy: '550e8400-e29b-41d4-a716-446655440002',
        attachments: []
    }
});
// OpenAPI schema for Update Interaction
exports.UpdateInteractionContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.UpdateInteractionInputSchema, {
    description: 'Interaction update data',
    example: {
        subject: 'Updated: Follow-up on proposal',
        content: 'Added additional requirements and adjusted timeline.'
    }
});
// OpenAPI schema for Interaction Response
exports.InteractionResponseContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.InteractionSchema.omit({ tenantId: true }), {
    description: 'Interaction information',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440005',
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        contactId: '550e8400-e29b-41d4-a716-446655440001',
        type: entities_1.InteractionType.CALL,
        subject: 'Follow-up on proposal',
        content: 'Discussed implementation timeline and next steps for the enterprise software project.',
        occurredAt: '2024-01-15T14:30:00.000Z',
        createdBy: '550e8400-e29b-41d4-a716-446655440002',
        attachments: [],
        createdAt: '2024-01-15T14:35:00.000Z',
        updatedAt: '2024-01-15T14:35:00.000Z',
        version: 1
    }
});
// Query parameters for listing interactions
exports.InteractionQueryContractSchema = (0, zod_openapi_1.zodOpenapi)(zod_1.z.object({
    customerId: zod_1.z.string().uuid(),
    type: zod_1.z.enum([
        entities_1.InteractionType.CALL,
        entities_1.InteractionType.EMAIL,
        entities_1.InteractionType.VISIT,
        entities_1.InteractionType.NOTE
    ]).optional(),
    from: zod_1.z.string().datetime().optional(),
    to: zod_1.z.string().datetime().optional(),
    page: zod_1.z.string().transform(Number).optional().default('1'),
    pageSize: zod_1.z.string().transform(Number).optional().default('20')
}), {
    description: 'Query parameters for interaction listing'
});
// Response schema for interaction list
exports.InteractionListResponseContractSchema = (0, zod_openapi_1.zodOpenapi)(zod_1.z.object({
    data: zod_1.z.array(exports.InteractionResponseContractSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number()
    })
}), {
    description: 'Paginated interaction list response'
});
//# sourceMappingURL=interaction-contracts.js.map