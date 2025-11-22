/**
 * Sales Order Entity
 * Complete Order Management with status workflows
 */

import { randomUUID } from 'crypto';

export type SalesOrderStatus = 
  | 'DRAFT'           // Entwurf
  | 'CONFIRMED'       // Bestätigt
  | 'IN_PROGRESS'     // In Bearbeitung
  | 'PARTIALLY_DELIVERED' // Teilgeliefert
  | 'DELIVERED'       // Geliefert
  | 'INVOICED'        // Berechnet
  | 'COMPLETED'       // Abgeschlossen
  | 'CANCELLED';      // Storniert

export type SalesOrderItemType = 'PRODUCT' | 'SERVICE';

export interface SalesOrderItem {
  id: string;
  itemType: SalesOrderItemType;
  articleId?: string;
  description: string;
  quantity: number;
  unitPrice: number;
  discountPercent: number;
  netAmount: number;
  taxRate: number;
  taxAmount: number;
  totalAmount: number;
  deliveryDate?: Date;
  notes?: string;
  deliveredQuantity?: number;
  invoicedQuantity?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateSalesOrderInput {
  customerId: string;
  sourceOfferId?: string;  // Verknüpfung zu Sales Offer
  subject: string;
  description: string;
  deliveryDate: Date;
  contactPerson?: string;
  paymentTerms?: string;
  currency?: string;
  taxRate?: number;
  shippingAddress?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  billingAddress?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  notes?: string;
  items: Omit<SalesOrderItem, 'id' | 'createdAt' | 'updatedAt'>[];
}

export interface UpdateSalesOrderInput {
  subject?: string;
  description?: string;
  deliveryDate?: Date;
  contactPerson?: string;
  paymentTerms?: string;
  currency?: string;
  taxRate?: number;
  shippingAddress?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  billingAddress?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  notes?: string;
}

export class SalesOrder {
  public readonly id: string;
  public readonly orderNumber: string;
  public readonly customerId: string;
  public readonly sourceOfferId?: string;
  public subject: string;
  public description: string;
  public status: SalesOrderStatus;
  public orderDate: Date;
  public deliveryDate: Date;
  public contactPerson?: string;
  public paymentTerms: string;
  public currency: string;
  public taxRate: number;
  public shippingAddress?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  public billingAddress?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  public notes?: string;
  public items: SalesOrderItem[];
  public subtotalAmount: number;
  public taxAmount: number;
  public totalAmount: number;
  public version: number;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public readonly createdBy: string;
  public updatedBy?: string;
  public confirmedAt?: Date;
  public confirmedBy?: string;
  public cancelledAt?: Date;
  public cancelledBy?: string;
  public cancellationReason?: string;

  constructor(
    customerId: string,
    subject: string,
    description: string,
    deliveryDate: Date,
    items: SalesOrderItem[],
    createdBy: string,
    options: {
      id?: string;
      orderNumber?: string;
      sourceOfferId?: string;
      contactPerson?: string;
      paymentTerms?: string;
      currency?: string;
      taxRate?: number;
      shippingAddress?: {
        street: string;
        postalCode: string;
        city: string;
        country: string;
        state?: string;
      };
      billingAddress?: {
        street: string;
        postalCode: string;
        city: string;
        country: string;
        state?: string;
      };
      notes?: string;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.orderNumber = options.orderNumber || this.generateOrderNumber();
    this.customerId = customerId;
    this.sourceOfferId = options.sourceOfferId;
    this.subject = subject;
    this.description = description;
    this.status = 'DRAFT';
    this.orderDate = new Date();
    this.deliveryDate = deliveryDate;
    this.contactPerson = options.contactPerson;
    this.paymentTerms = options.paymentTerms || '30 days net';
    this.currency = options.currency || 'EUR';
    this.taxRate = options.taxRate || 19.0;
    this.shippingAddress = options.shippingAddress;
    this.billingAddress = options.billingAddress;
    this.notes = options.notes;
    this.items = items;
    this.version = 1;
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.createdBy = createdBy;

    // Calculate totals
    this.calculateTotals();
  }

  private generateOrderNumber(): string {
    const now = new Date();
    const year = now.getFullYear().toString().slice(-2);
    const month = (now.getMonth() + 1).toString().padStart(2, '0');
    const day = now.getDate().toString().padStart(2, '0');
    const time = now.getTime().toString().slice(-6);
    return `SO-${year}${month}${day}-${time}`;
  }

  private calculateTotals(): void {
    this.subtotalAmount = this.items.reduce((sum, item) => sum + item.netAmount, 0);
    this.taxAmount = this.items.reduce((sum, item) => sum + item.taxAmount, 0);
    this.totalAmount = this.subtotalAmount + this.taxAmount;
  }

  public updateBasicInfo(updates: UpdateSalesOrderInput, updatedBy: string): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only update draft orders');
    }

    if (updates.subject !== undefined) this.subject = updates.subject;
    if (updates.description !== undefined) this.description = updates.description;
    if (updates.deliveryDate !== undefined) this.deliveryDate = updates.deliveryDate;
    if (updates.contactPerson !== undefined) this.contactPerson = updates.contactPerson;
    if (updates.paymentTerms !== undefined) this.paymentTerms = updates.paymentTerms;
    if (updates.currency !== undefined) this.currency = updates.currency;
    if (updates.taxRate !== undefined) this.taxRate = updates.taxRate;
    if (updates.shippingAddress !== undefined) this.shippingAddress = updates.shippingAddress;
    if (updates.billingAddress !== undefined) this.billingAddress = updates.billingAddress;
    if (updates.notes !== undefined) this.notes = updates.notes;

    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public addItem(item: Omit<SalesOrderItem, 'id' | 'createdAt' | 'updatedAt'>): SalesOrderItem {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only add items to draft orders');
    }

