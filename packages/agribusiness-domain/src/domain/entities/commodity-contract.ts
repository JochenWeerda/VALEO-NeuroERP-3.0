/**
 * Commodity Contract Entity
 * Forward Contracts for Commodity Trading
 * Based on OCA purchase_agriculture Forward Contracts pattern
 */

import { randomUUID } from 'crypto';

export type CommodityContractStatus = 
  | 'DRAFT'              // Entwurf
  | 'NEGOTIATING'         // Verhandlung
  | 'SIGNED'             // Unterzeichnet
  | 'ACTIVE'             // Aktiv
  | 'FULFILLED'          // Erfüllt
  | 'EXPIRED'            // Abgelaufen
  | 'CANCELLED';         // Storniert

export type CommodityType = 
  | 'WHEAT'              // Weizen
  | 'CORN'               // Mais
  | 'BARLEY'             // Gerste
  | 'RAPE'               // Raps
  | 'SOYBEAN'            // Sojabohnen
  | 'SUNFLOWER'          // Sonnenblumen
  | 'FERTILIZER'         // Düngemittel
  | 'FEED';              // Futtermittel

export type ContractType = 
  | 'FORWARD'            // Forward Contract (Festpreis)
  | 'FUTURES'            // Futures Contract
  | 'OPTION';            // Option Contract

export interface CommodityContractItem {
  id: string;
  commodity: CommodityType;
  quantity: number;
  unitOfMeasure: string;
  contractPrice: number;
  currency: string;
  deliveryDate: Date;
  qualitySpecifications?: {
    moisture?: number;
    protein?: number;
    impurities?: number;
    [key: string]: number | undefined;
  };
  notes?: string;
  fulfilledQuantity?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateCommodityContractInput {
  contractNumber: string;
  contractType: ContractType;
  supplierId: string;
  items: Omit<CommodityContractItem, 'id' | 'createdAt' | 'updatedAt' | 'fulfilledQuantity'>[];
  contractDate: Date;
  deliveryPeriodStart: Date;
  deliveryPeriodEnd: Date;
  paymentTerms: string;
  currency: string;
  hedgingStrategy?: string;
  notes?: string;
}

export interface UpdateCommodityContractInput {
  contractNumber?: string;
  supplierId?: string;
  deliveryPeriodStart?: Date;
  deliveryPeriodEnd?: Date;
  paymentTerms?: string;
  notes?: string;
}

export class CommodityContract {
  public readonly id: string;
  public contractNumber: string;
  public contractType: ContractType;
  public supplierId: string;
  public status: CommodityContractStatus;
  public items: CommodityContractItem[];
  public contractDate: Date;
  public deliveryPeriodStart: Date;
  public deliveryPeriodEnd: Date;
  public paymentTerms: string;
  public currency: string;
  public hedgingStrategy?: string;
  public notes?: string;
  public totalContractValue: number;
  public fulfilledValue: number;
  public remainingValue: number;
  public version: number;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public readonly createdBy: string;
  public updatedBy?: string;
  public signedAt?: Date;
  public signedBy?: string;
  public cancelledAt?: Date;
  public cancelledBy?: string;
  public cancellationReason?: string;

