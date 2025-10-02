/**
 * VALEO NeuroERP 3.0 - Order Entity Tests
 *
 * Unit tests for Order domain entity following TDD principles.
 */

import { describe, it, mock } from 'node:test';
import assert from 'node:assert';
import {
  OrderEntity,
  CreateOrderCommand,
  UpdateOrderCommand,
  OrderCreatedEvent,
  OrderUpdatedEvent
} from '../core/entities/order';
import { createOrderId } from '@packages/data-models/branded-types';

describe('OrderEntity', () => {
  const validId = createOrderId('test-id-123');
  const now = new Date('2025-01-01T00:00:00Z');

  describe('create', () => {
    it('should create a valid order entity', () => {
      // Arrange
      const command: CreateOrderCommand = {
        name: 'Test Order',
        status: 'active'
      };

      // Mock Date.now to return consistent timestamp
      const originalDate = global.Date;
      global.Date = class extends Date {
        constructor(...args: any[]) {
          if (args.length === 0) {
            super(now);
          } else {
            super(...args);
          }
        }
        static now() {
          return now.getTime();
        }
      } as any;

      try {
        // Act
        const entity = OrderEntity.create(command);

        // Assert
        assert.ok(entity.id);
        assert.equal(entity.name, 'Test Order');
        assert.equal(entity.status, 'active');
        assert.equal(entity.createdAt.getTime(), now.getTime());
        assert.equal(entity.updatedAt.getTime(), now.getTime());
        assert.ok(entity.isActive());
      } finally {
        global.Date = originalDate;
      }
    });

    it('should throw error for invalid name', () => {
      // Arrange
      const command: CreateOrderCommand = {
        name: '',
        status: 'active'
      };

      // Act & Assert
      assert.throws(
        () => OrderEntity.create(command),
        { message: 'Order name is required' }
      );
    });

    it('should throw error for missing name', () => {
      // Arrange
      const command: CreateOrderCommand = {
        name: '   ', // whitespace only
        status: 'active'
      };

      // Act & Assert
      assert.throws(
        () => OrderEntity.create(command),
        { message: 'Order name is required' }
      );
    });
  });

  describe('update', () => {
    let entity: OrderEntity;

    beforeEach(() => {
      const command: CreateOrderCommand = {
        name: 'Original Order',
        status: 'active'
      };
      entity = OrderEntity.create(command);
    });

    it('should update entity properties', () => {
      // Arrange
      const updateCommand: UpdateOrderCommand = {
        name: 'Updated Order',
        status: 'inactive'
      };

      // Act
      const updatedEntity = entity.update(updateCommand);

      // Assert
      assert.equal(updatedEntity.name, 'Updated Order');
      assert.equal(updatedEntity.status, 'inactive');
      assert.ok(updatedEntity.updatedAt > entity.updatedAt);
    });

    it('should partially update entity', () => {
      // Arrange
      const updateCommand: UpdateOrderCommand = {
        status: 'inactive'
        // name not provided, should remain unchanged
      };

      // Act
      const updatedEntity = entity.update(updateCommand);

      // Assert
      assert.equal(updatedEntity.name, 'Original Order'); // unchanged
      assert.equal(updatedEntity.status, 'inactive'); // updated
    });
  });

  describe('business methods', () => {
    it('should return correct active status', () => {
      // Arrange
      const activeCommand: CreateOrderCommand = {
        name: 'Active Order',
        status: 'active'
      };
      const inactiveCommand: CreateOrderCommand = {
        name: 'Inactive Order',
        status: 'inactive'
      };

      // Act
      const activeEntity = OrderEntity.create(activeCommand);
      const inactiveEntity = OrderEntity.create(inactiveCommand);

      // Assert
      assert.ok(activeEntity.isActive());
      assert.ok(!inactiveEntity.isActive());
    });
  });

  describe('domain events', () => {
    it('should create OrderCreatedEvent', () => {
      // Arrange
      const command: CreateOrderCommand = {
        name: 'Test Order',
        status: 'active'
      };
      const entity = OrderEntity.create(command);

      // Act
      const event = new OrderCreatedEvent(entity);

      // Assert
      assert.equal(event.type, 'OrderCreated');
      assert.equal(event.aggregateId, entity.id);
      assert.ok(event.occurredAt instanceof Date);
      assert.equal(event.order, entity);
    });

    it('should create OrderUpdatedEvent', () => {
      // Arrange
      const command: CreateOrderCommand = {
        name: 'Test Order',
        status: 'active'
      };
      const entity = OrderEntity.create(command);
      const changes = { status: 'inactive' };

      // Act
      const event = new OrderUpdatedEvent(entity, changes);

      // Assert
      assert.equal(event.type, 'OrderUpdated');
      assert.equal(event.aggregateId, entity.id);
      assert.ok(event.occurredAt instanceof Date);
      assert.equal(event.changes, changes);
    });
  });
});
