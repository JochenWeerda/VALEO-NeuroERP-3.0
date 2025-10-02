"use strict";
/**
 * VALEO NeuroERP 3.0 - Webhook Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.WebhookEntity = exports.WebhookUpdatedEvent = exports.WebhookCreatedEvent = void 0;
const branded_types_1 = require("@packages/data-models/branded-types");
class WebhookCreatedEvent {
    webhook;
    type = 'WebhookCreated';
    aggregateId;
    occurredAt;
    constructor(webhook) {
        this.webhook = webhook;
        this.aggregateId = webhook.id;
        this.occurredAt = new Date();
    }
}
exports.WebhookCreatedEvent = WebhookCreatedEvent;
class WebhookUpdatedEvent {
    webhook;
    changes;
    type = 'WebhookUpdated';
    aggregateId;
    occurredAt;
    constructor(webhook, changes) {
        this.webhook = webhook;
        this.changes = changes;
        this.aggregateId = webhook.id;
        this.occurredAt = new Date();
    }
}
exports.WebhookUpdatedEvent = WebhookUpdatedEvent;
class WebhookEntity {
    id;
    name;
    status;
    url;
    events;
    secret;
    createdAt;
    updatedAt;
    constructor(id, name, status, url, events, secret, createdAt, updatedAt) {
        this.id = id;
        this.name = name;
        this.status = status;
        this.url = url;
        this.events = events;
        this.secret = secret;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
    static create(command) {
        // Validate command
        WebhookEntity.validateCreateCommand(command);
        const id = (0, branded_types_1.createWebhookId)(crypto.randomUUID());
        const now = new Date();
        return new WebhookEntity(id, command.name ?? '', command.status ?? undefined, command.url ?? '', command.events ?? undefined, command.secret ?? '', now, now);
    }
    update(command) {
        // Validate command
        WebhookEntity.validateUpdateCommand(command);
        const changes = {};
        if (command.name !== undefined) {
            this.name = command.name;
            changes.name = command.name;
        }
        if (command.status !== undefined) {
            this.status = command.status;
            changes.status = command.status;
        }
        if (command.url !== undefined) {
            this.url = command.url;
            changes.url = command.url;
        }
        if (command.events !== undefined) {
            this.events = command.events;
            changes.events = command.events;
        }
        if (command.secret !== undefined) {
            this.secret = command.secret;
            changes.secret = command.secret;
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
            throw new Error('Webhook name is required');
        }
        // Add additional validation rules here
    }
    static validateUpdateCommand(command) {
        // Add update validation rules here
    }
}
exports.WebhookEntity = WebhookEntity;
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
