import { z } from 'zod';
// @ts-ignore - zod-openapi module
import { zodOpenapi } from 'zod-openapi';
import {
  OpportunitySchema,
  CreateOpportunityInputSchema,
  UpdateOpportunityInputSchema,
  OpportunityStage
} from '../domain/entities';

// OpenAPI schema for Opportunity Stage
export const OpportunityStageContractSchema = zodOpenapi(
  z.enum([
    OpportunityStage.LEAD,
    OpportunityStage.QUALIFIED,
    OpportunityStage.PROPOSAL,
    OpportunityStage.WON,
    OpportunityStage.LOST
  ]),
  {
    description: 'Opportunity stage in the sales pipeline',
    example: OpportunityStage.QUALIFIED
  }
);

// OpenAPI schema for Create Opportunity
export const CreateOpportunityContractSchema = zodOpenapi(
  CreateOpportunityInputSchema,
  {
    description: 'Opportunity creation data',
    example: {
      customerId: '550e8400-e29b-41d4-a716-446655440000',
      title: 'Enterprise Software Implementation',
      stage: OpportunityStage.QUALIFIED,
      expectedCloseDate: '2024-06-30T00:00:00.000Z',
      amountNet: 150000,
      currency: 'USD',
      probability: 0.75,
      ownerUserId: '550e8400-e29b-41d4-a716-446655440002'
    }
  }
);

// OpenAPI schema for Update Opportunity
export const UpdateOpportunityContractSchema = zodOpenapi(
  UpdateOpportunityInputSchema,
  {
    description: 'Opportunity update data',
    example: {
      stage: OpportunityStage.PROPOSAL,
      amountNet: 175000,
      probability: 0.85
    }
  }
);

// OpenAPI schema for Opportunity Response
export const OpportunityResponseContractSchema = zodOpenapi(
  OpportunitySchema.omit({ tenantId: true }),
  {
    description: 'Opportunity information',
    example: {
      id: '550e8400-e29b-41d4-a716-446655440003',
      customerId: '550e8400-e29b-41d4-a716-446655440000',
      title: 'Enterprise Software Implementation',
      stage: OpportunityStage.QUALIFIED,
      expectedCloseDate: '2024-06-30T00:00:00.000Z',
      amountNet: 150000,
      currency: 'USD',
      probability: 0.75,
      ownerUserId: '550e8400-e29b-41d4-a716-446655440002',
      createdAt: '2024-01-01T00:00:00.000Z',
      updatedAt: '2024-01-01T00:00:00.000Z',
      version: 1
    }
  }
);

// Query parameters for listing opportunities
export const OpportunityQueryContractSchema = zodOpenapi(
  z.object({
    customerId: z.string().uuid().optional(),
    stage: z.enum([
      OpportunityStage.LEAD,
      OpportunityStage.QUALIFIED,
      OpportunityStage.PROPOSAL,
      OpportunityStage.WON,
      OpportunityStage.LOST
    ]).optional(),
    ownerUserId: z.string().uuid().optional(),
    amountMin: z.number().nonnegative().optional(),
    amountMax: z.number().nonnegative().optional(),
    page: z.string().transform(Number).optional().default('1'),
    pageSize: z.string().transform(Number).optional().default('20')
  }),
  {
    description: 'Query parameters for opportunity listing'
  }
);

// Response schema for opportunity list
export const OpportunityListResponseContractSchema = zodOpenapi(
  z.object({
    data: z.array(OpportunityResponseContractSchema),
    pagination: z.object({
      page: z.number(),
      pageSize: z.number(),
      total: z.number(),
      totalPages: z.number()
    })
  }),
  {
    description: 'Paginated opportunity list response'
  }
);