"use strict";
/**
 * Production Domain Events for VALEO NeuroERP 3.0
 * Event definitions for production processes with GMP+/QS compliance
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.CAPAClosedEventSchema = exports.CAPACreatedEventSchema = exports.NonConformityCreatedEventSchema = exports.SamplingResultRecordedEventSchema = exports.SamplingAddedEventSchema = exports.CalibrationCheckedEventSchema = exports.FlushPerformedEventSchema = exports.CleaningPerformedEventSchema = exports.MobileRunFinishedEventSchema = exports.MobileRunStartedEventSchema = exports.BatchRejectedEventSchema = exports.BatchQuarantinedEventSchema = exports.BatchReleasedEventSchema = exports.BatchCreatedEventSchema = exports.MixOrderAbortedEventSchema = exports.MixOrderCompletedEventSchema = exports.MixOrderStartedEventSchema = exports.MixOrderStagedEventSchema = exports.MixOrderCreatedEventSchema = exports.RecipeArchivedEventSchema = exports.RecipeUpdatedEventSchema = exports.RecipeCreatedEventSchema = void 0;
const zod_1 = require("zod");
// Base Domain Event Schema
const BaseDomainEventSchema = zod_1.z.object({
    eventId: zod_1.z.string().uuid(),
    eventType: zod_1.z.string(),
    eventVersion: zod_1.z.number().int().min(1),
    occurredAt: zod_1.z.string().datetime(),
    tenantId: zod_1.z.string().uuid(),
    correlationId: zod_1.z.string().uuid().optional(),
    causationId: zod_1.z.string().uuid().optional()
});
// Recipe Events
exports.RecipeCreatedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.recipe.created'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        code: zod_1.z.string(),
        name: zod_1.z.string(),
        version: zod_1.z.number(),
        medicated: zod_1.z.boolean(),
        allergenTags: zod_1.z.array(zod_1.z.string())
    })
});
exports.RecipeUpdatedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.recipe.updated'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        code: zod_1.z.string(),
        name: zod_1.z.string(),
        version: zod_1.z.number(),
        changes: zod_1.z.array(zod_1.z.string())
    })
});
exports.RecipeArchivedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.recipe.archived'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        code: zod_1.z.string(),
        reason: zod_1.z.string().optional()
    })
});
// Mix Order Events
exports.MixOrderCreatedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.mix_order.created'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        orderNumber: zod_1.z.string(),
        type: zod_1.z.enum(['Plant', 'Mobile']),
        recipeId: zod_1.z.string().uuid(),
        targetQtyKg: zod_1.z.number(),
        customerId: zod_1.z.string().uuid().optional(),
        mobileUnitId: zod_1.z.string().uuid().optional()
    })
});
exports.MixOrderStagedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.mix_order.staged'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        orderNumber: zod_1.z.string(),
        type: zod_1.z.enum(['Plant', 'Mobile']),
        recipeId: zod_1.z.string().uuid(),
        plannedAt: zod_1.z.string().datetime()
    })
});
exports.MixOrderStartedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.mix_order.started'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        orderNumber: zod_1.z.string(),
        type: zod_1.z.enum(['Plant', 'Mobile']),
        startedAt: zod_1.z.string().datetime(),
        operatorId: zod_1.z.string().uuid().optional()
    })
});
exports.MixOrderCompletedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.mix_order.completed'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        orderNumber: zod_1.z.string(),
        type: zod_1.z.enum(['Plant', 'Mobile']),
        completedAt: zod_1.z.string().datetime(),
        durationMinutes: zod_1.z.number(),
        totalMassKg: zod_1.z.number(),
        energyKWh: zod_1.z.number().optional()
    })
});
exports.MixOrderAbortedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.mix_order.aborted'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        orderNumber: zod_1.z.string(),
        reason: zod_1.z.string(),
        abortedAt: zod_1.z.string().datetime()
    })
});
// Batch Events
exports.BatchCreatedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.batch.created'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        batchNumber: zod_1.z.string(),
        mixOrderId: zod_1.z.string().uuid(),
        producedQtyKg: zod_1.z.number(),
        recipeId: zod_1.z.string().uuid(),
        medicated: zod_1.z.boolean()
    })
});
exports.BatchReleasedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.batch.released'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        batchNumber: zod_1.z.string(),
        mixOrderId: zod_1.z.string().uuid(),
        releasedAt: zod_1.z.string().datetime(),
        outputLots: zod_1.z.array(zod_1.z.object({
            lotNumber: zod_1.z.string(),
            qtyKg: zod_1.z.number(),
            destination: zod_1.z.enum(['Inventory', 'DirectFarm'])
        }))
    })
});
exports.BatchQuarantinedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.batch.quarantined'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        batchNumber: zod_1.z.string(),
        reason: zod_1.z.string(),
        quarantinedAt: zod_1.z.string().datetime()
    })
});
exports.BatchRejectedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.batch.rejected'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        batchNumber: zod_1.z.string(),
        reason: zod_1.z.string(),
        rejectedAt: zod_1.z.string().datetime(),
        disposalMethod: zod_1.z.string().optional()
    })
});
// Mobile Run Events
exports.MobileRunStartedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.mobile_run.started'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        mobileUnitId: zod_1.z.string().uuid(),
        operatorId: zod_1.z.string().uuid(),
        customerId: zod_1.z.string().uuid(),
        location: zod_1.z.object({
            lat: zod_1.z.number(),
            lng: zod_1.z.number(),
            address: zod_1.z.string().optional()
        }),
        calibrationValid: zod_1.z.boolean(),
        startedAt: zod_1.z.string().datetime()
    })
});
exports.MobileRunFinishedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.mobile_run.finished'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        mobileUnitId: zod_1.z.string().uuid(),
        operatorId: zod_1.z.string().uuid(),
        durationHours: zod_1.z.number(),
        totalFlushMassKg: zod_1.z.number(),
        finishedAt: zod_1.z.string().datetime()
    })
});
// Cleaning Events
exports.CleaningPerformedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.cleaning.performed'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        mobileRunId: zod_1.z.string().uuid().optional(),
        type: zod_1.z.enum(['DryClean', 'Vacuum', 'Flush', 'WetClean']),
        usedMaterialSku: zod_1.z.string().optional(),
        flushMassKg: zod_1.z.number().optional(),
        validatedBy: zod_1.z.string(),
        performedAt: zod_1.z.string().datetime(),
        reason: zod_1.z.string().optional()
    })
});
exports.FlushPerformedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.flush.performed'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        mobileRunId: zod_1.z.string().uuid(),
        usedMaterialSku: zod_1.z.string(),
        flushMassKg: zod_1.z.number(),
        reason: zod_1.z.enum(['Sequencing', 'MedicatedTransition', 'ContaminationPrevention']),
        performedAt: zod_1.z.string().datetime(),
        validatedBy: zod_1.z.string()
    })
});
// Calibration Events
exports.CalibrationCheckedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.calibration.checked'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        mobileRunId: zod_1.z.string().uuid().optional(),
        deviceType: zod_1.z.enum(['Scale', 'Moisture', 'Temperature']),
        deviceId: zod_1.z.string(),
        result: zod_1.z.enum(['Pass', 'Fail']),
        checkedAt: zod_1.z.string().datetime(),
        checkedBy: zod_1.z.string(),
        nextDueDate: zod_1.z.string().datetime().optional()
    })
});
// Quality Events
exports.SamplingAddedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.sampling.added'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        batchId: zod_1.z.string().uuid(),
        sampleCode: zod_1.z.string(),
        analyte: zod_1.z.string(),
        takenAt: zod_1.z.string().datetime(),
        takenBy: zod_1.z.string(),
        retainedSample: zod_1.z.boolean()
    })
});
exports.SamplingResultRecordedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.sampling.result_recorded'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        batchId: zod_1.z.string().uuid(),
        sampleCode: zod_1.z.string(),
        analyte: zod_1.z.string(),
        value: zod_1.z.number(),
        unit: zod_1.z.string(),
        limitType: zod_1.z.enum(['Action', 'Reject']),
        decision: zod_1.z.enum(['Pass', 'Investigate', 'Reject']),
        labId: zod_1.z.string().uuid().optional(),
        recordedAt: zod_1.z.string().datetime(),
        recordedBy: zod_1.z.string()
    })
});
exports.NonConformityCreatedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.nc.created'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        refType: zod_1.z.enum(['batchId', 'mixOrderId', 'mobileRunId']),
        refId: zod_1.z.string().uuid(),
        type: zod_1.z.enum(['Contamination', 'SpecOut', 'Equipment', 'Process']),
        severity: zod_1.z.enum(['Low', 'Medium', 'High', 'Critical']),
        action: zod_1.z.enum(['Block', 'Rework', 'Dispose']),
        description: zod_1.z.string(),
        discoveredAt: zod_1.z.string().datetime(),
        discoveredBy: zod_1.z.string()
    })
});
exports.CAPACreatedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.capa.created'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        ncId: zod_1.z.string().uuid().optional(),
        title: zod_1.z.string(),
        type: zod_1.z.enum(['Correction', 'CorrectiveAction', 'PreventiveAction']),
        priority: zod_1.z.enum(['Low', 'Medium', 'High', 'Critical']),
        assignedTo: zod_1.z.string().uuid().optional(),
        dueDate: zod_1.z.string().datetime().optional(),
        createdBy: zod_1.z.string()
    })
});
exports.CAPAClosedEventSchema = BaseDomainEventSchema.extend({
    eventType: zod_1.z.literal('production.capa.closed'),
    payload: zod_1.z.object({
        id: zod_1.z.string().uuid(),
        effectiveness: zod_1.z.enum(['Effective', 'NotEffective', 'NotEvaluated']),
        closedAt: zod_1.z.string().datetime(),
        closedBy: zod_1.z.string(),
        summary: zod_1.z.string().optional()
    })
});
//# sourceMappingURL=production-events.js.map