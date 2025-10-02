/**
 * VALEO NeuroERP 3.0 - Lot Entity
 *
 * Represents inventory lots with expiry tracking and GS1 compliance
 */
export type LotStatus = 'active' | 'hold' | 'blocked' | 'expired' | 'consumed';
export interface LotAttributes {
    lotId: string;
    lotCode: string;
    sku: string;
    mfgDate?: Date;
    expDate?: Date;
    receivedDate: Date;
    supplierLot?: string;
    supplierId?: string;
    originCountry?: string;
    status: LotStatus;
    holdReason?: string;
    blockedReason?: string;
    qualityStatus: 'pending' | 'passed' | 'failed' | 'quarantined';
    qaNotes?: string;
    initialQty: number;
    remainingQty: number;
    allocatedQty: number;
    uom: string;
    unitCost?: number;
    totalCost?: number;
    customFields?: Record<string, any>;
    createdAt: Date;
    updatedAt: Date;
}
export declare class Lot {
    private _attributes;
    constructor(attributes: Omit<LotAttributes, 'lotId' | 'createdAt' | 'updatedAt'>);
    get lotId(): string;
    get lotCode(): string;
    get sku(): string;
    get expDate(): Date | undefined;
    get status(): LotStatus;
    get qualityStatus(): string;
    get remainingQty(): number;
    get allocatedQty(): number;
    get availableQty(): number;
    get attributes(): LotAttributes;
    isExpired(): boolean;
    isExpiringSoon(days?: number): boolean;
    canAllocate(quantity: number): boolean;
    isActive(): boolean;
    isOnHold(): boolean;
    isBlocked(): boolean;
    allocate(quantity: number): void;
    deallocate(quantity: number): void;
    consume(quantity: number): void;
    putOnHold(reason: string): void;
    releaseHold(): void;
    block(reason: string): void;
    updateQualityStatus(status: 'passed' | 'failed' | 'quarantined', notes?: string): void;
    updateCustomFields(fields: Record<string, any>): void;
    getFefoPriority(): number;
    private validate;
    static create(attributes: Omit<LotAttributes, 'lotId' | 'createdAt' | 'updatedAt'>): Lot;
    static fromAttributes(attributes: LotAttributes): Lot;
    getAgeInDays(): number;
    getDaysUntilExpiry(): number | null;
    hasCustomField(key: string): boolean;
    getCustomField(key: string): any;
    getKdeFields(): Record<string, any>;
    getGs1LotData(): Record<string, any>;
}
//# sourceMappingURL=lot.d.ts.map