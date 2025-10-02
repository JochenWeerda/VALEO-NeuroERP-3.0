/**
 * VALEO NeuroERP 3.0 - Product Entity Tests
 *
 * Unit tests for Product domain entity following TDD principles.
 */

import { describe, it, mock } from 'node:test';
import assert from 'node:assert';
import {
  ProductEntity,
  CreateProductCommand,
  UpdateProductCommand,
  ProductCreatedEvent,
  ProductUpdatedEvent
} from '../core/entities/product';
import { createProductId } from '@packages/data-models/branded-types';

describe('ProductEntity', () => {
  const validId = createProductId('test-id-123');
  const now = new Date('2025-01-01T00:00:00Z');

  describe('create', () => {
    it('should create a valid product entity', () => {
      // Arrange
      const command: CreateProductCommand = {
        name: 'Test Product',
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
        const entity = ProductEntity.create(command);

        // Assert
        assert.ok(entity.id);
        assert.equal(entity.name, 'Test Product');
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
      const command: CreateProductCommand = {
        name: '',
        status: 'active'
      };

      // Act & Assert
      assert.throws(
        () => ProductEntity.create(command),
        { message: 'Product name is required' }
      );
    });

    it('should throw error for missing name', () => {
      // Arrange
      const command: CreateProductCommand = {
        name: '   ', // whitespace only
        status: 'active'
      };

      // Act & Assert
      assert.throws(
        () => ProductEntity.create(command),
        { message: 'Product name is required' }
      );
    });
  });

  describe('update', () => {
    let entity: ProductEntity;

    beforeEach(() => {
      const command: CreateProductCommand = {
        name: 'Original Product',
        status: 'active'
      };
      entity = ProductEntity.create(command);
    });

    it('should update entity properties', () => {
      // Arrange
      const updateCommand: UpdateProductCommand = {
        name: 'Updated Product',
        status: 'inactive'
      };

      // Act
      const updatedEntity = entity.update(updateCommand);

      // Assert
      assert.equal(updatedEntity.name, 'Updated Product');
      assert.equal(updatedEntity.status, 'inactive');
      assert.ok(updatedEntity.updatedAt > entity.updatedAt);
    });

    it('should partially update entity', () => {
      // Arrange
      const updateCommand: UpdateProductCommand = {
        status: 'inactive'
        // name not provided, should remain unchanged
      };

      // Act
      const updatedEntity = entity.update(updateCommand);

      // Assert
      assert.equal(updatedEntity.name, 'Original Product'); // unchanged
      assert.equal(updatedEntity.status, 'inactive'); // updated
    });
  });

  describe('business methods', () => {
    it('should return correct active status', () => {
      // Arrange
      const activeCommand: CreateProductCommand = {
        name: 'Active Product',
        status: 'active'
      };
      const inactiveCommand: CreateProductCommand = {
        name: 'Inactive Product',
        status: 'inactive'
      };

      // Act
      const activeEntity = ProductEntity.create(activeCommand);
      const inactiveEntity = ProductEntity.create(inactiveCommand);

      // Assert
      assert.ok(activeEntity.isActive());
      assert.ok(!inactiveEntity.isActive());
    });
  });

  describe('domain events', () => {
    it('should create ProductCreatedEvent', () => {
      // Arrange
      const command: CreateProductCommand = {
        name: 'Test Product',
        status: 'active'
      };
      const entity = ProductEntity.create(command);

      // Act
      const event = new ProductCreatedEvent(entity);

      // Assert
      assert.equal(event.type, 'ProductCreated');
      assert.equal(event.aggregateId, entity.id);
      assert.ok(event.occurredAt instanceof Date);
      assert.equal(event.product, entity);
    });

    it('should create ProductUpdatedEvent', () => {
      // Arrange
      const command: CreateProductCommand = {
        name: 'Test Product',
        status: 'active'
      };
      const entity = ProductEntity.create(command);
      const changes = { status: 'inactive' };

      // Act
      const event = new ProductUpdatedEvent(entity, changes);

      // Assert
      assert.equal(event.type, 'ProductUpdated');
      assert.equal(event.aggregateId, entity.id);
      assert.ok(event.occurredAt instanceof Date);
      assert.equal(event.changes, changes);
    });
  });
});
