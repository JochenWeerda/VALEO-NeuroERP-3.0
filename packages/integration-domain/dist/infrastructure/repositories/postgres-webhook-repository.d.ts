/**
 * PostgreSQL Webhook Repository Implementation
 */
import { Webhook } from '@domain/entities/webhook.js';
import type { WebhookRepository, PaginationOptions, PaginatedResult, Result } from '@domain/interfaces/repositories.js';
import type { DatabaseConnection } from '../external/database-connection.js';
export declare class PostgresWebhookRepository implements WebhookRepository {
    private connection;
    constructor(connection: DatabaseConnection);
    findById(id: string): Promise<Result<Webhook | null, Error>>;
    findAll(options?: PaginationOptions): Promise<Result<PaginatedResult<Webhook>, Error>>;
    create(webhook: Webhook): Promise<Result<Webhook, Error>>;
    update(webhook: Webhook): Promise<Result<Webhook, Error>>;
    delete(id: string): Promise<Result<void, Error>>;
    findByIntegrationId(integrationId: string): Promise<Result<Webhook[], Error>>;
    findByName(name: string): Promise<Result<Webhook | null, Error>>;
    findByEvent(event: string): Promise<Result<Webhook[], Error>>;
    findActive(): Promise<Result<Webhook[], Error>>;
    findFailed(): Promise<Result<Webhook[], Error>>;
    private mapRowToWebhook;
    private mapSortField;
}
//# sourceMappingURL=postgres-webhook-repository.d.ts.map