/**
 * Tests for Domain Events Handler
 */

import { 
  InMemoryEventBus, 
  EventHandlerRegistry,
  EventPublisherService,
  IntegrationCreatedEventHandler,
  WebhookCreatedEventHandler,
  SyncJobCreatedEventHandler
} from '../services/domain-events-handler.js';
import { IntegrationCreatedEvent } from '@domain/events/integration-events.js';
import { WebhookCreatedEvent } from '@domain/events/webhook-events.js';
import { SyncJobCreatedEvent } from '@domain/events/sync-job-events.js';
import { IntegrationId } from '@domain/values/integration-id.js';
import { WebhookId } from '@domain/values/webhook-id.js';
import { SyncJobId } from '@domain/values/sync-job-id.js';

describe('InMemoryEventBus', () => {
  let eventBus: InMemoryEventBus;

  beforeEach(() => {
    eventBus = new InMemoryEventBus();
  });

  describe('publish and subscribe', () => {
    it('should publish events to registered handlers', async () => {
      const handler = {
        handle: jest.fn().mockResolvedValue(undefined)
      };

      eventBus.subscribe('integration.created', handler);

      const event = new IntegrationCreatedEvent(
        IntegrationId.create(),
        'Test Integration',
        'api',
        { config: 'test' }
      );

      await eventBus.publish(event);

      expect(handler.handle).toHaveBeenCalledWith(event);
    });

    it('should handle multiple handlers for same event type', async () => {
      const handler1 = {
        handle: jest.fn().mockResolvedValue(undefined)
      };
      const handler2 = {
        handle: jest.fn().mockResolvedValue(undefined)
      };

      eventBus.subscribe('integration.created', handler1);
      eventBus.subscribe('integration.created', handler2);

      const event = new IntegrationCreatedEvent(
        IntegrationId.create(),
        'Test Integration',
        'api',
        { config: 'test' }
      );

      await eventBus.publish(event);

      expect(handler1.handle).toHaveBeenCalledWith(event);
      expect(handler2.handle).toHaveBeenCalledWith(event);
    });

    it('should handle handler errors gracefully', async () => {
      const handler = {
        handle: jest.fn().mockRejectedValue(new Error('Handler error'))
      };

      eventBus.subscribe('integration.created', handler);

      const event = new IntegrationCreatedEvent(
        IntegrationId.create(),
        'Test Integration',
        'api',
        { config: 'test' }
      );

      // Should not throw
      await expect(eventBus.publish(event)).resolves.not.toThrow();

      expect(handler.handle).toHaveBeenCalledWith(event);
    });

    it('should unsubscribe handlers', () => {
      const handler = {
        handle: jest.fn().mockResolvedValue(undefined)
      };

      eventBus.subscribe('integration.created', handler);
      expect(eventBus.getHandlerCount('integration.created')).toBe(1);

      eventBus.unsubscribe('integration.created', handler);
      expect(eventBus.getHandlerCount('integration.created')).toBe(0);
    });

    it('should clear all handlers', () => {
      const handler = {
        handle: jest.fn().mockResolvedValue(undefined)
      };

      eventBus.subscribe('integration.created', handler);
      eventBus.subscribe('webhook.created', handler);
      eventBus.subscribe('syncjob.created', handler);

      expect(eventBus.getHandlerCount('integration.created')).toBe(1);
      expect(eventBus.getHandlerCount('webhook.created')).toBe(1);
      expect(eventBus.getHandlerCount('syncjob.created')).toBe(1);

      eventBus.clear();

      expect(eventBus.getHandlerCount('integration.created')).toBe(0);
      expect(eventBus.getHandlerCount('webhook.created')).toBe(0);
      expect(eventBus.getHandlerCount('syncjob.created')).toBe(0);
    });
  });
});

