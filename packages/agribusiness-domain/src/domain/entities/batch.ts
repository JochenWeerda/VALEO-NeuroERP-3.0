/**
 * Batch Entity
 * Complete Batch Traceability for Agribusiness
 * Based on Odoo stock_agriculture pattern
 */

import { randomUUID } from 'crypto';

export type BatchStatus = 
  | 'ACTIVE'           // Aktiv
  | 'ON_HOLD'          // Zurückgestellt
  | 'BLOCKED'          // Gesperrt
  | 'EXPIRED'          // Abgelaufen
  | 'CONSUMED';        // Verbraucht

export type BatchType = 
  | 'SEED'             // Saatgut
  | 'CROP'             // Ernte
  | 'FERTILIZER'       // Düngemittel
  | 'FEED'             // Futtermittel
  | 'PRODUCT';         // Endprodukt

export interface BatchTraceabilityNode {
  batchId: string;
  batchNumber: string;
  batchType: BatchType;
  productId?: string;
  productName?: string;
  quantity: number;
  originCountry?: string;
  harvestDate?: Date;
  parentBatchId?: string;
  qualityCertificateId?: string;
  createdAt: Date;
  children?: BatchTraceabilityNode[];
}

export interface BatchTraceabilityTree {
  root: BatchTraceabilityNode;
  depth: number;
  totalBatches: number;
  traceabilityChain: BatchTraceabilityNode[];
}

export interface CreateBatchInput {
  batchNumber: string;
  batchType: BatchType;
  productId?: string;
  originCountry?: string;
  harvestDate?: Date;
  expiryDate?: Date;
  parentBatchId?: string;
  qualityCertificateId?: string;
  initialQuantity: number;
  unitOfMeasure: string;
  notes?: string;
  customFields?: Record<string, unknown>;
}

export interface UpdateBatchInput {
  batchNumber?: string;
  originCountry?: string;
  harvestDate?: Date;
  expiryDate?: Date;
  qualityCertificateId?: string;
  notes?: string;
  customFields?: Record<string, unknown>;
}

export class Batch {
  public readonly id: string;
  public batchNumber: string;
  public batchType: BatchType;
  public productId?: string;
  public originCountry?: string;
  public harvestDate?: Date;
  public expiryDate?: Date;
  public parentBatchId?: string;
  public qualityCertificateId?: string;
  public status: BatchStatus;
  public initialQuantity: number;
  public remainingQuantity: number;
  public allocatedQuantity: number;
  public unitOfMeasure: string;
  public notes?: string;
  public customFields?: Record<string, unknown>;
  public version: number;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public readonly createdBy: string;
  public updatedBy?: string;

