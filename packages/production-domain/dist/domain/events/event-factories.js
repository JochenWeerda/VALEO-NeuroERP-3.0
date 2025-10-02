"use strict";
/**
 * Event Factory Functions for VALEO NeuroERP 3.0 Production Domain
 * Factory functions to create domain events with proper validation
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createRecipeCreatedEvent = createRecipeCreatedEvent;
exports.createRecipeUpdatedEvent = createRecipeUpdatedEvent;
exports.createRecipeArchivedEvent = createRecipeArchivedEvent;
exports.createMixOrderCreatedEvent = createMixOrderCreatedEvent;
exports.createMixOrderStagedEvent = createMixOrderStagedEvent;
exports.createMixOrderStartedEvent = createMixOrderStartedEvent;
exports.createMixOrderCompletedEvent = createMixOrderCompletedEvent;
exports.createMixOrderAbortedEvent = createMixOrderAbortedEvent;
exports.createBatchCreatedEvent = createBatchCreatedEvent;
exports.createBatchReleasedEvent = createBatchReleasedEvent;
exports.createBatchQuarantinedEvent = createBatchQuarantinedEvent;
exports.createBatchRejectedEvent = createBatchRejectedEvent;
exports.createMobileRunStartedEvent = createMobileRunStartedEvent;
exports.createMobileRunFinishedEvent = createMobileRunFinishedEvent;
exports.createCleaningPerformedEvent = createCleaningPerformedEvent;
exports.createFlushPerformedEvent = createFlushPerformedEvent;
exports.createCalibrationCheckedEvent = createCalibrationCheckedEvent;
exports.createSamplingAddedEvent = createSamplingAddedEvent;
exports.createSamplingResultRecordedEvent = createSamplingResultRecordedEvent;
exports.createNonConformityCreatedEvent = createNonConformityCreatedEvent;
exports.createCAPACreatedEvent = createCAPACreatedEvent;
exports.createCAPAClosedEvent = createCAPAClosedEvent;
exports.createCorrelatedEvent = createCorrelatedEvent;
exports.validateEventPayload = validateEventPayload;
const uuid_1 = require("uuid");
// Recipe Event Factories
function createRecipeCreatedEvent(data, tenantId, correlationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.recipe.created',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        correlationId,
        payload: data
    };
}
function createRecipeUpdatedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.recipe.updated',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createRecipeArchivedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.recipe.archived',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
// Mix Order Event Factories
function createMixOrderCreatedEvent(data, tenantId, correlationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.mix_order.created',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        correlationId,
        payload: data
    };
}
function createMixOrderStagedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.mix_order.staged',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createMixOrderStartedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.mix_order.started',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createMixOrderCompletedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.mix_order.completed',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createMixOrderAbortedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.mix_order.aborted',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
// Batch Event Factories
function createBatchCreatedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.batch.created',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createBatchReleasedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.batch.released',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createBatchQuarantinedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.batch.quarantined',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createBatchRejectedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.batch.rejected',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
// Mobile Run Event Factories
function createMobileRunStartedEvent(data, tenantId, correlationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.mobile_run.started',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        correlationId,
        payload: data
    };
}
function createMobileRunFinishedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.mobile_run.finished',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
// Cleaning Event Factories
function createCleaningPerformedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.cleaning.performed',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createFlushPerformedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.flush.performed',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
// Calibration Event Factories
function createCalibrationCheckedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.calibration.checked',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
// Quality Event Factories
function createSamplingAddedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.sampling.added',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createSamplingResultRecordedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.sampling.result_recorded',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createNonConformityCreatedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.nc.created',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createCAPACreatedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.capa.created',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
function createCAPAClosedEvent(data, tenantId, causationId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'production.capa.closed',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        causationId,
        payload: data
    };
}
// Helper function to create events with correlation chain
function createCorrelatedEvent(eventFactory, causationEvent) {
    return eventFactory(causationEvent?.eventId);
}
// Event validation helper
function validateEventPayload(schema, payload) {
    try {
        schema.parse(payload);
        return { valid: true };
    }
    catch (error) {
        return {
            valid: false,
            errors: error.errors?.map((e) => `${e.path.join('.')}: ${e.message}`) || ['Unknown validation error']
        };
    }
}
//# sourceMappingURL=event-factories.js.map