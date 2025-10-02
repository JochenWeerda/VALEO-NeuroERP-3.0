/**
 * Integration Application Service
 */
import { CreateIntegrationCommand, UpdateIntegrationCommand, DeleteIntegrationCommand, ActivateIntegrationCommand, DeactivateIntegrationCommand, CreateIntegrationUseCase, UpdateIntegrationUseCase, DeleteIntegrationUseCase, ActivateIntegrationUseCase, DeactivateIntegrationUseCase, GetIntegrationQuery, ListIntegrationsQuery, GetIntegrationQueryHandler, ListIntegrationsQueryHandler } from '../use-cases/integration-use-cases.js';
export class IntegrationApplicationService {
    unitOfWork;
    createIntegrationUseCase;
    updateIntegrationUseCase;
    deleteIntegrationUseCase;
    activateIntegrationUseCase;
    deactivateIntegrationUseCase;
    getIntegrationQueryHandler;
    listIntegrationsQueryHandler;
    constructor(unitOfWork) {
        this.unitOfWork = unitOfWork;
        // Initialize use cases
        this.createIntegrationUseCase = new CreateIntegrationUseCase(unitOfWork);
        this.updateIntegrationUseCase = new UpdateIntegrationUseCase(unitOfWork);
        this.deleteIntegrationUseCase = new DeleteIntegrationUseCase(unitOfWork);
        this.activateIntegrationUseCase = new ActivateIntegrationUseCase(unitOfWork);
        this.deactivateIntegrationUseCase = new DeactivateIntegrationUseCase(unitOfWork);
        // Initialize query handlers
        this.getIntegrationQueryHandler = new GetIntegrationQueryHandler(unitOfWork);
        this.listIntegrationsQueryHandler = new ListIntegrationsQueryHandler(unitOfWork);
    }
    // Command methods
    async createIntegration(request, userId) {
        const command = new CreateIntegrationCommand(request, userId);
        return await this.createIntegrationUseCase.execute(command);
    }
    async updateIntegration(id, request, userId) {
        const command = new UpdateIntegrationCommand(id, request, userId);
        return await this.updateIntegrationUseCase.execute(command);
    }
    async deleteIntegration(id, userId) {
        const command = new DeleteIntegrationCommand(id, userId);
        return await this.deleteIntegrationUseCase.execute(command);
    }
    async activateIntegration(id, userId) {
        const command = new ActivateIntegrationCommand(id, userId);
        return await this.activateIntegrationUseCase.execute(command);
    }
    async deactivateIntegration(id, userId) {
        const command = new DeactivateIntegrationCommand(id, userId);
        return await this.deactivateIntegrationUseCase.execute(command);
    }
    // Query methods
    async getIntegration(id) {
        const query = new GetIntegrationQuery(id);
        return await this.getIntegrationQueryHandler.execute(query);
    }
    async listIntegrations(query) {
        const queryObject = new ListIntegrationsQuery(query);
        return await this.listIntegrationsQueryHandler.execute(queryObject);
    }
    async getIntegrationByName(name) {
        try {
            const result = await this.unitOfWork.integrations.findByName(name);
            if (!result.success) {
                return result;
            }
            if (!result.data) {
                return { success: true, data: null };
            }
            return {
                success: true,
                data: this.mapToResponse(result.data)
            };
        }
        catch (error) {
            return {
                success: false,
                error: error
            };
        }
    }
    async getIntegrationsByType(type) {
        try {
            const result = await this.unitOfWork.integrations.findByType(type);
            if (!result.success) {
                return result;
            }
            const integrations = result.data.map(integration => this.mapToResponse(integration));
            return { success: true, data: integrations };
        }
        catch (error) {
            return {
                success: false,
                error: error
            };
        }
    }
    async getActiveIntegrations() {
        try {
            const result = await this.unitOfWork.integrations.findActive();
            if (!result.success) {
                return result;
            }
            const integrations = result.data.map(integration => this.mapToResponse(integration));
            return { success: true, data: integrations };
        }
        catch (error) {
            return {
                success: false,
                error: error
            };
        }
    }
    // Utility methods
    async healthCheck() {
        try {
            // Simple health check - try to query integrations
            const result = await this.unitOfWork.integrations.findAll({ page: 1, limit: 1 });
            if (result.success) {
                return {
                    success: true,
                    data: {
                        status: 'healthy',
                        timestamp: new Date().toISOString()
                    }
                };
            }
            else {
                return {
                    success: true,
                    data: {
                        status: 'degraded',
                        timestamp: new Date().toISOString()
                    }
                };
            }
        }
        catch (error) {
            return {
                success: false,
                error: error
            };
        }
    }
    async getStatistics() {
        try {
            // Get all integrations
            const allResult = await this.unitOfWork.integrations.findAll({ page: 1, limit: 1000 });
            if (!allResult.success) {
                return allResult;
            }
            const integrations = allResult.data.data;
            const total = integrations.length;
            const active = integrations.filter(i => i.isActive).length;
            const inactive = total - active;
            // Group by type
            const byType = {};
            integrations.forEach(integration => {
                byType[integration.type] = (byType[integration.type] || 0) + 1;
            });
            return {
                success: true,
                data: {
                    total,
                    active,
                    inactive,
                    byType
                }
            };
        }
        catch (error) {
            return {
                success: false,
                error: error
            };
        }
    }
    mapToResponse(integration) {
        return {
            id: integration.id,
            name: integration.name,
            type: integration.type,
            status: integration.status,
            config: integration.config,
            description: integration.description || null,
            tags: integration.tags,
            isActive: integration.isActive,
            createdAt: integration.createdAt.toISOString(),
            updatedAt: integration.updatedAt.toISOString(),
            createdBy: integration.createdBy,
            updatedBy: integration.updatedBy
        };
    }
}
//# sourceMappingURL=integration-application-service.js.map