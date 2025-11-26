/**
 * Delivery Note Entity
 * Complete Delivery Management with tracking and status workflows
 */

import { randomUUID } from 'crypto';

export type DeliveryNoteStatus = 
  | 'PREPARED'        // Vorbereitet
  | 'READY_FOR_PICKUP'// Abholbereit
  | 'IN_TRANSIT'      // Unterwegs
  | 'DELIVERED'       // Zugestellt
  | 'CONFIRMED'       // Bestätigt
  | 'RETURNED'        // Retourniert
  | 'CANCELLED';      // Storniert

export type DeliveryNoteItemType = 'PRODUCT' | 'SERVICE';

export interface DeliveryNoteItem {
  id: string;
  sourceOrderItemId?: string;  // Verknüpfung zum Original-Auftragsposten
  itemType: DeliveryNoteItemType;
  articleId?: string;
  description: string;
  orderedQuantity: number;     // Bestellte Menge
  deliveredQuantity: number;   // Tatsächlich gelieferte Menge
  unitPrice: number;
  discountPercent: number;
  netAmount: number;
  taxRate: number;
  taxAmount: number;
  totalAmount: number;
  serialNumbers?: string[];    // Seriennummern der gelieferten Artikel
  batchNumbers?: string[];     // Chargen-Nummern
  expiryDate?: Date;          // Verfallsdatum (bei verderblichen Waren)
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateDeliveryNoteInput {
  orderId: string;
  customerId: string;
  deliveryAddress: {
    name: string;
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  plannedDeliveryDate: Date;
  carrierInfo?: {
    carrierName: string;
    trackingNumber?: string;
    carrierService?: string; // Standard, Express, etc.
  };
  specialInstructions?: string;
  items: Omit<DeliveryNoteItem, 'id' | 'createdAt' | 'updatedAt'>[];
}

export interface UpdateDeliveryNoteInput {
  plannedDeliveryDate?: Date;
  deliveryAddress?: {
    name: string;
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  carrierInfo?: {
    carrierName: string;
    trackingNumber?: string;
    carrierService?: string;
  };
  specialInstructions?: string;
}

export class DeliveryNote {
  public readonly id: string;
  public readonly deliveryNoteNumber: string;
  public readonly orderId: string;
  public readonly customerId: string;
  public status: DeliveryNoteStatus;
  public deliveryAddress: {
    name: string;
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  public plannedDeliveryDate: Date;
  public actualDeliveryDate?: Date;
  public carrierInfo?: {
    carrierName: string;
    trackingNumber?: string;
    carrierService?: string;
  };
  public specialInstructions?: string;
  public items: DeliveryNoteItem[];
  public subtotalAmount: number;
  public taxAmount: number;
  public totalAmount: number;
  public weight?: number;          // Gesamtgewicht in kg
  public dimensions?: {            // Abmessungen in cm
    length: number;
    width: number;
    height: number;
  };
  public packagesCount: number;    // Anzahl Pakete/Kartons
  public version: number;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public readonly createdBy: string;
  public updatedBy?: string;
  public preparedAt?: Date;
  public preparedBy?: string;
  public shippedAt?: Date;
  public shippedBy?: string;
  public deliveredAt?: Date;
  public confirmedAt?: Date;
  public confirmedBy?: string;    // Kunde, der Lieferung bestätigt hat
  public deliveryProof?: {
    signatureBase64?: string;     // Digitale Unterschrift
    photoBase64?: string;         // Foto als Nachweis
    recipientName?: string;       // Name des Empfängers
    notes?: string;
  };

  constructor(
    orderId: string,
    customerId: string,
    deliveryAddress: {
      name: string;
      street: string;
      postalCode: string;
      city: string;
      country: string;
      state?: string;
    },
    plannedDeliveryDate: Date,
    items: DeliveryNoteItem[],
    createdBy: string,
    options: {
      id?: string;
      deliveryNoteNumber?: string;
      carrierInfo?: {
        carrierName: string;
        trackingNumber?: string;
        carrierService?: string;
      };
      specialInstructions?: string;
      weight?: number;
      dimensions?: {
        length: number;
        width: number;
        height: number;
      };
      packagesCount?: number;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.deliveryNoteNumber = options.deliveryNoteNumber || this.generateDeliveryNoteNumber();
    this.orderId = orderId;
    this.customerId = customerId;
    this.status = 'PREPARED';
    this.deliveryAddress = deliveryAddress;
    this.plannedDeliveryDate = plannedDeliveryDate;
    this.carrierInfo = options.carrierInfo;
    this.specialInstructions = options.specialInstructions;
    this.items = items;
    this.weight = options.weight;
    this.dimensions = options.dimensions;
    this.packagesCount = options.packagesCount || 1;
    this.version = 1;
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.createdBy = createdBy;

    // Calculate totals
    this.calculateTotals();
  }

  private generateDeliveryNoteNumber(): string {
    const now = new Date();
    const year = now.getFullYear().toString().slice(-2);
    const month = (now.getMonth() + 1).toString().padStart(2, '0');
    const day = now.getDate().toString().padStart(2, '0');
    const time = now.getTime().toString().slice(-6);
    return `DN-${year}${month}${day}-${time}`;
  }

  private calculateTotals(): void {
    this.subtotalAmount = this.items.reduce((sum, item) => sum + item.netAmount, 0);
    this.taxAmount = this.items.reduce((sum, item) => sum + item.taxAmount, 0);
    this.totalAmount = this.subtotalAmount + this.taxAmount;
  }

  public updateBasicInfo(updates: UpdateDeliveryNoteInput, updatedBy: string): void {
    if (!['PREPARED', 'READY_FOR_PICKUP'].includes(this.status)) {
      throw new Error('Can only update prepared or ready delivery notes');
    }

    if (updates.plannedDeliveryDate !== undefined) this.plannedDeliveryDate = updates.plannedDeliveryDate;
    if (updates.deliveryAddress !== undefined) this.deliveryAddress = updates.deliveryAddress;
    if (updates.carrierInfo !== undefined) this.carrierInfo = updates.carrierInfo;
    if (updates.specialInstructions !== undefined) this.specialInstructions = updates.specialInstructions;

    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public addItem(item: Omit<DeliveryNoteItem, 'id' | 'createdAt' | 'updatedAt'>): DeliveryNoteItem {
    if (this.status !== 'PREPARED') {
      throw new Error('Can only add items to prepared delivery notes');
    }

    const newItem: DeliveryNoteItem = {
      ...item,
      id: randomUUID(),
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.items.push(newItem);
    this.calculateTotals();
    this.updatedAt = new Date();
    this.version++;

    return newItem;
  }

  public updateItem(itemId: string, updates: Partial<Omit<DeliveryNoteItem, 'id' | 'createdAt' | 'updatedAt'>>): void {
    if (this.status !== 'PREPARED') {
      throw new Error('Can only update items in prepared delivery notes');
    }

    const itemIndex = this.items.findIndex(item => item.id === itemId);
    if (itemIndex === -1) {
      throw new Error('Item not found');
    }

    const item = this.items[itemIndex];
    Object.assign(item, updates, { updatedAt: new Date() });

    // Recalculate item totals if quantities or pricing changed
    if (updates.deliveredQuantity !== undefined || updates.unitPrice !== undefined || 
        updates.discountPercent !== undefined || updates.taxRate !== undefined) {
      
      const deliveredQuantity = updates.deliveredQuantity ?? item.deliveredQuantity;
      const unitPrice = updates.unitPrice ?? item.unitPrice;
      const discountPercent = updates.discountPercent ?? item.discountPercent;
      const taxRate = updates.taxRate ?? item.taxRate;

      item.netAmount = deliveredQuantity * unitPrice * (1 - discountPercent / 100);
      item.taxAmount = item.netAmount * (taxRate / 100);
      item.totalAmount = item.netAmount + item.taxAmount;
    }

    this.calculateTotals();
    this.updatedAt = new Date();
    this.version++;
  }

  public removeItem(itemId: string): void {
    if (this.status !== 'PREPARED') {
      throw new Error('Can only remove items from prepared delivery notes');
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

  public markReadyForPickup(preparedBy: string): void {
    if (this.status !== 'PREPARED') {
      throw new Error('Can only mark prepared delivery notes as ready for pickup');
    }

    if (this.items.length === 0) {
      throw new Error('Cannot mark delivery note ready without items');
    }

    this.status = 'READY_FOR_PICKUP';
    this.preparedAt = new Date();
    this.preparedBy = preparedBy;
    this.updatedBy = preparedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public markInTransit(shippedBy: string, trackingNumber?: string): void {
    if (this.status !== 'READY_FOR_PICKUP') {
      throw new Error('Can only mark ready delivery notes as in transit');
    }

    this.status = 'IN_TRANSIT';
    this.shippedAt = new Date();
    this.shippedBy = shippedBy;
    
    if (trackingNumber && this.carrierInfo) {
      this.carrierInfo.trackingNumber = trackingNumber;
    }

    this.updatedBy = shippedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public markDelivered(deliveredAt?: Date): void {
    if (this.status !== 'IN_TRANSIT') {
      throw new Error('Can only mark in-transit delivery notes as delivered');
    }

    this.status = 'DELIVERED';
    this.deliveredAt = deliveredAt || new Date();
    this.actualDeliveryDate = this.deliveredAt;
    this.updatedAt = new Date();
    this.version++;
  }

  public confirmDelivery(
    confirmedBy: string, 
    deliveryProof?: {
      signatureBase64?: string;
      photoBase64?: string;
      recipientName?: string;
      notes?: string;
    }
  ): void {
    if (this.status !== 'DELIVERED') {
      throw new Error('Can only confirm delivered delivery notes');
    }

    this.status = 'CONFIRMED';
    this.confirmedAt = new Date();
    this.confirmedBy = confirmedBy;
    this.deliveryProof = deliveryProof;
    this.updatedBy = confirmedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public markReturned(returnedBy: string, reason: string): void {
    if (!['IN_TRANSIT', 'DELIVERED'].includes(this.status)) {
      throw new Error('Can only mark in-transit or delivered items as returned');
    }

    this.status = 'RETURNED';
    this.specialInstructions = `RETURNED: ${reason}`;
    this.updatedBy = returnedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public cancel(cancelledBy: string, reason: string): void {
    if (['CONFIRMED', 'CANCELLED'].includes(this.status)) {
      throw new Error('Cannot cancel confirmed or already cancelled delivery notes');
    }

    this.status = 'CANCELLED';
    this.specialInstructions = `CANCELLED: ${reason}`;
    this.updatedBy = cancelledBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public canBeShipped(): boolean {
    return this.status === 'READY_FOR_PICKUP';
  }

  public canBeDelivered(): boolean {
    return this.status === 'IN_TRANSIT';
  }

  public canBeConfirmed(): boolean {
    return this.status === 'DELIVERED';
  }

  public canBeCancelled(): boolean {
    return !['CONFIRMED', 'CANCELLED'].includes(this.status);
  }

  public isOverdue(): boolean {
    const now = new Date();
    return this.plannedDeliveryDate < now && 
           !['DELIVERED', 'CONFIRMED', 'CANCELLED'].includes(this.status);
  }

  public getDeliveryDuration(): number | null {
    if (!this.shippedAt || !this.deliveredAt) {
      return null;
    }
    return Math.round((this.deliveredAt.getTime() - this.shippedAt.getTime()) / (1000 * 60 * 60 * 24));
  }

  public getFullyDeliveredItems(): DeliveryNoteItem[] {
    return this.items.filter(item => item.deliveredQuantity >= item.orderedQuantity);
  }

  public getPartiallyDeliveredItems(): DeliveryNoteItem[] {
    return this.items.filter(item => 
      item.deliveredQuantity > 0 && item.deliveredQuantity < item.orderedQuantity
    );
  }

  public getMissingItems(): DeliveryNoteItem[] {
    return this.items.filter(item => item.deliveredQuantity === 0);
  }

  public toJSON(): any {
    return {
      id: this.id,
      deliveryNoteNumber: this.deliveryNoteNumber,
      orderId: this.orderId,
      customerId: this.customerId,
      status: this.status,
      deliveryAddress: this.deliveryAddress,
      plannedDeliveryDate: this.plannedDeliveryDate.toISOString(),
      actualDeliveryDate: this.actualDeliveryDate?.toISOString(),
      carrierInfo: this.carrierInfo,
      specialInstructions: this.specialInstructions,
      items: this.items.map(item => ({
        ...item,
        createdAt: item.createdAt.toISOString(),
        updatedAt: item.updatedAt.toISOString(),
        expiryDate: item.expiryDate?.toISOString()
      })),
      subtotalAmount: this.subtotalAmount,
      taxAmount: this.taxAmount,
      totalAmount: this.totalAmount,
      weight: this.weight,
      dimensions: this.dimensions,
      packagesCount: this.packagesCount,
      version: this.version,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      createdBy: this.createdBy,
      updatedBy: this.updatedBy,
      preparedAt: this.preparedAt?.toISOString(),
      preparedBy: this.preparedBy,
      shippedAt: this.shippedAt?.toISOString(),
      shippedBy: this.shippedBy,
      deliveredAt: this.deliveredAt?.toISOString(),
      confirmedAt: this.confirmedAt?.toISOString(),
      confirmedBy: this.confirmedBy,
      deliveryProof: this.deliveryProof
    };
  }
}
