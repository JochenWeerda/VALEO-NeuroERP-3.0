/**
 * VALEO NeuroERP 3.0 - SKU Entity
 *
 * Represents a Stock Keeping Unit with GS1 compliance and WMS attributes
 */

// uuidv4 wurde nicht verwendet
// Zeitkonstanten
const MS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MS_PER_DAY = MS_PER_SECOND * SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY;

export interface SkuAttributes {
  sku: string;
  gtin?: string; // GS1 GTIN
  description: string;
  category: string;
  uom: string; // Unit of Measure
  weight?: number;
  volume?: number;
  dimensions?: {
    length: number;
    width: number;
    height: number;
  };
  tempZone: 'frozen' | 'refrigerated' | 'ambient' | 'heated';
  hazmat: boolean;
  hazmatClass?: string;
  abcClass: 'A' | 'B' | 'C';
  velocityClass: 'X' | 'Y' | 'Z'; // XYZ analysis
  minOrderQty?: number;
  maxOrderQty?: number;
  reorderPoint?: number;
  safetyStock?: number;
  shelfLifeDays?: number;
  serialTracked: boolean;
  lotTracked: boolean;
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export class Sku {
  private _attributes: SkuAttributes;

  constructor(attributes: Omit<SkuAttributes, 'createdAt' | 'updatedAt'>) {
    this._attributes = {
      ...attributes,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    this.validate();
  }

  // Getters
  get sku(): string { return this._attributes.sku; }
  get gtin(): string | undefined { return this._attributes.gtin; }
  get description(): string { return this._attributes.description; }
  get category(): string { return this._attributes.category; }
  get uom(): string { return this._attributes.uom; }
  get tempZone(): string { return this._attributes.tempZone; }
  get hazmat(): boolean { return this._attributes.hazmat; }
  get abcClass(): string { return this._attributes.abcClass; }
  get velocityClass(): string { return this._attributes.velocityClass; }
  get serialTracked(): boolean { return this._attributes.serialTracked; }
  get lotTracked(): boolean { return this._attributes.lotTracked; }
  get active(): boolean { return this._attributes.active; }
  get attributes(): SkuAttributes { return { ...this._attributes }; }

  // Business logic methods
  isPerishable(): boolean {
    return this._attributes.shelfLifeDays !== undefined && this._attributes.shelfLifeDays > 0;
  }

  isHighValue(): boolean {
    return this._attributes.abcClass === 'A';
  }

  isFastMoving(): boolean {
    return this._attributes.velocityClass === 'X';
  }

  requiresSpecialHandling(): boolean {
    return this._attributes.hazmat || this._attributes.tempZone !== 'ambient';
  }

  canExpire(expiryDate: Date): boolean {
    if (!this._attributes.shelfLifeDays) return false;
    const now = new Date();
    const daysUntilExpiry = Math.floor((expiryDate.getTime() - now.getTime()) / MS_PER_DAY);
    return daysUntilExpiry <= this._attributes.shelfLifeDays;
  }

  update(attributes: Partial<Omit<SkuAttributes, 'sku' | 'createdAt'>>): void {
    this._attributes = {
      ...this._attributes,
      ...attributes,
      updatedAt: new Date()
    };
    this.validate();
  }

  deactivate(): void {
    this._attributes.active = false;
    this._attributes.updatedAt = new Date();
  }

  activate(): void {
    this._attributes.active = true;
    this._attributes.updatedAt = new Date();
  }

  private validate(): void {
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

  private isValidGtin(gtin: string): boolean {
    // Basic GTIN validation (8, 12, 13, 14 digits)
    const cleanGtin = gtin.replace(/[^0-9]/g, '');
    return /^[0-9]{8,14}$/.test(cleanGtin);
  }

  // Factory methods
  static create(attributes: Omit<SkuAttributes, 'createdAt' | 'updatedAt'>): Sku {
    return new Sku(attributes);
  }

  static fromAttributes(attributes: SkuAttributes): Sku {
    const sku = new Sku(attributes);
    sku._attributes = attributes;
    return sku;
  }
}