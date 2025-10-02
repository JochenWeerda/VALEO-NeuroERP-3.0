"use strict";
/**
 * VALEO NeuroERP 3.0 - Lot Entity
 *
 * Represents inventory lots with expiry tracking and GS1 compliance
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.Lot = void 0;
const uuid_1 = require("uuid");
class Lot {
    constructor(attributes) {
        this._attributes = {
            ...attributes,
            lotId: (0, uuid_1.v4)(),
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.validate();
    }
    // Getters
    get lotId() { return this._attributes.lotId; }
    get lotCode() { return this._attributes.lotCode; }
    get sku() { return this._attributes.sku; }
    get expDate() { return this._attributes.expDate; }
    get status() { return this._attributes.status; }
    get qualityStatus() { return this._attributes.qualityStatus; }
    get remainingQty() { return this._attributes.remainingQty; }
    get allocatedQty() { return this._attributes.allocatedQty; }
    get availableQty() { return this._attributes.remainingQty - this._attributes.allocatedQty; }
    get attributes() { return { ...this._attributes }; }
    // Business logic methods
    isExpired() {
        if (!this._attributes.expDate)
            return false;
        return new Date() > this._attributes.expDate;
    }
    isExpiringSoon(days = 30) {
        if (!this._attributes.expDate)
            return false;
        const now = new Date();
        const daysUntilExpiry = Math.floor((this._attributes.expDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        return daysUntilExpiry <= days && daysUntilExpiry > 0;
    }
    canAllocate(quantity) {
        return this.availableQty >= quantity && this.isActive();
    }
    isActive() {
        return this._attributes.status === 'active' && !this.isExpired();
    }
    isOnHold() {
        return this._attributes.status === 'hold';
    }
    isBlocked() {
        return this._attributes.status === 'blocked';
    }
    allocate(quantity) {
        if (!this.canAllocate(quantity)) {
            throw new Error(`Cannot allocate ${quantity} from lot ${this._attributes.lotCode}`);
        }
        this._attributes.allocatedQty += quantity;
        this._attributes.updatedAt = new Date();
    }
    deallocate(quantity) {
        this._attributes.allocatedQty = Math.max(0, this._attributes.allocatedQty - quantity);
        this._attributes.updatedAt = new Date();
    }
    consume(quantity) {
        if (quantity > this._attributes.allocatedQty) {
            throw new Error(`Cannot consume ${quantity}, only ${this._attributes.allocatedQty} allocated`);
        }
        this._attributes.allocatedQty -= quantity;
        this._attributes.remainingQty -= quantity;
        this._attributes.updatedAt = new Date();
        if (this._attributes.remainingQty <= 0) {
            this._attributes.status = 'consumed';
        }
    }
    putOnHold(reason) {
        this._attributes.status = 'hold';
        this._attributes.holdReason = reason;
        this._attributes.updatedAt = new Date();
    }
    releaseHold() {
        if (this._attributes.status === 'hold') {
            this._attributes.status = 'active';
            this._attributes.holdReason = undefined;
            this._attributes.updatedAt = new Date();
        }
    }
    block(reason) {
        this._attributes.status = 'blocked';
        this._attributes.blockedReason = reason;
        this._attributes.updatedAt = new Date();
    }
    updateQualityStatus(status, notes) {
        this._attributes.qualityStatus = status;
        if (notes) {
            this._attributes.qaNotes = notes;
        }
        if (status === 'failed') {
            this.block('Quality inspection failed');
        }
        else if (status === 'quarantined') {
            this.putOnHold('Quarantined for quality review');
        }
        else if (status === 'passed' && this._attributes.status === 'hold') {
            this.releaseHold();
        }
        this._attributes.updatedAt = new Date();
    }
    updateCustomFields(fields) {
        this._attributes.customFields = {
            ...this._attributes.customFields,
            ...fields
        };
        this._attributes.updatedAt = new Date();
    }
    // FEFO (First Expiry, First Out) priority
    getFefoPriority() {
        if (!this._attributes.expDate)
            return 999999; // No expiry = lowest priority
        if (this.isExpired())
            return -1; // Expired = highest priority (should be handled)
        const now = new Date();
        const daysUntilExpiry = Math.floor((this._attributes.expDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        return Math.max(0, daysUntilExpiry); // Lower number = higher priority
    }
    validate() {
        if (!this._attributes.lotCode || this._attributes.lotCode.trim() === '') {
            throw new Error('Lot code is required');
        }
        if (!this._attributes.sku || this._attributes.sku.trim() === '') {
            throw new Error('SKU is required');
        }
        if (this._attributes.initialQty <= 0) {
            throw new Error('Initial quantity must be positive');
        }
        if (this._attributes.remainingQty < 0) {
            throw new Error('Remaining quantity cannot be negative');
        }
        if (this._attributes.allocatedQty < 0) {
            throw new Error('Allocated quantity cannot be negative');
        }
        if (this._attributes.allocatedQty > this._attributes.remainingQty) {
            throw new Error('Allocated quantity cannot exceed remaining quantity');
        }
        if (this._attributes.mfgDate && this._attributes.expDate) {
            if (this._attributes.mfgDate >= this._attributes.expDate) {
                throw new Error('Manufacturing date must be before expiry date');
            }
        }
    }
    // Factory methods
    static create(attributes) {
        return new Lot(attributes);
    }
    static fromAttributes(attributes) {
        const lot = new Lot(attributes);
        lot._attributes = attributes;
        return lot;
    }
    // Utility methods
    getAgeInDays() {
        const now = new Date();
        return Math.floor((now.getTime() - this._attributes.receivedDate.getTime()) / (1000 * 60 * 60 * 24));
    }
    getDaysUntilExpiry() {
        if (!this._attributes.expDate)
            return null;
        const now = new Date();
        return Math.floor((this._attributes.expDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    }
    hasCustomField(key) {
        return this._attributes.customFields?.[key] !== undefined;
    }
    getCustomField(key) {
        return this._attributes.customFields?.[key];
    }
    // FSMA 204 compliance helpers
    getKdeFields() {
        return {
            lotNumber: this._attributes.lotCode,
            harvestDate: this._attributes.mfgDate?.toISOString(),
            expirationDate: this._attributes.expDate?.toISOString(),
            originCountry: this._attributes.originCountry,
            ...this._attributes.customFields
        };
    }
    // GS1 compliance
    getGs1LotData() {
        return {
            '10': this._attributes.lotCode, // BATCH/LOT
            '11': this._attributes.mfgDate?.toISOString().substring(2, 8), // PROD DATE (YYMMDD)
            '17': this._attributes.expDate?.toISOString().substring(2, 8), // EXP DATE (YYMMDD)
            '30': this._attributes.remainingQty.toString() // VAR COUNT
        };
    }
}
exports.Lot = Lot;
//# sourceMappingURL=lot.js.map