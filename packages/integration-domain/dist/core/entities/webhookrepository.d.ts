import { WebhookRepositoryId } from '@valero-neuroerp/data-models';
export interface WebhookRepository {
    id: WebhookRepositoryId;
    name: string;
    type: string;
    configuration: Record<string, any>;
    createdAt: Date;
    updatedAt: Date;
}
export declare function createWebhookRepository(data: Omit<WebhookRepository, 'id' | 'createdAt' | 'updatedAt'>): WebhookRepository;
//# sourceMappingURL=webhookrepository.d.ts.map