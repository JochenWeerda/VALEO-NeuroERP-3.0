/**
 * Role Entity for VALEO NeuroERP 3.0 HR Domain
 * HR-specific roles separate from system-wide roles
 */

import { z } from 'zod';

export const RoleSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  key: z.string().min(1).max(100),
  name: z.string().min(1).max(200),
  permissions: z.array(z.string()),
  editable: z.boolean(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type Role = z.infer<typeof RoleSchema>;

export class RoleEntity {
  private data: Role;

  constructor(data: Role) {
    this.data = RoleSchema.parse(data);
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get key(): string { return this.data.key; }
  get name(): string { return this.data.name; }
  get permissions(): string[] { return [...this.data.permissions]; }
  get editable(): boolean { return this.data.editable; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  // Business Methods
  hasPermission(permission: string): boolean {
    return this.data.permissions.includes(permission);
  }

  canEdit(): boolean {
    return this.data.editable;
  }

  // State Changes
  updateName(name: string, updatedBy?: string): RoleEntity {
    return new RoleEntity({
      ...this.data,
      name,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  addPermission(permission: string, updatedBy?: string): RoleEntity {
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

  removePermission(permission: string, updatedBy?: string): RoleEntity {
    return new RoleEntity({
      ...this.data,
      permissions: this.data.permissions.filter(p => p !== permission),
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  // Export for persistence
  toJSON(): Role {
    return { ...this.data };
  }

  // Factory methods
  static create(data: Omit<Role, 'id' | 'createdAt' | 'updatedAt'>): RoleEntity {
    const now = new Date().toISOString();
    return new RoleEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }

  static fromJSON(data: Role): RoleEntity {
    return new RoleEntity(data);
  }
}

