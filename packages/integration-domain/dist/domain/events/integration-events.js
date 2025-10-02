/**
 * Integration Domain Events
 */
import { BaseDomainEvent } from './base-domain-event.js';
export class IntegrationCreatedEvent extends BaseDomainEvent {
    constructor(integrationId, name, type, metadata = {}) {
        super('integration.created', integrationId.value, 1, metadata);
    }
    getData() {
        return {
            integrationId: this.aggregateId,
            name: this.metadata.name,
            type: this.metadata.type
        };
    }
}
export class IntegrationUpdatedEvent extends BaseDomainEvent {
    constructor(integrationId, changes, metadata = {}) {
        super('integration.updated', integrationId.value, 1, { ...metadata, changes });
    }
    getData() {
        return {
            integrationId: this.aggregateId,
            changes: this.metadata.changes
        };
    }
}
export class IntegrationDeletedEvent extends BaseDomainEvent {
    constructor(integrationId, reason, metadata = {}) {
        super('integration.deleted', integrationId.value, 1, { ...metadata, reason });
    }
    getData() {
        return {
            integrationId: this.aggregateId,
            reason: this.metadata.reason
        };
    }
}
//# sourceMappingURL=integration-events.js.map