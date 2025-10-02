/**
 * VALEO NeuroERP 3.0 - Webhook Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
import { WebhookId } from '@packages/data-models/branded-types';
import { DomainEvent } from '@packages/data-models/domain-events';
export interface Webhook {
    readonly id: WebhookId;
    name: string;
    status?: string;
    url: string;
    events: string[];
    secret?: string;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
export interface CreateWebhookCommand {
    name: string;
    status?: string;
    url: string;
    events: string[];
    secret?: string;
}
export interface UpdateWebhookCommand {
    name?: string;
    status?: string;
    url?: string;
    events?: string[];
    secret?: string;
}
export declare class WebhookCreatedEvent implements DomainEvent {
    readonly webhook: Webhook;
    readonly type = "WebhookCreated";
    readonly aggregateId: WebhookId;
    readonly occurredAt: Date;
    constructor(webhook: Webhook);
}
export declare class WebhookUpdatedEvent implements DomainEvent {
    readonly webhook: Webhook;
    readonly changes: Record<string, any>;
    readonly type = "WebhookUpdated";
    readonly aggregateId: WebhookId;
    readonly occurredAt: Date;
    constructor(webhook: Webhook, changes: Record<string, any>);
}
export declare class WebhookEntity implements Webhook {
    readonly id: WebhookId;
    name: string;
    status?: string;
    url: string;
    events: string[];
    secret?: string;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    private constructor();
    static create(command: CreateWebhookCommand): WebhookEntity;
    update(command: UpdateWebhookCommand): WebhookEntity;
    isActive(): boolean;
    private static validateCreateCommand;
    private static validateUpdateCommand;
}
//***REMOVED*** sourceMappingURL=webhook.d.ts.map