/**
 * Sync Job Domain Events
 */
import { BaseDomainEvent } from './base-domain-event.js';
export class SyncJobCreatedEvent extends BaseDomainEvent {
    constructor(syncJobId, name, source, target, metadata = {}) {
        super('syncjob.created', syncJobId.value, 1, { ...metadata, name, source, target });
    }
    getData() {
        return {
            syncJobId: this.aggregateId,
            name: this.metadata.name,
            source: this.metadata.source,
            target: this.metadata.target
        };
    }
}
export class SyncJobStartedEvent extends BaseDomainEvent {
    constructor(syncJobId, metadata = {}) {
        super('syncjob.started', syncJobId.value, 1, metadata);
    }
    getData() {
        return {
            syncJobId: this.aggregateId
        };
    }
}
export class SyncJobCompletedEvent extends BaseDomainEvent {
    constructor(syncJobId, recordsProcessed, duration, metadata = {}) {
        super('syncjob.completed', syncJobId.value, 1, { ...metadata, recordsProcessed, duration });
    }
    getData() {
        return {
            syncJobId: this.aggregateId,
            recordsProcessed: this.metadata.recordsProcessed,
            duration: this.metadata.duration
        };
    }
}
export class SyncJobFailedEvent extends BaseDomainEvent {
    constructor(syncJobId, error, metadata = {}) {
        super('syncjob.failed', syncJobId.value, 1, { ...metadata, error });
    }
    getData() {
        return {
            syncJobId: this.aggregateId,
            error: this.metadata.error
        };
    }
}
//# sourceMappingURL=sync-job-events.js.map