/**
 * Integration API Controller
 */
import { validateCreateIntegrationRequest, validateUpdateIntegrationRequest, validateIntegrationQuery } from '@application/dto/integration-dto.js';
import { HttpStatusCode, createNotFoundError, createConflictError, createInternalServerError, createUnauthorizedError } from '../errors/api-errors.js';
export class IntegrationController {
    integrationService;
    constructor(integrationService) {
        this.integrationService = integrationService;
    }
    // GET /integrations
    async listIntegrations(req, res) {
        try {
            const query = validateIntegrationQuery({
                page: parseInt(req.query.page) || 1,
                limit: parseInt(req.query.limit) || 10,
                sortBy: req.query.sortBy,
                sortOrder: req.query.sortOrder,
                type: req.query.type,
                status: req.query.status,
                tags: req.query.tags ? req.query.tags.split(',') : undefined,
                isActive: req.query.isActive ? req.query.isActive === 'true' : undefined
            });
            const result = await this.integrationService.listIntegrations(query);
            if (!result.success) {
                throw createInternalServerError('Failed to retrieve integrations', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // GET /integrations/:id
    async getIntegration(req, res) {
        try {
            const { id } = req.params;
            if (!id) {
                throw createNotFoundError('Integration', '');
            }
            const result = await this.integrationService.getIntegration(id);
            if (!result.success) {
                throw createInternalServerError('Failed to retrieve integration', {
                    error: result.error?.message
                });
            }
            if (!result.data) {
                throw createNotFoundError('Integration', id);
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // POST /integrations
    async createIntegration(req, res) {
        try {
            const request = validateCreateIntegrationRequest(req.body);
            const userId = this.extractUserId(req);
            const result = await this.integrationService.createIntegration(request, userId);
            if (!result.success) {
                if (result.error?.message.includes('already exists')) {
                    throw createConflictError('Integration', 'name', request.name);
                }
                throw createInternalServerError('Failed to create integration', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.CREATED).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // PUT /integrations/:id
    async updateIntegration(req, res) {
        try {
            const { id } = req.params;
            const request = validateUpdateIntegrationRequest(req.body);
            const userId = this.extractUserId(req);
            if (!id) {
                throw createNotFoundError('Integration', '');
            }
            const result = await this.integrationService.updateIntegration(id, request, userId);
            if (!result.success) {
                if (result.error?.message.includes('not found')) {
                    throw createNotFoundError('Integration', id);
                }
                if (result.error?.message.includes('already exists')) {
                    throw createConflictError('Integration', 'name', request.name || '');
                }
                throw createInternalServerError('Failed to update integration', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // DELETE /integrations/:id
    async deleteIntegration(req, res) {
        try {
            const { id } = req.params;
            const userId = this.extractUserId(req);
            if (!id) {
                throw createNotFoundError('Integration', '');
            }
            const result = await this.integrationService.deleteIntegration(id, userId);
            if (!result.success) {
                if (result.error?.message.includes('not found')) {
                    throw createNotFoundError('Integration', id);
                }
                throw createInternalServerError('Failed to delete integration', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.NO_CONTENT).send();
        }
        catch (error) {
            throw error;
        }
    }
    // POST /integrations/:id/activate
    async activateIntegration(req, res) {
        try {
            const { id } = req.params;
            const userId = this.extractUserId(req);
            if (!id) {
                throw createNotFoundError('Integration', '');
            }
            const result = await this.integrationService.activateIntegration(id, userId);
            if (!result.success) {
                if (result.error?.message.includes('not found')) {
                    throw createNotFoundError('Integration', id);
                }
                throw createInternalServerError('Failed to activate integration', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // POST /integrations/:id/deactivate
    async deactivateIntegration(req, res) {
        try {
            const { id } = req.params;
            const userId = this.extractUserId(req);
            if (!id) {
                throw createNotFoundError('Integration', '');
            }
            const result = await this.integrationService.deactivateIntegration(id, userId);
            if (!result.success) {
                if (result.error?.message.includes('not found')) {
                    throw createNotFoundError('Integration', id);
                }
                throw createInternalServerError('Failed to deactivate integration', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // GET /integrations/by-name/:name
    async getIntegrationByName(req, res) {
        try {
            const { name } = req.params;
            if (!name) {
                throw createNotFoundError('Integration', '');
            }
            const result = await this.integrationService.getIntegrationByName(name);
            if (!result.success) {
                throw createInternalServerError('Failed to retrieve integration', {
                    error: result.error?.message
                });
            }
            if (!result.data) {
                throw createNotFoundError('Integration', name);
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // GET /integrations/by-type/:type
    async getIntegrationsByType(req, res) {
        try {
            const { type } = req.params;
            if (!type) {
                throw createNotFoundError('Integration type', '');
            }
            const result = await this.integrationService.getIntegrationsByType(type);
            if (!result.success) {
                throw createInternalServerError('Failed to retrieve integrations', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // GET /integrations/active
    async getActiveIntegrations(req, res) {
        try {
            const result = await this.integrationService.getActiveIntegrations();
            if (!result.success) {
                throw createInternalServerError('Failed to retrieve active integrations', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // GET /integrations/statistics
    async getStatistics(req, res) {
        try {
            const result = await this.integrationService.getStatistics();
            if (!result.success) {
                throw createInternalServerError('Failed to retrieve statistics', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // GET /integrations/health
    async healthCheck(req, res) {
        try {
            const result = await this.integrationService.healthCheck();
            if (!result.success) {
                throw createInternalServerError('Health check failed', {
                    error: result.error?.message
                });
            }
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: result.data
            });
        }
        catch (error) {
            throw error;
        }
    }
    // Helper method to extract user ID from request
    extractUserId(req) {
        // In a real implementation, this would extract from JWT token or session
        const userId = req.headers['x-user-id'] || req.user?.id;
        if (!userId) {
            throw createUnauthorizedError('User ID is required');
        }
        return userId;
    }
}
//# sourceMappingURL=integration-controller.js.map