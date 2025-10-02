"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiKeyUpdatedEvent = exports.ApiKeyCreatedEvent = void 0;
exports.createApiKey = createApiKey;
const data_models_1 = require("@valero-neuroerp/data-models");
class ApiKeyCreatedEvent {
    id = (0, data_models_1.createId)('ApiKeyCreatedEvent');
    aggregateType = 'ApiKey';
    version = 1;
    occurredOn = new Date();
    data;
    constructor(apiKeyId, integrationId, name) {
        this.data = { apiKeyId, integrationId, name };
    }
}
exports.ApiKeyCreatedEvent = ApiKeyCreatedEvent;
class ApiKeyUpdatedEvent {
    id = (0, data_models_1.createId)('ApiKeyUpdatedEvent');
    aggregateType = 'ApiKey';
    version = 1;
    occurredOn = new Date();
    data;
    constructor(apiKeyId, changes) {
        this.data = { apiKeyId, changes };
    }
}
exports.ApiKeyUpdatedEvent = ApiKeyUpdatedEvent;
function createApiKey(data) {
    return {
        ...data,
        id: (0, data_models_1.createId)('ApiKeyId'),
        createdAt: new Date(),
        updatedAt: new Date()
    };
}
//# sourceMappingURL=apikey.js.map