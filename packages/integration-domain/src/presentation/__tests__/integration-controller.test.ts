/**
 * Tests for Integration Controller
 */

import request from 'supertest';
import { IntegrationController } from '../controllers/integration-controller.js';
import { IntegrationApplicationService } from '@application/services/integration-application-service.js';
import { UnitOfWorkFactory } from '@infrastructure/index.js';
import { HttpStatusCode } from '../errors/api-errors.js';

// Mock Express app for testing
const createTestApp = (controller: IntegrationController) => {
  const express = require('express');
  const app = express();
  
  app.use(express.json());
  
  // Mock routes
  app.get('/integrations', (req: any, res: any) => controller.listIntegrations(req, res));
  app.get('/integrations/:id', (req: any, res: any) => controller.getIntegration(req, res));
  app.post('/integrations', (req: any, res: any) => controller.createIntegration(req, res));
  app.put('/integrations/:id', (req: any, res: any) => controller.updateIntegration(req, res));
  app.delete('/integrations/:id', (req: any, res: any) => controller.deleteIntegration(req, res));
  app.post('/integrations/:id/activate', (req: any, res: any) => controller.activateIntegration(req, res));
  app.post('/integrations/:id/deactivate', (req: any, res: any) => controller.deactivateIntegration(req, res));
  app.get('/integrations/by-name/:name', (req: any, res: any) => controller.getIntegrationByName(req, res));
  app.get('/integrations/by-type/:type', (req: any, res: any) => controller.getIntegrationsByType(req, res));
  app.get('/integrations/active', (req: any, res: any) => controller.getActiveIntegrations(req, res));
  app.get('/integrations/statistics', (req: any, res: any) => controller.getStatistics(req, res));
  app.get('/integrations/health', (req: any, res: any) => controller.healthCheck(req, res));
  
  return app;
};

