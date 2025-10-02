/**
 * VALEO NeuroERP 3.0 - REST WebhookRepository Repository
 *
 * REST API implementation of WebhookRepository repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */
import { WebhookRepository } from '../../core/entities/webhookrepository';
import { WebhookRepositoryId } from '@valero-neuroerp/data-models/branded-types';
import { WebhookRepositoryRepository } from './webhookrepository-repository';
export declare class RestWebhookRepositoryRepository implements WebhookRepositoryRepository {
    private baseUrl;
    private apiToken?;
    constructor(baseUrl: string, apiToken?: string);
    private request;
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
//# sourceMappingURL=rest-webhookrepository-repository.d.ts.map