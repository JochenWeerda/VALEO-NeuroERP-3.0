"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpportunityListResponseContractSchema = exports.OpportunityQueryContractSchema = exports.OpportunityResponseContractSchema = exports.UpdateOpportunityContractSchema = exports.CreateOpportunityContractSchema = exports.OpportunityStageContractSchema = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
const entities_1 = require("../domain/entities");
// OpenAPI schema for Opportunity Stage
exports.OpportunityStageContractSchema = (0, zod_openapi_1.zodOpenapi)(zod_1.z.enum([
    entities_1.OpportunityStage.LEAD,
    entities_1.OpportunityStage.QUALIFIED,
    entities_1.OpportunityStage.PROPOSAL,
    entities_1.OpportunityStage.WON,
    entities_1.OpportunityStage.LOST
]), {
    description: 'Opportunity stage in the sales pipeline',
    example: entities_1.OpportunityStage.QUALIFIED
});
// OpenAPI schema for Create Opportunity
exports.CreateOpportunityContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.CreateOpportunityInputSchema, {
    description: 'Opportunity creation data',
    example: {
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        title: 'Enterprise Software Implementation',
        stage: entities_1.OpportunityStage.QUALIFIED,
        expectedCloseDate: '2024-06-30T00:00:00.000Z',
        amountNet: 150000,
        currency: 'USD',
        probability: 0.75,
        ownerUserId: '550e8400-e29b-41d4-a716-446655440002'
    }
});
// OpenAPI schema for Update Opportunity
exports.UpdateOpportunityContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.UpdateOpportunityInputSchema, {
    description: 'Opportunity update data',
    example: {
        stage: entities_1.OpportunityStage.PROPOSAL,
        amountNet: 175000,
        probability: 0.85
    }
});
// OpenAPI schema for Opportunity Response
exports.OpportunityResponseContractSchema = (0, zod_openapi_1.zodOpenapi)(entities_1.OpportunitySchema.omit({ tenantId: true }), {
    description: 'Opportunity information',
    example: {
        id: '550e8400-e29b-41d4-a716-446655440003',
        customerId: '550e8400-e29b-41d4-a716-446655440000',
        title: 'Enterprise Software Implementation',
        stage: entities_1.OpportunityStage.QUALIFIED,
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
exports.OpportunityQueryContractSchema = (0, zod_openapi_1.zodOpenapi)(zod_1.z.object({
    customerId: zod_1.z.string().uuid().optional(),
    stage: zod_1.z.enum([
        entities_1.OpportunityStage.LEAD,
        entities_1.OpportunityStage.QUALIFIED,
        entities_1.OpportunityStage.PROPOSAL,
        entities_1.OpportunityStage.WON,
        entities_1.OpportunityStage.LOST
    ]).optional(),
    ownerUserId: zod_1.z.string().uuid().optional(),
    amountMin: zod_1.z.number().nonnegative().optional(),
    amountMax: zod_1.z.number().nonnegative().optional(),
    page: zod_1.z.string().transform(Number).optional().default('1'),
    pageSize: zod_1.z.string().transform(Number).optional().default('20')
}), {
    description: 'Query parameters for opportunity listing'
});
// Response schema for opportunity list
exports.OpportunityListResponseContractSchema = (0, zod_openapi_1.zodOpenapi)(zod_1.z.object({
    data: zod_1.z.array(exports.OpportunityResponseContractSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number()
    })
}), {
    description: 'Paginated opportunity list response'
});
//# sourceMappingURL=opportunity-contracts.js.map