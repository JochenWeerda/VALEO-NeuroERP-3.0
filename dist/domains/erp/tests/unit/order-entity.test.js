"use strict";
/**
 * VALEO NeuroERP 3.0 - Order Entity Tests
 *
 * Unit tests for Order domain entity following TDD principles.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const node_assert_1 = __importDefault(require("node:assert"));
const order_1 = require("../core/entities/order");
const branded_types_1 = require("@packages/data-models/branded-types");
(0, node_test_1.describe)('OrderEntity', () => {
    const validId = (0, branded_types_1.createOrderId)('test-id-123');
    const now = new Date('2025-01-01T00:00:00Z');
    (0, node_test_1.describe)('create', () => {
        (0, node_test_1.it)('should create a valid order entity', () => {
            // Arrange
            const command = {
                name: 'Test Order',
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
                const entity = order_1.OrderEntity.create(command);
                // Assert
                node_assert_1.default.ok(entity.id);
                node_assert_1.default.equal(entity.name, 'Test Order');
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
            node_assert_1.default.throws(() => order_1.OrderEntity.create(command), { message: 'Order name is required' });
        });
        (0, node_test_1.it)('should throw error for missing name', () => {
            // Arrange
            const command = {
                name: '   ', // whitespace only
                status: 'active'
            };
            // Act & Assert
            node_assert_1.default.throws(() => order_1.OrderEntity.create(command), { message: 'Order name is required' });
        });
    });
    (0, node_test_1.describe)('update', () => {
        let entity;
        beforeEach(() => {
            const command = {
                name: 'Original Order',
                status: 'active'
            };
            entity = order_1.OrderEntity.create(command);
        });
        (0, node_test_1.it)('should update entity properties', () => {
            // Arrange
            const updateCommand = {
                name: 'Updated Order',
                status: 'inactive'
            };
            // Act
            const updatedEntity = entity.update(updateCommand);
            // Assert
            node_assert_1.default.equal(updatedEntity.name, 'Updated Order');
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
            node_assert_1.default.equal(updatedEntity.name, 'Original Order'); // unchanged
            node_assert_1.default.equal(updatedEntity.status, 'inactive'); // updated
        });
    });
    (0, node_test_1.describe)('business methods', () => {
        (0, node_test_1.it)('should return correct active status', () => {
            // Arrange
            const activeCommand = {
                name: 'Active Order',
                status: 'active'
            };
            const inactiveCommand = {
                name: 'Inactive Order',
                status: 'inactive'
            };
            // Act
            const activeEntity = order_1.OrderEntity.create(activeCommand);
            const inactiveEntity = order_1.OrderEntity.create(inactiveCommand);
            // Assert
            node_assert_1.default.ok(activeEntity.isActive());
            node_assert_1.default.ok(!inactiveEntity.isActive());
        });
    });
    (0, node_test_1.describe)('domain events', () => {
        (0, node_test_1.it)('should create OrderCreatedEvent', () => {
            // Arrange
            const command = {
                name: 'Test Order',
                status: 'active'
            };
            const entity = order_1.OrderEntity.create(command);
            // Act
            const event = new order_1.OrderCreatedEvent(entity);
            // Assert
            node_assert_1.default.equal(event.type, 'OrderCreated');
            node_assert_1.default.equal(event.aggregateId, entity.id);
            node_assert_1.default.ok(event.occurredAt instanceof Date);
            node_assert_1.default.equal(event.order, entity);
        });
        (0, node_test_1.it)('should create OrderUpdatedEvent', () => {
            // Arrange
            const command = {
                name: 'Test Order',
                status: 'active'
            };
            const entity = order_1.OrderEntity.create(command);
            const changes = { status: 'inactive' };
            // Act
            const event = new order_1.OrderUpdatedEvent(entity, changes);
            // Assert
            node_assert_1.default.equal(event.type, 'OrderUpdated');
            node_assert_1.default.equal(event.aggregateId, entity.id);
            node_assert_1.default.ok(event.occurredAt instanceof Date);
            node_assert_1.default.equal(event.changes, changes);
        });
    });
});
