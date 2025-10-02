/**
 * Integration Domain Events
 */

import { BaseDomainEvent } from './base-domain-event.js';
import type { IntegrationId } from '../values/integration-id.js';

export class IntegrationCreatedEvent extends BaseDomainEvent {
  constructor(
    integrationId: IntegrationId,
    name: string,
    type: string,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'integration.created',
      integrationId.value,
      1,
      metadata
    );
  }

  getData(): Record<string, unknown> {
    return {
      integrationId: this.aggregateId,
      name: this.metadata.name,
      type: this.metadata.type
    };
  }
}

export class IntegrationUpdatedEvent extends BaseDomainEvent {
  constructor(
    integrationId: IntegrationId,
    changes: Record<string, unknown>,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'integration.updated',
      integrationId.value,
      1,
      { ...metadata, changes }
    );
  }

  getData(): Record<string, unknown> {
    return {
      integrationId: this.aggregateId,
      changes: this.metadata.changes
    };
  }
}

export class IntegrationDeletedEvent extends BaseDomainEvent {
  constructor(
    integrationId: IntegrationId,
    reason: string,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'integration.deleted',
      integrationId.value,
      1,
      { ...metadata, reason }
    );
  }

  getData(): Record<string, unknown> {
    return {
      integrationId: this.aggregateId,
      reason: this.metadata.reason
    };
  }
}
