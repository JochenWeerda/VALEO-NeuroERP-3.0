/**
 * Webhook Entity
 */
import { WebhookId } from '../values/webhook-id.js';
import { WebhookCreatedEvent, WebhookTriggeredEvent, WebhookFailedEvent } from '../events/webhook-events.js';
export class Webhook {
    props;
    _events = [];
    constructor(props) {
        this.props = props;
    }
    // Factory method
    static create(name, integrationId, config, events, createdBy, description, tags = []) {
        const now = new Date();
        const id = WebhookId.create();
        const webhook = new Webhook({
            id,
            name,
            integrationId,
            config,
            events,
            status: 'pending',
            isActive: true,
            description,
            tags,
            createdAt: now,
            updatedAt: now,
            createdBy,
            updatedBy: createdBy
        });
        webhook._events.push(new WebhookCreatedEvent(id, name, config.url, {
            integrationId,
            config,
            events,
            description,
            tags,
            createdBy
        }));
        return webhook;
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
    get events() {
        return [...this.props.events];
    }
    get status() {
        return this.props.status;
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
    trigger(payload, updatedBy) {
        if (!this.props.isActive) {
            throw new Error('Cannot trigger inactive webhook');
        }
        if (this.props.status === 'error') {
            throw new Error('Cannot trigger webhook with error status');
        }
        this.props.status = 'active';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new WebhookTriggeredEvent(this.props.id, payload, {}, {
            updatedBy
        }));
    }
    markTriggered(payload, response, updatedBy) {
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new WebhookTriggeredEvent(this.props.id, payload, response, {
            updatedBy
        }));
    }
    markFailed(error, retryCount, updatedBy) {
        this.props.status = 'error';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new WebhookFailedEvent(this.props.id, error, retryCount, {
            updatedBy
        }));
    }
    activate(updatedBy) {
        if (this.props.status === 'error') {
            throw new Error('Cannot activate webhook with error status');
        }
        this.props.isActive = true;
        this.props.status = 'active';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
    }
    deactivate(updatedBy) {
        this.props.isActive = false;
        this.props.status = 'inactive';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
    }
    updateConfig(config, updatedBy) {
        this.props.config = { ...config };
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
            events: this.props.events,
            status: this.props.status,
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
        return new Webhook({
            id: WebhookId.fromString(data.id),
            name: data.name,
            integrationId: data.integrationId,
            config: data.config,
            events: data.events,
            status: data.status,
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
//# sourceMappingURL=webhook.js.map