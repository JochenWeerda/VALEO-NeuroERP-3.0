"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.IntegrationService = void 0;
class IntegrationService {
    integrations = [];
    async createIntegration(integration) {
        this.integrations.push(integration);
        return integration;
    }
    async getIntegration(id) {
        return this.integrations.find(i => i.id === id) || null;
    }
    async getAllIntegrations() {
        return [...this.integrations];
    }
}
exports.IntegrationService = IntegrationService;
//# sourceMappingURL=integration-service.js.map