"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.IntegrationCreatedEvent = void 0;
exports.createIntegration = createIntegration;
const data_models_1 = require("@valero-neuroerp/data-models");
class IntegrationCreatedEvent {
    id = (0, data_models_1.createId)('IntegrationCreatedEvent');
    aggregateType = 'Integration';
    version = 1;
    occurredOn = new Date();
    data;
    constructor(integrationId, name, type) {
        this.data = { integrationId, name, type };
    }
}
exports.IntegrationCreatedEvent = IntegrationCreatedEvent;
function createIntegration(data) {
    return {
        ...data,
        id: (0, data_models_1.createId)('IntegrationId'),
        createdAt: new Date(),
        updatedAt: new Date()
    };
}
//# sourceMappingURL=integration.js.map