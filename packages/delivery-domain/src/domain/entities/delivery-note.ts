/**
 * Delivery Note Domain Entity
 * ISO 27001 Communications Security Compliant
 * Lieferschein - Dokument zur Bestätigung des Warenversands
 */

import { randomUUID } from 'crypto';

export enum DeliveryNoteStatus {
  ENTWURF = 'ENTWURF',
  VERSENDET = 'VERSENDET',
  GELIEFERT = 'GELIEFERT',
  STORNIERT = 'STORNIERT'
}

export enum DeliveryNoteItemType {
  PRODUCT = 'PRODUCT',
  SERVICE = 'SERVICE'
}

export class DeliveryNoteItem {
  public readonly id: string;
  public readonly deliveryNoteId: string;
  public readonly itemType: DeliveryNoteItemType;
  public readonly articleId: string | undefined;
  public readonly description: string;
  public readonly quantity: number;
  public readonly unitPrice: number;
  public readonly discountPercent: number;
  public readonly discountAmount: number;
  public readonly totalAmount: number;
  public readonly notes: string | undefined;

  constructor(
    deliveryNoteId: string,
    itemType: DeliveryNoteItemType,
    description: string,
    quantity: number,
    unitPrice: number,
    discountPercent: number = 0,
    articleId?: string,
    notes?: string,
    id?: string
  ) {
    this.id = id || randomUUID();
    this.deliveryNoteId = deliveryNoteId;
    this.itemType = itemType;
    this.articleId = articleId;
    this.description = description;
    this.quantity = quantity;
    this.unitPrice = unitPrice;
    this.discountPercent = discountPercent;
    this.discountAmount = (unitPrice * quantity * discountPercent) / 100;
    this.totalAmount = (unitPrice * quantity) - this.discountAmount;
    this.notes = notes;
  }

  public updateQuantity(quantity: number): DeliveryNoteItem {
    return new DeliveryNoteItem(
      this.deliveryNoteId,
      this.itemType,
      this.description,
      quantity,
      this.unitPrice,
      this.discountPercent,
      this.articleId,
      this.notes,
      this.id
    );
  }

  public updateDiscount(discountPercent: number): DeliveryNoteItem {
    return new DeliveryNoteItem(
      this.deliveryNoteId,
      this.itemType,
      this.description,
      this.quantity,
      this.unitPrice,
      discountPercent,
      this.articleId,
      this.notes,
      this.id
    );
  }
}

export interface CreateDeliveryNoteInput {
  salesOfferId?: string;
  customerId: string;
  subject: string;
  description: string;
  deliveryDate: Date;
  shippingAddress: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
  };
  items: Array<{
    itemType: DeliveryNoteItemType;
    articleId?: string;
    description: string;
    quantity: number;
    unitPrice: number;
    discountPercent?: number;
    notes?: string;
  }>;
  carrierId?: string;
  trackingNumber?: string;
  notes?: string;
}

export interface UpdateDeliveryNoteInput {
  subject?: string;
  description?: string;
  deliveryDate?: Date;
  shippingAddress?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
  };
  carrierId?: string;
  trackingNumber?: string;
  notes?: string;
}

export type DeliveryNoteStatusType = DeliveryNoteStatus;