describe('Event Handlers', () => {
  describe('IntegrationCreatedEventHandler', () => {
    it('should handle integration created events', async () => {
      const handler = new IntegrationCreatedEventHandler();
      const event = new IntegrationCreatedEvent(
        IntegrationId.create(),
        'Test Integration',
        'api',
        { config: 'test' }
      );

      // Should not throw
      await expect(handler.handle(event)).resolves.not.toThrow();
    });
  });

  describe('WebhookCreatedEventHandler', () => {
    it('should handle webhook created events', async () => {
      const handler = new WebhookCreatedEventHandler();
      const event = new WebhookCreatedEvent(
        WebhookId.create(),
        'Test Webhook',
        'https://webhook.test.com',
        { integrationId: 'test' }
      );

      // Should not throw
      await expect(handler.handle(event)).resolves.not.toThrow();
    });
  });

  describe('SyncJobCreatedEventHandler', () => {
    it('should handle sync job created events', async () => {
      const handler = new SyncJobCreatedEventHandler();
      const event = new SyncJobCreatedEvent(
        SyncJobId.create(),
        'Test Sync Job',
        'database',
        'api',
        { integrationId: 'test' }
      );

      // Should not throw
      await expect(handler.handle(event)).resolves.not.toThrow();
    });
  });
});

describe('EventHandlerRegistry', () => {
  let eventBus: InMemoryEventBus;
  let registry: EventHandlerRegistry;

  beforeEach(() => {
    eventBus = new InMemoryEventBus();
    registry = new EventHandlerRegistry(eventBus);
  });

  it('should register all event handlers', () => {
    registry.registerAllHandlers();

    // Check that handlers are registered for all event types
    expect(eventBus.getHandlerCount('integration.created')).toBe(1);
    expect(eventBus.getHandlerCount('integration.updated')).toBe(1);
    expect(eventBus.getHandlerCount('integration.deleted')).toBe(1);
    expect(eventBus.getHandlerCount('webhook.created')).toBe(1);
    expect(eventBus.getHandlerCount('webhook.triggered')).toBe(1);
    expect(eventBus.getHandlerCount('webhook.failed')).toBe(1);
    expect(eventBus.getHandlerCount('syncjob.created')).toBe(1);
    expect(eventBus.getHandlerCount('syncjob.started')).toBe(1);
    expect(eventBus.getHandlerCount('syncjob.completed')).toBe(1);
    expect(eventBus.getHandlerCount('syncjob.failed')).toBe(1);
  });

  it('should unregister all event handlers', () => {
    registry.registerAllHandlers();
    
    // Verify handlers are registered
    expect(eventBus.getHandlerCount('integration.created')).toBe(1);

    registry.unregisterAllHandlers();

    // Verify handlers are unregistered
    expect(eventBus.getHandlerCount('integration.created')).toBe(0);
  });
});

describe('EventPublisherService', () => {
  let eventBus: InMemoryEventBus;
  let publisher: EventPublisherService;

  beforeEach(() => {
    eventBus = new InMemoryEventBus();
    publisher = new EventPublisherService(eventBus);
  });

  it('should publish single event', async () => {
    const handler = {
      handle: jest.fn().mockResolvedValue(undefined)
    };

    eventBus.subscribe('integration.created', handler);

    const event = new IntegrationCreatedEvent(
      IntegrationId.create(),
      'Test Integration',
      'api',
      { config: 'test' }
    );

    await publisher.publishEvent(event);

    expect(handler.handle).toHaveBeenCalledWith(event);
  });

  it('should publish multiple events', async () => {
    const handler = {
      handle: jest.fn().mockResolvedValue(undefined)
    };

    eventBus.subscribe('integration.created', handler);

    const events = [
      new IntegrationCreatedEvent(
        IntegrationId.create(),
        'Integration 1',
        'api',
        { config: 'test1' }
      ),
      new IntegrationCreatedEvent(
        IntegrationId.create(),
        'Integration 2',
        'webhook',
        { config: 'test2' }
      )
    ];

    await publisher.publishDomainEvents(events);

    expect(handler.handle).toHaveBeenCalledTimes(2);
    expect(handler.handle).toHaveBeenCalledWith(events[0]);
    expect(handler.handle).toHaveBeenCalledWith(events[1]);
  });

  it('should handle publishing errors gracefully', async () => {
    const handler = {
      handle: jest.fn().mockRejectedValue(new Error('Handler error'))
    };

    eventBus.subscribe('integration.created', handler);

    const event = new IntegrationCreatedEvent(
      IntegrationId.create(),
      'Test Integration',
      'api',
      { config: 'test' }
    );

    // Should not throw
    await expect(publisher.publishEvent(event)).resolves.not.toThrow();

    expect(handler.handle).toHaveBeenCalledWith(event);
  });
});
