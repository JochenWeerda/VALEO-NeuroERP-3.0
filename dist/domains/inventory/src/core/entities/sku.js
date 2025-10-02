"use strict";
/**
 * VALEO NeuroERP 3.0 - SKU Entity
 *
 * Represents a Stock Keeping Unit with GS1 compliance and WMS attributes
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.Sku = void 0;
class Sku {
    _attributes;
    constructor(attributes) {
        this._attributes = {
            ...attributes,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.validate();
    }
    // Getters
    get sku() { return this._attributes.sku; }
    get gtin() { return this._attributes.gtin; }
    get description() { return this._attributes.description; }
    get category() { return this._attributes.category; }
    get uom() { return this._attributes.uom; }
    get tempZone() { return this._attributes.tempZone; }
    get hazmat() { return this._attributes.hazmat; }
    get abcClass() { return this._attributes.abcClass; }
    get velocityClass() { return this._attributes.velocityClass; }
    get serialTracked() { return this._attributes.serialTracked; }
    get lotTracked() { return this._attributes.lotTracked; }
    get active() { return this._attributes.active; }
    get attributes() { return { ...this._attributes }; }
    // Business logic methods
    isPerishable() {
        return this._attributes.shelfLifeDays !== undefined && this._attributes.shelfLifeDays > 0;
    }
    isHighValue() {
        return this._attributes.abcClass === 'A';
    }
    isFastMoving() {
        return this._attributes.velocityClass === 'X';
    }
    requiresSpecialHandling() {
        return this._attributes.hazmat || this._attributes.tempZone !== 'ambient';
    }
    canExpire(expiryDate) {
        if (!this._attributes.shelfLifeDays)
            return false;
        const now = new Date();
        const daysUntilExpiry = Math.floor((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        return daysUntilExpiry <= this._attributes.shelfLifeDays;
    }
    update(attributes) {
        this._attributes = {
            ...this._attributes,
            ...attributes,
            updatedAt: new Date()
        };
        this.validate();
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
        if (!this._attributes.sku || this._attributes.sku.trim() === '') {
            throw new Error('SKU is required');
        }
        if (!this._attributes.description || this._attributes.description.trim() === '') {
            throw new Error('Description is required');
        }
        if (this._attributes.gtin && !this.isValidGtin(this._attributes.gtin)) {
            throw new Error('Invalid GTIN format');
        }
        if (this._attributes.weight && this._attributes.weight <= 0) {
            throw new Error('Weight must be positive');
        }
        if (this._attributes.volume && this._attributes.volume <= 0) {
            throw new Error('Volume must be positive');
        }
    }
    isValidGtin(gtin) {
        // Basic GTIN validation (8, 12, 13, 14 digits)
        const cleanGtin = gtin.replace(/[^0-9]/g, '');
        return /^[0-9]{8,14}$/.test(cleanGtin);
    }
    // Factory methods
    static create(attributes) {
        return new Sku(attributes);
    }
    static fromAttributes(attributes) {
        const sku = new Sku(attributes);
        sku._attributes = attributes;
        return sku;
    }
}
exports.Sku = Sku;
