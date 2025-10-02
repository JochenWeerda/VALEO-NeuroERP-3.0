/**
 * VALEO NeuroERP 3.0 - In-Memory SyncJobRepository Repository
 *
 * In-memory implementation of SyncJobRepository repository for testing.
 * Stores data in memory with no persistence.
 */
import { SyncJobRepository } from '../../core/entities/syncjobrepository';
import { SyncJobRepositoryId } from '@valero-neuroerp/data-models/branded-types';
import { SyncJobRepositoryRepository } from './syncjobrepository-repository';
export declare class InMemorySyncJobRepositoryRepository implements SyncJobRepositoryRepository {
    private storage;
    findById(id: SyncJobRepositoryId): Promise<SyncJobRepository | null>;
    findAll(): Promise<SyncJobRepository[]>;
    create(entity: SyncJobRepository): Promise<void>;
    update(id: SyncJobRepositoryId, entity: SyncJobRepository): Promise<void>;
    delete(id: SyncJobRepositoryId): Promise<void>;
    exists(id: SyncJobRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<SyncJobRepository[]>;
    findByStatus(value: string): Promise<SyncJobRepository[]>;
    clear(): void;
    seed(data: SyncJobRepository[]): void;
}
//# sourceMappingURL=in-memory-syncjobrepository-repository.d.ts.map