/**
 * Base Entity for VALEO NeuroERP 3.0
 * Common functionality for all domain entities
 */
import type { EntityId, AuditId } from '../value-objects/branded-types.js';
export declare abstract class BaseEntity {
    protected readonly _id: EntityId;
    protected readonly _createdAt: Date;
    protected _updatedAt: Date;
    protected _version: number;
    constructor(id: EntityId, createdAt?: Date, updatedAt?: Date, version?: number);
    get id(): EntityId;
    get createdAt(): Date;
    get updatedAt(): Date;
    get version(): number;
    protected markAsUpdated(): void;
    equals(other: BaseEntity): boolean;
    hashCode(): string;
}
export declare abstract class AuditableEntity extends BaseEntity {
    protected _createdBy?: AuditId;
    protected _updatedBy?: AuditId;
    constructor(id: EntityId, createdAt?: Date, updatedAt?: Date, version?: number, createdBy?: AuditId, updatedBy?: AuditId);
    get createdBy(): AuditId | undefined;
    get updatedBy(): AuditId | undefined;
    protected markAsUpdated(updatedBy?: AuditId): void;
    setCreatedBy(createdBy: AuditId): void;
    setUpdatedBy(updatedBy: AuditId): void;
}
//# sourceMappingURL=base-entity.d.ts.map