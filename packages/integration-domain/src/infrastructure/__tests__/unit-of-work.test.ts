/**
 * Tests for Unit of Work Pattern
 */

import { InMemoryUnitOfWork, UnitOfWorkFactory, UnitOfWorkManager } from '../repositories/unit-of-work.js';
import { Integration, Webhook, SyncJob } from '@domain/index.js';

describe('InMemoryUnitOfWork', () => {
  let unitOfWork: InMemoryUnitOfWork;

  beforeEach(() => {
    unitOfWork = UnitOfWorkFactory.createInMemory();
  });

  describe('basic operations', () => {
    it('should create and find entities across repositories', async () => {
      await unitOfWork.begin();

      // Create entities
      const integration = Integration.create(
        'Test Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      const webhook = Webhook.create(
        'Test Webhook',
        integration.id,
        {
          url: 'https://webhook.test.com',
          method: 'POST'
        },
        ['test.event'],
        'user123'
      );

      const syncJob = SyncJob.create(
        'Test Sync Job',
        integration.id,
        {
          source: { type: 'database', connection: {} },
          target: { type: 'api', connection: {} }
        },
        'user123'
      );

      // Save entities
      await unitOfWork.integrations.create(integration);
      await unitOfWork.webhooks.create(webhook);
      await unitOfWork.syncJobs.create(syncJob);

      // Verify entities exist
      const integrationResult = await unitOfWork.integrations.findById(integration.id);
      const webhookResult = await unitOfWork.webhooks.findById(webhook.id);
      const syncJobResult = await unitOfWork.syncJobs.findById(syncJob.id);

      expect(integrationResult.success).toBe(true);
      expect(integrationResult.data).toEqual(integration);

      expect(webhookResult.success).toBe(true);
      expect(webhookResult.data).toEqual(webhook);

      expect(syncJobResult.success).toBe(true);
      expect(syncJobResult.data).toEqual(syncJob);

      await unitOfWork.commit();
    });

    it('should rollback all changes', async () => {
      await unitOfWork.begin();

      const integration = Integration.create(
        'Test Integration',
        'api',
        { endpoint: 'https://api.test.com' },
        'user123'
      );

      await unitOfWork.integrations.create(integration);

      // Verify entity exists before rollback
      const beforeRollback = await unitOfWork.integrations.findById(integration.id);
      expect(beforeRollback.success).toBe(true);
      expect(beforeRollback.data).toEqual(integration);

      await unitOfWork.rollback();

      // Verify entity is gone after rollback
      const afterRollback = await unitOfWork.integrations.findById(integration.id);
      expect(afterRollback.success).toBe(true);
      expect(afterRollback.data).toBeNull();
    });

    it('should prevent operations after commit', async () => {
      await unitOfWork.begin();
      await unitOfWork.commit();

      await expect(unitOfWork.begin()).rejects.toThrow('Unit of Work has already been committed or rolled back');
      await expect(unitOfWork.commit()).rejects.toThrow('Unit of Work has already been committed or rolled back');
      await expect(unitOfWork.rollback()).rejects.toThrow('Cannot rollback committed Unit of Work');
    });

    it('should prevent operations after rollback', async () => {
      await unitOfWork.begin();
      await unitOfWork.rollback();

      await expect(unitOfWork.begin()).rejects.toThrow('Unit of Work has already been committed or rolled back');
      await expect(unitOfWork.rollback()).rejects.toThrow('Unit of Work has already been committed or rolled back');
      await expect(unitOfWork.commit()).rejects.toThrow('Cannot commit rolled back Unit of Work');
    });
  });

  describe('state management', () => {
    it('should track committed state', async () => {
      expect(unitOfWork.isCommitted()).toBe(false);
      expect(unitOfWork.isRolledBack()).toBe(false);

      await unitOfWork.begin();
      expect(unitOfWork.isCommitted()).toBe(false);
      expect(unitOfWork.isRolledBack()).toBe(false);

      await unitOfWork.commit();
      expect(unitOfWork.isCommitted()).toBe(true);
      expect(unitOfWork.isRolledBack()).toBe(false);
    });

    it('should track rolled back state', async () => {
      expect(unitOfWork.isCommitted()).toBe(false);
      expect(unitOfWork.isRolledBack()).toBe(false);

      await unitOfWork.begin();
      expect(unitOfWork.isCommitted()).toBe(false);
      expect(unitOfWork.isRolledBack()).toBe(false);

      await unitOfWork.rollback();
      expect(unitOfWork.isCommitted()).toBe(false);
      expect(unitOfWork.isRolledBack()).toBe(true);
    });
  });
});

describe('UnitOfWorkManager', () => {
  let manager: UnitOfWorkManager;

  beforeEach(() => {
    manager = new UnitOfWorkManager();
  });

  describe('withTransaction', () => {
    it('should execute operation and commit on success', async () => {
      const unitOfWork = UnitOfWorkFactory.createInMemory();
      
      const result = await manager.withTransaction(unitOfWork, async (uow) => {
        const integration = Integration.create(
          'Test Integration',
          'api',
          { endpoint: 'https://api.test.com' },
          'user123'
        );

        await uow.integrations.create(integration);
        return integration;
      });

      expect(result.name).toBe('Test Integration');
      expect(unitOfWork.isCommitted()).toBe(true);

      // Verify entity was persisted
      const findResult = await unitOfWork.integrations.findById(result.id);
      expect(findResult.success).toBe(true);
      expect(findResult.data).toEqual(result);
    });

    it('should rollback on error', async () => {
      const unitOfWork = UnitOfWorkFactory.createInMemory();
      
      await expect(
        manager.withTransaction(unitOfWork, async (uow) => {
          const integration = Integration.create(
            'Test Integration',
            'api',
            { endpoint: 'https://api.test.com' },
            'user123'
          );

          await uow.integrations.create(integration);
          throw new Error('Simulated error');
        })
      ).rejects.toThrow('Simulated error');

      expect(unitOfWork.isRolledBack()).toBe(true);

      // Verify entity was not persisted
      const findResult = await unitOfWork.integrations.findByName('Test Integration');
      expect(findResult.success).toBe(true);
      expect(findResult.data).toBeNull();
    });

    it('should track current unit of work', async () => {
      const unitOfWork = UnitOfWorkFactory.createInMemory();
      
      expect(manager.getCurrentUnitOfWork()).toBeNull();
      expect(manager.hasActiveTransaction()).toBe(false);

      const promise = manager.withTransaction(unitOfWork, async (uow) => {
        expect(manager.getCurrentUnitOfWork()).toBe(uow);
        expect(manager.hasActiveTransaction()).toBe(true);
        return 'success';
      });

      expect(manager.getCurrentUnitOfWork()).toBeNull();
      expect(manager.hasActiveTransaction()).toBe(false);

      await promise;
    });
  });
});
