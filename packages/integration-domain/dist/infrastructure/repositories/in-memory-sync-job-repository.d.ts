/**
 * InMemory Sync Job Repository Implementation
 */
import { SyncJob } from '@domain/entities/sync-job.js';
import type { SyncJobRepository, PaginationOptions, PaginatedResult, Result } from '@domain/interfaces/repositories.js';
export declare class InMemorySyncJobRepository implements SyncJobRepository {
    private syncJobs;
    private integrationIndex;
    private nameIndex;
    private statusIndex;
    private nextRunIndex;
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
    private getSortValue;
    private addToIntegrationIndex;
    private removeFromIntegrationIndex;
    private addToStatusIndex;
    private removeFromStatusIndex;
    private addToNextRunIndex;
    private removeFromNextRunIndex;
    clear(): void;
    getCount(): number;
}
//# sourceMappingURL=in-memory-sync-job-repository.d.ts.map