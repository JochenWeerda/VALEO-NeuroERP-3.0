import { z } from 'zod';
import {
  CreateOpportunityInputSchema,
  OpportunitySchema,
  OpportunityStage,
  UpdateOpportunityInputSchema
} from '../domain/entities';

// OpenAPI schema for Opportunity Stage
export const OpportunityStageContractSchema = z.enum([
  OpportunityStage.LEAD,
  OpportunityStage.QUALIFIED,
  OpportunityStage.PROPOSAL,
  OpportunityStage.WON,
  OpportunityStage.LOST
]).meta({
  description: 'Opportunity stage in the sales pipeline',
  example: OpportunityStage.QUALIFIED
});

// OpenAPI schema for Create Opportunity
export const CreateOpportunityContractSchema = CreateOpportunityInputSchema.meta({
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
});

// OpenAPI schema for Update Opportunity
export const UpdateOpportunityContractSchema = UpdateOpportunityInputSchema.meta({
  description: 'Opportunity update data',
  example: {
    stage: OpportunityStage.PROPOSAL,
    amountNet: 175000,
    probability: 0.85
  }
});

// OpenAPI schema for Opportunity Response
export const OpportunityResponseContractSchema = OpportunitySchema.omit({ tenantId: true }).meta({
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
});

// Query parameters for listing opportunities
export const OpportunityQueryContractSchema = z.object({
  customerId: z.string().guid().optional(),
  stage: z.enum([
    OpportunityStage.LEAD,
    OpportunityStage.QUALIFIED,
    OpportunityStage.PROPOSAL,
    OpportunityStage.WON,
    OpportunityStage.LOST
  ]).optional(),
  ownerUserId: z.string().guid().optional(),
  amountMin: z.number().nonnegative().optional(),
  amountMax: z.number().nonnegative().optional(),
  page: z.string().transform(Number).optional().prefault('1'),
  pageSize: z.string().transform(Number).optional().prefault('20')
}).meta({
  description: 'Query parameters for opportunity listing'
});

// Response schema for opportunity list
export const OpportunityListResponseContractSchema = z.object({
  data: z.array(OpportunityResponseContractSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number()
  })
}).meta({
  description: 'Paginated opportunity list response'
});