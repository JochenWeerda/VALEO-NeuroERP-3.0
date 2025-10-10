"use strict";
/**
 * Role Entity for VALEO NeuroERP 3.0 HR Domain
 * HR-specific roles separate from system-wide roles
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RoleEntity = exports.RoleSchema = void 0;
const uuid_1 = require("uuid");
const zod_1 = require("zod");
const ROLE_KEY_MIN_LENGTH = 1;
const ROLE_KEY_MAX_LENGTH = 100;
const ROLE_NAME_MIN_LENGTH = 1;
const ROLE_NAME_MAX_LENGTH = 200;
exports.RoleSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    key: zod_1.z.string().min(ROLE_KEY_MIN_LENGTH).max(ROLE_KEY_MAX_LENGTH),
    name: zod_1.z.string().min(ROLE_NAME_MIN_LENGTH).max(ROLE_NAME_MAX_LENGTH),
    permissions: zod_1.z.array(zod_1.z.string()),
    editable: zod_1.z.boolean(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class RoleEntity {
    data;
    constructor(data) {
        this.data = exports.RoleSchema.parse(data);
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get key() { return this.data.key; }
    get name() { return this.data.name; }
    get permissions() { return [...this.data.permissions]; }
    get editable() { return this.data.editable; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    // Business Methods
    hasPermission(permission) {
        return this.data.permissions.includes(permission);
    }
    canEdit() {
        return this.data.editable;
    }
    // State Changes
    updateName(name, updatedBy) {
        if (name === this.data.name) {
            return this;
        }
        return this.clone({ name, updatedBy });
    }
    addPermission(permission, updatedBy) {
        if (this.hasPermission(permission)) {
            return this;
        }
        return this.clone({
            permissions: [...this.data.permissions, permission],
            updatedBy
        });
    }
    removePermission(permission, updatedBy) {
        if (!this.hasPermission(permission)) {
            return this;
        }
        return this.clone({
            permissions: this.data.permissions.filter(p => p !== permission),
            updatedBy
        });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    clone(overrides) {
        const now = new Date().toISOString();
        return new RoleEntity({
            ...this.data,
            ...overrides,
            updatedAt: now
        });
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new RoleEntity({
            ...data,
            id: (0, uuid_1.v4)(),
            createdAt: now,
            updatedAt: now
        });
    }
    static fromJSON(data) {
        return new RoleEntity(data);
    }
}
exports.RoleEntity = RoleEntity;
//# sourceMappingURL=role.js.map