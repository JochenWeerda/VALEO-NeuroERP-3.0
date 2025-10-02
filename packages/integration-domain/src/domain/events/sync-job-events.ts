/**
 * Sync Job Domain Events
 */

import { BaseDomainEvent } from './base-domain-event.js';
import type { SyncJobId } from '../values/sync-job-id.js';

export class SyncJobCreatedEvent extends BaseDomainEvent {
  constructor(
    syncJobId: SyncJobId,
    name: string,
    source: string,
    target: string,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'syncjob.created',
      syncJobId.value,
      1,
      { ...metadata, name, source, target }
    );
  }

  getData(): Record<string, unknown> {
    return {
      syncJobId: this.aggregateId,
      name: this.metadata.name,
      source: this.metadata.source,
      target: this.metadata.target
    };
  }
}

export class SyncJobStartedEvent extends BaseDomainEvent {
  constructor(
    syncJobId: SyncJobId,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'syncjob.started',
      syncJobId.value,
      1,
      metadata
    );
  }

  getData(): Record<string, unknown> {
    return {
      syncJobId: this.aggregateId
    };
  }
}

export class SyncJobCompletedEvent extends BaseDomainEvent {
  constructor(
    syncJobId: SyncJobId,
    recordsProcessed: number,
    duration: number,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'syncjob.completed',
      syncJobId.value,
      1,
      { ...metadata, recordsProcessed, duration }
    );
  }

  getData(): Record<string, unknown> {
    return {
      syncJobId: this.aggregateId,
      recordsProcessed: this.metadata.recordsProcessed,
      duration: this.metadata.duration
    };
  }
}

export class SyncJobFailedEvent extends BaseDomainEvent {
  constructor(
    syncJobId: SyncJobId,
    error: string,
    metadata: Record<string, unknown> = {}
  ) {
    super(
      'syncjob.failed',
      syncJobId.value,
      1,
      { ...metadata, error }
    );
  }

  getData(): Record<string, unknown> {
    return {
      syncJobId: this.aggregateId,
      error: this.metadata.error
    };
  }
}
