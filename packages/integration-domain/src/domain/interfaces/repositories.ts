/**
 * Repository Interfaces
 */

import type { PaginatedResult, PaginationOptions, Result } from '@shared/types/common.js';

// Re-export shared types for convenience
export type { PaginationOptions, PaginatedResult, Result } from '@shared/types/common.js';
import type { Integration } from '../entities/integration.js';
import type { Webhook } from '../entities/webhook.js';
import type { SyncJob } from '../entities/sync-job.js';

/**
 * Base Repository Interface
 */
export interface BaseRepository<T> {
  findById(id: string): Promise<Result<T | null, Error>>;
  findAll(options?: PaginationOptions): Promise<Result<PaginatedResult<T>, Error>>;
  create(entity: T): Promise<Result<T, Error>>;
  update(entity: T): Promise<Result<T, Error>>;
  delete(id: string): Promise<Result<void, Error>>;
}

/**
 * Integration Repository Interface
 */
export interface IntegrationRepository extends BaseRepository<Integration> {
  findByName(name: string): Promise<Result<Integration | null, Error>>;
  findByType(type: string): Promise<Result<Integration[], Error>>;
  findByStatus(status: string): Promise<Result<Integration[], Error>>;
  findByTags(tags: string[]): Promise<Result<Integration[], Error>>;
  findActive(): Promise<Result<Integration[], Error>>;
}

/**
 * Webhook Repository Interface
 */
export interface WebhookRepository extends BaseRepository<Webhook> {
  findByIntegrationId(integrationId: string): Promise<Result<Webhook[], Error>>;
  findByName(name: string): Promise<Result<Webhook | null, Error>>;
  findByEvent(event: string): Promise<Result<Webhook[], Error>>;
  findActive(): Promise<Result<Webhook[], Error>>;
  findFailed(): Promise<Result<Webhook[], Error>>;
}

/**
 * Sync Job Repository Interface
 */
export interface SyncJobRepository extends BaseRepository<SyncJob> {
  findByIntegrationId(integrationId: string): Promise<Result<SyncJob[], Error>>;
  findByName(name: string): Promise<Result<SyncJob | null, Error>>;
  findByStatus(status: string): Promise<Result<SyncJob[], Error>>;
  findScheduled(): Promise<Result<SyncJob[], Error>>;
  findRunning(): Promise<Result<SyncJob[], Error>>;
  findFailed(): Promise<Result<SyncJob[], Error>>;
}

/**
 * Unit of Work Interface for Transactions
 */
export interface UnitOfWork {
  integrations: IntegrationRepository;
  webhooks: WebhookRepository;
  syncJobs: SyncJobRepository;
  
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
}
