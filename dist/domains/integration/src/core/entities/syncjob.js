"use strict";
/**
 * VALEO NeuroERP 3.0 - SyncJob Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SyncJobEntity = exports.SyncJobUpdatedEvent = exports.SyncJobCreatedEvent = void 0;
const branded_types_1 = require("@packages/data-models/branded-types");
class SyncJobCreatedEvent {
    syncjob;
    type = 'SyncJobCreated';
    aggregateId;
    occurredAt;
    constructor(syncjob) {
        this.syncjob = syncjob;
        this.aggregateId = syncjob.id;
        this.occurredAt = new Date();
    }
}
exports.SyncJobCreatedEvent = SyncJobCreatedEvent;
class SyncJobUpdatedEvent {
    syncjob;
    changes;
    type = 'SyncJobUpdated';
    aggregateId;
    occurredAt;
    constructor(syncjob, changes) {
        this.syncjob = syncjob;
        this.changes = changes;
        this.aggregateId = syncjob.id;
        this.occurredAt = new Date();
    }
}
exports.SyncJobUpdatedEvent = SyncJobUpdatedEvent;
class SyncJobEntity {
    id;
    name;
    status;
    source;
    target;
    lastSync;
    errorMessage;
    createdAt;
    updatedAt;
    constructor(id, name, status, source, target, lastSync, errorMessage, createdAt, updatedAt) {
        this.id = id;
        this.name = name;
        this.status = status;
        this.source = source;
        this.target = target;
        this.lastSync = lastSync;
        this.errorMessage = errorMessage;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
    static create(command) {
        // Validate command
        SyncJobEntity.validateCreateCommand(command);
        const id = (0, branded_types_1.createSyncJobId)(crypto.randomUUID());
        const now = new Date();
        return new SyncJobEntity(id, command.name ?? '', command.status ?? undefined, command.source ?? '', command.target ?? '', command.lastSync ?? new Date(), command.errorMessage ?? '', now, now);
    }
    update(command) {
        // Validate command
        SyncJobEntity.validateUpdateCommand(command);
        const changes = {};
        if (command.name !== undefined) {
            this.name = command.name;
            changes.name = command.name;
        }
        if (command.status !== undefined) {
            this.status = command.status;
            changes.status = command.status;
        }
        if (command.source !== undefined) {
            this.source = command.source;
            changes.source = command.source;
        }
        if (command.target !== undefined) {
            this.target = command.target;
            changes.target = command.target;
        }
        if (command.lastSync !== undefined) {
            this.lastSync = command.lastSync;
            changes.lastSync = command.lastSync;
        }
        if (command.errorMessage !== undefined) {
            this.errorMessage = command.errorMessage;
            changes.errorMessage = command.errorMessage;
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
            throw new Error('SyncJob name is required');
        }
        // Add additional validation rules here
    }
    static validateUpdateCommand(command) {
        // Add update validation rules here
    }
}
exports.SyncJobEntity = SyncJobEntity;
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
