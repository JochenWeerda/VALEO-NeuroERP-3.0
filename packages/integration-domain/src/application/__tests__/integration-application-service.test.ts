/**
 * Tests for Integration Application Service
 */

import { IntegrationApplicationService } from '../services/integration-application-service.js';
import { UnitOfWorkFactory } from '@infrastructure/index.js';
import { validateCreateIntegrationRequest, validateUpdateIntegrationRequest } from '../dto/integration-dto.js';

describe('IntegrationApplicationService', () => {
  let applicationService: IntegrationApplicationService;
  let unitOfWork: any;

  beforeEach(() => {
    unitOfWork = UnitOfWorkFactory.createInMemory();
    applicationService = new IntegrationApplicationService(unitOfWork);
  });

  describe('createIntegration', () => {
    it('should create a new integration successfully', async () => {
      const request = validateCreateIntegrationRequest({
        name: 'Test API Integration',
        type: 'api',
        config: {
          endpoint: 'https://api.test.com',
          timeout: 30000
        },
        description: 'Test integration for unit tests',
        tags: ['test', 'api']
      });

      const result = await applicationService.createIntegration(request, 'user123');

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data!.name).toBe('Test API Integration');
      expect(result.data!.type).toBe('api');
      expect(result.data!.createdBy).toBe('user123');
    });

    it('should reject duplicate integration names', async () => {
      const request = validateCreateIntegrationRequest({
        name: 'Duplicate Name',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      });

      // Create first integration
      await applicationService.createIntegration(request, 'user123');

      // Try to create second integration with same name
      const result = await applicationService.createIntegration(request, 'user456');

      expect(result.success).toBe(false);
      expect(result.error?.message).toContain('already exists');
    });

    it('should validate request data', async () => {
      const invalidRequest = {
        name: '', // Invalid: empty name
        type: 'invalid-type', // Invalid type
        config: {} // Missing required config
      };

      expect(() => validateCreateIntegrationRequest(invalidRequest)).toThrow();
    });
  });

  describe('updateIntegration', () => {
    it('should update an existing integration', async () => {
      // Create integration first
      const createRequest = validateCreateIntegrationRequest({
        name: 'Original Name',
        type: 'api',
        config: { endpoint: 'https://original.api.com' }
      });

      const createResult = await applicationService.createIntegration(createRequest, 'user123');
      expect(createResult.success).toBe(true);

      // Update integration
      const updateRequest = validateUpdateIntegrationRequest({
        name: 'Updated Name',
        config: { endpoint: 'https://updated.api.com' },
        description: 'Updated description'
      });

      const updateResult = await applicationService.updateIntegration(
        createResult.data!.id,
        updateRequest,
        'user456'
      );

      expect(updateResult.success).toBe(true);
      expect(updateResult.data!.name).toBe('Updated Name');
      expect(updateResult.data!.description).toBe('Updated description');
      expect(updateResult.data!.updatedBy).toBe('user456');
    });

    it('should reject update of non-existent integration', async () => {
      const updateRequest = validateUpdateIntegrationRequest({
        name: 'Non-existent'
      });

      const result = await applicationService.updateIntegration(
        'non-existent-id',
        updateRequest,
        'user123'
      );

      expect(result.success).toBe(false);
      expect(result.error?.message).toContain('not found');
    });
  });

  describe('deleteIntegration', () => {
    it('should delete an existing integration', async () => {
      // Create integration first
      const createRequest = validateCreateIntegrationRequest({
        name: 'To Be Deleted',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      });

      const createResult = await applicationService.createIntegration(createRequest, 'user123');
      expect(createResult.success).toBe(true);

      // Delete integration
      const deleteResult = await applicationService.deleteIntegration(
        createResult.data!.id,
        'user456'
      );

      expect(deleteResult.success).toBe(true);

      // Verify integration is deleted
      const getResult = await applicationService.getIntegration(createResult.data!.id);
      expect(getResult.success).toBe(true);
      expect(getResult.data).toBeNull();
    });

    it('should reject deletion of non-existent integration', async () => {
      const result = await applicationService.deleteIntegration('non-existent-id', 'user123');

      expect(result.success).toBe(false);
      expect(result.error?.message).toContain('not found');
    });
  });

  describe('activateIntegration', () => {
    it('should activate an existing integration', async () => {
      // Create integration first
      const createRequest = validateCreateIntegrationRequest({
        name: 'To Be Activated',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      });

      const createResult = await applicationService.createIntegration(createRequest, 'user123');
      expect(createResult.success).toBe(true);

      // Activate integration
      const activateResult = await applicationService.activateIntegration(
        createResult.data!.id,
        'user456'
      );

      expect(activateResult.success).toBe(true);
      expect(activateResult.data!.status).toBe('active');
      expect(activateResult.data!.isActive).toBe(true);
    });
  });

  describe('deactivateIntegration', () => {
    it('should deactivate an existing integration', async () => {
      // Create and activate integration first
      const createRequest = validateCreateIntegrationRequest({
        name: 'To Be Deactivated',
        type: 'api',
        config: { endpoint: 'https://api.test.com' }
      });

      const createResult = await applicationService.createIntegration(createRequest, 'user123');
      expect(createResult.success).toBe(true);

      await applicationService.activateIntegration(createResult.data!.id, 'user123');

      // Deactivate integration
      const deactivateResult = await applicationService.deactivateIntegration(
        createResult.data!.id,
        'user456'
      );

      expect(deactivateResult.success).toBe(true);
      expect(deactivateResult.data!.status).toBe('inactive');
      expect(deactivateResult.data!.isActive).toBe(false);
    });
  });

  describe('query methods', () => {
    beforeEach(async () => {
      // Create test data
      const integrations = [
        { name: 'API Integration 1', type: 'api' as const },
        { name: 'Webhook Integration 1', type: 'webhook' as const },
        { name: 'API Integration 2', type: 'api' as const }
      ];

      for (const integration of integrations) {
        const request = validateCreateIntegrationRequest({
          ...integration,
          config: { endpoint: 'https://api.test.com' }
        });
        await applicationService.createIntegration(request, 'user123');
      }
    });

    it('should get integration by id', async () => {
      const listResult = await applicationService.listIntegrations({ page: 1, limit: 1 });
      expect(listResult.success).toBe(true);
      expect(listResult.data!.data).toHaveLength(1);

      const integration = listResult.data!.data[0];
      const getResult = await applicationService.getIntegration(integration.id);

      expect(getResult.success).toBe(true);
      expect(getResult.data).toEqual(integration);
    });

    it('should list integrations with pagination', async () => {
      const result = await applicationService.listIntegrations({
        page: 1,
        limit: 2
      });

      expect(result.success).toBe(true);
      expect(result.data!.data).toHaveLength(2);
      expect(result.data!.pagination.total).toBe(3);
      expect(result.data!.pagination.totalPages).toBe(2);
      expect(result.data!.pagination.hasNext).toBe(true);
      expect(result.data!.pagination.hasPrev).toBe(false);
    });

    it('should get integrations by type', async () => {
      const result = await applicationService.getIntegrationsByType('api');

      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(2);
      expect(result.data!.every(i => i.type === 'api')).toBe(true);
    });

    it('should get active integrations', async () => {
      // Activate one integration
      const listResult = await applicationService.listIntegrations({ page: 1, limit: 1 });
      const integration = listResult.data!.data[0];
      await applicationService.activateIntegration(integration.id, 'user123');

      const result = await applicationService.getActiveIntegrations();

      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
      expect(result.data![0].isActive).toBe(true);
    });
  });

  describe('utility methods', () => {
    it('should perform health check', async () => {
      const result = await applicationService.healthCheck();

      expect(result.success).toBe(true);
      expect(result.data!.status).toBe('healthy');
      expect(result.data!.timestamp).toBeDefined();
    });

    it('should get statistics', async () => {
      // Create test data
      const integrations = [
        { name: 'API Integration', type: 'api' as const },
        { name: 'Webhook Integration', type: 'webhook' as const }
      ];

      for (const integration of integrations) {
        const request = validateCreateIntegrationRequest({
          ...integration,
          config: { endpoint: 'https://api.test.com' }
        });
        await applicationService.createIntegration(request, 'user123');
      }

      // Activate one integration
      const listResult = await applicationService.listIntegrations({ page: 1, limit: 1 });
      const integration = listResult.data!.data[0];
      await applicationService.activateIntegration(integration.id, 'user123');

      const result = await applicationService.getStatistics();

      expect(result.success).toBe(true);
      expect(result.data!.total).toBe(2);
      expect(result.data!.active).toBe(1);
      expect(result.data!.inactive).toBe(1);
      expect(result.data!.byType.api).toBe(1);
      expect(result.data!.byType.webhook).toBe(1);
    });
  });
});
