/**
 * Webhook Entity
 */

import type { BaseEntity, EntityStatus } from '@shared/types/common.js';
import { WebhookId } from '../values/webhook-id.js';
import { WebhookCreatedEvent, WebhookFailedEvent, WebhookTriggeredEvent } from '../events/webhook-events.js';

export interface WebhookConfig {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  timeout?: number;
  retryPolicy?: {
    maxRetries: number;
    backoffMs: number;
  };
  authentication?: {
    type: 'bearer' | 'basic' | 'api-key';
    credentials: Record<string, string>;
  };
  [key: string]: unknown;
}

export interface WebhookProps {
  id: WebhookId;
  name: string;
  integrationId: string;
  config: WebhookConfig;
  events: string[];
  status: EntityStatus;
  isActive: boolean;
  description?: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy: string;
}

export class Webhook implements BaseEntity {
  private _events: Array<WebhookCreatedEvent | WebhookTriggeredEvent | WebhookFailedEvent> = [];

  constructor(private readonly props: WebhookProps) {}

  // Factory method
  static create(
    name: string,
    integrationId: string,
    config: WebhookConfig,
    events: string[],
    createdBy: string,
    description?: string,
    tags: string[] = []
  ): Webhook {
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

    webhook._events.push(
      new WebhookCreatedEvent(id, name, config.url, {
        integrationId,
        config,
        events,
        description,
        tags,
        createdBy
      })
    );

    return webhook;
  }

  // Getters
  get id(): string {
    return this.props.id.value;
  }

  get name(): string {
    return this.props.name;
  }

  get integrationId(): string {
    return this.props.integrationId;
  }

  get config(): WebhookConfig {
    return { ...this.props.config };
  }

  get events(): string[] {
    return [...this.props.events];
  }

  get status(): EntityStatus {
    return this.props.status;
  }

  get isActive(): boolean {
    return this.props.isActive;
  }

  get description(): string | undefined {
    return this.props.description;
  }

  get tags(): string[] {
    return [...this.props.tags];
  }

  get createdAt(): Date {
    return this.props.createdAt;
  }

  get updatedAt(): Date {
    return this.props.updatedAt;
  }

  get createdBy(): string {
    return this.props.createdBy;
  }

  get updatedBy(): string {
    return this.props.updatedBy;
  }

  // Business methods
  trigger(payload: Record<string, unknown>, updatedBy: string): void {
    if (!this.props.isActive) {
      throw new Error('Cannot trigger inactive webhook');
    }

    if (this.props.status === 'error') {
      throw new Error('Cannot trigger webhook with error status');
    }

    this.props.status = 'active';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new WebhookTriggeredEvent(this.props.id, payload, {}, {
        updatedBy
      })
    );
  }

  markTriggered(payload: Record<string, unknown>, response: Record<string, unknown>, updatedBy: string): void {
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new WebhookTriggeredEvent(this.props.id, payload, response, {
        updatedBy
      })
    );
  }

  markFailed(error: string, retryCount: number, updatedBy: string): void {
    this.props.status = 'error';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new WebhookFailedEvent(this.props.id, error, retryCount, {
        updatedBy
      })
    );
  }

  activate(updatedBy: string): void {
    if (this.props.status === 'error') {
      throw new Error('Cannot activate webhook with error status');
    }

    this.props.isActive = true;
    this.props.status = 'active';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;
  }

  deactivate(updatedBy: string): void {
    this.props.isActive = false;
    this.props.status = 'inactive';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;
  }

  updateConfig(config: WebhookConfig, updatedBy: string): void {
    this.props.config = { ...config };
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;
  }

  // Domain events
  getUncommittedEvents(): Array<WebhookCreatedEvent | WebhookTriggeredEvent | WebhookFailedEvent> {
    return [...this._events];
  }

  markEventsAsCommitted(): void {
    this._events = [];
  }

  // Serialization
  toJSON(): Record<string, unknown> {
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

  static fromJSON(data: Record<string, unknown>): Webhook {
    return new Webhook({
      id: WebhookId.fromString(data.id as string),
      name: data.name as string,
      integrationId: data.integrationId as string,
      config: data.config as WebhookConfig,
      events: data.events as string[],
      status: data.status as EntityStatus,
      isActive: data.isActive as boolean,
      description: data.description as string,
      tags: data.tags as string[],
      createdAt: new Date(data.createdAt as string),
      updatedAt: new Date(data.updatedAt as string),
      createdBy: data.createdBy as string,
      updatedBy: data.updatedBy as string
    });
  }
}