    const newItem: SalesOrderItem = {
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

  public updateItem(itemId: string, updates: Partial<Omit<SalesOrderItem, 'id' | 'createdAt' | 'updatedAt'>>): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only update items in draft orders');
    }

    const itemIndex = this.items.findIndex(item => item.id === itemId);
    if (itemIndex === -1) {
      throw new Error('Item not found');
    }

    const item = this.items[itemIndex];
    Object.assign(item, updates, { updatedAt: new Date() });

    // Recalculate item totals if pricing changed
    if (updates.quantity !== undefined || updates.unitPrice !== undefined || 
        updates.discountPercent !== undefined || updates.taxRate !== undefined) {
      
      const quantity = updates.quantity ?? item.quantity;
      const unitPrice = updates.unitPrice ?? item.unitPrice;
      const discountPercent = updates.discountPercent ?? item.discountPercent;
      const taxRate = updates.taxRate ?? item.taxRate;

      item.netAmount = quantity * unitPrice * (1 - discountPercent / 100);
      item.taxAmount = item.netAmount * (taxRate / 100);
      item.totalAmount = item.netAmount + item.taxAmount;
    }

    this.calculateTotals();
    this.updatedAt = new Date();
    this.version++;
  }

  public removeItem(itemId: string): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only remove items from draft orders');
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

  public confirm(confirmedBy: string): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only confirm draft orders');
    }

    if (this.items.length === 0) {
      throw new Error('Cannot confirm order without items');
    }

    this.status = 'CONFIRMED';
    this.confirmedAt = new Date();
    this.confirmedBy = confirmedBy;
    this.updatedBy = confirmedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public startProgress(updatedBy: string): void {
    if (this.status !== 'CONFIRMED') {
      throw new Error('Can only start progress on confirmed orders');
    }

    this.status = 'IN_PROGRESS';
    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public markPartiallyDelivered(updatedBy: string): void {
    if (!['CONFIRMED', 'IN_PROGRESS'].includes(this.status)) {
      throw new Error('Can only mark confirmed or in-progress orders as partially delivered');
    }

    this.status = 'PARTIALLY_DELIVERED';
    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public markDelivered(updatedBy: string): void {
    if (!['CONFIRMED', 'IN_PROGRESS', 'PARTIALLY_DELIVERED'].includes(this.status)) {
      throw new Error('Invalid status transition to delivered');
    }

    this.status = 'DELIVERED';
    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public markInvoiced(updatedBy: string): void {
    if (this.status !== 'DELIVERED') {
      throw new Error('Can only invoice delivered orders');
    }

    this.status = 'INVOICED';
    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public markCompleted(updatedBy: string): void {
    if (this.status !== 'INVOICED') {
      throw new Error('Can only complete invoiced orders');
    }

    this.status = 'COMPLETED';
    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public cancel(cancelledBy: string, reason: string): void {
    if (['DELIVERED', 'INVOICED', 'COMPLETED', 'CANCELLED'].includes(this.status)) {
      throw new Error('Cannot cancel orders in this status');
    }

    this.status = 'CANCELLED';
    this.cancelledAt = new Date();
    this.cancelledBy = cancelledBy;
    this.cancellationReason = reason;
    this.updatedBy = cancelledBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public canBeDelivered(): boolean {
    return ['CONFIRMED', 'IN_PROGRESS', 'PARTIALLY_DELIVERED'].includes(this.status);
  }

  public canBeInvoiced(): boolean {
    return this.status === 'DELIVERED';
  }

  public canBeCancelled(): boolean {
    return !['DELIVERED', 'INVOICED', 'COMPLETED', 'CANCELLED'].includes(this.status);
  }

  public toJSON(): any {
    return {
      id: this.id,
      orderNumber: this.orderNumber,
      customerId: this.customerId,
      sourceOfferId: this.sourceOfferId,
      subject: this.subject,
      description: this.description,
      status: this.status,
      orderDate: this.orderDate.toISOString(),
      deliveryDate: this.deliveryDate.toISOString(),
      contactPerson: this.contactPerson,
      paymentTerms: this.paymentTerms,
      currency: this.currency,
      taxRate: this.taxRate,
      shippingAddress: this.shippingAddress,
      billingAddress: this.billingAddress,
      notes: this.notes,
      items: this.items.map(item => ({
        ...item,
        createdAt: item.createdAt.toISOString(),
        updatedAt: item.updatedAt.toISOString(),
        deliveryDate: item.deliveryDate?.toISOString()
      })),
      subtotalAmount: this.subtotalAmount,
      taxAmount: this.taxAmount,
      totalAmount: this.totalAmount,
      version: this.version,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      createdBy: this.createdBy,
      updatedBy: this.updatedBy,
      confirmedAt: this.confirmedAt?.toISOString(),
      confirmedBy: this.confirmedBy,
      cancelledAt: this.cancelledAt?.toISOString(),
      cancelledBy: this.cancelledBy,
      cancellationReason: this.cancellationReason
    };
  }
}
