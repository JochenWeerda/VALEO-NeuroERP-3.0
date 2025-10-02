/**
 * Sync Job Domain Events
 */
import { BaseDomainEvent } from './base-domain-event.js';
import type { SyncJobId } from '../values/sync-job-id.js';
export declare class SyncJobCreatedEvent extends BaseDomainEvent {
    constructor(syncJobId: SyncJobId, name: string, source: string, target: string, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
export declare class SyncJobStartedEvent extends BaseDomainEvent {
    constructor(syncJobId: SyncJobId, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
export declare class SyncJobCompletedEvent extends BaseDomainEvent {
    constructor(syncJobId: SyncJobId, recordsProcessed: number, duration: number, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
export declare class SyncJobFailedEvent extends BaseDomainEvent {
    constructor(syncJobId: SyncJobId, error: string, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
//# sourceMappingURL=sync-job-events.d.ts.map