/**
 * VALEO NeuroERP 3.0 - SyncJob Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
import { SyncJobId } from '@valero-neuroerp/data-models/branded-types';
import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';
export interface SyncJob {
    readonly id: SyncJobId;
    name: string;
    status?: string;
    source: string;
    target: string;
    lastSync?: Date;
    errorMessage?: string;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
export interface CreateSyncJobCommand {
    name: string;
    status?: string;
    source: string;
    target: string;
    lastSync?: Date;
    errorMessage?: string;
}
export interface UpdateSyncJobCommand {
    name?: string;
    status?: string;
    source?: string;
    target?: string;
    lastSync?: Date;
    errorMessage?: string;
}
export declare class SyncJobCreatedEvent implements DomainEvent {
    id: string;
    aggregateType: string;
    version: number;
    occurredOn: Date;
    data: {
        syncJobId: SyncJobId;
        syncjob: SyncJob;
    };
    constructor(syncjob: SyncJob);
}
export declare class SyncJobUpdatedEvent implements DomainEvent {
    id: string;
    aggregateType: string;
    version: number;
    occurredOn: Date;
    data: {
        syncJobId: SyncJobId;
        syncjob: SyncJob;
        changes: Record<string, any>;
    };
    constructor(syncjob: SyncJob, changes: Record<string, any>);
}
export declare class SyncJobEntity implements SyncJob {
    readonly id: SyncJobId;
    name: string;
    status?: string;
    source: string;
    target: string;
    lastSync?: Date;
    errorMessage?: string;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    private constructor();
    static create(command: CreateSyncJobCommand): SyncJobEntity;
    update(command: UpdateSyncJobCommand): SyncJobEntity;
    isActive(): boolean;
    private static validateCreateCommand;
    private static validateUpdateCommand;
}
//# sourceMappingURL=syncjob.d.ts.map