import { z } from 'zod';
import {
  CreateInteractionInputSchema,
  InteractionSchema,
  InteractionType,
  UpdateInteractionInputSchema
} from '../domain/entities';

// OpenAPI schema for Interaction Type
export const InteractionTypeContractSchema = z.enum([
  InteractionType.CALL,
  InteractionType.EMAIL,
  InteractionType.VISIT,
  InteractionType.NOTE
]).meta({
  description: 'Type of customer interaction',
  example: InteractionType.CALL
});

// OpenAPI schema for Attachment
export const AttachmentContractSchema = z.object({
  id: z.string().guid(),
  filename: z.string(),
  url: z.string().url(),
  size: z.number().nonnegative(),
  mimeType: z.string()
}).meta({
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
export const CreateInteractionContractSchema = CreateInteractionInputSchema.meta({
  description: 'Interaction creation data',
  example: {
    customerId: '550e8400-e29b-41d4-a716-446655440000',
    contactId: '550e8400-e29b-41d4-a716-446655440001',
    type: InteractionType.CALL,
    subject: 'Follow-up on proposal',
    content: 'Discussed implementation timeline and next steps for the enterprise software project.',
    occurredAt: '2024-01-15T14:30:00.000Z',
    createdBy: '550e8400-e29b-41d4-a716-446655440002',
    attachments: []
  }
});

// OpenAPI schema for Update Interaction
export const UpdateInteractionContractSchema = UpdateInteractionInputSchema.meta({
  description: 'Interaction update data',
  example: {
    subject: 'Updated: Follow-up on proposal',
    content: 'Added additional requirements and adjusted timeline.'
  }
});

// OpenAPI schema for Interaction Response
export const InteractionResponseContractSchema = InteractionSchema.omit({ tenantId: true }).meta({
  description: 'Interaction information',
  example: {
    id: '550e8400-e29b-41d4-a716-446655440005',
    customerId: '550e8400-e29b-41d4-a716-446655440000',
    contactId: '550e8400-e29b-41d4-a716-446655440001',
    type: InteractionType.CALL,
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
export const InteractionQueryContractSchema = z.object({
  customerId: z.string().guid(),
  type: z.enum([
    InteractionType.CALL,
    InteractionType.EMAIL,
    InteractionType.VISIT,
    InteractionType.NOTE
  ]).optional(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional(),
  page: z.string().transform(Number).optional().prefault('1'),
  pageSize: z.string().transform(Number).optional().prefault('20')
}).meta({
  description: 'Query parameters for interaction listing'
});

// Response schema for interaction list
export const InteractionListResponseContractSchema = z.object({
  data: z.array(InteractionResponseContractSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number()
  })
}).meta({
  description: 'Paginated interaction list response'
});