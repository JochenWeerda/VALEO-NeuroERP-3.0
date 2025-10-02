/**
 * Integration Entity
 */
import { IntegrationId } from '../values/integration-id.js';
import { IntegrationCreatedEvent, IntegrationUpdatedEvent } from '../events/integration-events.js';
export class Integration {
    props;
    _events = [];
    constructor(props) {
        this.props = props;
    }
    // Factory method
    static create(name, type, config, createdBy, description, tags = []) {
        const now = new Date();
        const id = IntegrationId.create();
        const integration = new Integration({
            id,
            name,
            type,
            status: 'pending',
            config,
            description,
            tags,
            isActive: true,
            createdAt: now,
            updatedAt: now,
            createdBy,
            updatedBy: createdBy
        });
        integration._events.push(new IntegrationCreatedEvent(id, name, type, {
            config,
            description,
            tags,
            createdBy
        }));
        return integration;
    }
    // Getters
    get id() {
        return this.props.id.value;
    }
    get name() {
        return this.props.name;
    }
    get type() {
        return this.props.type;
    }
    get status() {
        return this.props.status;
    }
    get config() {
        return { ...this.props.config };
    }
    get description() {
        return this.props.description;
    }
    get tags() {
        return [...this.props.tags];
    }
    get isActive() {
        return this.props.isActive;
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
    updateConfig(config, updatedBy) {
        const oldConfig = this.props.config;
        this.props.config = { ...config };
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new IntegrationUpdatedEvent(this.props.id, { config }, {
            oldConfig,
            updatedBy
        }));
    }
    activate(updatedBy) {
        if (this.props.status === 'error') {
            throw new Error('Cannot activate integration with error status');
        }
        this.props.isActive = true;
        this.props.status = 'active';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new IntegrationUpdatedEvent(this.props.id, { isActive: true, status: 'active' }, {
            updatedBy
        }));
    }
    deactivate(updatedBy) {
        this.props.isActive = false;
        this.props.status = 'inactive';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new IntegrationUpdatedEvent(this.props.id, { isActive: false, status: 'inactive' }, {
            updatedBy
        }));
    }
    markAsError(error, updatedBy) {
        this.props.status = 'error';
        this.props.updatedAt = new Date();
        this.props.updatedBy = updatedBy;
        this._events.push(new IntegrationUpdatedEvent(this.props.id, { status: 'error', error }, {
            updatedBy
        }));
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
            type: this.props.type,
            status: this.props.status,
            config: this.props.config,
            description: this.props.description,
            tags: this.props.tags,
            isActive: this.props.isActive,
            createdAt: this.props.createdAt.toISOString(),
            updatedAt: this.props.updatedAt.toISOString(),
            createdBy: this.props.createdBy,
            updatedBy: this.props.updatedBy
        };
    }
    static fromJSON(data) {
        return new Integration({
            id: IntegrationId.fromString(data.id),
            name: data.name,
            type: data.type,
            status: data.status,
            config: data.config,
            description: data.description,
            tags: data.tags,
            isActive: data.isActive,
            createdAt: new Date(data.createdAt),
            updatedAt: new Date(data.updatedAt),
            createdBy: data.createdBy,
            updatedBy: data.updatedBy
        });
    }
}
//# sourceMappingURL=integration.js.map