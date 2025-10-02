/**
 * VALEO NeuroERP 3.0 - Inventory Entity Tests
 *
 * Unit tests for Inventory domain entity following TDD principles.
 */

import { describe, it, mock } from 'node:test';
import assert from 'node:assert';
import {
  InventoryEntity,
  CreateInventoryCommand,
  UpdateInventoryCommand,
  InventoryCreatedEvent,
  InventoryUpdatedEvent
} from '../core/entities/inventory';
import { createInventoryId } from '@packages/data-models/branded-types';

describe('InventoryEntity', () => {
  const validId = createInventoryId('test-id-123');
  const now = new Date('2025-01-01T00:00:00Z');

  describe('create', () => {
    it('should create a valid inventory entity', () => {
      // Arrange
      const command: CreateInventoryCommand = {
        name: 'Test Inventory',
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
        const entity = InventoryEntity.create(command);

        // Assert
        assert.ok(entity.id);
        assert.equal(entity.name, 'Test Inventory');
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
      const command: CreateInventoryCommand = {
        name: '',
        status: 'active'
      };

      // Act & Assert
      assert.throws(
        () => InventoryEntity.create(command),
        { message: 'Inventory name is required' }
      );
    });

    it('should throw error for missing name', () => {
      // Arrange
      const command: CreateInventoryCommand = {
        name: '   ', // whitespace only
        status: 'active'
      };

      // Act & Assert
      assert.throws(
        () => InventoryEntity.create(command),
        { message: 'Inventory name is required' }
      );
    });
  });

  describe('update', () => {
    let entity: InventoryEntity;

    beforeEach(() => {
      const command: CreateInventoryCommand = {
        name: 'Original Inventory',
        status: 'active'
      };
      entity = InventoryEntity.create(command);
    });

    it('should update entity properties', () => {
      // Arrange
      const updateCommand: UpdateInventoryCommand = {
        name: 'Updated Inventory',
        status: 'inactive'
      };

      // Act
      const updatedEntity = entity.update(updateCommand);

      // Assert
      assert.equal(updatedEntity.name, 'Updated Inventory');
      assert.equal(updatedEntity.status, 'inactive');
      assert.ok(updatedEntity.updatedAt > entity.updatedAt);
    });

    it('should partially update entity', () => {
      // Arrange
      const updateCommand: UpdateInventoryCommand = {
        status: 'inactive'
        // name not provided, should remain unchanged
      };

      // Act
      const updatedEntity = entity.update(updateCommand);

      // Assert
      assert.equal(updatedEntity.name, 'Original Inventory'); // unchanged
      assert.equal(updatedEntity.status, 'inactive'); // updated
    });
  });

  describe('business methods', () => {
    it('should return correct active status', () => {
      // Arrange
      const activeCommand: CreateInventoryCommand = {
        name: 'Active Inventory',
        status: 'active'
      };
      const inactiveCommand: CreateInventoryCommand = {
        name: 'Inactive Inventory',
        status: 'inactive'
      };

      // Act
      const activeEntity = InventoryEntity.create(activeCommand);
      const inactiveEntity = InventoryEntity.create(inactiveCommand);

      // Assert
      assert.ok(activeEntity.isActive());
      assert.ok(!inactiveEntity.isActive());
    });
  });

  describe('domain events', () => {
    it('should create InventoryCreatedEvent', () => {
      // Arrange
      const command: CreateInventoryCommand = {
        name: 'Test Inventory',
        status: 'active'
      };
      const entity = InventoryEntity.create(command);

      // Act
      const event = new InventoryCreatedEvent(entity);

      // Assert
      assert.equal(event.type, 'InventoryCreated');
      assert.equal(event.aggregateId, entity.id);
      assert.ok(event.occurredAt instanceof Date);
      assert.equal(event.inventory, entity);
    });

    it('should create InventoryUpdatedEvent', () => {
      // Arrange
      const command: CreateInventoryCommand = {
        name: 'Test Inventory',
        status: 'active'
      };
      const entity = InventoryEntity.create(command);
      const changes = { status: 'inactive' };

      // Act
      const event = new InventoryUpdatedEvent(entity, changes);

      // Assert
      assert.equal(event.type, 'InventoryUpdated');
      assert.equal(event.aggregateId, entity.id);
      assert.ok(event.occurredAt instanceof Date);
      assert.equal(event.changes, changes);
    });
  });
});
