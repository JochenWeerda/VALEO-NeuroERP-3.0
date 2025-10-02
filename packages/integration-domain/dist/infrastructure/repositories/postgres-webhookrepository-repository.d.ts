/**
 * VALEO NeuroERP 3.0 - Postgres WebhookRepository Repository
 *
 * PostgreSQL implementation of WebhookRepository repository.
 * Handles database operations with proper error handling and transactions.
 */
import { WebhookRepository } from '../../core/entities/webhookrepository';
import { WebhookRepositoryId } from '@valero-neuroerp/data-models/branded-types';
import { PostgresConnection } from '@valero-neuroerp/utilities/postgres';
import { WebhookRepositoryRepository } from './webhookrepository-repository';
export declare class PostgresWebhookRepositoryRepository implements WebhookRepositoryRepository {
    private db;
    constructor(db: PostgresConnection);
    findById(id: WebhookRepositoryId): Promise<WebhookRepository | null>;
    findAll(): Promise<WebhookRepository[]>;
    create(entity: WebhookRepository): Promise<void>;
    update(id: WebhookRepositoryId, entity: WebhookRepository): Promise<void>;
    delete(id: WebhookRepositoryId): Promise<void>;
    exists(id: WebhookRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<WebhookRepository[]>;
    findByStatus(value: string): Promise<WebhookRepository[]>;
    private mapRowToEntity;
}
//# sourceMappingURL=postgres-webhookrepository-repository.d.ts.map