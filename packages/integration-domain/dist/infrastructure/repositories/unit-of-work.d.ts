/**
 * Unit of Work Pattern Implementation
 */
import type { UnitOfWork, IntegrationRepository, WebhookRepository, SyncJobRepository } from '@domain/interfaces/repositories.js';
import type { DatabaseConnection } from '../external/database-connection.js';
/**
 * InMemory Unit of Work for Testing
 */
export declare class InMemoryUnitOfWork implements UnitOfWork {
    integrations: IntegrationRepository;
    webhooks: WebhookRepository;
    syncJobs: SyncJobRepository;
    private committed;
    private rolledBack;
    constructor();
    begin(): Promise<void>;
    commit(): Promise<void>;
    rollback(): Promise<void>;
    isCommitted(): boolean;
    isRolledBack(): boolean;
}
/**
 * PostgreSQL Unit of Work with Transaction Support
 */
export declare class PostgresUnitOfWork implements UnitOfWork {
    private connection;
    integrations: IntegrationRepository;
    webhooks: WebhookRepository;
    syncJobs: SyncJobRepository;
    private transaction;
    private committed;
    private rolledBack;
    constructor(connection: DatabaseConnection);
    begin(): Promise<void>;
    commit(): Promise<void>;
    rollback(): Promise<void>;
    isCommitted(): boolean;
    isRolledBack(): boolean;
}
/**
 * Unit of Work Factory
 */
export declare class UnitOfWorkFactory {
    static createInMemory(): InMemoryUnitOfWork;
    static createPostgres(connection: DatabaseConnection): PostgresUnitOfWork;
}
/**
 * Unit of Work Manager for handling transactions
 */
export declare class UnitOfWorkManager {
    private currentUnitOfWork;
    withTransaction<T>(unitOfWork: UnitOfWork, operation: (uow: UnitOfWork) => Promise<T>): Promise<T>;
    getCurrentUnitOfWork(): UnitOfWork | null;
    hasActiveTransaction(): boolean;
}
//# sourceMappingURL=unit-of-work.d.ts.map