/**
 * Webhook Entity
 */
import type { BaseEntity, EntityStatus } from '@shared/types/common.js';
import { WebhookId } from '../values/webhook-id.js';
import { WebhookCreatedEvent, WebhookTriggeredEvent, WebhookFailedEvent } from '../events/webhook-events.js';
export interface WebhookConfig {
    url: string;
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    headers?: Record<string, string>;
    timeout?: number;
    retryPolicy?: {
        maxRetries: number;
        backoffMs: number;
    };
    authentication?: {
        type: 'bearer' | 'basic' | 'api-key';
        credentials: Record<string, string>;
    };
    [key: string]: unknown;
}
export interface WebhookProps {
    id: WebhookId;
    name: string;
    integrationId: string;
    config: WebhookConfig;
    events: string[];
    status: EntityStatus;
    isActive: boolean;
    description?: string;
    tags: string[];
    createdAt: Date;
    updatedAt: Date;
    createdBy: string;
    updatedBy: string;
}
export declare class Webhook implements BaseEntity {
    private props;
    private _events;
    constructor(props: WebhookProps);
    static create(name: string, integrationId: string, config: WebhookConfig, events: string[], createdBy: string, description?: string, tags?: string[]): Webhook;
    get id(): string;
    get name(): string;
    get integrationId(): string;
    get config(): WebhookConfig;
    get events(): string[];
    get status(): EntityStatus;
    get isActive(): boolean;
    get description(): string | undefined;
    get tags(): string[];
    get createdAt(): Date;
    get updatedAt(): Date;
    get createdBy(): string;
    get updatedBy(): string;
    trigger(payload: Record<string, unknown>, updatedBy: string): void;
    markTriggered(payload: Record<string, unknown>, response: Record<string, unknown>, updatedBy: string): void;
    markFailed(error: string, retryCount: number, updatedBy: string): void;
    activate(updatedBy: string): void;
    deactivate(updatedBy: string): void;
    updateConfig(config: WebhookConfig, updatedBy: string): void;
    getUncommittedEvents(): Array<WebhookCreatedEvent | WebhookTriggeredEvent | WebhookFailedEvent>;
    markEventsAsCommitted(): void;
    toJSON(): Record<string, unknown>;
    static fromJSON(data: Record<string, unknown>): Webhook;
}
//# sourceMappingURL=webhook.d.ts.map