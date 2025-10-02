/**
 * Webhook Domain Events
 */
import { BaseDomainEvent } from './base-domain-event.js';
export class WebhookCreatedEvent extends BaseDomainEvent {
    constructor(webhookId, name, url, metadata = {}) {
        super('webhook.created', webhookId.value, 1, { ...metadata, name, url });
    }
    getData() {
        return {
            webhookId: this.aggregateId,
            name: this.metadata.name,
            url: this.metadata.url
        };
    }
}
export class WebhookTriggeredEvent extends BaseDomainEvent {
    constructor(webhookId, payload, response, metadata = {}) {
        super('webhook.triggered', webhookId.value, 1, { ...metadata, payload, response });
    }
    getData() {
        return {
            webhookId: this.aggregateId,
            payload: this.metadata.payload,
            response: this.metadata.response
        };
    }
}
export class WebhookFailedEvent extends BaseDomainEvent {
    constructor(webhookId, error, retryCount, metadata = {}) {
        super('webhook.failed', webhookId.value, 1, { ...metadata, error, retryCount });
    }
    getData() {
        return {
            webhookId: this.aggregateId,
            error: this.metadata.error,
            retryCount: this.metadata.retryCount
        };
    }
}
//# sourceMappingURL=webhook-events.js.map