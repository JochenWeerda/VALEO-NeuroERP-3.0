/**
 * Integration Domain Events
 */
import { BaseDomainEvent } from './base-domain-event.js';
import type { IntegrationId } from '../values/integration-id.js';
export declare class IntegrationCreatedEvent extends BaseDomainEvent {
    constructor(integrationId: IntegrationId, name: string, type: string, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
export declare class IntegrationUpdatedEvent extends BaseDomainEvent {
    constructor(integrationId: IntegrationId, changes: Record<string, unknown>, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
export declare class IntegrationDeletedEvent extends BaseDomainEvent {
    constructor(integrationId: IntegrationId, reason: string, metadata?: Record<string, unknown>);
    getData(): Record<string, unknown>;
}
//# sourceMappingURL=integration-events.d.ts.map