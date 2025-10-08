/**
 * Role Entity for VALEO NeuroERP 3.0 HR Domain
 * HR-specific roles separate from system-wide roles
 */

import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';

const ROLE_KEY_MIN_LENGTH = 1;
const ROLE_KEY_MAX_LENGTH = 100;
const ROLE_NAME_MIN_LENGTH = 1;
const ROLE_NAME_MAX_LENGTH = 200;

export const RoleSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  key: z.string().min(ROLE_KEY_MIN_LENGTH).max(ROLE_KEY_MAX_LENGTH),
  name: z.string().min(ROLE_NAME_MIN_LENGTH).max(ROLE_NAME_MAX_LENGTH),
  permissions: z.array(z.string()),
  editable: z.boolean(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type Role = z.infer<typeof RoleSchema>;

export class RoleEntity {
  private readonly data: Role;

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
    if (name === this.data.name) {
      return this;
    }

    return this.clone({ name, updatedBy });
  }

  addPermission(permission: string, updatedBy?: string): RoleEntity {
    if (this.hasPermission(permission)) {
      return this;
    }

    return this.clone({
      permissions: [...this.data.permissions, permission],
      updatedBy
    });
  }

  removePermission(permission: string, updatedBy?: string): RoleEntity {
    if (!this.hasPermission(permission)) {
      return this;
    }

    return this.clone({
      permissions: this.data.permissions.filter(p => p !== permission),
      updatedBy
    });
  }

  // Export for persistence
  toJSON(): Role {
    return { ...this.data };
  }

  private clone(overrides: Partial<Role>): RoleEntity {
    const now = new Date().toISOString();
    return new RoleEntity({
      ...this.data,
      ...overrides,
      updatedAt: now
    });
  }

  // Factory methods
  static create(data: Omit<Role, 'id' | 'createdAt' | 'updatedAt'>): RoleEntity {
    const now = new Date().toISOString();
    return new RoleEntity({
      ...data,
      id: uuidv4(),
      createdAt: now,
      updatedAt: now
    });
  }

  static fromJSON(data: Role): RoleEntity {
    return new RoleEntity(data);
  }
}

