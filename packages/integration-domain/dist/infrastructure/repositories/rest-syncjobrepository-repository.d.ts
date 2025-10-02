/**
 * VALEO NeuroERP 3.0 - REST SyncJobRepository Repository
 *
 * REST API implementation of SyncJobRepository repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */
import { SyncJobRepository } from '../../core/entities/syncjobrepository';
import { SyncJobRepositoryId } from '@valero-neuroerp/data-models/branded-types';
import { SyncJobRepositoryRepository } from './syncjobrepository-repository';
export declare class RestSyncJobRepositoryRepository implements SyncJobRepositoryRepository {
    private baseUrl;
    private apiToken?;
    constructor(baseUrl: string, apiToken?: string);
    private request;
    findById(id: SyncJobRepositoryId): Promise<SyncJobRepository | null>;
    findAll(): Promise<SyncJobRepository[]>;
    create(entity: SyncJobRepository): Promise<void>;
    update(id: SyncJobRepositoryId, entity: SyncJobRepository): Promise<void>;
    delete(id: SyncJobRepositoryId): Promise<void>;
    exists(id: SyncJobRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<SyncJobRepository[]>;
    findByStatus(value: string): Promise<SyncJobRepository[]>;
}
//# sourceMappingURL=rest-syncjobrepository-repository.d.ts.map