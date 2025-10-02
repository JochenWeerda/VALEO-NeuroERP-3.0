"use strict";
/**
 * VALEO NeuroERP 3.0 - Inventory Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryEntity = exports.InventoryUpdatedEvent = exports.InventoryCreatedEvent = void 0;
const branded_types_1 = require("@valero-neuroerp/data-models/branded-types");
class InventoryCreatedEvent {
    inventory;
    type = 'InventoryCreated';
    aggregateId;
    occurredAt;
    constructor(inventory) {
        this.inventory = inventory;
        this.aggregateId = inventory.id;
        this.occurredAt = new Date();
    }
}
exports.InventoryCreatedEvent = InventoryCreatedEvent;
class InventoryUpdatedEvent {
    inventory;
    changes;
    type = 'InventoryUpdated';
    aggregateId;
    occurredAt;
    constructor(inventory, changes) {
        this.inventory = inventory;
        this.changes = changes;
        this.aggregateId = inventory.id;
        this.occurredAt = new Date();
    }
}
exports.InventoryUpdatedEvent = InventoryUpdatedEvent;
class InventoryEntity {
    id;
    name;
    status;
    productId;
    quantity;
    reservedQuantity;
    availableQuantity;
    reorderLevel;
    reorderQuantity;
    lastUpdated;
    createdAt;
    updatedAt;
    constructor(id, name, productId, quantity, reservedQuantity, availableQuantity, reorderLevel, reorderQuantity, lastUpdated, createdAt, updatedAt, status) {
        this.id = id;
        this.name = name;
        this.status = status;
        this.productId = productId;
        this.quantity = quantity;
        this.reservedQuantity = reservedQuantity;
        this.availableQuantity = availableQuantity;
        this.reorderLevel = reorderLevel;
        this.reorderQuantity = reorderQuantity;
        this.lastUpdated = lastUpdated;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
    static create(command) {
        // Validate command
        InventoryEntity.validateCreateCommand(command);
        const id = (0, branded_types_1.createInventoryId)(crypto.randomUUID());
        const now = new Date();
        return new InventoryEntity(id, command.name ?? '', command.productId ?? '', command.quantity ?? 0, command.reservedQuantity ?? 0, command.availableQuantity ?? 0, command.reorderLevel ?? 0, command.reorderQuantity ?? 0, command.lastUpdated ?? new Date(), now, now, command.status ?? undefined);
    }
    update(command) {
        // Validate command
        InventoryEntity.validateUpdateCommand(command);
        const changes = {};
        if (command.name !== undefined) {
            this.name = command.name;
            changes.name = command.name;
        }
        if (command.status !== undefined) {
            this.status = command.status;
            changes.status = command.status;
        }
        if (command.productId !== undefined) {
            this.productId = command.productId;
            changes.productId = command.productId;
        }
        if (command.quantity !== undefined) {
            this.quantity = command.quantity;
            changes.quantity = command.quantity;
        }
        if (command.reservedQuantity !== undefined) {
            this.reservedQuantity = command.reservedQuantity;
            changes.reservedQuantity = command.reservedQuantity;
        }
        if (command.availableQuantity !== undefined) {
            this.availableQuantity = command.availableQuantity;
            changes.availableQuantity = command.availableQuantity;
        }
        if (command.reorderLevel !== undefined) {
            this.reorderLevel = command.reorderLevel;
            changes.reorderLevel = command.reorderLevel;
        }
        if (command.reorderQuantity !== undefined) {
            this.reorderQuantity = command.reorderQuantity;
            changes.reorderQuantity = command.reorderQuantity;
        }
        if (command.lastUpdated !== undefined) {
            this.lastUpdated = command.lastUpdated;
            changes.lastUpdated = command.lastUpdated;
        }
        this.updatedAt = new Date();
        changes.updatedAt = this.updatedAt;
        return this;
    }
    // Business methods
    isActive() {
        return this.status === 'active';
    }
    // Validation methods
    static validateCreateCommand(command) {
        if (!command.name || command.name.trim().length === 0) {
            throw new Error('Inventory name is required');
        }
        // Add additional validation rules here
    }
    static validateUpdateCommand(command) {
        // Add update validation rules here
    }
}
exports.InventoryEntity = InventoryEntity;
// Utility functions
function getDefaultValue(type) {
    switch (type) {
        case 'string': return '';
        case 'number': return 0;
        case 'boolean': return false;
        case 'Date': return new Date();
        default: return null;
    }
}
