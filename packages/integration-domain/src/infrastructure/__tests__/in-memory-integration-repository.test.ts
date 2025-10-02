/**
 * Tests for InMemory Integration Repository
 */

import { InMemoryIntegrationRepository } from '../repositories/in-memory-integration-repository.js';
import { Integration, IntegrationId } from '@domain/index.js';

describe('InMemoryIntegrationRepository', () => {
  let repository: InMemoryIntegrationRepository;

  beforeEach(() => {
    repository = new InMemoryIntegrationRepository();
  });

  describe('create', () => {
    it('should create a new integration', async () => {
      const integration = Integration.create(
        'Test Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123',
        'Test integration for unit tests',
        ['test', 'api']
      );

      const result = await repository.create(integration);

      expect(result.success).toBe(true);
      expect(result.data).toBe(integration);
      expect(repository.getCount()).toBe(1);
    });

    it('should reject duplicate names', async () => {
      const integration1 = Integration.create(
        'Duplicate Name',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      const integration2 = Integration.create(
        'Duplicate Name',
        'webhook',
        { endpoint: 'https://webhook.test.com' },
        'user456'
      );

      await repository.create(integration1);
      const result = await repository.create(integration2);

      expect(result.success).toBe(false);
      expect(result.error?.message).toContain('already exists');
    });
  });

  describe('findById', () => {
    it('should find integration by id', async () => {
      const integration = Integration.create(
        'Test Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await repository.create(integration);
      const result = await repository.findById(integration.id);

      expect(result.success).toBe(true);
      expect(result.data).toEqual(integration);
    });

    it('should return null for non-existent id', async () => {
      const result = await repository.findById('non-existent-id');

      expect(result.success).toBe(true);
      expect(result.data).toBeNull();
    });
  });

  describe('findByName', () => {
    it('should find integration by name', async () => {
      const integration = Integration.create(
        'Unique Name',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await repository.create(integration);
      const result = await repository.findByName('Unique Name');

      expect(result.success).toBe(true);
      expect(result.data).toEqual(integration);
    });
  });

  describe('findByType', () => {
    it('should find integrations by type', async () => {
      const apiIntegration = Integration.create(
        'API Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      const webhookIntegration = Integration.create(
        'Webhook Integration',
        'webhook',
        { endpoint: 'https://webhook.test.com' },
        'user123'
      );

      await repository.create(apiIntegration);
      await repository.create(webhookIntegration);

      const result = await repository.findByType('api');

      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
      expect(result.data![0]).toEqual(apiIntegration);
    });
  });

  describe('findByStatus', () => {
    it('should find integrations by status', async () => {
      const integration = Integration.create(
        'Test Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await repository.create(integration);
      integration.activate('user123');

      const result = await repository.findByStatus('active');

      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
      expect(result.data![0]).toEqual(integration);
    });
  });

  describe('findActive', () => {
    it('should find only active integrations', async () => {
      const activeIntegration = Integration.create(
        'Active Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      const inactiveIntegration = Integration.create(
        'Inactive Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await repository.create(activeIntegration);
      await repository.create(inactiveIntegration);

      activeIntegration.activate('user123');
      inactiveIntegration.deactivate('user123');

      await repository.update(activeIntegration);
      await repository.update(inactiveIntegration);

      const result = await repository.findActive();

      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
      expect(result.data![0]).toEqual(activeIntegration);
    });
  });

  describe('update', () => {
    it('should update existing integration', async () => {
      const integration = Integration.create(
        'Test Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await repository.create(integration);
      integration.updateConfig({ endpoint: 'https://updated.api.test.com' }, 'user456');

      const result = await repository.update(integration);

      expect(result.success).toBe(true);
      expect(result.data).toEqual(integration);
    });

    it('should reject update with duplicate name', async () => {
      const integration1 = Integration.create(
        'Original Name',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      const integration2 = Integration.create(
        'Different Name',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await repository.create(integration1);
      await repository.create(integration2);

      // Try to rename integration2 to integration1's name
      integration2['props'].name = 'Original Name';

      const result = await repository.update(integration2);

      expect(result.success).toBe(false);
      expect(result.error?.message).toContain('already exists');
    });
  });

  describe('delete', () => {
    it('should delete existing integration', async () => {
      const integration = Integration.create(
        'Test Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await repository.create(integration);
      const deleteResult = await repository.delete(integration.id);

      expect(deleteResult.success).toBe(true);

      const findResult = await repository.findById(integration.id);
      expect(findResult.success).toBe(true);
      expect(findResult.data).toBeNull();
    });
  });

  describe('findAll with pagination', () => {
    it('should return paginated results', async () => {
      // Create multiple integrations
      for (let i = 0; i < 5; i++) {
        const integration = Integration.create(
          `Integration ${i}`,
          'api',
          { endpoint: `https://api${i}.test.com` },
          'user123'
        );
        await repository.create(integration);
      }

      const result = await repository.findAll({ page: 1, limit: 3 });

      expect(result.success).toBe(true);
      expect(result.data?.data).toHaveLength(3);
      expect(result.data?.pagination.total).toBe(5);
      expect(result.data?.pagination.totalPages).toBe(2);
      expect(result.data?.pagination.hasNext).toBe(true);
      expect(result.data?.pagination.hasPrev).toBe(false);
    });
  });

  describe('clear', () => {
    it('should clear all integrations', async () => {
      const integration = Integration.create(
        'Test Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await repository.create(integration);
      expect(repository.getCount()).toBe(1);

      repository.clear();
      expect(repository.getCount()).toBe(0);
    });
  });
});
