/**
 * Base Domain Event
 */
import { generateId } from '@shared/utils/id-generator.js';
export class BaseDomainEvent {
    eventId;
    eventType;
    aggregateId;
    version;
    occurredAt;
    metadata;
    constructor(eventType, aggregateId, version = 1, metadata = {}) {
        this.eventId = generateId();
        this.eventType = eventType;
        this.aggregateId = aggregateId;
        this.version = version;
        this.occurredAt = new Date();
        this.metadata = metadata;
    }
    toJSON() {
        return {
            eventId: this.eventId,
            eventType: this.eventType,
            aggregateId: this.aggregateId,
            version: this.version,
            occurredAt: this.occurredAt.toISOString(),
            metadata: this.metadata,
            data: this.getData()
        };
    }
}
//# sourceMappingURL=base-domain-event.js.map