  constructor(
    contractNumber: string,
    contractType: ContractType,
    supplierId: string,
    items: CommodityContractItem[],
    contractDate: Date,
    deliveryPeriodStart: Date,
    deliveryPeriodEnd: Date,
    paymentTerms: string,
    currency: string,
    createdBy: string,
    options: {
      id?: string;
      hedgingStrategy?: string;
      notes?: string;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.contractNumber = contractNumber;
    this.contractType = contractType;
    this.supplierId = supplierId;
    this.status = 'DRAFT';
    this.items = items;
    this.contractDate = contractDate;
    this.deliveryPeriodStart = deliveryPeriodStart;
    this.deliveryPeriodEnd = deliveryPeriodEnd;
    this.paymentTerms = paymentTerms;
    this.currency = currency;
    this.hedgingStrategy = options.hedgingStrategy;
    this.notes = options.notes;
    this.version = 1;
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.createdBy = createdBy;

    // Calculate totals
    this.calculateTotals();
    this.validate();
  }

  private validate(): void {
    if (!this.contractNumber || this.contractNumber.trim() === '') {
      throw new Error('Contract number is required');
    }

    if (!this.supplierId || this.supplierId.trim() === '') {
      throw new Error('Supplier ID is required');
    }

    if (this.items.length === 0) {
      throw new Error('At least one contract item is required');
    }

    if (this.deliveryPeriodStart >= this.deliveryPeriodEnd) {
      throw new Error('Delivery period start must be before end');
    }

    if (this.contractDate > this.deliveryPeriodStart) {
      throw new Error('Contract date should not be after delivery period start');
    }
  }

  private calculateTotals(): void {
    this.totalContractValue = this.items.reduce((sum, item) => {
      return sum + (item.contractPrice * item.quantity);
    }, 0);

    this.fulfilledValue = this.items.reduce((sum, item) => {
      const fulfilledQty = item.fulfilledQuantity || 0;
      return sum + (item.contractPrice * fulfilledQty);
    }, 0);

    this.remainingValue = this.totalContractValue - this.fulfilledValue;
  }

  public updateBasicInfo(updates: UpdateCommodityContractInput, updatedBy: string): void {
    if (!['DRAFT', 'NEGOTIATING'].includes(this.status)) {
      throw new Error('Can only update draft or negotiating contracts');
    }

    if (updates.contractNumber !== undefined) this.contractNumber = updates.contractNumber;
    if (updates.supplierId !== undefined) this.supplierId = updates.supplierId;
    if (updates.deliveryPeriodStart !== undefined) this.deliveryPeriodStart = updates.deliveryPeriodStart;
    if (updates.deliveryPeriodEnd !== undefined) this.deliveryPeriodEnd = updates.deliveryPeriodEnd;
    if (updates.paymentTerms !== undefined) this.paymentTerms = updates.paymentTerms;
    if (updates.notes !== undefined) this.notes = updates.notes;

    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
    this.validate();
  }

  public addItem(item: Omit<CommodityContractItem, 'id' | 'createdAt' | 'updatedAt' | 'fulfilledQuantity'>): CommodityContractItem {
    if (!['DRAFT', 'NEGOTIATING'].includes(this.status)) {
      throw new Error('Can only add items to draft or negotiating contracts');
    }

    const newItem: CommodityContractItem = {
      ...item,
      id: randomUUID(),
      fulfilledQuantity: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.items.push(newItem);
    this.calculateTotals();
    this.updatedAt = new Date();
    this.version++;

    return newItem;
  }

  public updateItem(itemId: string, updates: Partial<Omit<CommodityContractItem, 'id' | 'createdAt' | 'updatedAt'>>): void {
    if (!['DRAFT', 'NEGOTIATING'].includes(this.status)) {
      throw new Error('Can only update items in draft or negotiating contracts');
    }

    const itemIndex = this.items.findIndex(item => item.id === itemId);
    if (itemIndex === -1) {
      throw new Error('Item not found');
    }

    Object.assign(this.items[itemIndex], updates, { updatedAt: new Date() });
    this.calculateTotals();
    this.updatedAt = new Date();
    this.version++;
  }

  public removeItem(itemId: string): void {
    if (!['DRAFT', 'NEGOTIATING'].includes(this.status)) {
      throw new Error('Can only remove items from draft or negotiating contracts');
    }

    const itemIndex = this.items.findIndex(item => item.id === itemId);
    if (itemIndex === -1) {
      throw new Error('Item not found');
    }

    this.items.splice(itemIndex, 1);
    this.calculateTotals();
    this.updatedAt = new Date();
    this.version++;
  }

  public startNegotiation(updatedBy: string): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only start negotiation from draft status');
    }

    this.status = 'NEGOTIATING';
    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public sign(signedBy: string): void {
    if (!['DRAFT', 'NEGOTIATING'].includes(this.status)) {
      throw new Error('Can only sign draft or negotiating contracts');
    }

    this.status = 'SIGNED';
    this.signedAt = new Date();
    this.signedBy = signedBy;
    this.updatedBy = signedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public activate(activatedBy: string): void {
    if (this.status !== 'SIGNED') {
      throw new Error('Can only activate signed contracts');
    }

    this.status = 'ACTIVE';
    this.updatedBy = activatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public recordFulfillment(itemId: string, fulfilledQuantity: number, updatedBy: string): void {
    if (this.status !== 'ACTIVE') {
      throw new Error('Can only record fulfillment for active contracts');
    }

    const item = this.items.find(i => i.id === itemId);
    if (!item) {
      throw new Error('Item not found');
    }

    const currentFulfilled = item.fulfilledQuantity || 0;
    const newFulfilled = currentFulfilled + fulfilledQuantity;

    if (newFulfilled > item.quantity) {
      throw new Error('Fulfilled quantity cannot exceed contract quantity');
    }

    item.fulfilledQuantity = newFulfilled;
    this.calculateTotals();
    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;

    // Check if contract is fully fulfilled
    const allFulfilled = this.items.every(i => (i.fulfilledQuantity || 0) >= i.quantity);
    if (allFulfilled) {
      this.status = 'FULFILLED';
    }
  }

  public cancel(cancelledBy: string, reason: string): void {
    if (['FULFILLED', 'CANCELLED'].includes(this.status)) {
      throw new Error('Cannot cancel fulfilled or already cancelled contracts');
    }

    this.status = 'CANCELLED';
    this.cancelledAt = new Date();
    this.cancelledBy = cancelledBy;
    this.cancellationReason = reason;
    this.updatedBy = cancelledBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public isExpired(): boolean {
    return new Date() > this.deliveryPeriodEnd && this.status === 'ACTIVE';
  }

  public isInDeliveryPeriod(): boolean {
    const now = new Date();
    return now >= this.deliveryPeriodStart && now <= this.deliveryPeriodEnd;
  }

  public getFulfillmentProgress(): number {
    if (this.totalContractValue === 0) return 0;
    return (this.fulfilledValue / this.totalContractValue) * 100;
  }

  public getDaysUntilDeliveryStart(): number {
    const now = new Date();
    if (now >= this.deliveryPeriodStart) return 0;
    return Math.ceil((this.deliveryPeriodStart.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  }

  public getDaysUntilDeliveryEnd(): number {
    const now = new Date();
    if (now > this.deliveryPeriodEnd) return 0;
    return Math.ceil((this.deliveryPeriodEnd.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  }

  public toJSON(): any {
    return {
      id: this.id,
      contractNumber: this.contractNumber,
      contractType: this.contractType,
      supplierId: this.supplierId,
      status: this.status,
      items: this.items.map(item => ({
        ...item,
        deliveryDate: item.deliveryDate.toISOString(),
        createdAt: item.createdAt.toISOString(),
        updatedAt: item.updatedAt.toISOString()
      })),
      contractDate: this.contractDate.toISOString(),
      deliveryPeriodStart: this.deliveryPeriodStart.toISOString(),
      deliveryPeriodEnd: this.deliveryPeriodEnd.toISOString(),
      paymentTerms: this.paymentTerms,
      currency: this.currency,
      hedgingStrategy: this.hedgingStrategy,
      notes: this.notes,
      totalContractValue: this.totalContractValue,
      fulfilledValue: this.fulfilledValue,
      remainingValue: this.remainingValue,
      fulfillmentProgress: this.getFulfillmentProgress(),
      isExpired: this.isExpired(),
      isInDeliveryPeriod: this.isInDeliveryPeriod(),
      daysUntilDeliveryStart: this.getDaysUntilDeliveryStart(),
      daysUntilDeliveryEnd: this.getDaysUntilDeliveryEnd(),
      version: this.version,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      createdBy: this.createdBy,
      updatedBy: this.updatedBy,
      signedAt: this.signedAt?.toISOString(),
      signedBy: this.signedBy,
      cancelledAt: this.cancelledAt?.toISOString(),
      cancelledBy: this.cancelledBy,
      cancellationReason: this.cancellationReason
    };
  }
}
