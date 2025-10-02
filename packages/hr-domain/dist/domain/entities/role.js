"use strict";
/**
 * Role Entity for VALEO NeuroERP 3.0 HR Domain
 * HR-specific roles separate from system-wide roles
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RoleEntity = exports.RoleSchema = void 0;
const zod_1 = require("zod");
exports.RoleSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    key: zod_1.z.string().min(1).max(100),
    name: zod_1.z.string().min(1).max(200),
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
        return new RoleEntity({
            ...this.data,
            name,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    addPermission(permission, updatedBy) {
        if (this.hasPermission(permission)) {
            return this;
        }
        return new RoleEntity({
            ...this.data,
            permissions: [...this.data.permissions, permission],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    removePermission(permission, updatedBy) {
        return new RoleEntity({
            ...this.data,
            permissions: this.data.permissions.filter(p => p !== permission),
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new RoleEntity({
            ...data,
            id: require('uuid').v4(),
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