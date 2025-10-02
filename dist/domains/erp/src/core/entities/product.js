"use strict";
/**
 * VALEO NeuroERP 3.0 - Product Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProductEntity = exports.ProductUpdatedEvent = exports.ProductCreatedEvent = void 0;
exports.createProduct = createProduct;
exports.isValidProductId = isValidProductId;
exports.formatPrice = formatPrice;
const branded_types_1 = require("@valero-neuroerp/data-models/branded-types");
class ProductCreatedEvent {
    constructor(product) {
        this.product = product;
        this.type = 'ProductCreated';
        this.aggregateId = product.id;
        this.occurredAt = new Date();
    }
}
exports.ProductCreatedEvent = ProductCreatedEvent;
class ProductUpdatedEvent {
    constructor(product, changes) {
        this.product = product;
        this.changes = changes;
        this.type = 'ProductUpdated';
        this.aggregateId = product.id;
        this.occurredAt = new Date();
    }
}
exports.ProductUpdatedEvent = ProductUpdatedEvent;
class ProductEntity {
    constructor(id, name, sku, price, category, createdAt, updatedAt, status, description) {
        this.id = id;
        this.name = name;
        this.status = status;
        this.sku = sku;
        this.price = price;
        this.category = category;
        this.description = description;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
    static create(command) {
        // Validate command
        ProductEntity.validateCreateCommand(command);
        const id = (0, branded_types_1.createId)('ProductId');
        const now = new Date();
        return new ProductEntity(id, command.name, command.sku, command.price, command.category, now, now, command.status, command.description);
    }
    update(command) {
        // Validate command
        ProductEntity.validateUpdateCommand(command);
        const changes = {};
        if (command.name !== undefined) {
            this.name = command.name;
            changes.name = command.name;
        }
        if (command.status !== undefined) {
            this.status = command.status;
            changes.status = command.status;
        }
        if (command.sku !== undefined) {
            this.sku = command.sku;
            changes.sku = command.sku;
        }
        if (command.price !== undefined) {
            this.price = command.price;
            changes.price = command.price;
        }
        if (command.category !== undefined) {
            this.category = command.category;
            changes.category = command.category;
        }
        if (command.description !== undefined) {
            this.description = command.description;
            changes.description = command.description;
        }
        this.updatedAt = new Date();
        changes.updatedAt = this.updatedAt;
        return this;
    }
    // Business methods
    isActive() {
        return this.status === 'active';
    }
    isInStock() {
        // This would typically check inventory levels
        return true;
    }
    calculateTotalPrice(quantity, taxRate = 0.19) {
        const netTotal = this.price * quantity;
        return netTotal * (1 + taxRate);
    }
    // Validation methods
    static validateCreateCommand(command) {
        if (!command.name || command.name.trim().length === 0) {
            throw new Error('Product name is required');
        }
        if (!command.sku || command.sku.trim().length === 0) {
            throw new Error('Product SKU is required');
        }
        if (command.price <= 0) {
            throw new Error('Product price must be greater than zero');
        }
        if (!command.category || command.category.trim().length === 0) {
            throw new Error('Product category is required');
        }
    }
    static validateUpdateCommand(command) {
        if (command.name !== undefined && command.name.trim().length === 0) {
            throw new Error('Product name cannot be empty');
        }
        if (command.sku !== undefined && command.sku.trim().length === 0) {
            throw new Error('Product SKU cannot be empty');
        }
        if (command.price !== undefined && command.price <= 0) {
            throw new Error('Product price must be greater than zero');
        }
        if (command.category !== undefined && command.category.trim().length === 0) {
            throw new Error('Product category cannot be empty');
        }
    }
}
exports.ProductEntity = ProductEntity;
// Utility functions
function createProduct(command) {
    return ProductEntity.create(command);
}
function isValidProductId(id) {
    return typeof id === 'string' && id.length > 0;
}
function formatPrice(price, currency = 'EUR') {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency
    }).format(price);
}
