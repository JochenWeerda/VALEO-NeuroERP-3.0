/**
 * Sync Job Entity
 */
import { SyncJobId } from '../values/sync-job-id.js';
import { SyncJobCreatedEvent, SyncJobStartedEvent, SyncJobCompletedEvent, SyncJobFailedEvent } from '../events/sync-job-events.js';
export class SyncJob {
    props;
    _events = [];
    constructor(props) {
        this.props = props;
    }
    // Factory method
    static create(name, integrationId, config, createdBy, description, tags = []) {
        const now = new Date();
        const id = SyncJobId.create();
        const syncJob = new SyncJob({
            id,
            name,
            integrationId,
            config,
            status: 'pending',
            recordsProcessed: 0,
            isActive: true,
            description,
            tags,
            createdAt: now,
            updatedAt: now,
            createdBy,
            updatedBy: createdBy
        });
        syncJob._events.push(new SyncJobCreatedEvent(id, name, config.source.type, config.target.type, {
            integrationId,
            config,
            description,
            tags,
            createdBy
        }));
        return syncJob;
    }
    // Getters
    get id() {
        return this.props.id.value;
    }
    get name() {
        return this.props.name;
    }
    get integrationId() {
        return this.props.integrationId;
    }
    get config() {
        return { ...this.props.config };
    }
    get status() {
        return this.props.status;
    }
    get lastRun() {
        return this.props.lastRun;
    }
    get nextRun() {
        return this.props.nextRun;
    }
    get recordsProcessed() {
        return this.props.recordsProcessed;
    }
    get errorMessage() {
        return this.props.errorMessage;
    }
    get isActive() {
        return this.props.isActive;
    }
    get description() {
        return this.props.description;
    }
    get tags() {
        return [...this.props.tags];
    }
    get createdAt() {
        return this.props.createdAt;
    }
    get updatedAt() {
        return this.props.updatedAt;
    }
    get createdBy() {
        return this.props.createdBy;
    }
    get updatedBy() {
        return this.props.updatedBy;
    }
    // Business methods
    start(updatedBy) {
        if (!this.props.isActive) {
            throw new Error('Cannot start inactive sync job');
        }
        if (this.props.status === 'running') {
            throw new Error('Sync job is already running');
        }
        this.props.status = 'running';
        this.props.lastRun = new Date();
        this.props.errorMessage = undefined;
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new SyncJobStartedEvent(this.props.id, {
            updatedBy
        }));
    }
    complete(recordsProcessed, duration, updatedBy) {
        if (this.props.status !== 'running') {
            throw new Error('Cannot complete sync job that is not running');
        }
        this.props.status = 'completed';
        this.props.recordsProcessed += recordsProcessed;
        this.props.errorMessage = undefined;
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new SyncJobCompletedEvent(this.props.id, recordsProcessed, duration, {
            updatedBy,
            totalRecords: this.props.recordsProcessed
        }));
    }
    fail(error, updatedBy) {
        this.props.status = 'failed';
        this.props.errorMessage = error;
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new SyncJobFailedEvent(this.props.id, error, {
            updatedBy
        }));
    }
    cancel(updatedBy) {
        if (this.props.status === 'completed') {
            throw new Error('Cannot cancel completed sync job');
        }
        this.props.status = 'cancelled';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
    }
    scheduleNextRun(nextRun, updatedBy) {
        this.props.nextRun = nextRun;
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
    }
    activate(updatedBy) {
        if (this.props.status === 'failed') {
            throw new Error('Cannot activate sync job with error status');
        }
        this.props.isActive = true;
        this.props.status = 'pending';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
    }
    deactivate(updatedBy) {
        this.props.isActive = false;
        this.props.status = 'cancelled';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
    }
    // Domain events
    getUncommittedEvents() {
        return [...this._events];
    }
    markEventsAsCommitted() {
        this._events = [];
    }
    // Serialization
    toJSON() {
        return {
            id: this.props.id.value,
            name: this.props.name,
            integrationId: this.props.integrationId,
            config: this.props.config,
            status: this.props.status,
            lastRun: this.props.lastRun?.toISOString(),
            nextRun: this.props.nextRun?.toISOString(),
            recordsProcessed: this.props.recordsProcessed,
            errorMessage: this.props.errorMessage,
            isActive: this.props.isActive,
            description: this.props.description,
            tags: this.props.tags,
            createdAt: this.props.createdAt.toISOString(),
            updatedAt: this.props.updatedAt.toISOString(),
            createdBy: this.props.createdBy,
            updatedBy: this.props.updatedBy
        };
    }
    static fromJSON(data) {
        return new SyncJob({
            id: SyncJobId.fromString(data.id),
            name: data.name,
            integrationId: data.integrationId,
            config: data.config,
            status: data.status,
            lastRun: data.lastRun ? new Date(data.lastRun) : undefined,
            nextRun: data.nextRun ? new Date(data.nextRun) : undefined,
            recordsProcessed: data.recordsProcessed,
            errorMessage: data.errorMessage,
            isActive: data.isActive,
            description: data.description,
            tags: data.tags,
            createdAt: new Date(data.createdAt),
            updatedAt: new Date(data.updatedAt),
            createdBy: data.createdBy,
            updatedBy: data.updatedBy
        });
    }
}
//# sourceMappingURL=sync-job.js.map