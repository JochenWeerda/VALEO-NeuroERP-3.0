import { z } from 'zod';

/**
 * Base Event Schema
 */
export const BaseEventSchema = z.object({
  eventType: z.string(),
  occurredAt: z.string().datetime(),
  version: z.string().default('1.0'),
});

/**
 * Quality Plan Events
 */
export const PlanCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.plan.created'),
  payload: z.object({
    tenantId: z.string(),
    planId: z.string(),
    name: z.string(),
    commodity: z.string().optional(),
    contractId: z.string().optional(),
  }),
});

export const PlanUpdatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.plan.updated'),
  payload: z.object({
    tenantId: z.string(),
    planId: z.string(),
  }),
});

export const PlanDeactivatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.plan.deactivated'),
  payload: z.object({
    tenantId: z.string(),
    planId: z.string(),
  }),
});

/**
 * Sample Events
 */
export const SampleTakenEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.sample.taken'),
  payload: z.object({
    tenantId: z.string(),
    sampleId: z.string(),
    sampleCode: z.string(),
    batchId: z.string().optional(),
    contractId: z.string().optional(),
    source: z.string(),
    takenBy: z.string(),
  }),
});

export const SampleResultAddedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.sample.result.added'),
  payload: z.object({
    tenantId: z.string(),
    sampleId: z.string(),
    resultId: z.string(),
    analyte: z.string(),
    value: z.number(),
    result: z.string(),
  }),
});

export const SampleAnalyzedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.sample.analyzed'),
  payload: z.object({
    tenantId: z.string(),
    sampleId: z.string(),
    sampleCode: z.string(),
    status: z.string(),
    batchId: z.string().optional(),
    contractId: z.string().optional(),
    allPass: z.boolean(),
  }),
});

/**
 * Quality Status Events
 */
export const BatchReleasedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.batch.released'),
  payload: z.object({
    tenantId: z.string(),
    batchId: z.string(),
    sampleId: z.string(),
  }),
});

export const BatchRejectedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.batch.rejected'),
  payload: z.object({
    tenantId: z.string(),
    batchId: z.string(),
    sampleId: z.string().optional(),
    reason: z.string(),
  }),
});

export const QualityIssueDetectedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.issue.detected'),
  payload: z.object({
    tenantId: z.string(),
    sampleId: z.string(),
    status: z.string(),
    batchId: z.string().optional(),
    contractId: z.string().optional(),
  }),
});

/**
 * NC Events
 */
export const NCCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.nc.created'),
  payload: z.object({
    tenantId: z.string(),
    ncId: z.string(),
    ncNumber: z.string(),
    type: z.string(),
    severity: z.string(),
    batchId: z.string().optional(),
    contractId: z.string().optional(),
  }),
});

export const NCUpdatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.nc.updated'),
  payload: z.object({
    tenantId: z.string(),
    ncId: z.string(),
    status: z.string(),
  }),
});

export const NCClosedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.nc.closed'),
  payload: z.object({
    tenantId: z.string(),
    ncId: z.string(),
    closedBy: z.string(),
  }),
});

/**
 * CAPA Events
 */
export const CAPACreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.capa.created'),
  payload: z.object({
    tenantId: z.string(),
    capaId: z.string(),
    capaNumber: z.string(),
    type: z.string(),
    linkedNcIds: z.array(z.string()),
  }),
});

export const CAPAImplementedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.capa.implemented'),
  payload: z.object({
    tenantId: z.string(),
    capaId: z.string(),
  }),
});

export const CAPAVerifiedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('quality.capa.verified'),
  payload: z.object({
    tenantId: z.string(),
    capaId: z.string(),
    verifiedBy: z.string(),
    effectivenessCheck: z.boolean(),
  }),
});

// Export all event schemas as union type
export type QualityEvent =
  | z.infer<typeof PlanCreatedEventSchema>
  | z.infer<typeof PlanUpdatedEventSchema>
  | z.infer<typeof PlanDeactivatedEventSchema>
  | z.infer<typeof SampleTakenEventSchema>
  | z.infer<typeof SampleResultAddedEventSchema>
  | z.infer<typeof SampleAnalyzedEventSchema>
  | z.infer<typeof BatchReleasedEventSchema>
  | z.infer<typeof BatchRejectedEventSchema>
  | z.infer<typeof QualityIssueDetectedEventSchema>
  | z.infer<typeof NCCreatedEventSchema>
  | z.infer<typeof NCUpdatedEventSchema>
  | z.infer<typeof NCClosedEventSchema>
  | z.infer<typeof CAPACreatedEventSchema>
  | z.infer<typeof CAPAImplementedEventSchema>
  | z.infer<typeof CAPAVerifiedEventSchema>;
