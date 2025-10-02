"use strict";
/**
 * VALEO NeuroERP 3.0 - Order Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderEntity = exports.OrderUpdatedEvent = exports.OrderCreatedEvent = void 0;
class OrderCreatedEvent {
    constructor(order) {
        this.order = order;
        this.type = 'OrderCreated';
        this.aggregateId = order.id;
        this.occurredAt = new Date();
    }
}
exports.OrderCreatedEvent = OrderCreatedEvent;
class OrderUpdatedEvent {
    constructor(order, changes) {
        this.order = order;
        this.changes = changes;
        this.type = 'OrderUpdated';
        this.aggregateId = order.id;
        this.occurredAt = new Date();
    }
}
exports.OrderUpdatedEvent = OrderUpdatedEvent;
class OrderEntity {
    constructor(id, name, orderNumber, customerId, items, subtotal, tax, total, status, deliveryDate, createdAt, updatedAt) {
        this.id = id;
        this.name = name;
        if (status !== undefined) {
            this.status = status;
        }
        this.orderNumber = orderNumber;
        this.customerId = customerId;
        this.items = items;
        this.subtotal = subtotal;
        this.tax = tax;
        this.total = total;
        if (deliveryDate !== undefined) {
            this.deliveryDate = deliveryDate;
        }
        this.createdAt = createdAt ?? new Date();
        this.updatedAt = updatedAt ?? new Date();
    }
    static create(command) {
        // Validate command
        OrderEntity.validateCreateCommand(command);
        const id = crypto.randomUUID();
        const now = new Date();
        return new OrderEntity(id, command.name ?? '', command.orderNumber ?? '', command.customerId ?? '', command.items ?? [], command.subtotal ?? 0, command.tax ?? 0, command.total ?? 0, command.status, command.deliveryDate, now, now);
    }
    update(command) {
        // Validate command
        OrderEntity.validateUpdateCommand(command);
        const changes = {};
        if (command.name !== undefined) {
            this.name = command.name;
            changes.name = command.name;
        }
        if (command.status !== undefined) {
            this.status = command.status;
            changes.status = command.status;
        }
        if (command.orderNumber !== undefined) {
            this.orderNumber = command.orderNumber;
            changes.orderNumber = command.orderNumber;
        }
        if (command.customerId !== undefined) {
            this.customerId = command.customerId;
            changes.customerId = command.customerId;
        }
        if (command.items !== undefined) {
            this.items = command.items;
            changes.items = command.items;
        }
        if (command.subtotal !== undefined) {
            this.subtotal = command.subtotal;
            changes.subtotal = command.subtotal;
        }
        if (command.tax !== undefined) {
            this.tax = command.tax;
            changes.tax = command.tax;
        }
        if (command.total !== undefined) {
            this.total = command.total;
            changes.total = command.total;
        }
        if (command.deliveryDate !== undefined) {
            this.deliveryDate = command.deliveryDate;
            changes.deliveryDate = command.deliveryDate;
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
            throw new Error('Order name is required');
        }
        // Add additional validation rules here
    }
    static validateUpdateCommand(command) {
        // Add update validation rules here
    }
}
exports.OrderEntity = OrderEntity;
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
