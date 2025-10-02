/**
 * VALEO NeuroERP 3.0 - SyncJobRepository Repository Interface
 *
 * Defines the contract for SyncJobRepository data access operations.
 * Follows Repository pattern for clean data access abstraction.
 */
import { SyncJobRepository } from '../../core/entities/syncjobrepository';
import { SyncJobRepositoryId } from '@valero-neuroerp/data-models/branded-types';
export interface SyncJobRepositoryRepository {
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
//# sourceMappingURL=syncjobrepository-repository.d.ts.map