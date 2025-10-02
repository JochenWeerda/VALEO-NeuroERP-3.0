/**
 * Base Entity for VALEO NeuroERP 3.0
 * Common functionality for all domain entities
 */
export class BaseEntity {
    _id;
    _createdAt;
    _updatedAt;
    _version;
    constructor(id, createdAt = new Date(), updatedAt = new Date(), version = 1) {
        this._id = id;
        this._createdAt = createdAt;
        this._updatedAt = updatedAt;
        this._version = version;
    }
    get id() {
        return this._id;
    }
    get createdAt() {
        return this._createdAt;
    }
    get updatedAt() {
        return this._updatedAt;
    }
    get version() {
        return this._version;
    }
    markAsUpdated() {
        this._updatedAt = new Date();
        this._version++;
    }
    equals(other) {
        return this._id === other._id;
    }
    hashCode() {
        return this._id;
    }
}
export class AuditableEntity extends BaseEntity {
    _createdBy;
    _updatedBy;
    constructor(id, createdAt = new Date(), updatedAt = new Date(), version = 1, createdBy, updatedBy) {
        super(id, createdAt, updatedAt, version);
        this._createdBy = createdBy;
        this._updatedBy = updatedBy;
    }
    get createdBy() {
        return this._createdBy;
    }
    get updatedBy() {
        return this._updatedBy;
    }
    markAsUpdated(updatedBy) {
        super.markAsUpdated();
        this._updatedBy = updatedBy;
    }
    setCreatedBy(createdBy) {
        this._createdBy = createdBy;
    }
    setUpdatedBy(updatedBy) {
        this._updatedBy = updatedBy;
    }
}
//# sourceMappingURL=base-entity.js.map