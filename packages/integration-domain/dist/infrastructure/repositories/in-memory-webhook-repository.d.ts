/**
 * InMemory Webhook Repository Implementation
 */
import { Webhook } from '@domain/entities/webhook.js';
import type { WebhookRepository, PaginationOptions, PaginatedResult, Result } from '@domain/interfaces/repositories.js';
export declare class InMemoryWebhookRepository implements WebhookRepository {
    private webhooks;
    private integrationIndex;
    private nameIndex;
    private eventIndex;
    private statusIndex;
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
    private getSortValue;
    private addToIntegrationIndex;
    private removeFromIntegrationIndex;
    private addToEventIndex;
    private removeFromEventIndex;
    private addToStatusIndex;
    private removeFromStatusIndex;
    clear(): void;
    getCount(): number;
}
//# sourceMappingURL=in-memory-webhook-repository.d.ts.map