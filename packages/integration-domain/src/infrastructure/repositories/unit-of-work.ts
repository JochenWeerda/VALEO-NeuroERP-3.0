/**
 * Unit of Work Pattern Implementation
 */

import type { IntegrationRepository, SyncJobRepository, UnitOfWork, WebhookRepository } from '@domain/interfaces/repositories.js';
import type { DatabaseConnection, DatabaseTransaction } from '../external/database-connection.js';
import { InMemoryIntegrationRepository } from './in-memory-integration-repository.js';
import { InMemoryWebhookRepository } from './in-memory-webhook-repository.js';
import { InMemorySyncJobRepository } from './in-memory-sync-job-repository.js';
import { PostgresIntegrationRepository } from './postgres-integration-repository.js';
import { PostgresWebhookRepository } from './postgres-webhook-repository.js';
import { PostgresSyncJobRepository } from './postgres-sync-job-repository.js';

/**
 * InMemory Unit of Work for Testing
 */
export class InMemoryUnitOfWork implements UnitOfWork {
  public integrations: IntegrationRepository;
  public webhooks: WebhookRepository;
  public syncJobs: SyncJobRepository;

  private committed = false;
  private rolledBack = false;

  constructor() {
    this.integrations = new InMemoryIntegrationRepository();
    this.webhooks = new InMemoryWebhookRepository();
    this.syncJobs = new InMemorySyncJobRepository();
  }

  async begin(): Promise<void> {
    if (this.committed || this.rolledBack) {
      throw new Error('Unit of Work has already been committed or rolled back');
    }
    // In-memory implementation doesn't need explicit transaction handling
  }

  async commit(): Promise<void> {
    if (this.rolledBack) {
      throw new Error('Cannot commit rolled back Unit of Work');
    }
    this.committed = true;
  }

  async rollback(): Promise<void> {
    if (this.committed) {
      throw new Error('Cannot rollback committed Unit of Work');
    }
    this.rolledBack = true;
    
    // Clear all repositories
    (this.integrations as InMemoryIntegrationRepository).clear();
    (this.webhooks as InMemoryWebhookRepository).clear();
    (this.syncJobs as InMemorySyncJobRepository).clear();
  }

  isCommitted(): boolean {
    return this.committed;
  }

  isRolledBack(): boolean {
    return this.rolledBack;
  }
}

/**
 * PostgreSQL Unit of Work with Transaction Support
 */
export class PostgresUnitOfWork implements UnitOfWork {
  public integrations: IntegrationRepository;
  public webhooks: WebhookRepository;
  public syncJobs: SyncJobRepository;

  private transaction: DatabaseTransaction | null = null;
  private committed = false;
  private rolledBack = false;

  constructor(private readonly connection: DatabaseConnection) {
    // Initialize repositories with connection (will be updated with transaction)
    this.integrations = new PostgresIntegrationRepository(connection);
    this.webhooks = new PostgresWebhookRepository(connection);
    this.syncJobs = new PostgresSyncJobRepository(connection);
  }

  async begin(): Promise<void> {
    if (this.committed || this.rolledBack) {
      throw new Error('Unit of Work has already been committed or rolled back');
    }

    this.transaction = await this.connection.transaction(async (tx) => {
      // Create new repository instances with transaction
      this.integrations = new PostgresIntegrationRepository(this.connection);
      this.webhooks = new PostgresWebhookRepository(this.connection);
      this.syncJobs = new PostgresSyncJobRepository(this.connection);
    }) as any;
  }

  async commit(): Promise<void> {
    if (this.rolledBack) {
      throw new Error('Cannot commit rolled back Unit of Work');
    }

    if (this.transaction) {
      await this.transaction.commit();
      this.transaction = null;
    }

    this.committed = true;
  }

  async rollback(): Promise<void> {
    if (this.committed) {
      throw new Error('Cannot rollback committed Unit of Work');
    }

    if (this.transaction) {
      await this.transaction.rollback();
      this.transaction = null;
    }

    this.rolledBack = true;
  }

  isCommitted(): boolean {
    return this.committed;
  }

  isRolledBack(): boolean {
    return this.rolledBack;
  }
}

/**
 * Unit of Work Factory
 */
export class UnitOfWorkFactory {
  static createInMemory(): InMemoryUnitOfWork {
    return new InMemoryUnitOfWork();
  }

  static createPostgres(connection: DatabaseConnection): PostgresUnitOfWork {
    return new PostgresUnitOfWork(connection);
  }
}

/**
 * Unit of Work Manager for handling transactions
 */
export class UnitOfWorkManager {
  private currentUnitOfWork: UnitOfWork | null = null;

  async withTransaction<T>(
    unitOfWork: UnitOfWork,
    operation: (uow: UnitOfWork) => Promise<T>
  ): Promise<T> {
    this.currentUnitOfWork = unitOfWork;

    try {
      await unitOfWork.begin();
      const result = await operation(unitOfWork);
      await unitOfWork.commit();
      return result;
    } catch (error) {
      await unitOfWork.rollback();
      throw error;
    } finally {
      this.currentUnitOfWork = null;
    }
  }

  getCurrentUnitOfWork(): UnitOfWork | null {
    return this.currentUnitOfWork;
  }

  hasActiveTransaction(): boolean {
    return this.currentUnitOfWork !== null;
  }
}
