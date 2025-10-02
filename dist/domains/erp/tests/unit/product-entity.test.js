"use strict";
/**
 * VALEO NeuroERP 3.0 - Product Entity Tests
 *
 * Unit tests for Product domain entity following TDD principles.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const node_assert_1 = __importDefault(require("node:assert"));
const product_1 = require("../core/entities/product");
const branded_types_1 = require("@packages/data-models/branded-types");
(0, node_test_1.describe)('ProductEntity', () => {
    const validId = (0, branded_types_1.createProductId)('test-id-123');
    const now = new Date('2025-01-01T00:00:00Z');
    (0, node_test_1.describe)('create', () => {
        (0, node_test_1.it)('should create a valid product entity', () => {
            // Arrange
            const command = {
                name: 'Test Product',
                status: 'active'
            };
            // Mock Date.now to return consistent timestamp
            const originalDate = global.Date;
            global.Date = class extends Date {
                constructor(...args) {
                    if (args.length === 0) {
                        super(now);
                    }
                    else {
                        super(...args);
                    }
                }
                static now() {
                    return now.getTime();
                }
            };
            try {
                // Act
                const entity = product_1.ProductEntity.create(command);
                // Assert
                node_assert_1.default.ok(entity.id);
                node_assert_1.default.equal(entity.name, 'Test Product');
                node_assert_1.default.equal(entity.status, 'active');
                node_assert_1.default.equal(entity.createdAt.getTime(), now.getTime());
                node_assert_1.default.equal(entity.updatedAt.getTime(), now.getTime());
                node_assert_1.default.ok(entity.isActive());
            }
            finally {
                global.Date = originalDate;
            }
        });
        (0, node_test_1.it)('should throw error for invalid name', () => {
            // Arrange
            const command = {
                name: '',
                status: 'active'
            };
            // Act & Assert
            node_assert_1.default.throws(() => product_1.ProductEntity.create(command), { message: 'Product name is required' });
        });
        (0, node_test_1.it)('should throw error for missing name', () => {
            // Arrange
            const command = {
                name: '   ', // whitespace only
                status: 'active'
            };
            // Act & Assert
            node_assert_1.default.throws(() => product_1.ProductEntity.create(command), { message: 'Product name is required' });
        });
    });
    (0, node_test_1.describe)('update', () => {
        let entity;
        beforeEach(() => {
            const command = {
                name: 'Original Product',
                status: 'active'
            };
            entity = product_1.ProductEntity.create(command);
        });
        (0, node_test_1.it)('should update entity properties', () => {
            // Arrange
            const updateCommand = {
                name: 'Updated Product',
                status: 'inactive'
            };
            // Act
            const updatedEntity = entity.update(updateCommand);
            // Assert
            node_assert_1.default.equal(updatedEntity.name, 'Updated Product');
            node_assert_1.default.equal(updatedEntity.status, 'inactive');
            node_assert_1.default.ok(updatedEntity.updatedAt > entity.updatedAt);
        });
        (0, node_test_1.it)('should partially update entity', () => {
            // Arrange
            const updateCommand = {
                status: 'inactive'
                // name not provided, should remain unchanged
            };
            // Act
            const updatedEntity = entity.update(updateCommand);
            // Assert
            node_assert_1.default.equal(updatedEntity.name, 'Original Product'); // unchanged
            node_assert_1.default.equal(updatedEntity.status, 'inactive'); // updated
        });
    });
    (0, node_test_1.describe)('business methods', () => {
        (0, node_test_1.it)('should return correct active status', () => {
            // Arrange
            const activeCommand = {
                name: 'Active Product',
                status: 'active'
            };
            const inactiveCommand = {
                name: 'Inactive Product',
                status: 'inactive'
            };
            // Act
            const activeEntity = product_1.ProductEntity.create(activeCommand);
            const inactiveEntity = product_1.ProductEntity.create(inactiveCommand);
            // Assert
            node_assert_1.default.ok(activeEntity.isActive());
            node_assert_1.default.ok(!inactiveEntity.isActive());
        });
    });
    (0, node_test_1.describe)('domain events', () => {
        (0, node_test_1.it)('should create ProductCreatedEvent', () => {
            // Arrange
            const command = {
                name: 'Test Product',
                status: 'active'
            };
            const entity = product_1.ProductEntity.create(command);
            // Act
            const event = new product_1.ProductCreatedEvent(entity);
            // Assert
            node_assert_1.default.equal(event.type, 'ProductCreated');
            node_assert_1.default.equal(event.aggregateId, entity.id);
            node_assert_1.default.ok(event.occurredAt instanceof Date);
            node_assert_1.default.equal(event.product, entity);
        });
        (0, node_test_1.it)('should create ProductUpdatedEvent', () => {
            // Arrange
            const command = {
                name: 'Test Product',
                status: 'active'
            };
            const entity = product_1.ProductEntity.create(command);
            const changes = { status: 'inactive' };
            // Act
            const event = new product_1.ProductUpdatedEvent(entity, changes);
            // Assert
            node_assert_1.default.equal(event.type, 'ProductUpdated');
            node_assert_1.default.equal(event.aggregateId, entity.id);
            node_assert_1.default.ok(event.occurredAt instanceof Date);
            node_assert_1.default.equal(event.changes, changes);
        });
    });
});
