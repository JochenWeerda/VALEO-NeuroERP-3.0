/**
 * Base Entity for VALEO NeuroERP 3.0
 * Common functionality for all domain entities
 */

import type { EntityId, AuditId } from '../value-objects/branded-types.js';

export abstract class BaseEntity {
  protected readonly _id: EntityId;
  protected readonly _createdAt: Date;
  protected _updatedAt: Date;
  protected _version: number;

  constructor(
    id: EntityId,
    createdAt: Date = new Date(),
    updatedAt: Date = new Date(),
    version: number = 1
  ) {
    this._id = id;
    this._createdAt = createdAt;
    this._updatedAt = updatedAt;
    this._version = version;
  }

  get id(): EntityId {
    return this._id;
  }

  get createdAt(): Date {
    return this._createdAt;
  }

  get updatedAt(): Date {
    return this._updatedAt;
  }

  get version(): number {
    return this._version;
  }

  protected markAsUpdated(): void {
    this._updatedAt = new Date();
    this._version++;
  }

  equals(other: BaseEntity): boolean {
    return this._id === other._id;
  }

  hashCode(): string {
    return this._id;
  }
}

export abstract class AuditableEntity extends BaseEntity {
  protected _createdBy?: AuditId;
  protected _updatedBy?: AuditId;

  constructor(
    id: EntityId,
    createdAt: Date = new Date(),
    updatedAt: Date = new Date(),
    version: number = 1,
    createdBy?: AuditId,
    updatedBy?: AuditId
  ) {
    super(id, createdAt, updatedAt, version);
    this._createdBy = createdBy;
    this._updatedBy = updatedBy;
  }

  get createdBy(): AuditId | undefined {
    return this._createdBy;
  }

  get updatedBy(): AuditId | undefined {
    return this._updatedBy;
  }

  protected markAsUpdated(updatedBy?: AuditId): void {
    super.markAsUpdated();
    this._updatedBy = updatedBy;
  }

  setCreatedBy(createdBy: AuditId): void {
    this._createdBy = createdBy;
  }

  setUpdatedBy(updatedBy: AuditId): void {
    this._updatedBy = updatedBy;
  }
}

