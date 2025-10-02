/**
 * Production Domain Events for VALEO NeuroERP 3.0
 * Event definitions for production processes with GMP+/QS compliance
 */

import { z } from 'zod';

// Base Domain Event Schema
const BaseDomainEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.string(),
  eventVersion: z.number().int().min(1),
  occurredAt: z.string().datetime(),
  tenantId: z.string().uuid(),
  correlationId: z.string().uuid().optional(),
  causationId: z.string().uuid().optional()
});

// Recipe Events
export const RecipeCreatedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.recipe.created'),
  payload: z.object({
    id: z.string().uuid(),
    code: z.string(),
    name: z.string(),
    version: z.number(),
    medicated: z.boolean(),
    allergenTags: z.array(z.string())
  })
});

export const RecipeUpdatedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.recipe.updated'),
  payload: z.object({
    id: z.string().uuid(),
    code: z.string(),
    name: z.string(),
    version: z.number(),
    changes: z.array(z.string())
  })
});

export const RecipeArchivedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.recipe.archived'),
  payload: z.object({
    id: z.string().uuid(),
    code: z.string(),
    reason: z.string().optional()
  })
});

// Mix Order Events
export const MixOrderCreatedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.mix_order.created'),
  payload: z.object({
    id: z.string().uuid(),
    orderNumber: z.string(),
    type: z.enum(['Plant', 'Mobile']),
    recipeId: z.string().uuid(),
    targetQtyKg: z.number(),
    customerId: z.string().uuid().optional(),
    mobileUnitId: z.string().uuid().optional()
  })
});

export const MixOrderStagedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.mix_order.staged'),
  payload: z.object({
    id: z.string().uuid(),
    orderNumber: z.string(),
    type: z.enum(['Plant', 'Mobile']),
    recipeId: z.string().uuid(),
    plannedAt: z.string().datetime()
  })
});

export const MixOrderStartedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.mix_order.started'),
  payload: z.object({
    id: z.string().uuid(),
    orderNumber: z.string(),
    type: z.enum(['Plant', 'Mobile']),
    startedAt: z.string().datetime(),
    operatorId: z.string().uuid().optional()
  })
});

export const MixOrderCompletedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.mix_order.completed'),
  payload: z.object({
    id: z.string().uuid(),
    orderNumber: z.string(),
    type: z.enum(['Plant', 'Mobile']),
    completedAt: z.string().datetime(),
    durationMinutes: z.number(),
    totalMassKg: z.number(),
    energyKWh: z.number().optional()
  })
});

export const MixOrderAbortedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.mix_order.aborted'),
  payload: z.object({
    id: z.string().uuid(),
    orderNumber: z.string(),
    reason: z.string(),
    abortedAt: z.string().datetime()
  })
});

// Batch Events
export const BatchCreatedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.batch.created'),
  payload: z.object({
    id: z.string().uuid(),
    batchNumber: z.string(),
    mixOrderId: z.string().uuid(),
    producedQtyKg: z.number(),
    recipeId: z.string().uuid(),
    medicated: z.boolean()
  })
});

export const BatchReleasedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.batch.released'),
  payload: z.object({
    id: z.string().uuid(),
    batchNumber: z.string(),
    mixOrderId: z.string().uuid(),
    releasedAt: z.string().datetime(),
    outputLots: z.array(z.object({
      lotNumber: z.string(),
      qtyKg: z.number(),
      destination: z.enum(['Inventory', 'DirectFarm'])
    }))
  })
});

export const BatchQuarantinedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.batch.quarantined'),
  payload: z.object({
    id: z.string().uuid(),
    batchNumber: z.string(),
    reason: z.string(),
    quarantinedAt: z.string().datetime()
  })
});

export const BatchRejectedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.batch.rejected'),
  payload: z.object({
    id: z.string().uuid(),
    batchNumber: z.string(),
    reason: z.string(),
    rejectedAt: z.string().datetime(),
    disposalMethod: z.string().optional()
  })
});

// Mobile Run Events
export const MobileRunStartedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.mobile_run.started'),
  payload: z.object({
    id: z.string().uuid(),
    mobileUnitId: z.string().uuid(),
    operatorId: z.string().uuid(),
    customerId: z.string().uuid(),
    location: z.object({
      lat: z.number(),
      lng: z.number(),
      address: z.string().optional()
    }),
    calibrationValid: z.boolean(),
    startedAt: z.string().datetime()
  })
});

export const MobileRunFinishedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.mobile_run.finished'),
  payload: z.object({
    id: z.string().uuid(),
    mobileUnitId: z.string().uuid(),
    operatorId: z.string().uuid(),
    durationHours: z.number(),
    totalFlushMassKg: z.number(),
    finishedAt: z.string().datetime()
  })
});

// Cleaning Events
export const CleaningPerformedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.cleaning.performed'),
  payload: z.object({
    id: z.string().uuid(),
    mobileRunId: z.string().uuid().optional(),
    type: z.enum(['DryClean', 'Vacuum', 'Flush', 'WetClean']),
    usedMaterialSku: z.string().optional(),
    flushMassKg: z.number().optional(),
    validatedBy: z.string(),
    performedAt: z.string().datetime(),
    reason: z.string().optional()
  })
});

export const FlushPerformedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.flush.performed'),
  payload: z.object({
    id: z.string().uuid(),
    mobileRunId: z.string().uuid(),
    usedMaterialSku: z.string(),
    flushMassKg: z.number(),
    reason: z.enum(['Sequencing', 'MedicatedTransition', 'ContaminationPrevention']),
    performedAt: z.string().datetime(),
    validatedBy: z.string()
  })
});

