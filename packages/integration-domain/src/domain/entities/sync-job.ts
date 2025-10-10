/**
 * Sync Job Entity
 */

import type { BaseEntity, EntityStatus } from '@shared/types/common.js';
import { SyncJobId } from '../values/sync-job-id.js';
import { SyncJobCompletedEvent, SyncJobCreatedEvent, SyncJobFailedEvent, SyncJobStartedEvent } from '../events/sync-job-events.js';

export type SyncJobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface SyncJobConfig {
  source: {
    type: 'database' | 'api' | 'file' | 'message-queue';
    connection: Record<string, unknown>;
    query?: string;
    filters?: Record<string, unknown>;
  };
  target: {
    type: 'database' | 'api' | 'file' | 'message-queue';
    connection: Record<string, unknown>;
    mapping?: Record<string, string>;
    batchSize?: number;
  };
  schedule?: {
    cron?: string;
    interval?: number;
    timezone?: string;
  };
  retryPolicy?: {
    maxRetries: number;
    backoffMs: number;
  };
  [key: string]: unknown;
}

export interface SyncJobProps {
  id: SyncJobId;
  name: string;
  integrationId: string;
  config: SyncJobConfig;
  status: SyncJobStatus;
  lastRun?: Date;
  nextRun?: Date;
  recordsProcessed: number;
  errorMessage?: string;
  isActive: boolean;
  description?: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy: string;
}

export class SyncJob implements BaseEntity {
  private _events: Array<SyncJobCreatedEvent | SyncJobStartedEvent | SyncJobCompletedEvent | SyncJobFailedEvent> = [];

  constructor(private readonly props: SyncJobProps) {}

  // Factory method
  static create(
    name: string,
    integrationId: string,
    config: SyncJobConfig,
    createdBy: string,
    description?: string,
    tags: string[] = []
  ): SyncJob {
    const now = new Date();
    const id = SyncJobId.create();

    const syncJob = new SyncJob({
      id,
      name,
      integrationId,
      config,
      status: 'pending',
      recordsProcessed: 0,
      isActive: true,
      description,
      tags,
      createdAt: now,
      updatedAt: now,
      createdBy,
      updatedBy: createdBy
    });

    syncJob._events.push(
      new SyncJobCreatedEvent(id, name, config.source.type, config.target.type, {
        integrationId,
        config,
        description,
        tags,
        createdBy
      })
    );

    return syncJob;
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

  get config(): SyncJobConfig {
    return { ...this.props.config };
  }

  get status(): SyncJobStatus {
    return this.props.status;
  }

  get lastRun(): Date | undefined {
    return this.props.lastRun;
  }

  get nextRun(): Date | undefined {
    return this.props.nextRun;
  }

  get recordsProcessed(): number {
    return this.props.recordsProcessed;
  }

  get errorMessage(): string | undefined {
    return this.props.errorMessage;
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
  start(updatedBy: string): void {
    if (!this.props.isActive) {
      throw new Error('Cannot start inactive sync job');
    }

    if (this.props.status === 'running') {
      throw new Error('Sync job is already running');
    }

    this.props.status = 'running';
    this.props.lastRun = new Date();
    this.props.errorMessage = undefined;
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new SyncJobStartedEvent(this.props.id, {
        updatedBy
      })
    );
  }

  complete(recordsProcessed: number, duration: number, updatedBy: string): void {
    if (this.props.status !== 'running') {
      throw new Error('Cannot complete sync job that is not running');
    }

    this.props.status = 'completed';
    this.props.recordsProcessed += recordsProcessed;
    this.props.errorMessage = undefined;
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new SyncJobCompletedEvent(this.props.id, recordsProcessed, duration, {
        updatedBy,
        totalRecords: this.props.recordsProcessed
      })
    );
  }

  fail(error: string, updatedBy: string): void {
    this.props.status = 'failed';
    this.props.errorMessage = error;
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;

    this._events.push(
      new SyncJobFailedEvent(this.props.id, error, {
        updatedBy
      })
    );
  }

  cancel(updatedBy: string): void {
    if (this.props.status === 'completed') {
      throw new Error('Cannot cancel completed sync job');
    }

    this.props.status = 'cancelled';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;
  }

  scheduleNextRun(nextRun: Date, updatedBy: string): void {
    this.props.nextRun = nextRun;
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;
  }

  activate(updatedBy: string): void {
    if (this.props.status === 'failed') {
      throw new Error('Cannot activate sync job with error status');
    }

    this.props.isActive = true;
    this.props.status = 'pending';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;
  }

  deactivate(updatedBy: string): void {
    this.props.isActive = false;
    this.props.status = 'cancelled';
    this.props.updatedAt = new Date();
    this.props.updatedBy = updatedBy;
  }

  // Domain events
  getUncommittedEvents(): Array<SyncJobCreatedEvent | SyncJobStartedEvent | SyncJobCompletedEvent | SyncJobFailedEvent> {
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
      status: this.props.status,
      lastRun: this.props.lastRun?.toISOString(),
      nextRun: this.props.nextRun?.toISOString(),
      recordsProcessed: this.props.recordsProcessed,
      errorMessage: this.props.errorMessage,
      isActive: this.props.isActive,
      description: this.props.description,
      tags: this.props.tags,
      createdAt: this.props.createdAt.toISOString(),
      updatedAt: this.props.updatedAt.toISOString(),
      createdBy: this.props.createdBy,
      updatedBy: this.props.updatedBy
    };
  }

  static fromJSON(data: Record<string, unknown>): SyncJob {
    return new SyncJob({
      id: SyncJobId.fromString(data.id as string),
      name: data.name as string,
      integrationId: data.integrationId as string,
      config: data.config as SyncJobConfig,
      status: data.status as SyncJobStatus,
      lastRun: data.lastRun ? new Date(data.lastRun as string) : undefined,
      nextRun: data.nextRun ? new Date(data.nextRun as string) : undefined,
      recordsProcessed: data.recordsProcessed as number,
      errorMessage: data.errorMessage as string,
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
