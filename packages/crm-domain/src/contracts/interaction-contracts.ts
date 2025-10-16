import { z } from 'zod';
// @ts-ignore - zod-openapi module
import { zodOpenapi } from 'zod-openapi';
import {
  InteractionSchema,
  CreateInteractionInputSchema,
  UpdateInteractionInputSchema,
  InteractionType
} from '../domain/entities';

// OpenAPI schema for Interaction Type
export const InteractionTypeContractSchema = zodOpenapi(
  z.enum([
    InteractionType.CALL,
    InteractionType.EMAIL,
    InteractionType.VISIT,
    InteractionType.NOTE
  ]),
  {
    description: 'Type of customer interaction',
    example: InteractionType.CALL
  }
);

// OpenAPI schema for Attachment
export const AttachmentContractSchema = zodOpenapi(
  z.object({
    id: z.string().uuid(),
    filename: z.string(),
    url: z.string().url(),
    size: z.number().nonnegative(),
    mimeType: z.string()
  }),
  {
    description: 'File attachment information',
    example: {
      id: '550e8400-e29b-41d4-a716-446655440004',
      filename: 'meeting-notes.pdf',
      url: 'https://cdn.example.com/attachments/meeting-notes.pdf',
      size: 245760,
      mimeType: 'application/pdf'
    }
  }
);

// OpenAPI schema for Create Interaction
export const CreateInteractionContractSchema = zodOpenapi(
  CreateInteractionInputSchema,
  {
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
  }
);

// OpenAPI schema for Update Interaction
export const UpdateInteractionContractSchema = zodOpenapi(
  UpdateInteractionInputSchema,
  {
    description: 'Interaction update data',
    example: {
      subject: 'Updated: Follow-up on proposal',
      content: 'Added additional requirements and adjusted timeline.'
    }
  }
);

// OpenAPI schema for Interaction Response
export const InteractionResponseContractSchema = zodOpenapi(
  InteractionSchema.omit({ tenantId: true }),
  {
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
  }
);

// Query parameters for listing interactions
export const InteractionQueryContractSchema = zodOpenapi(
  z.object({
    customerId: z.string().uuid(),
    type: z.enum([
      InteractionType.CALL,
      InteractionType.EMAIL,
      InteractionType.VISIT,
      InteractionType.NOTE
    ]).optional(),
    from: z.string().datetime().optional(),
    to: z.string().datetime().optional(),
    page: z.string().transform(Number).optional().default('1'),
    pageSize: z.string().transform(Number).optional().default('20')
  }),
  {
    description: 'Query parameters for interaction listing'
  }
);

// Response schema for interaction list
export const InteractionListResponseContractSchema = zodOpenapi(
  z.object({
    data: z.array(InteractionResponseContractSchema),
    pagination: z.object({
      page: z.number(),
      pageSize: z.number(),
      total: z.number(),
      totalPages: z.number()
    })
  }),
  {
    description: 'Paginated interaction list response'
  }
);