  constructor(
    batchNumber: string,
    batchType: BatchType,
    initialQuantity: number,
    unitOfMeasure: string,
    createdBy: string,
    options: {
      id?: string;
      productId?: string;
      originCountry?: string;
      harvestDate?: Date;
      expiryDate?: Date;
      parentBatchId?: string;
      qualityCertificateId?: string;
      notes?: string;
      customFields?: Record<string, unknown>;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.batchNumber = batchNumber;
    this.batchType = batchType;
    this.productId = options.productId;
    this.originCountry = options.originCountry;
    this.harvestDate = options.harvestDate;
    this.expiryDate = options.expiryDate;
    this.parentBatchId = options.parentBatchId;
    this.qualityCertificateId = options.qualityCertificateId;
    this.status = 'ACTIVE';
    this.initialQuantity = initialQuantity;
    this.remainingQuantity = initialQuantity;
    this.allocatedQuantity = 0;
    this.unitOfMeasure = unitOfMeasure;
    this.notes = options.notes;
    this.customFields = options.customFields;
    this.version = 1;
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.createdBy = createdBy;

    this.validate();
  }

  private validate(): void {
    if (!this.batchNumber || this.batchNumber.trim() === '') {
      throw new Error('Batch number is required');
    }

    if (this.initialQuantity <= 0) {
      throw new Error('Initial quantity must be positive');
    }

    if (this.remainingQuantity < 0) {
      throw new Error('Remaining quantity cannot be negative');
    }

    if (this.allocatedQuantity < 0) {
      throw new Error('Allocated quantity cannot be negative');
    }

    if (this.allocatedQuantity > this.remainingQuantity) {
      throw new Error('Allocated quantity cannot exceed remaining quantity');
    }

    if (this.harvestDate && this.expiryDate && this.harvestDate >= this.expiryDate) {
      throw new Error('Harvest date must be before expiry date');
    }
  }

  public updateBasicInfo(updates: UpdateBatchInput, updatedBy: string): void {
    if (this.status !== 'ACTIVE') {
      throw new Error('Can only update active batches');
    }

    if (updates.batchNumber !== undefined) this.batchNumber = updates.batchNumber;
    if (updates.originCountry !== undefined) this.originCountry = updates.originCountry;
    if (updates.harvestDate !== undefined) this.harvestDate = updates.harvestDate;
    if (updates.expiryDate !== undefined) this.expiryDate = updates.expiryDate;
    if (updates.qualityCertificateId !== undefined) this.qualityCertificateId = updates.qualityCertificateId;
    if (updates.notes !== undefined) this.notes = updates.notes;
    if (updates.customFields !== undefined) {
      this.customFields = {
        ...this.customFields,
        ...updates.customFields
      };
    }

    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
    this.validate();
  }

  public allocate(quantity: number): void {
    if (!this.canAllocate(quantity)) {
      throw new Error(`Cannot allocate ${quantity} from batch ${this.batchNumber}`);
    }

    this.allocatedQuantity += quantity;
    this.updatedAt = new Date();
    this.version++;
  }

  public deallocate(quantity: number): void {
    this.allocatedQuantity = Math.max(0, this.allocatedQuantity - quantity);
    this.updatedAt = new Date();
    this.version++;
  }

  public consume(quantity: number): void {
    if (quantity > this.allocatedQuantity) {
      throw new Error(`Cannot consume ${quantity}, only ${this.allocatedQuantity} allocated`);
    }

    this.allocatedQuantity -= quantity;
    this.remainingQuantity -= quantity;
    this.updatedAt = new Date();
    this.version++;

    if (this.remainingQuantity <= 0) {
      this.status = 'CONSUMED';
    }
  }

  public putOnHold(reason: string): void {
    if (this.status !== 'ACTIVE') {
      throw new Error('Can only put active batches on hold');
    }

    this.status = 'ON_HOLD';
    this.notes = `${this.notes || ''}\n[HOLD] ${reason}`.trim();
    this.updatedAt = new Date();
    this.version++;
  }

  public releaseHold(): void {
    if (this.status === 'ON_HOLD') {
      this.status = 'ACTIVE';
      this.updatedAt = new Date();
      this.version++;
    }
  }

  public block(reason: string): void {
    this.status = 'BLOCKED';
    this.notes = `${this.notes || ''}\n[BLOCKED] ${reason}`.trim();
    this.updatedAt = new Date();
    this.version++;
  }

  public isExpired(): boolean {
    if (!this.expiryDate) return false;
    return new Date() > this.expiryDate;
  }

  public isExpiringSoon(days: number = 30): boolean {
    if (!this.expiryDate) return false;
    const now = new Date();
    const daysUntilExpiry = Math.ceil((this.expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= days && daysUntilExpiry > 0;
  }

  public canAllocate(quantity: number): boolean {
    return this.availableQuantity >= quantity && this.isActive();
  }

  public isActive(): boolean {
    return this.status === 'ACTIVE' && !this.isExpired();
  }

  public get availableQuantity(): number {
    return this.remainingQuantity - this.allocatedQuantity;
  }

  public getDaysUntilExpiry(): number | null {
    if (!this.expiryDate) return null;
    const now = new Date();
    return Math.ceil((this.expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  }

  public getAgeInDays(): number {
    const now = new Date();
    const startDate = this.harvestDate || this.createdAt;
    return Math.floor((now.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
  }

  public toJSON(): any {
    return {
      id: this.id,
      batchNumber: this.batchNumber,
      batchType: this.batchType,
      productId: this.productId,
      originCountry: this.originCountry,
      harvestDate: this.harvestDate?.toISOString(),
      expiryDate: this.expiryDate?.toISOString(),
      parentBatchId: this.parentBatchId,
      qualityCertificateId: this.qualityCertificateId,
      status: this.status,
      initialQuantity: this.initialQuantity,
      remainingQuantity: this.remainingQuantity,
      allocatedQuantity: this.allocatedQuantity,
      availableQuantity: this.availableQuantity,
      unitOfMeasure: this.unitOfMeasure,
      notes: this.notes,
      customFields: this.customFields,
      isExpired: this.isExpired(),
      isExpiringSoon: this.isExpiringSoon(),
      daysUntilExpiry: this.getDaysUntilExpiry(),
      ageInDays: this.getAgeInDays(),
      version: this.version,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      createdBy: this.createdBy,
      updatedBy: this.updatedBy
    };
  }
}
