/**
 * VALEO NeuroERP 3.0 - SyncJob Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
import { SyncJobId } from '@packages/data-models/branded-types';
import { DomainEvent } from '@packages/data-models/domain-events';
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
    readonly syncjob: SyncJob;
    readonly type = "SyncJobCreated";
    readonly aggregateId: SyncJobId;
    readonly occurredAt: Date;
    constructor(syncjob: SyncJob);
}
export declare class SyncJobUpdatedEvent implements DomainEvent {
    readonly syncjob: SyncJob;
    readonly changes: Record<string, any>;
    readonly type = "SyncJobUpdated";
    readonly aggregateId: SyncJobId;
    readonly occurredAt: Date;
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
//***REMOVED*** sourceMappingURL=syncjob.d.ts.map