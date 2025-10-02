"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createWebhookRepository = createWebhookRepository;
const data_models_1 = require("@valero-neuroerp/data-models");
function createWebhookRepository(data) {
    return {
        ...data,
        id: (0, data_models_1.createId)('WebhookRepositoryId'),
        createdAt: new Date(),
        updatedAt: new Date()
    };
}
//# sourceMappingURL=webhookrepository.js.map