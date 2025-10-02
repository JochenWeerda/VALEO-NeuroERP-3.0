/**
 * Event Factory Functions for VALEO NeuroERP 3.0 Production Domain
 * Factory functions to create domain events with proper validation
 */
import type { RecipeCreatedEvent, RecipeUpdatedEvent, RecipeArchivedEvent, MixOrderCreatedEvent, MixOrderStagedEvent, MixOrderStartedEvent, MixOrderCompletedEvent, MixOrderAbortedEvent, BatchCreatedEvent, BatchReleasedEvent, BatchQuarantinedEvent, BatchRejectedEvent, MobileRunStartedEvent, MobileRunFinishedEvent, CleaningPerformedEvent, FlushPerformedEvent, CalibrationCheckedEvent, SamplingAddedEvent, SamplingResultRecordedEvent, NonConformityCreatedEvent, CAPACreatedEvent, CAPAClosedEvent } from './production-events';
export declare function createRecipeCreatedEvent(data: RecipeCreatedEvent['payload'], tenantId: string, correlationId?: string): RecipeCreatedEvent;
export declare function createRecipeUpdatedEvent(data: RecipeUpdatedEvent['payload'], tenantId: string, causationId?: string): RecipeUpdatedEvent;
export declare function createRecipeArchivedEvent(data: RecipeArchivedEvent['payload'], tenantId: string, causationId?: string): RecipeArchivedEvent;
export declare function createMixOrderCreatedEvent(data: MixOrderCreatedEvent['payload'], tenantId: string, correlationId?: string): MixOrderCreatedEvent;
export declare function createMixOrderStagedEvent(data: MixOrderStagedEvent['payload'], tenantId: string, causationId?: string): MixOrderStagedEvent;
export declare function createMixOrderStartedEvent(data: MixOrderStartedEvent['payload'], tenantId: string, causationId?: string): MixOrderStartedEvent;
export declare function createMixOrderCompletedEvent(data: MixOrderCompletedEvent['payload'], tenantId: string, causationId?: string): MixOrderCompletedEvent;
export declare function createMixOrderAbortedEvent(data: MixOrderAbortedEvent['payload'], tenantId: string, causationId?: string): MixOrderAbortedEvent;
export declare function createBatchCreatedEvent(data: BatchCreatedEvent['payload'], tenantId: string, causationId?: string): BatchCreatedEvent;
export declare function createBatchReleasedEvent(data: BatchReleasedEvent['payload'], tenantId: string, causationId?: string): BatchReleasedEvent;
export declare function createBatchQuarantinedEvent(data: BatchQuarantinedEvent['payload'], tenantId: string, causationId?: string): BatchQuarantinedEvent;
export declare function createBatchRejectedEvent(data: BatchRejectedEvent['payload'], tenantId: string, causationId?: string): BatchRejectedEvent;
export declare function createMobileRunStartedEvent(data: MobileRunStartedEvent['payload'], tenantId: string, correlationId?: string): MobileRunStartedEvent;
export declare function createMobileRunFinishedEvent(data: MobileRunFinishedEvent['payload'], tenantId: string, causationId?: string): MobileRunFinishedEvent;
export declare function createCleaningPerformedEvent(data: CleaningPerformedEvent['payload'], tenantId: string, causationId?: string): CleaningPerformedEvent;
export declare function createFlushPerformedEvent(data: FlushPerformedEvent['payload'], tenantId: string, causationId?: string): FlushPerformedEvent;
export declare function createCalibrationCheckedEvent(data: CalibrationCheckedEvent['payload'], tenantId: string, causationId?: string): CalibrationCheckedEvent;
export declare function createSamplingAddedEvent(data: SamplingAddedEvent['payload'], tenantId: string, causationId?: string): SamplingAddedEvent;
export declare function createSamplingResultRecordedEvent(data: SamplingResultRecordedEvent['payload'], tenantId: string, causationId?: string): SamplingResultRecordedEvent;
export declare function createNonConformityCreatedEvent(data: NonConformityCreatedEvent['payload'], tenantId: string, causationId?: string): NonConformityCreatedEvent;
export declare function createCAPACreatedEvent(data: CAPACreatedEvent['payload'], tenantId: string, causationId?: string): CAPACreatedEvent;
export declare function createCAPAClosedEvent(data: CAPAClosedEvent['payload'], tenantId: string, causationId?: string): CAPAClosedEvent;
export declare function createCorrelatedEvent<T extends {
    eventId: string;
    causationId?: string;
}>(eventFactory: (correlationId?: string) => T, causationEvent?: {
    eventId: string;
}): T;
export declare function validateEventPayload<T>(schema: any, payload: T): {
    valid: boolean;
    errors?: string[];
};
//# sourceMappingURL=event-factories.d.ts.map