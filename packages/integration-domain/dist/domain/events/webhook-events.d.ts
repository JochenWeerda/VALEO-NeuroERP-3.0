/**
 * Webhook Domain Events
 */
import { BaseDomainEvent } from './base-domain-event.js';
import type { WebhookId } from '../values/webhook-id.js';
export declare class WebhookCreatedEvent extends BaseDomainEvent {
    constructor(webhookId: WebhookId, name: string, url: string, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
export declare class WebhookTriggeredEvent extends BaseDomainEvent {
    constructor(webhookId: WebhookId, payload: Record<string, unknown>, response: Record<string, unknown>, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
export declare class WebhookFailedEvent extends BaseDomainEvent {
    constructor(webhookId: WebhookId, error: string, retryCount: number, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
//# sourceMappingURL=webhook-events.d.ts.map