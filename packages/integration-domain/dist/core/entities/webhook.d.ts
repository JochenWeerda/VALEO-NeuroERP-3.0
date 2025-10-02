/**
 * VALEO NeuroERP 3.0 - Webhook Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
import { WebhookId } from '@valero-neuroerp/data-models/branded-types';
import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';
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
    id: string;
    aggregateType: string;
    version: number;
    occurredOn: Date;
    data: {
        webhookId: WebhookId;
        webhook: Webhook;
    };
    constructor(webhook: Webhook);
}
export declare class WebhookUpdatedEvent implements DomainEvent {
    id: string;
    aggregateType: string;
    version: number;
    occurredOn: Date;
    data: {
        webhookId: WebhookId;
        webhook: Webhook;
        changes: Record<string, any>;
    };
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
//# sourceMappingURL=webhook.d.ts.map