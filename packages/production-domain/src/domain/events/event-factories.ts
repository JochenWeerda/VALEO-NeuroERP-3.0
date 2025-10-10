/**
 * Event Factory Functions for VALEO NeuroERP 3.0 Production Domain
 * Factory functions to create domain events with proper validation
 */

import { v4 as uuidv4 } from 'uuid';
import type {
  BatchCreatedEvent,
  BatchQuarantinedEvent,
  BatchRejectedEvent,
  BatchReleasedEvent,
  CAPAClosedEvent,
  CAPACreatedEvent,
  CalibrationCheckedEvent,
  CleaningPerformedEvent,
  FlushPerformedEvent,
  MixOrderAbortedEvent,
  MixOrderCompletedEvent,
  MixOrderCreatedEvent,
  MixOrderStagedEvent,
  MixOrderStartedEvent,
  MobileRunFinishedEvent,
  MobileRunStartedEvent,
  NonConformityCreatedEvent,
  RecipeArchivedEvent,
  RecipeCreatedEvent,
  RecipeUpdatedEvent,
  SamplingAddedEvent,
  SamplingResultRecordedEvent
} from './production-events';

// Recipe Event Factories
export function createRecipeCreatedEvent(
  data: RecipeCreatedEvent['payload'],
  tenantId: string,
  correlationId?: string
): RecipeCreatedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.recipe.created',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    correlationId,
    payload: data
  };
}

export function createRecipeUpdatedEvent(
  data: RecipeUpdatedEvent['payload'],
  tenantId: string,
  causationId?: string
): RecipeUpdatedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.recipe.updated',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createRecipeArchivedEvent(
  data: RecipeArchivedEvent['payload'],
  tenantId: string,
  causationId?: string
): RecipeArchivedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.recipe.archived',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

// Mix Order Event Factories
export function createMixOrderCreatedEvent(
  data: MixOrderCreatedEvent['payload'],
  tenantId: string,
  correlationId?: string
): MixOrderCreatedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.mix_order.created',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    correlationId,
    payload: data
  };
}

export function createMixOrderStagedEvent(
  data: MixOrderStagedEvent['payload'],
  tenantId: string,
  causationId?: string
): MixOrderStagedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.mix_order.staged',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createMixOrderStartedEvent(
  data: MixOrderStartedEvent['payload'],
  tenantId: string,
  causationId?: string
): MixOrderStartedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.mix_order.started',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createMixOrderCompletedEvent(
  data: MixOrderCompletedEvent['payload'],
  tenantId: string,
  causationId?: string
): MixOrderCompletedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.mix_order.completed',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createMixOrderAbortedEvent(
  data: MixOrderAbortedEvent['payload'],
  tenantId: string,
  causationId?: string
): MixOrderAbortedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.mix_order.aborted',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

// Batch Event Factories
export function createBatchCreatedEvent(
  data: BatchCreatedEvent['payload'],
  tenantId: string,
  causationId?: string
): BatchCreatedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.batch.created',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createBatchReleasedEvent(
  data: BatchReleasedEvent['payload'],
  tenantId: string,
  causationId?: string
): BatchReleasedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.batch.released',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createBatchQuarantinedEvent(
  data: BatchQuarantinedEvent['payload'],
  tenantId: string,
  causationId?: string
): BatchQuarantinedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.batch.quarantined',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createBatchRejectedEvent(
  data: BatchRejectedEvent['payload'],
  tenantId: string,
  causationId?: string
): BatchRejectedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.batch.rejected',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

// Mobile Run Event Factories
export function createMobileRunStartedEvent(
  data: MobileRunStartedEvent['payload'],
  tenantId: string,
  correlationId?: string
): MobileRunStartedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.mobile_run.started',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    correlationId,
    payload: data
  };
}

export function createMobileRunFinishedEvent(
  data: MobileRunFinishedEvent['payload'],
  tenantId: string,
  causationId?: string
): MobileRunFinishedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.mobile_run.finished',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

// Cleaning Event Factories
export function createCleaningPerformedEvent(
  data: CleaningPerformedEvent['payload'],
  tenantId: string,
  causationId?: string
): CleaningPerformedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.cleaning.performed',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createFlushPerformedEvent(
  data: FlushPerformedEvent['payload'],
  tenantId: string,
  causationId?: string
): FlushPerformedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.flush.performed',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

// Calibration Event Factories
export function createCalibrationCheckedEvent(
  data: CalibrationCheckedEvent['payload'],
  tenantId: string,
  causationId?: string
): CalibrationCheckedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.calibration.checked',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

// Quality Event Factories
export function createSamplingAddedEvent(
  data: SamplingAddedEvent['payload'],
  tenantId: string,
  causationId?: string
): SamplingAddedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.sampling.added',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createSamplingResultRecordedEvent(
  data: SamplingResultRecordedEvent['payload'],
  tenantId: string,
  causationId?: string
): SamplingResultRecordedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.sampling.result_recorded',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createNonConformityCreatedEvent(
  data: NonConformityCreatedEvent['payload'],
  tenantId: string,
  causationId?: string
): NonConformityCreatedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.nc.created',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createCAPACreatedEvent(
  data: CAPACreatedEvent['payload'],
  tenantId: string,
  causationId?: string
): CAPACreatedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.capa.created',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

export function createCAPAClosedEvent(
  data: CAPAClosedEvent['payload'],
  tenantId: string,
  causationId?: string
): CAPAClosedEvent {
  return {
    eventId: uuidv4(),
    eventType: 'production.capa.closed',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    causationId,
    payload: data
  };
}

// Helper function to create events with correlation chain
export function createCorrelatedEvent<T extends { eventId: string; causationId?: string }>(
  eventFactory: (correlationId?: string) => T,
  causationEvent?: { eventId: string }
): T {
  return eventFactory(causationEvent?.eventId);
}

// Event validation helper
export function validateEventPayload<T>(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types
  schema: any,
  payload: T
): { valid: boolean; errors?: string[] } {
  try {
    schema.parse(payload);
    return { valid: true };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) {
    return {
      valid: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      errors: (error.errors !== undefined && error.errors !== null) ? error.errors.map((e: any) => `${e.path.join('.')}: ${e.message}`) : ['Unknown validation error']
    };
  }
}

