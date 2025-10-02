/**
 * Sync Job Entity
 */
import type { BaseEntity } from '@shared/types/common.js';
import { SyncJobId } from '../values/sync-job-id.js';
import { SyncJobCreatedEvent, SyncJobStartedEvent, SyncJobCompletedEvent, SyncJobFailedEvent } from '../events/sync-job-events.js';
export type SyncJobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export interface SyncJobConfig {
    source: {
        type: 'database' | 'api' | 'file' | 'message-queue';
        connection: Record<string, unknown>;
        query?: string;
        filters?: Record<string, unknown>;
    };
    target: {
        type: 'database' | 'api' | 'file' | 'message-queue';
        connection: Record<string, unknown>;
        mapping?: Record<string, string>;
        batchSize?: number;
    };
    schedule?: {
        cron?: string;
        interval?: number;
        timezone?: string;
    };
    retryPolicy?: {
        maxRetries: number;
        backoffMs: number;
    };
    [key: string]: unknown;
}
export interface SyncJobProps {
    id: SyncJobId;
    name: string;
    integrationId: string;
    config: SyncJobConfig;
    status: SyncJobStatus;
    lastRun?: Date;
    nextRun?: Date;
    recordsProcessed: number;
    errorMessage?: string;
    isActive: boolean;
    description?: string;
    tags: string[];
    createdAt: Date;
    updatedAt: Date;
    createdBy: string;
    updatedBy: string;
}
export declare class SyncJob implements BaseEntity {
    private props;
    private _events;
    constructor(props: SyncJobProps);
    static create(name: string, integrationId: string, config: SyncJobConfig, createdBy: string, description?: string, tags?: string[]): SyncJob;
    get id(): string;
    get name(): string;
    get integrationId(): string;
    get config(): SyncJobConfig;
    get status(): SyncJobStatus;
    get lastRun(): Date | undefined;
    get nextRun(): Date | undefined;
    get recordsProcessed(): number;
    get errorMessage(): string | undefined;
    get isActive(): boolean;
    get description(): string | undefined;
    get tags(): string[];
    get createdAt(): Date;
    get updatedAt(): Date;
    get createdBy(): string;
    get updatedBy(): string;
    start(updatedBy: string): void;
    complete(recordsProcessed: number, duration: number, updatedBy: string): void;
    fail(error: string, updatedBy: string): void;
    cancel(updatedBy: string): void;
    scheduleNextRun(nextRun: Date, updatedBy: string): void;
    activate(updatedBy: string): void;
    deactivate(updatedBy: string): void;
    getUncommittedEvents(): Array<SyncJobCreatedEvent | SyncJobStartedEvent | SyncJobCompletedEvent | SyncJobFailedEvent>;
    markEventsAsCommitted(): void;
    toJSON(): Record<string, unknown>;
    static fromJSON(data: Record<string, unknown>): SyncJob;
}
//# sourceMappingURL=sync-job.d.ts.map