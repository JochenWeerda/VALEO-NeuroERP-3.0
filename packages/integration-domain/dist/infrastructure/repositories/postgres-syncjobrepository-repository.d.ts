/**
 * VALEO NeuroERP 3.0 - Postgres SyncJobRepository Repository
 *
 * PostgreSQL implementation of SyncJobRepository repository.
 * Handles database operations with proper error handling and transactions.
 */
import { SyncJobRepository } from '../../core/entities/syncjobrepository';
import { SyncJobRepositoryId } from '@valero-neuroerp/data-models/branded-types';
import { PostgresConnection } from '@valero-neuroerp/utilities/postgres';
import { SyncJobRepositoryRepository } from './syncjobrepository-repository';
export declare class PostgresSyncJobRepositoryRepository implements SyncJobRepositoryRepository {
    private db;
    constructor(db: PostgresConnection);
    findById(id: SyncJobRepositoryId): Promise<SyncJobRepository | null>;
    findAll(): Promise<SyncJobRepository[]>;
    create(entity: SyncJobRepository): Promise<void>;
    update(id: SyncJobRepositoryId, entity: SyncJobRepository): Promise<void>;
    delete(id: SyncJobRepositoryId): Promise<void>;
    exists(id: SyncJobRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<SyncJobRepository[]>;
    findByStatus(value: string): Promise<SyncJobRepository[]>;
    private mapRowToEntity;
}
//# sourceMappingURL=postgres-syncjobrepository-repository.d.ts.map