/**
 * Change Log Entity
 * Tracks all changes to entities with reasons for audit trail
 */

import { z } from 'zod';
import { randomUUID } from 'crypto';

export const ChangeActionType = z.enum([
  'CREATE',
  'UPDATE',
  'DELETE',
  'CANCEL',
  'AMEND',
  'RESTORE',
]);

export type ChangeActionType = z.infer<typeof ChangeActionType>;

export const ChangeLogSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().min(1),
  entityType: z.string(), // e.g., "Farmer", "Contract", "Batch"
  entityId: z.string(),
  action: ChangeActionType,
  reason: z.string().optional(), // Required for DELETE, CANCEL, AMEND
  oldValue: z.record(z.unknown()).optional(), // Previous state (JSON)
  newValue: z.record(z.unknown()).optional(), // New state (JSON)
  changedFields: z.array(z.string()).optional(), // List of changed field names
  userId: z.string(),
  userName: z.string().optional(),
  userEmail: z.string().optional(),
  ipAddress: z.string().optional(),
  userAgent: z.string().optional(),
  timestamp: z.date(),
  metadata: z.record(z.unknown()).optional(), // Additional metadata
});

export type ChangeLog = z.infer<typeof ChangeLogSchema>;

export interface CreateChangeLogInput {
  tenantId: string;
  entityType: string;
  entityId: string;
  action: ChangeActionType;
  reason?: string;
  oldValue?: Record<string, any>;
  newValue?: Record<string, any>;
  changedFields?: string[];
  userId: string;
  userName?: string;
  userEmail?: string;
  ipAddress?: string;
  userAgent?: string;
  metadata?: Record<string, any>;
}

export class ChangeLogEntity {
  static create(input: CreateChangeLogInput): ChangeLog {
    // Validate reason for actions that require it
    if (
      (input.action === 'DELETE' ||
        input.action === 'CANCEL' ||
        input.action === 'AMEND') &&
      (!input.reason || input.reason.trim().length === 0)
    ) {
      throw new Error(
        `Reason is required for ${input.action} action for audit trail`
      );
    }

    if (
      input.reason &&
      (input.action === 'DELETE' ||
        input.action === 'CANCEL' ||
        input.action === 'AMEND') &&
      input.reason.trim().length < 10
    ) {
      throw new Error(
        `Reason must be at least 10 characters for ${input.action} action`
      );
    }

    // Detect changed fields if not provided
    const changedFields =
      input.changedFields ||
      this.detectChangedFields(input.oldValue, input.newValue);

    return {
      id: randomUUID(),
      tenantId: input.tenantId,
      entityType: input.entityType,
      entityId: input.entityId,
      action: input.action,
      reason: input.reason,
      oldValue: input.oldValue,
      newValue: input.newValue,
      changedFields,
      userId: input.userId,
      userName: input.userName,
      userEmail: input.userEmail,
      ipAddress: input.ipAddress,
      userAgent: input.userAgent,
      timestamp: new Date(),
      metadata: input.metadata,
    };
  }

  /**
   * Detect changed fields between old and new values
   */
  private static detectChangedFields(
    oldValue?: Record<string, any>,
    newValue?: Record<string, any>
  ): string[] {
    if (!oldValue || !newValue) {
      return [];
    }

    const changed: string[] = [];
    const allKeys = new Set([
      ...Object.keys(oldValue),
      ...Object.keys(newValue),
    ]);

    for (const key of allKeys) {
      const oldVal = oldValue[key];
      const newVal = newValue[key];

      if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        changed.push(key);
      }
    }

    return changed;
  }

  /**
   * Create change log for CREATE action
   */
  static createForCreate(
    entityType: string,
    entityId: string,
    newValue: Record<string, any>,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): ChangeLog {
    return this.create({
      tenantId,
      entityType,
      entityId,
      action: 'CREATE',
      newValue,
      userId,
      userName: options?.userName,
      userEmail: options?.userEmail,
      ipAddress: options?.ipAddress,
      userAgent: options?.userAgent,
      metadata: options?.metadata,
    });
  }

  /**
   * Create change log for UPDATE action
   */
  static createForUpdate(
    entityType: string,
    entityId: string,
    oldValue: Record<string, any>,
    newValue: Record<string, any>,
    userId: string,
    tenantId: string,
    options?: {
      reason?: string;
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): ChangeLog {
    return this.create({
      tenantId,
      entityType,
      entityId,
      action: 'UPDATE',
      oldValue,
      newValue,
      reason: options?.reason,
      userId,
      userName: options?.userName,
      userEmail: options?.userEmail,
      ipAddress: options?.ipAddress,
      userAgent: options?.userAgent,
      metadata: options?.metadata,
    });
  }

  /**
   * Create change log for DELETE action
   */
  static createForDelete(
    entityType: string,
    entityId: string,
    oldValue: Record<string, any>,
    reason: string,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): ChangeLog {
    return this.create({
      tenantId,
      entityType,
      entityId,
      action: 'DELETE',
      oldValue,
      reason,
      userId,
      userName: options?.userName,
      userEmail: options?.userEmail,
      ipAddress: options?.ipAddress,
      userAgent: options?.userAgent,
      metadata: options?.metadata,
    });
  }

  /**
   * Create change log for CANCEL action
   */
  static createForCancel(
    entityType: string,
    entityId: string,
    oldValue: Record<string, any>,
    reason: string,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): ChangeLog {
    return this.create({
      tenantId,
      entityType,
      entityId,
      action: 'CANCEL',
      oldValue,
      reason,
      userId,
      userName: options?.userName,
      userEmail: options?.userEmail,
      ipAddress: options?.ipAddress,
      userAgent: options?.userAgent,
      metadata: options?.metadata,
    });
  }

  /**
   * Create change log for AMEND action
   */
  static createForAmend(
    entityType: string,
    entityId: string,
    oldValue: Record<string, any>,
    newValue: Record<string, any>,
    reason: string,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): ChangeLog {
    return this.create({
      tenantId,
      entityType,
      entityId,
      action: 'AMEND',
      oldValue,
      newValue,
      reason,
      userId,
      userName: options?.userName,
      userEmail: options?.userEmail,
      ipAddress: options?.ipAddress,
      userAgent: options?.userAgent,
      metadata: options?.metadata,
    });
  }

  /**
   * Create change log for RESTORE action
   */
  static createForRestore(
    entityType: string,
    entityId: string,
    newValue: Record<string, any>,
    reason: string,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): ChangeLog {
    return this.create({
      tenantId,
      entityType,
      entityId,
      action: 'RESTORE',
      newValue,
      reason,
      userId,
      userName: options?.userName,
      userEmail: options?.userEmail,
      ipAddress: options?.ipAddress,
      userAgent: options?.userAgent,
      metadata: options?.metadata,
    });
  }
}

