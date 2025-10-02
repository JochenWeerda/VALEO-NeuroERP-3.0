/**
 * PostgreSQL Sync Job Repository Implementation
 */
import { SyncJob } from '@domain/entities/sync-job.js';
import type { SyncJobRepository, PaginationOptions, PaginatedResult, Result } from '@domain/interfaces/repositories.js';
import type { DatabaseConnection } from '../external/database-connection.js';
export declare class PostgresSyncJobRepository implements SyncJobRepository {
    private connection;
    constructor(connection: DatabaseConnection);
    findById(id: string): Promise<Result<SyncJob | null, Error>>;
    findAll(options?: PaginationOptions): Promise<Result<PaginatedResult<SyncJob>, Error>>;
    create(syncJob: SyncJob): Promise<Result<SyncJob, Error>>;
    update(syncJob: SyncJob): Promise<Result<SyncJob, Error>>;
    delete(id: string): Promise<Result<void, Error>>;
    findByIntegrationId(integrationId: string): Promise<Result<SyncJob[], Error>>;
    findByName(name: string): Promise<Result<SyncJob | null, Error>>;
    findByStatus(status: string): Promise<Result<SyncJob[], Error>>;
    findScheduled(): Promise<Result<SyncJob[], Error>>;
    findRunning(): Promise<Result<SyncJob[], Error>>;
    findFailed(): Promise<Result<SyncJob[], Error>>;
    private mapRowToSyncJob;
    private mapSortField;
}
//# sourceMappingURL=postgres-sync-job-repository.d.ts.map