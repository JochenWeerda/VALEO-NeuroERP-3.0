import { Webhook } from '../core/entities/webhook';
export declare class WebhookService {
    private webhooks;
    createWebhook(webhook: Webhook): Promise<Webhook>;
    getWebhook(id: string): Promise<Webhook | null>;
    getAllWebhooks(): Promise<Webhook[]>;
}
//# sourceMappingURL=webhook-service.d.ts.map