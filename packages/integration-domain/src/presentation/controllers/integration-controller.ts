/**
 * Integration API Controller
 */

import type { Request, Response } from 'express';
import { IntegrationApplicationService } from '@application/services/integration-application-service.js';
import { 
  validateCreateIntegrationRequest,
  validateIntegrationQuery,
  validateUpdateIntegrationRequest 
} from '@application/dto/integration-dto.js';
import { 
  HttpStatusCode,
  createConflictError,
  createInternalServerError,
  createNotFoundError,
  createUnauthorizedError
} from '../errors/api-errors.js';

export class IntegrationController {
  constructor(private readonly integrationService: IntegrationApplicationService) {}

  // GET /integrations
  async listIntegrations(req: Request, res: Response): Promise<void> {
    const query = validateIntegrationQuery({
        page: parseInt(req.query.page as string) || 1,
        limit: parseInt(req.query.limit as string) || 10,
        sortBy: req.query.sortBy as string,
        sortOrder: req.query.sortOrder as 'asc' | 'desc',
        type: req.query.type as string,
        status: req.query.status as string,
        tags: req.query.tags ? (req.query.tags as string).split(',') : undefined,
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

  // GET /integrations/:id
  async getIntegration(req: Request, res: Response): Promise<void> {
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

  // POST /integrations
  async createIntegration(req: Request, res: Response): Promise<void> {
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

  // PUT /integrations/:id
  async updateIntegration(req: Request, res: Response): Promise<void> {
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

  // DELETE /integrations/:id
  async deleteIntegration(req: Request, res: Response): Promise<void> {
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

  // POST /integrations/:id/activate
  async activateIntegration(req: Request, res: Response): Promise<void> {
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

  // POST /integrations/:id/deactivate
  async deactivateIntegration(req: Request, res: Response): Promise<void> {
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

  // GET /integrations/by-name/:name
  async getIntegrationByName(req: Request, res: Response): Promise<void> {
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

  // GET /integrations/by-type/:type
  async getIntegrationsByType(req: Request, res: Response): Promise<void> {
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

  // GET /integrations/active
  async getActiveIntegrations(req: Request, res: Response): Promise<void> {
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

  // GET /integrations/statistics
  async getStatistics(req: Request, res: Response): Promise<void> {
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

  // GET /integrations/health
  async healthCheck(req: Request, res: Response): Promise<void> {
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

  // Helper method to extract user ID from request
  private extractUserId(req: Request): string {
    // In a real implementation, this would extract from JWT token or session
    const userId = req.headers['x-user-id'] as string || (req as any).user?.id;
    
    if (!userId) {
      throw createUnauthorizedError('User ID is required');
    }

    return userId;
  }
}
