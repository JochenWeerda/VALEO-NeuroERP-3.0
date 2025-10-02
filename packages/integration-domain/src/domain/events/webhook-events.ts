/**
 * Webhook Domain Events
 */

import { BaseDomainEvent } from './base-domain-event.js';
import type { WebhookId } from '../values/webhook-id.js';

export class WebhookCreatedEvent extends BaseDomainEvent {
  constructor(
    webhookId: WebhookId,
    name: string,
    url: string,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'webhook.created',
      webhookId.value,
      1,
      { ...metadata, name, url }
    );
  }

  getData(): Record<string, unknown> {
    return {
      webhookId: this.aggregateId,
      name: this.metadata.name,
      url: this.metadata.url
    };
  }
}

export class WebhookTriggeredEvent extends BaseDomainEvent {
  constructor(
    webhookId: WebhookId,
    payload: Record<string, unknown>,
    response: Record<string, unknown>,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'webhook.triggered',
      webhookId.value,
      1,
      { ...metadata, payload, response }
    );
  }

  getData(): Record<string, unknown> {
    return {
      webhookId: this.aggregateId,
      payload: this.metadata.payload,
      response: this.metadata.response
    };
  }
}

export class WebhookFailedEvent extends BaseDomainEvent {
  constructor(
    webhookId: WebhookId,
    error: string,
    retryCount: number,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'webhook.failed',
      webhookId.value,
      1,
      { ...metadata, error, retryCount }
    );
  }

  getData(): Record<string, unknown> {
    return {
      webhookId: this.aggregateId,
      error: this.metadata.error,
      retryCount: this.metadata.retryCount
    };
  }
}
