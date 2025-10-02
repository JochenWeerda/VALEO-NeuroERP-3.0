"use strict";
/**
 * VALEO NeuroERP 3.0 - Inventory Entity Tests
 *
 * Unit tests for Inventory domain entity following TDD principles.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const node_assert_1 = __importDefault(require("node:assert"));
const inventory_1 = require("../core/entities/inventory");
const branded_types_1 = require("@packages/data-models/branded-types");
(0, node_test_1.describe)('InventoryEntity', () => {
    const validId = (0, branded_types_1.createInventoryId)('test-id-123');
    const now = new Date('2025-01-01T00:00:00Z');
    (0, node_test_1.describe)('create', () => {
        (0, node_test_1.it)('should create a valid inventory entity', () => {
            // Arrange
            const command = {
                name: 'Test Inventory',
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
                const entity = inventory_1.InventoryEntity.create(command);
                // Assert
                node_assert_1.default.ok(entity.id);
                node_assert_1.default.equal(entity.name, 'Test Inventory');
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
            node_assert_1.default.throws(() => inventory_1.InventoryEntity.create(command), { message: 'Inventory name is required' });
        });
        (0, node_test_1.it)('should throw error for missing name', () => {
            // Arrange
            const command = {
                name: '   ', // whitespace only
                status: 'active'
            };
            // Act & Assert
            node_assert_1.default.throws(() => inventory_1.InventoryEntity.create(command), { message: 'Inventory name is required' });
        });
    });
    (0, node_test_1.describe)('update', () => {
        let entity;
        beforeEach(() => {
            const command = {
                name: 'Original Inventory',
                status: 'active'
            };
            entity = inventory_1.InventoryEntity.create(command);
        });
        (0, node_test_1.it)('should update entity properties', () => {
            // Arrange
            const updateCommand = {
                name: 'Updated Inventory',
                status: 'inactive'
            };
            // Act
            const updatedEntity = entity.update(updateCommand);
            // Assert
            node_assert_1.default.equal(updatedEntity.name, 'Updated Inventory');
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
            node_assert_1.default.equal(updatedEntity.name, 'Original Inventory'); // unchanged
            node_assert_1.default.equal(updatedEntity.status, 'inactive'); // updated
        });
    });
    (0, node_test_1.describe)('business methods', () => {
        (0, node_test_1.it)('should return correct active status', () => {
            // Arrange
            const activeCommand = {
                name: 'Active Inventory',
                status: 'active'
            };
            const inactiveCommand = {
                name: 'Inactive Inventory',
                status: 'inactive'
            };
            // Act
            const activeEntity = inventory_1.InventoryEntity.create(activeCommand);
            const inactiveEntity = inventory_1.InventoryEntity.create(inactiveCommand);
            // Assert
            node_assert_1.default.ok(activeEntity.isActive());
            node_assert_1.default.ok(!inactiveEntity.isActive());
        });
    });
    (0, node_test_1.describe)('domain events', () => {
        (0, node_test_1.it)('should create InventoryCreatedEvent', () => {
            // Arrange
            const command = {
                name: 'Test Inventory',
                status: 'active'
            };
            const entity = inventory_1.InventoryEntity.create(command);
            // Act
            const event = new inventory_1.InventoryCreatedEvent(entity);
            // Assert
            node_assert_1.default.equal(event.type, 'InventoryCreated');
            node_assert_1.default.equal(event.aggregateId, entity.id);
            node_assert_1.default.ok(event.occurredAt instanceof Date);
            node_assert_1.default.equal(event.inventory, entity);
        });
        (0, node_test_1.it)('should create InventoryUpdatedEvent', () => {
            // Arrange
            const command = {
                name: 'Test Inventory',
                status: 'active'
            };
            const entity = inventory_1.InventoryEntity.create(command);
            const changes = { status: 'inactive' };
            // Act
            const event = new inventory_1.InventoryUpdatedEvent(entity, changes);
            // Assert
            node_assert_1.default.equal(event.type, 'InventoryUpdated');
            node_assert_1.default.equal(event.aggregateId, entity.id);
            node_assert_1.default.ok(event.occurredAt instanceof Date);
            node_assert_1.default.equal(event.changes, changes);
        });
    });
});
