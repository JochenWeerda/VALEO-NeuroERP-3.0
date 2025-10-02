/**
 * VALEO NeuroERP 3.0 - SyncJob Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */

import { SyncJobId, createSyncJobId } from '@packages/data-models/branded-types';
import { DomainEvent } from '@packages/data-models/domain-events';

export interface SyncJob {
  readonly id: SyncJobId;
  name: string;
  status?: string;
  source: string;
  target: string;
  lastSync?: Date;
  errorMessage?: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}

export interface CreateSyncJobCommand {
  name: string;
  status?: string;
  source: string;
  target: string;
  lastSync?: Date;
  errorMessage?: string;
}

export interface UpdateSyncJobCommand {
  name?: string;
  status?: string;
  source?: string;
  target?: string;
  lastSync?: Date;
  errorMessage?: string;
}

export class SyncJobCreatedEvent implements DomainEvent {
  readonly type = 'SyncJobCreated';
  readonly aggregateId: SyncJobId;
  readonly occurredAt: Date;

  constructor(
    public readonly syncjob: SyncJob
  ) {
    this.aggregateId = syncjob.id;
    this.occurredAt = new Date();
  }
}

export class SyncJobUpdatedEvent implements DomainEvent {
  readonly type = 'SyncJobUpdated';
  readonly aggregateId: SyncJobId;
  readonly occurredAt: Date;

  constructor(
    public readonly syncjob: SyncJob,
    public readonly changes: Record<string, any>
  ) {
    this.aggregateId = syncjob.id;
    this.occurredAt = new Date();
  }
}

export class SyncJobEntity implements SyncJob {
  public readonly id: SyncJobId;
  public name: string;
  public status?: string;
  public source: string;
  public target: string;
  public lastSync?: Date;
  public errorMessage?: string;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;

  private constructor(
    id: SyncJobId,
    name: string,
    status?: string,
    source: string,
    target: string,
    lastSync?: Date,
    errorMessage?: string,
    createdAt: Date,
    updatedAt: Date
  ) {
    this.id = id;
    this.name = name;
    this.status = status;
    this.source = source;
    this.target = target;
    this.lastSync = lastSync;
    this.errorMessage = errorMessage;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
  }

  static create(command: CreateSyncJobCommand): SyncJobEntity {
    // Validate command
    SyncJobEntity.validateCreateCommand(command);

    const id = createSyncJobId(crypto.randomUUID());
    const now = new Date();

    return new SyncJobEntity(
      id,
      command.name ?? '',
      command.status ?? undefined,
      command.source ?? '',
      command.target ?? '',
      command.lastSync ?? new Date(),
      command.errorMessage ?? '',
      now,
      now
    );
  }

  update(command: UpdateSyncJobCommand): SyncJobEntity {
    // Validate command
    SyncJobEntity.validateUpdateCommand(command);

    const changes: Record<string, any> = {};

    if (command.name !== undefined) {
      this.name = command.name;
      changes.name = command.name;
    }
    if (command.status !== undefined) {
      this.status = command.status;
      changes.status = command.status;
    }
    if (command.source !== undefined) {
      this.source = command.source;
      changes.source = command.source;
    }
    if (command.target !== undefined) {
      this.target = command.target;
      changes.target = command.target;
    }
    if (command.lastSync !== undefined) {
      this.lastSync = command.lastSync;
      changes.lastSync = command.lastSync;
    }
    if (command.errorMessage !== undefined) {
      this.errorMessage = command.errorMessage;
      changes.errorMessage = command.errorMessage;
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
  private static validateCreateCommand(command: CreateSyncJobCommand): void {
    if (!command.name || command.name.trim().length === 0) {
      throw new Error('SyncJob name is required');
    }
    // Add additional validation rules here
  }

  private static validateUpdateCommand(command: UpdateSyncJobCommand): void {
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
