/**
 * InMemory Integration Repository Implementation
 */
import { Integration } from '@domain/entities/integration.js';
import type { IntegrationRepository, PaginationOptions, PaginatedResult, Result } from '@domain/interfaces/repositories.js';
export declare class InMemoryIntegrationRepository implements IntegrationRepository {
    private integrations;
    private nameIndex;
    private typeIndex;
    private statusIndex;
    private tagsIndex;
    findById(id: string): Promise<Result<Integration | null, Error>>;
    findAll(options?: PaginationOptions): Promise<Result<PaginatedResult<Integration>, Error>>;
    create(integration: Integration): Promise<Result<Integration, Error>>;
    update(integration: Integration): Promise<Result<Integration, Error>>;
    delete(id: string): Promise<Result<void, Error>>;
    findByName(name: string): Promise<Result<Integration | null, Error>>;
    findByType(type: string): Promise<Result<Integration[], Error>>;
    findByStatus(status: string): Promise<Result<Integration[], Error>>;
    findByTags(tags: string[]): Promise<Result<Integration[], Error>>;
    findActive(): Promise<Result<Integration[], Error>>;
    private getSortValue;
    private addToTypeIndex;
    private removeFromTypeIndex;
    private addToStatusIndex;
    private removeFromStatusIndex;
    private addToTagsIndex;
    private removeFromTagsIndex;
    clear(): void;
    getCount(): number;
}
//# sourceMappingURL=in-memory-integration-repository.d.ts.map