// Calibration Events
export const CalibrationCheckedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.calibration.checked'),
  payload: z.object({
    id: z.string().uuid(),
    mobileRunId: z.string().uuid().optional(),
    deviceType: z.enum(['Scale', 'Moisture', 'Temperature']),
    deviceId: z.string(),
    result: z.enum(['Pass', 'Fail']),
    checkedAt: z.string().datetime(),
    checkedBy: z.string(),
    nextDueDate: z.string().datetime().optional()
  })
});

// Quality Events
export const SamplingAddedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.sampling.added'),
  payload: z.object({
    id: z.string().uuid(),
    batchId: z.string().uuid(),
    sampleCode: z.string(),
    analyte: z.string(),
    takenAt: z.string().datetime(),
    takenBy: z.string(),
    retainedSample: z.boolean()
  })
});

export const SamplingResultRecordedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.sampling.result_recorded'),
  payload: z.object({
    id: z.string().uuid(),
    batchId: z.string().uuid(),
    sampleCode: z.string(),
    analyte: z.string(),
    value: z.number(),
    unit: z.string(),
    limitType: z.enum(['Action', 'Reject']),
    decision: z.enum(['Pass', 'Investigate', 'Reject']),
    labId: z.string().uuid().optional(),
    recordedAt: z.string().datetime(),
    recordedBy: z.string()
  })
});

export const NonConformityCreatedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.nc.created'),
  payload: z.object({
    id: z.string().uuid(),
    refType: z.enum(['batchId', 'mixOrderId', 'mobileRunId']),
    refId: z.string().uuid(),
    type: z.enum(['Contamination', 'SpecOut', 'Equipment', 'Process']),
    severity: z.enum(['Low', 'Medium', 'High', 'Critical']),
    action: z.enum(['Block', 'Rework', 'Dispose']),
    description: z.string(),
    discoveredAt: z.string().datetime(),
    discoveredBy: z.string()
  })
});

export const CAPACreatedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.capa.created'),
  payload: z.object({
    id: z.string().uuid(),
    ncId: z.string().uuid().optional(),
    title: z.string(),
    type: z.enum(['Correction', 'CorrectiveAction', 'PreventiveAction']),
    priority: z.enum(['Low', 'Medium', 'High', 'Critical']),
    assignedTo: z.string().uuid().optional(),
    dueDate: z.string().datetime().optional(),
    createdBy: z.string()
  })
});

export const CAPAClosedEventSchema = BaseDomainEventSchema.extend({
  eventType: z.literal('production.capa.closed'),
  payload: z.object({
    id: z.string().uuid(),
    effectiveness: z.enum(['Effective', 'NotEffective', 'NotEvaluated']),
    closedAt: z.string().datetime(),
    closedBy: z.string(),
    summary: z.string().optional()
  })
});

// Type definitions
export type BaseDomainEvent = z.infer<typeof BaseDomainEventSchema>;
export type RecipeCreatedEvent = z.infer<typeof RecipeCreatedEventSchema>;
export type RecipeUpdatedEvent = z.infer<typeof RecipeUpdatedEventSchema>;
export type RecipeArchivedEvent = z.infer<typeof RecipeArchivedEventSchema>;
export type MixOrderCreatedEvent = z.infer<typeof MixOrderCreatedEventSchema>;
export type MixOrderStagedEvent = z.infer<typeof MixOrderStagedEventSchema>;
export type MixOrderStartedEvent = z.infer<typeof MixOrderStartedEventSchema>;
export type MixOrderCompletedEvent = z.infer<typeof MixOrderCompletedEventSchema>;
export type MixOrderAbortedEvent = z.infer<typeof MixOrderAbortedEventSchema>;
export type BatchCreatedEvent = z.infer<typeof BatchCreatedEventSchema>;
export type BatchReleasedEvent = z.infer<typeof BatchReleasedEventSchema>;
export type BatchQuarantinedEvent = z.infer<typeof BatchQuarantinedEventSchema>;
export type BatchRejectedEvent = z.infer<typeof BatchRejectedEventSchema>;
export type MobileRunStartedEvent = z.infer<typeof MobileRunStartedEventSchema>;
export type MobileRunFinishedEvent = z.infer<typeof MobileRunFinishedEventSchema>;
export type CleaningPerformedEvent = z.infer<typeof CleaningPerformedEventSchema>;
export type FlushPerformedEvent = z.infer<typeof FlushPerformedEventSchema>;
export type CalibrationCheckedEvent = z.infer<typeof CalibrationCheckedEventSchema>;
export type SamplingAddedEvent = z.infer<typeof SamplingAddedEventSchema>;
export type SamplingResultRecordedEvent = z.infer<typeof SamplingResultRecordedEventSchema>;
export type NonConformityCreatedEvent = z.infer<typeof NonConformityCreatedEventSchema>;
export type CAPACreatedEvent = z.infer<typeof CAPACreatedEventSchema>;
export type CAPAClosedEvent = z.infer<typeof CAPAClosedEventSchema>;

// Union type for all production events
export type ProductionDomainEvent = 
  | RecipeCreatedEvent
  | RecipeUpdatedEvent
  | RecipeArchivedEvent
  | MixOrderCreatedEvent
  | MixOrderStagedEvent
  | MixOrderStartedEvent
  | MixOrderCompletedEvent
  | MixOrderAbortedEvent
  | BatchCreatedEvent
  | BatchReleasedEvent
  | BatchQuarantinedEvent
  | BatchRejectedEvent
  | MobileRunStartedEvent
  | MobileRunFinishedEvent
  | CleaningPerformedEvent
  | FlushPerformedEvent
  | CalibrationCheckedEvent
  | SamplingAddedEvent
  | SamplingResultRecordedEvent
  | NonConformityCreatedEvent
  | CAPACreatedEvent
  | CAPAClosedEvent;

