import { SyncJobRepositoryId } from '@valero-neuroerp/data-models';
export interface SyncJobRepository {
    id: SyncJobRepositoryId;
    name: string;
    type: string;
    configuration: Record<string, any>;
    createdAt: Date;
    updatedAt: Date;
}
export declare function createSyncJobRepository(data: Omit<SyncJobRepository, 'id' | 'createdAt' | 'updatedAt'>): SyncJobRepository;
//# sourceMappingURL=syncjobrepository.d.ts.map