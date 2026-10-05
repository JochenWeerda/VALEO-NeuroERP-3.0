/**
 * VALEO NeuroERP 3.0 - Webhook Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */

import { WebhookId, createWebhookId } from '@packages/data-models/branded-types';
import { DomainEvent } from '@packages/data-models/domain-events';

export interface Webhook {
  readonly id: WebhookId;
  name: string;
  status?: string;
  url: string;
  events: string[];
  secret?: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}

export interface CreateWebhookCommand {
  name: string;
  status?: string;
  url: string;
  events: string[];
  secret?: string;
}

export interface UpdateWebhookCommand {
  name?: string;
  status?: string;
  url?: string;
  events?: string[];
  secret?: string;
}

export class WebhookCreatedEvent implements DomainEvent {
  readonly type = 'WebhookCreated';
  readonly aggregateId: WebhookId;
  readonly occurredAt: Date;

  constructor(
    public readonly webhook: Webhook
  ) {
    this.aggregateId = webhook.id;
    this.occurredAt = new Date();
  }
}

export class WebhookUpdatedEvent implements DomainEvent {
  readonly type = 'WebhookUpdated';
  readonly aggregateId: WebhookId;
  readonly occurredAt: Date;

  constructor(
    public readonly webhook: Webhook,
    public readonly changes: Record<string, any>
  ) {
    this.aggregateId = webhook.id;
    this.occurredAt = new Date();
  }
}

export class WebhookEntity implements Webhook {
  public readonly id: WebhookId;
  public name: string;
  public status?: string;
  public url: string;
  public events: string[];
  public secret?: string;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;

  private constructor(
    id: WebhookId,
    name: string,
    status?: string,
    url: string,
    events: string[],
    secret?: string,
    createdAt: Date,
    updatedAt: Date
  ) {
    this.id = id;
    this.name = name;
    this.status = status;
    this.url = url;
    this.events = events;
    this.secret = secret;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
  }

  static create(command: CreateWebhookCommand): WebhookEntity {
    // Validate command
    WebhookEntity.validateCreateCommand(command);

    const id = createWebhookId(crypto.randomUUID());
    const now = new Date();

    return new WebhookEntity(
      id,
      command.name ?? '',
      command.status ?? undefined,
      command.url ?? '',
      command.events ?? undefined,
      command.secret ?? '',
      now,
      now
    );
  }

  update(command: UpdateWebhookCommand): WebhookEntity {
    // Validate command
    WebhookEntity.validateUpdateCommand(command);

    const changes: Record<string, any> = {};

    if (command.name !== undefined) {
      this.name = command.name;
      changes.name = command.name;
    }
    if (command.status !== undefined) {
      this.status = command.status;
      changes.status = command.status;
    }
    if (command.url !== undefined) {
      this.url = command.url;
      changes.url = command.url;
    }
    if (command.events !== undefined) {
      this.events = command.events;
      changes.events = command.events;
    }
    if (command.secret !== undefined) {
      this.secret = command.secret;
      changes.secret = command.secret;
    }

    (this as any).updatedAt = new Date();
    changes.updatedAt = this.updatedAt;

    return this;
  }

  // Business methods
  isActive(): boolean {
    return this.status === 'active';
  }

  // Validation methods
  private static validateCreateCommand(command: CreateWebhookCommand): void {
    if (!command.name || command.name.trim().length === 0) {
      throw new Error('Webhook name is required');
    }
    // Add additional validation rules here
  }

  private static validateUpdateCommand(command: UpdateWebhookCommand): void {
    // Add update validation rules here
  }
}

// Utility functions
function getDefaultValue(type: string): any {
  switch (type) {
    case 'string': return '';
    case 'number': return 0;
    case 'boolean': return false;
    case 'Date': return new Date();
    default: return null;
  }
}
