/**
 * VALEO NeuroERP 3.0 - WebhookRepository Repository Interface
 *
 * Defines the contract for WebhookRepository data access operations.
 * Follows Repository pattern for clean data access abstraction.
 */
import { WebhookRepository } from '../../core/entities/webhookrepository';
import { WebhookRepositoryId } from '@valero-neuroerp/data-models/branded-types';
export interface WebhookRepositoryRepository {
    findById(id: WebhookRepositoryId): Promise<WebhookRepository | null>;
    findAll(): Promise<WebhookRepository[]>;
    create(entity: WebhookRepository): Promise<void>;
    update(id: WebhookRepositoryId, entity: WebhookRepository): Promise<void>;
    delete(id: WebhookRepositoryId): Promise<void>;
    exists(id: WebhookRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<WebhookRepository[]>;
    findByStatus(value: string): Promise<WebhookRepository[]>;
}
//# sourceMappingURL=webhookrepository-repository.d.ts.map