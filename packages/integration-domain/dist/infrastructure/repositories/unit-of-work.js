/**
 * Unit of Work Pattern Implementation
 */
import { InMemoryIntegrationRepository } from './in-memory-integration-repository.js';
import { InMemoryWebhookRepository } from './in-memory-webhook-repository.js';
import { InMemorySyncJobRepository } from './in-memory-sync-job-repository.js';
import { PostgresIntegrationRepository } from './postgres-integration-repository.js';
import { PostgresWebhookRepository } from './postgres-webhook-repository.js';
import { PostgresSyncJobRepository } from './postgres-sync-job-repository.js';
/**
 * InMemory Unit of Work for Testing
 */
export class InMemoryUnitOfWork {
    integrations;
    webhooks;
    syncJobs;
    committed = false;
    rolledBack = false;
    constructor() {
        this.integrations = new InMemoryIntegrationRepository();
        this.webhooks = new InMemoryWebhookRepository();
        this.syncJobs = new InMemorySyncJobRepository();
    }
    async begin() {
        if (this.committed || this.rolledBack) {
            throw new Error('Unit of Work has already been committed or rolled back');
        }
        // In-memory implementation doesn't need explicit transaction handling
    }
    async commit() {
        if (this.rolledBack) {
            throw new Error('Cannot commit rolled back Unit of Work');
        }
        this.committed = true;
    }
    async rollback() {
        if (this.committed) {
            throw new Error('Cannot rollback committed Unit of Work');
        }
        this.rolledBack = true;
        // Clear all repositories
        this.integrations.clear();
        this.webhooks.clear();
        this.syncJobs.clear();
    }
    isCommitted() {
        return this.committed;
    }
    isRolledBack() {
        return this.rolledBack;
    }
}
/**
 * PostgreSQL Unit of Work with Transaction Support
 */
export class PostgresUnitOfWork {
    connection;
    integrations;
    webhooks;
    syncJobs;
    transaction = null;
    committed = false;
    rolledBack = false;
    constructor(connection) {
        this.connection = connection;
        // Initialize repositories with connection (will be updated with transaction)
        this.integrations = new PostgresIntegrationRepository(connection);
        this.webhooks = new PostgresWebhookRepository(connection);
        this.syncJobs = new PostgresSyncJobRepository(connection);
    }
    async begin() {
        if (this.committed || this.rolledBack) {
            throw new Error('Unit of Work has already been committed or rolled back');
        }
        this.transaction = await this.connection.transaction(async (tx) => {
            // Create new repository instances with transaction
            this.integrations = new PostgresIntegrationRepository(this.connection);
            this.webhooks = new PostgresWebhookRepository(this.connection);
            this.syncJobs = new PostgresSyncJobRepository(this.connection);
        });
    }
    async commit() {
        if (this.rolledBack) {
            throw new Error('Cannot commit rolled back Unit of Work');
        }
        if (this.transaction) {
            await this.transaction.commit();
            this.transaction = null;
        }
        this.committed = true;
    }
    async rollback() {
        if (this.committed) {
            throw new Error('Cannot rollback committed Unit of Work');
        }
        if (this.transaction) {
            await this.transaction.rollback();
            this.transaction = null;
        }
        this.rolledBack = true;
    }
    isCommitted() {
        return this.committed;
    }
    isRolledBack() {
        return this.rolledBack;
    }
}
/**
 * Unit of Work Factory
 */
export class UnitOfWorkFactory {
    static createInMemory() {
        return new InMemoryUnitOfWork();
    }
    static createPostgres(connection) {
        return new PostgresUnitOfWork(connection);
    }
}
/**
 * Unit of Work Manager for handling transactions
 */
export class UnitOfWorkManager {
    currentUnitOfWork = null;
    async withTransaction(unitOfWork, operation) {
        this.currentUnitOfWork = unitOfWork;
        try {
            await unitOfWork.begin();
            const result = await operation(unitOfWork);
            await unitOfWork.commit();
            return result;
        }
        catch (error) {
            await unitOfWork.rollback();
            throw error;
        }
        finally {
            this.currentUnitOfWork = null;
        }
    }
    getCurrentUnitOfWork() {
        return this.currentUnitOfWork;
    }
    hasActiveTransaction() {
        return this.currentUnitOfWork !== null;
    }
}
//# sourceMappingURL=unit-of-work.js.map