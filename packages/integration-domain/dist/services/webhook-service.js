"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WebhookService = void 0;
class WebhookService {
    webhooks = [];
    async createWebhook(webhook) {
        this.webhooks.push(webhook);
        return webhook;
    }
    async getWebhook(id) {
        return this.webhooks.find(w => w.id === id) || null;
    }
    async getAllWebhooks() {
        return [...this.webhooks];
    }
}
exports.WebhookService = WebhookService;
//# sourceMappingURL=webhook-service.js.map