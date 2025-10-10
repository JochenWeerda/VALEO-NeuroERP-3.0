/**
 * Integration Entity
 */

import { generateId } from '@shared/utils/id-generator.js';
import type { BaseEntity, EntityStatus } from '@shared/types/common.js';
import { IntegrationId } from '../values/integration-id.js';
import { IntegrationCreatedEvent, IntegrationUpdatedEvent } from '../events/integration-events.js';

export type IntegrationType = 'api' | 'webhook' | 'file' | 'database' | 'message-queue';

export interface IntegrationConfig {
  endpoint?: string;
  credentials?: Record<string, string>;
  headers?: Record<string, string>;
  timeout?: number;
  retryPolicy?: {
    maxRetries: number;
    backoffMs: number;
  };
  [key: string]: unknown;
}

export interface IntegrationProps {
  id: IntegrationId;
  name: string;
  type: IntegrationType;
  status: EntityStatus;
  config: IntegrationConfig;
  description?: string;
  tags: string[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy: string;
}

export class Integration implements BaseEntity {
  private _events: Array<IntegrationCreatedEvent | IntegrationUpdatedEvent> = [];

  constructor(private readonly props: IntegrationProps) {}

  // Factory method
  static create(
    name: string,
    type: IntegrationType,
    config: IntegrationConfig,
    createdBy: string,
    description?: string,
    tags: string[] = []
  ): Integration {
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

    integration._events.push(
      new IntegrationCreatedEvent(id, name, type, {
        config,
        description,
        tags,
        createdBy
      })
    );

    return integration;
  }

  // Getters
  get id(): string {
    return this.props.id.value;
  }

  get name(): string {
    return this.props.name;
  }

  get type(): IntegrationType {
    return this.props.type;
  }

  get status(): EntityStatus {
    return this.props.status;
  }

  get config(): IntegrationConfig {
    return { ...this.props.config };
  }

  get description(): string | undefined {
    return this.props.description;
  }

  get tags(): string[] {
    return [...this.props.tags];
  }

  get isActive(): boolean {
    return this.props.isActive;
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
  updateConfig(config: IntegrationConfig, updatedBy: string): void {
    const oldConfig = this.props.config;
    this.props.config = { ...config };
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new IntegrationUpdatedEvent(this.props.id, { config }, {
        oldConfig,
        updatedBy
      })
    );
  }

  activate(updatedBy: string): void {
    if (this.props.status === 'error') {
      throw new Error('Cannot activate integration with error status');
    }

    this.props.isActive = true;
    this.props.status = 'active';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new IntegrationUpdatedEvent(this.props.id, { isActive: true, status: 'active' }, {
        updatedBy
      })
    );
  }

  deactivate(updatedBy: string): void {
    this.props.isActive = false;
    this.props.status = 'inactive';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new IntegrationUpdatedEvent(this.props.id, { isActive: false, status: 'inactive' }, {
        updatedBy
      })
    );
  }

  markAsError(error: string, updatedBy: string): void {
    this.props.status = 'error';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new IntegrationUpdatedEvent(this.props.id, { status: 'error', error }, {
        updatedBy
      })
    );
  }

  // Domain events
  getUncommittedEvents(): Array<IntegrationCreatedEvent | IntegrationUpdatedEvent> {
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

  static fromJSON(data: Record<string, unknown>): Integration {
    return new Integration({
      id: IntegrationId.fromString(data.id as string),
      name: data.name as string,
      type: data.type as IntegrationType,
      status: data.status as EntityStatus,
      config: data.config as IntegrationConfig,
      description: data.description as string,
      tags: data.tags as string[],
      isActive: data.isActive as boolean,
      createdAt: new Date(data.createdAt as string),
      updatedAt: new Date(data.updatedAt as string),
      createdBy: data.createdBy as string,
      updatedBy: data.updatedBy as string
    });
  }
}
