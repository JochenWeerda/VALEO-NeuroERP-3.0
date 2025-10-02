/**
 * PostgreSQL Integration Repository Implementation
 */
import { Integration } from '@domain/entities/integration.js';
import type { IntegrationRepository, PaginationOptions, PaginatedResult, Result } from '@domain/interfaces/repositories.js';
import type { DatabaseConnection } from '../external/database-connection.js';
export declare class PostgresIntegrationRepository implements IntegrationRepository {
    private connection;
    constructor(connection: DatabaseConnection);
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
    private mapRowToIntegration;
    private mapSortField;
}
//# sourceMappingURL=postgres-integration-repository.d.ts.map