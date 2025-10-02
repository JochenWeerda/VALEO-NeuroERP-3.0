"use strict";
/**
 * VALEO NeuroERP 3.0 - Location Entity
 *
 * Represents warehouse locations with capacity and zoning
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.Location = void 0;
const uuid_1 = require("uuid");
class Location {
    constructor(attributes) {
        this._attributes = {
            ...attributes,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.validate();
    }
    // Getters
    get locationId() { return this._attributes.locationId; }
    get code() { return this._attributes.code; }
    get type() { return this._attributes.type; }
    get zone() { return this._attributes.zone; }
    get capacity() { return { ...this._attributes.capacity }; }
    get active() { return this._attributes.active; }
    get blocked() { return this._attributes.blocked; }
    get tempControlled() { return this._attributes.tempControlled; }
    get hazmatAllowed() { return this._attributes.hazmatAllowed; }
    get attributes() { return { ...this._attributes }; }
    // Business logic methods
    isPickLocation() {
        return this._attributes.type === 'pick';
    }
    isReserveLocation() {
        return this._attributes.type === 'reserve';
    }
    isQuarantineLocation() {
        return this._attributes.type === 'qc';
    }
    canStoreSku(sku) {
        if (!this._attributes.active || this._attributes.blocked) {
            return false;
        }
        // Temperature zone compatibility
        if (this._attributes.tempControlled) {
            if (sku.tempZone !== this._attributes.zone) {
                return false;
            }
        }
        // Hazmat compatibility
        if (sku.hazmat && !this._attributes.hazmatAllowed) {
            return false;
        }
        // Capacity checks
        if (sku.weight && this._attributes.capacity.maxWeight) {
            // Would need current weight in location - simplified check
            if (sku.weight > this._attributes.capacity.maxWeight) {
                return false;
            }
        }
        if (sku.volume && this._attributes.capacity.maxVolume) {
            // Would need current volume in location - simplified check
            if (sku.volume > this._attributes.capacity.maxVolume) {
                return false;
            }
        }
        return true;
    }
    getDistanceTo(otherLocation) {
        if (!this._attributes.coordinates || !otherLocation._attributes.coordinates) {
            return 0; // No coordinate data available
        }
        const dx = this._attributes.coordinates.x - otherLocation._attributes.coordinates.x;
        const dy = this._attributes.coordinates.y - otherLocation._attributes.coordinates.y;
        const dz = this._attributes.coordinates.z - otherLocation._attributes.coordinates.z;
        return Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
    block(reason) {
        this._attributes.blocked = true;
        this._attributes.blockReason = reason;
        this._attributes.updatedAt = new Date();
    }
    unblock() {
        this._attributes.blocked = false;
        this._attributes.blockReason = undefined;
        this._attributes.updatedAt = new Date();
    }
    updateCapacity(newCapacity) {
        this._attributes.capacity = {
            ...this._attributes.capacity,
            ...newCapacity
        };
        this._attributes.updatedAt = new Date();
    }
    recordCount() {
        this._attributes.lastCount = new Date();
        this._attributes.updatedAt = new Date();
    }
    deactivate() {
        this._attributes.active = false;
        this._attributes.updatedAt = new Date();
    }
    activate() {
        this._attributes.active = true;
        this._attributes.updatedAt = new Date();
    }
    validate() {
        if (!this._attributes.locationId || this._attributes.locationId.trim() === '') {
            throw new Error('Location ID is required');
        }
        if (!this._attributes.code || this._attributes.code.trim() === '') {
            throw new Error('Location code is required');
        }
        if (this._attributes.tempControlled) {
            if (this._attributes.tempMin === undefined || this._attributes.tempMax === undefined) {
                throw new Error('Temperature controlled locations must have min/max temperatures');
            }
            if (this._attributes.tempMin >= this._attributes.tempMax) {
                throw new Error('Min temperature must be less than max temperature');
            }
        }
        if (this._attributes.capacity.maxQty && this._attributes.capacity.maxQty <= 0) {
            throw new Error('Max quantity must be positive');
        }
        if (this._attributes.capacity.maxWeight && this._attributes.capacity.maxWeight <= 0) {
            throw new Error('Max weight must be positive');
        }
        if (this._attributes.capacity.maxVolume && this._attributes.capacity.maxVolume <= 0) {
            throw new Error('Max volume must be positive');
        }
    }
    // Factory methods
    static create(attributes) {
        return new Location({
            ...attributes,
            locationId: (0, uuid_1.v4)()
        });
    }
    static fromAttributes(attributes) {
        const location = new Location(attributes);
        location._attributes = attributes;
        return location;
    }
    // Utility methods
    getFullAddress() {
        const parts = [
            this._attributes.aisle,
            this._attributes.rack,
            this._attributes.shelf,
            this._attributes.bin
        ].filter(Boolean);
        return parts.length > 0 ? parts.join('-') : this._attributes.code;
    }
    isInZone(zone) {
        return this._attributes.zone === zone;
    }
    supportsTemperature(tempZone) {
        if (!this._attributes.tempControlled) {
            return tempZone === 'ambient';
        }
        return tempZone === this._attributes.zone;
    }
}
exports.Location = Location;
//# sourceMappingURL=location.js.map