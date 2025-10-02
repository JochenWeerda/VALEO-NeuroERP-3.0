/**
 * VALEO NeuroERP 3.0 - In-Memory WebhookRepository Repository
 *
 * In-memory implementation of WebhookRepository repository for testing.
 * Stores data in memory with no persistence.
 */
import { WebhookRepository } from '../../core/entities/webhookrepository';
import { WebhookRepositoryId } from '@valero-neuroerp/data-models/branded-types';
import { WebhookRepositoryRepository } from './webhookrepository-repository';
export declare class InMemoryWebhookRepositoryRepository implements WebhookRepositoryRepository {
    private storage;
    findById(id: WebhookRepositoryId): Promise<WebhookRepository | null>;
    findAll(): Promise<WebhookRepository[]>;
    create(entity: WebhookRepository): Promise<void>;
    update(id: WebhookRepositoryId, entity: WebhookRepository): Promise<void>;
    delete(id: WebhookRepositoryId): Promise<void>;
    exists(id: WebhookRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<WebhookRepository[]>;
    findByStatus(value: string): Promise<WebhookRepository[]>;
    clear(): void;
    seed(data: WebhookRepository[]): void;
}
//# sourceMappingURL=in-memory-webhookrepository-repository.d.ts.map