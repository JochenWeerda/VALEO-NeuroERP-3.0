/**
 * Integration Entity
 */
import type { BaseEntity, EntityStatus } from '@shared/types/common.js';
import { IntegrationId } from '../values/integration-id.js';
import { IntegrationCreatedEvent, IntegrationUpdatedEvent } from '../events/integration-events.js';
export type IntegrationType = 'api' | 'webhook' | 'file' | 'database' | 'message-queue';
export interface IntegrationConfig {
    endpoint?: string;
    credentials?: Record<string, string>;
    headers?: Record<string, string>;
    timeout?: number;
    retryPolicy?: {
        maxRetries: number;
        backoffMs: number;
    };
    [key: string]: unknown;
}
export interface IntegrationProps {
    id: IntegrationId;
    name: string;
    type: IntegrationType;
    status: EntityStatus;
    config: IntegrationConfig;
    description?: string;
    tags: string[];
    isActive: boolean;
    createdAt: Date;
    updatedAt: Date;
    createdBy: string;
    updatedBy: string;
}
export declare class Integration implements BaseEntity {
    private props;
    private _events;
    constructor(props: IntegrationProps);
    static create(name: string, type: IntegrationType, config: IntegrationConfig, createdBy: string, description?: string, tags?: string[]): Integration;
    get id(): string;
    get name(): string;
    get type(): IntegrationType;
    get status(): EntityStatus;
    get config(): IntegrationConfig;
    get description(): string | undefined;
    get tags(): string[];
    get isActive(): boolean;
    get createdAt(): Date;
    get updatedAt(): Date;
    get createdBy(): string;
    get updatedBy(): string;
    updateConfig(config: IntegrationConfig, updatedBy: string): void;
    activate(updatedBy: string): void;
    deactivate(updatedBy: string): void;
    markAsError(error: string, updatedBy: string): void;
    getUncommittedEvents(): Array<IntegrationCreatedEvent | IntegrationUpdatedEvent>;
    markEventsAsCommitted(): void;
    toJSON(): Record<string, unknown>;
    static fromJSON(data: Record<string, unknown>): Integration;
}
//# sourceMappingURL=integration.d.ts.map