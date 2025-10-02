/**
 * Base Domain Event for VALEO NeuroERP 3.0
 * Foundation for all domain events
 */
export class BaseDomainEvent {
    id;
    aggregateId;
    eventType;
    occurredAt;
    version;
    causationId;
    correlationId;
    metadata;
    constructor(aggregateId, eventType, version = 1, causationId, correlationId, metadata = {}) {
        this.id = this.generateEventId();
        this.aggregateId = aggregateId;
        this.eventType = eventType;
        this.occurredAt = new Date();
        this.version = version;
        this.causationId = causationId;
        this.correlationId = correlationId;
        this.metadata = { ...metadata };
    }
    generateEventId() {
        return `${this.eventType}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    getEventData() {
        const data = {};
        // Extract all properties except the base event properties
        const baseProperties = ['id', 'aggregateId', 'eventType', 'occurredAt', 'version', 'causationId', 'correlationId', 'metadata'];
        for (const [key, value] of Object.entries(this)) {
            if (!baseProperties.includes(key)) {
                data[key] = value;
            }
        }
        return data;
    }
    toString() {
        return JSON.stringify({
            id: this.id,
            aggregateId: this.aggregateId,
            eventType: this.eventType,
            occurredAt: this.occurredAt.toISOString(),
            version: this.version,
            causationId: this.causationId,
            correlationId: this.correlationId,
            metadata: this.metadata,
            data: this.getEventData()
        });
    }
}
//# sourceMappingURL=base-domain-event.js.map