export class DeliveryNote {
  public readonly id: string;
  public readonly deliveryNoteNumber: string;
  public readonly salesOfferId: string | undefined;
  public readonly customerId: string;
  public readonly subject: string;
  public readonly description: string;
  public readonly status: DeliveryNoteStatus;
  public readonly deliveryDate: Date;
  public readonly shippingAddress: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
  };
  public readonly items: DeliveryNoteItem[];
  public readonly subtotal: number;
  public readonly taxRate: number;
  public readonly taxAmount: number;
  public readonly totalAmount: number;
  public readonly carrierId: string | undefined;
  public readonly trackingNumber: string | undefined;
  public readonly notes: string | undefined;
  public readonly createdBy: string;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;
  public readonly version: number;

  // Status tracking
  public readonly shippedAt: Date | undefined;
  public readonly shippedBy: string | undefined;
  public readonly deliveredAt: Date | undefined;
  public readonly deliveredBy: string | undefined;

  constructor(
    customerId: string,
    subject: string,
    description: string,
    deliveryDate: Date,
    shippingAddress: {
      street: string;
      postalCode: string;
      city: string;
      country: string;
    },
    items: DeliveryNoteItem[],
    createdBy: string,
    options: {
      id?: string;
      deliveryNoteNumber?: string;
      salesOfferId?: string;
      carrierId?: string;
      trackingNumber?: string;
      notes?: string;
      status?: DeliveryNoteStatus;
      version?: number;
      shippedAt?: Date;
      shippedBy?: string;
      deliveredAt?: Date;
      deliveredBy?: string;
      createdAt?: Date;
      updatedAt?: Date;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.deliveryNoteNumber = options.deliveryNoteNumber || this.generateDeliveryNoteNumber();
    this.salesOfferId = options.salesOfferId;
    this.customerId = customerId;
    this.subject = subject;
    this.description = description;
    this.status = options.status || DeliveryNoteStatus.ENTWURF;
    this.deliveryDate = deliveryDate;
    this.shippingAddress = shippingAddress;
    this.items = items;
    this.taxRate = 19.0; // Default German VAT
    this.carrierId = options.carrierId;
    this.trackingNumber = options.trackingNumber;
    this.createdBy = createdBy;
    this.createdAt = options.createdAt || new Date();
    this.updatedAt = options.updatedAt || new Date();
    this.version = options.version || 1;

    // Status tracking
    this.shippedAt = options.shippedAt;
    this.shippedBy = options.shippedBy;
    this.deliveredAt = options.deliveredAt;
    this.deliveredBy = options.deliveredBy;

    // Calculate totals
    this.subtotal = this.calculateSubtotal();
    this.taxAmount = (this.subtotal * this.taxRate) / 100;
    this.totalAmount = this.subtotal + this.taxAmount;
    this.notes = options.notes;
  }

  private generateDeliveryNoteNumber(): string {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const timestamp = now.getTime().toString().slice(-4);
    return `DN-${year}${month}${day}-${timestamp}`;
  }

  private calculateSubtotal(): number {
    return this.items.reduce((sum, item) => sum + item.totalAmount, 0);
  }

  public addItem(item: DeliveryNoteItem): DeliveryNote {
    if (item.deliveryNoteId !== this.id) {
      throw new Error('Item does not belong to this delivery note');
    }

    const newItems = [...this.items, item];
    return new DeliveryNote(
      this.customerId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.shippingAddress,
      newItems,
      this.createdBy,
      {
        id: this.id,
        deliveryNoteNumber: this.deliveryNoteNumber,
        salesOfferId: this.salesOfferId,
        carrierId: this.carrierId,
        trackingNumber: this.trackingNumber,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        shippedAt: this.shippedAt,
        shippedBy: this.shippedBy,
        deliveredAt: this.deliveredAt,
        deliveredBy: this.deliveredBy,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public removeItem(itemId: string): DeliveryNote {
    const newItems = this.items.filter(item => item.id !== itemId);
    if (newItems.length === this.items.length) {
      throw new Error('Item not found in delivery note');
    }

    return new DeliveryNote(
      this.customerId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.shippingAddress,
      newItems,
      this.createdBy,
      {
        id: this.id,
        deliveryNoteNumber: this.deliveryNoteNumber,
        salesOfferId: this.salesOfferId,
        carrierId: this.carrierId,
        trackingNumber: this.trackingNumber,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        shippedAt: this.shippedAt,
        shippedBy: this.shippedBy,
        deliveredAt: this.deliveredAt,
        deliveredBy: this.deliveredBy,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public updateItem(updatedItem: DeliveryNoteItem): DeliveryNote {
    const newItems = this.items.map(item =>
      item.id === updatedItem.id ? updatedItem : item
    );

    return new DeliveryNote(
      this.customerId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.shippingAddress,
      newItems,
      this.createdBy,
      {
        id: this.id,
        deliveryNoteNumber: this.deliveryNoteNumber,
        salesOfferId: this.salesOfferId,
        carrierId: this.carrierId,
        trackingNumber: this.trackingNumber,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        shippedAt: this.shippedAt,
        shippedBy: this.shippedBy,
        deliveredAt: this.deliveredAt,
        deliveredBy: this.deliveredBy,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public ship(shippedBy: string, carrierId?: string, trackingNumber?: string): DeliveryNote {
    if (this.status !== DeliveryNoteStatus.ENTWURF) {
      throw new Error('Only draft delivery notes can be shipped');
    }

    return new DeliveryNote(
      this.customerId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.shippingAddress,
      this.items,
      this.createdBy,
      {
        id: this.id,
        deliveryNoteNumber: this.deliveryNoteNumber,
        salesOfferId: this.salesOfferId,
        carrierId: carrierId || this.carrierId,
        trackingNumber: trackingNumber || this.trackingNumber,
        notes: this.notes,
        status: DeliveryNoteStatus.VERSENDET,
        version: this.version + 1,
        shippedAt: new Date(),
        shippedBy: shippedBy,
        deliveredAt: this.deliveredAt,
        deliveredBy: this.deliveredBy,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public deliver(deliveredBy: string): DeliveryNote {
    if (this.status !== DeliveryNoteStatus.VERSENDET) {
      throw new Error('Only shipped delivery notes can be delivered');
    }

    return new DeliveryNote(
      this.customerId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.shippingAddress,
      this.items,
      this.createdBy,
      {
        id: this.id,
        deliveryNoteNumber: this.deliveryNoteNumber,
        salesOfferId: this.salesOfferId,
        carrierId: this.carrierId,
        trackingNumber: this.trackingNumber,
        notes: this.notes,
        status: DeliveryNoteStatus.GELIEFERT,
        version: this.version + 1,
        shippedAt: this.shippedAt,
        shippedBy: this.shippedBy,
        deliveredAt: new Date(),
        deliveredBy: deliveredBy,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public cancel(): DeliveryNote {
    if (this.status === DeliveryNoteStatus.GELIEFERT) {
      throw new Error('Delivered delivery notes cannot be cancelled');
    }

    return new DeliveryNote(
      this.customerId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.shippingAddress,
      this.items,
      this.createdBy,
      {
        id: this.id,
        deliveryNoteNumber: this.deliveryNoteNumber,
        salesOfferId: this.salesOfferId,
        carrierId: this.carrierId,
        trackingNumber: this.trackingNumber,
        notes: this.notes,
        status: DeliveryNoteStatus.STORNIERT,
        version: this.version + 1,
        shippedAt: this.shippedAt,
        shippedBy: this.shippedBy,
        deliveredAt: this.deliveredAt,
        deliveredBy: this.deliveredBy,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public canBeModified(): boolean {
    return this.status === DeliveryNoteStatus.ENTWURF;
  }

  public isOverdue(): boolean {
    return new Date() > this.deliveryDate && this.status !== DeliveryNoteStatus.GELIEFERT;
  }

  public toJSON() {
    return {
      id: this.id,
      deliveryNoteNumber: this.deliveryNoteNumber,
      salesOfferId: this.salesOfferId,
      customerId: this.customerId,
      subject: this.subject,
      description: this.description,
      status: this.status,
      deliveryDate: this.deliveryDate.toISOString(),
      shippingAddress: this.shippingAddress,
      items: this.items.map(item => ({
        id: item.id,
        itemType: item.itemType,
        articleId: item.articleId,
        description: item.description,
        quantity: item.quantity,
        unitPrice: item.unitPrice,
        discountPercent: item.discountPercent,
        discountAmount: item.discountAmount,
        totalAmount: item.totalAmount,
        notes: item.notes
      })),
      subtotal: this.subtotal,
      taxRate: this.taxRate,
      taxAmount: this.taxAmount,
      totalAmount: this.totalAmount,
      carrierId: this.carrierId,
      trackingNumber: this.trackingNumber,
      notes: this.notes,
      createdBy: this.createdBy,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      version: this.version,
      shippedAt: this.shippedAt?.toISOString(),
      shippedBy: this.shippedBy,
      deliveredAt: this.deliveredAt?.toISOString(),
      deliveredBy: this.deliveredBy
    };
  }
}