describe('IntegrationController', () => {
  let controller: IntegrationController;
  let applicationService: IntegrationApplicationService;
  let app: any;

  beforeEach(() => {
    const unitOfWork = UnitOfWorkFactory.createInMemory();
    applicationService = new IntegrationApplicationService(unitOfWork);
    controller = new IntegrationController(applicationService);
    app = createTestApp(controller);
  });

  describe('POST /integrations', () => {
    it('should create a new integration', async () => {
      const integrationData = {
        name: 'Test API Integration',
        type: 'api',
        config: {
          endpoint: 'https://api.test.com',
          timeout: 30000
        },
        description: 'Test integration',
        tags: ['test']
      };

      const response = await request(app)
        .post('/integrations')
        .set('x-user-id', 'user123')
        .send(integrationData)
        .expect(HttpStatusCode.CREATED);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.data.name).toBe(integrationData.name);
      expect(response.body.data.type).toBe(integrationData.type);
      expect(response.body.data.createdBy).toBe('user123');
    });

    it('should reject invalid integration data', async () => {
      const invalidData = {
        name: '', // Invalid: empty name
        type: 'invalid-type', // Invalid type
        config: {} // Missing required config
      };

      const response = await request(app)
        .post('/integrations')
        .set('x-user-id', 'user123')
        .send(invalidData)
        .expect(HttpStatusCode.UNPROCESSABLE_ENTITY);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBeDefined();
    });

    it('should reject request without user ID', async () => {
      const integrationData = {
        name: 'Test Integration',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      };

      const response = await request(app)
        .post('/integrations')
        .send(integrationData)
        .expect(HttpStatusCode.UNAUTHORIZED);

      expect(response.body.success).toBe(false);
      expect(response.body.error.message).toContain('User ID is required');
    });
  });

  describe('GET /integrations', () => {
    beforeEach(async () => {
      // Create test data
      const integrations = [
        { name: 'API Integration 1', type: 'api' as const },
        { name: 'Webhook Integration 1', type: 'webhook' as const },
        { name: 'API Integration 2', type: 'api' as const }
      ];

      for (const integration of integrations) {
        await applicationService.createIntegration({
          ...integration,
          config: { endpoint: 'https://api.test.com' }
        }, 'user123');
      }
    });

    it('should list integrations with pagination', async () => {
      const response = await request(app)
        .get('/integrations?page=1&limit=2')
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.data).toHaveLength(2);
      expect(response.body.data.pagination.total).toBe(3);
      expect(response.body.data.pagination.totalPages).toBe(2);
    });

    it('should filter integrations by type', async () => {
      const response = await request(app)
        .get('/integrations?type=api')
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.data).toHaveLength(2);
      expect(response.body.data.data.every((i: any) => i.type === 'api')).toBe(true);
    });

    it('should sort integrations', async () => {
      const response = await request(app)
        .get('/integrations?sortBy=name&sortOrder=asc')
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.data[0].name).toBe('API Integration 1');
    });
  });

  describe('GET /integrations/:id', () => {
    it('should get integration by ID', async () => {
      // Create integration first
      const createResult = await applicationService.createIntegration({
        name: 'Test Integration',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      }, 'user123');

      expect(createResult.success).toBe(true);
      const integrationId = createResult.data!.id;

      const response = await request(app)
        .get(`/integrations/${integrationId}`)
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.id).toBe(integrationId);
      expect(response.body.data.name).toBe('Test Integration');
    });

    it('should return 404 for non-existent integration', async () => {
      const response = await request(app)
        .get('/integrations/non-existent-id')
        .expect(HttpStatusCode.NOT_FOUND);

      expect(response.body.success).toBe(false);
      expect(response.body.error.message).toContain('not found');
    });
  });

  describe('PUT /integrations/:id', () => {
    it('should update existing integration', async () => {
      // Create integration first
      const createResult = await applicationService.createIntegration({
        name: 'Original Name',
        type: 'api',
        config: { endpoint: 'https://original.api.com' }
      }, 'user123');

      expect(createResult.success).toBe(true);
      const integrationId = createResult.data!.id;

      const updateData = {
        name: 'Updated Name',
        description: 'Updated description'
      };

      const response = await request(app)
        .put(`/integrations/${integrationId}`)
        .set('x-user-id', 'user456')
        .send(updateData)
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.name).toBe('Updated Name');
      expect(response.body.data.description).toBe('Updated description');
      expect(response.body.data.updatedBy).toBe('user456');
    });

    it('should return 404 for non-existent integration', async () => {
      const response = await request(app)
        .put('/integrations/non-existent-id')
        .set('x-user-id', 'user123')
        .send({ name: 'Updated Name' })
        .expect(HttpStatusCode.NOT_FOUND);

      expect(response.body.success).toBe(false);
      expect(response.body.error.message).toContain('not found');
    });
  });

  describe('DELETE /integrations/:id', () => {
    it('should delete existing integration', async () => {
      // Create integration first
      const createResult = await applicationService.createIntegration({
        name: 'To Be Deleted',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      }, 'user123');

      expect(createResult.success).toBe(true);
      const integrationId = createResult.data!.id;

      await request(app)
        .delete(`/integrations/${integrationId}`)
        .set('x-user-id', 'user456')
        .expect(HttpStatusCode.NO_CONTENT);

      // Verify integration is deleted
      const getResult = await applicationService.getIntegration(integrationId);
      expect(getResult.success).toBe(true);
      expect(getResult.data).toBeNull();
    });

    it('should return 404 for non-existent integration', async () => {
      const response = await request(app)
        .delete('/integrations/non-existent-id')
        .set('x-user-id', 'user123')
        .expect(HttpStatusCode.NOT_FOUND);

      expect(response.body.success).toBe(false);
      expect(response.body.error.message).toContain('not found');
    });
  });

  describe('POST /integrations/:id/activate', () => {
    it('should activate integration', async () => {
      // Create integration first
      const createResult = await applicationService.createIntegration({
        name: 'To Be Activated',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      }, 'user123');

      expect(createResult.success).toBe(true);
      const integrationId = createResult.data!.id;

      const response = await request(app)
        .post(`/integrations/${integrationId}/activate`)
        .set('x-user-id', 'user456')
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('active');
      expect(response.body.data.isActive).toBe(true);
    });
  });

  describe('POST /integrations/:id/deactivate', () => {
    it('should deactivate integration', async () => {
      // Create and activate integration first
      const createResult = await applicationService.createIntegration({
        name: 'To Be Deactivated',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      }, 'user123');

      expect(createResult.success).toBe(true);
      const integrationId = createResult.data!.id;

      await applicationService.activateIntegration(integrationId, 'user123');

      const response = await request(app)
        .post(`/integrations/${integrationId}/deactivate`)
        .set('x-user-id', 'user456')
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('inactive');
      expect(response.body.data.isActive).toBe(false);
    });
  });

  describe('GET /integrations/statistics', () => {
    it('should return integration statistics', async () => {
      // Create test data
      const integrations = [
        { name: 'API Integration', type: 'api' as const },
        { name: 'Webhook Integration', type: 'webhook' as const }
      ];

      for (const integration of integrations) {
        await applicationService.createIntegration({
          ...integration,
          config: { endpoint: 'https://api.test.com' }
        }, 'user123');
      }

      // Activate one integration
      const listResult = await applicationService.listIntegrations({ page: 1, limit: 1 });
      const integration = listResult.data!.data[0];
      await applicationService.activateIntegration(integration.id, 'user123');

      const response = await request(app)
        .get('/integrations/statistics')
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.total).toBe(2);
      expect(response.body.data.active).toBe(1);
      expect(response.body.data.inactive).toBe(1);
      expect(response.body.data.byType.api).toBe(1);
      expect(response.body.data.byType.webhook).toBe(1);
    });
  });

  describe('GET /integrations/health', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/integrations/health')
        .expect(HttpStatusCode.OK);

      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('healthy');
      expect(response.body.data.timestamp).toBeDefined();
    });
  });
});

