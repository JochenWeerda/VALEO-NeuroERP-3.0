/**
 * Purchase Order Domain Entity
 * ISO 27001 Communications Security Compliant
 * Bestellung - Dokument zur Regelung des Einkaufs von Waren/Dienstleistungen
 */

import { randomUUID } from 'crypto';

export enum PurchaseOrderStatus {
  ENTWURF = 'ENTWURF',
  FREIGEGEBEN = 'FREIGEGEBEN',
  BESTELLT = 'BESTELLT',
  TEILGELIEFERT = 'TEILGELIEFERT',
  GELIEFERT = 'GELIEFERT',
  STORNIERT = 'STORNIERT'
}

export enum PurchaseOrderItemType {
  PRODUCT = 'PRODUCT',
  SERVICE = 'SERVICE'
}

export class PurchaseOrderItem {
  public readonly id: string;
  public readonly purchaseOrderId: string;
  public readonly itemType: PurchaseOrderItemType;
  public readonly articleId: string | undefined;
  public readonly description: string;
  public readonly quantity: number;
  public readonly unitPrice: number;
  public readonly discountPercent: number;
  public readonly discountAmount: number;
  public readonly totalAmount: number;
  public readonly deliveryDate: Date | undefined;
  public readonly notes: string | undefined;

  constructor(
    purchaseOrderId: string,
    itemType: PurchaseOrderItemType,
    description: string,
    quantity: number,
    unitPrice: number,
    discountPercent: number = 0,
    articleId?: string,
    deliveryDate?: Date,
    notes?: string,
    id?: string
  ) {
    this.id = id || randomUUID();
    this.purchaseOrderId = purchaseOrderId;
    this.itemType = itemType;
    this.articleId = articleId;
    this.description = description;
    this.quantity = quantity;
    this.unitPrice = unitPrice;
    this.discountPercent = discountPercent;
    this.discountAmount = (unitPrice * quantity * discountPercent) / 100;
    this.totalAmount = (unitPrice * quantity) - this.discountAmount;
    this.deliveryDate = deliveryDate;
    this.notes = notes;
  }

  public updateQuantity(quantity: number): PurchaseOrderItem {
    return new PurchaseOrderItem(
      this.purchaseOrderId,
      this.itemType,
      this.description,
      quantity,
      this.unitPrice,
      this.discountPercent,
      this.articleId,
      this.deliveryDate,
      this.notes,
      this.id
    );
  }

  public updateDeliveryDate(deliveryDate: Date): PurchaseOrderItem {
    return new PurchaseOrderItem(
      this.purchaseOrderId,
      this.itemType,
      this.description,
      this.quantity,
      this.unitPrice,
      this.discountPercent,
      this.articleId,
      deliveryDate,
      this.notes,
      this.id
    );
  }
}

export interface CreatePurchaseOrderInput {
  supplierId: string;
  subject: string;
  description: string;
  deliveryDate: Date;
  items: Array<{
    itemType: PurchaseOrderItemType;
    articleId?: string;
    description: string;
    quantity: number;
    unitPrice: number;
    discountPercent?: number;
    deliveryDate?: Date;
    notes?: string;
  }>;
  contactPerson?: string;
  paymentTerms?: string;
  currency?: string;
  taxRate?: number;
  shippingAddress?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
  };
  notes?: string;
}

export interface UpdatePurchaseOrderInput {
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
  };
  notes?: string;
}

export type PurchaseOrderStatusType = PurchaseOrderStatus;

export class PurchaseOrder {
  public readonly id: string;
  public readonly purchaseOrderNumber: string;
  public readonly supplierId: string;
  public readonly subject: string;
  public readonly description: string;
  public readonly status: PurchaseOrderStatus;
  public readonly orderDate: Date;
  public readonly deliveryDate: Date;
  public readonly contactPerson: string | undefined;
  public readonly paymentTerms: string | undefined;
  public readonly currency: string;
  public readonly items: PurchaseOrderItem[];
  public readonly subtotal: number;
  public readonly taxRate: number;
  public readonly taxAmount: number;
  public readonly totalAmount: number;
  public readonly shippingAddress: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
  } | undefined;
  public readonly notes: string | undefined;
  public readonly createdBy: string;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;
  public readonly version: number;

  // Approval workflow
  public readonly approvedAt: Date | undefined;
  public readonly approvedBy: string | undefined;
  public readonly orderedAt: Date | undefined;
  public readonly orderedBy: string | undefined;

  constructor(
    supplierId: string,
    subject: string,
    description: string,
    deliveryDate: Date,
    items: PurchaseOrderItem[],
    createdBy: string,
    options: {
      id?: string;
      purchaseOrderNumber?: string;
      contactPerson?: string | undefined;
      paymentTerms?: string | undefined;
      currency?: string;
      taxRate?: number;
      shippingAddress?: {
        street: string;
        postalCode: string;
        city: string;
        country: string;
      } | undefined;
      notes?: string | undefined;
      status?: PurchaseOrderStatus;
      version?: number;
      approvedAt?: Date | undefined;
      approvedBy?: string | undefined;
      orderedAt?: Date | undefined;
      orderedBy?: string | undefined;
      createdAt?: Date;
      updatedAt?: Date;
      orderDate?: Date;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.purchaseOrderNumber = options.purchaseOrderNumber || this.generatePurchaseOrderNumber();
    this.supplierId = supplierId;
    this.subject = subject;
    this.description = description;
    this.status = options.status || PurchaseOrderStatus.ENTWURF;
    this.orderDate = options.orderDate || new Date();
    this.deliveryDate = deliveryDate;
    this.contactPerson = options.contactPerson;
    this.paymentTerms = options.paymentTerms;
    this.currency = options.currency || 'EUR';
    this.items = items;
    this.taxRate = options.taxRate || 19.0; // Default German VAT
    this.shippingAddress = options.shippingAddress;
    this.createdBy = createdBy;
    this.createdAt = options.createdAt || new Date();
    this.updatedAt = options.updatedAt || new Date();
    this.version = options.version || 1;

    // Approval workflow
    this.approvedAt = options.approvedAt;
    this.approvedBy = options.approvedBy;
    this.orderedAt = options.orderedAt;
    this.orderedBy = options.orderedBy;

    // Calculate totals
    this.subtotal = this.calculateSubtotal();
    this.taxAmount = (this.subtotal * this.taxRate) / 100;
    this.totalAmount = this.subtotal + this.taxAmount;
    this.notes = options.notes;
  }

  private generatePurchaseOrderNumber(): string {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const timestamp = now.getTime().toString().slice(-4);
    return `PO-${year}${month}${day}-${timestamp}`;
  }

  private calculateSubtotal(): number {
    return this.items.reduce((sum, item) => sum + item.totalAmount, 0);
  }

  public addItem(item: PurchaseOrderItem): PurchaseOrder {
    if (item.purchaseOrderId !== this.id) {
      throw new Error('Item does not belong to this purchase order');
    }

    const newItems = [...this.items, item];
    return new PurchaseOrder(
      this.supplierId,
      this.subject,
      this.description,
      this.deliveryDate,
      newItems,
      this.createdBy,
      {
        id: this.id,
        purchaseOrderNumber: this.purchaseOrderNumber,
        contactPerson: this.contactPerson,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        shippingAddress: this.shippingAddress,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        approvedAt: this.approvedAt,
        approvedBy: this.approvedBy,
        orderedAt: this.orderedAt,
        orderedBy: this.orderedBy,
        createdAt: this.createdAt,
        updatedAt: new Date(),
        orderDate: this.orderDate
      }
    );
  }

  public removeItem(itemId: string): PurchaseOrder {
    const newItems = this.items.filter(item => item.id !== itemId);
    if (newItems.length === this.items.length) {
      throw new Error('Item not found in purchase order');
    }

    return new PurchaseOrder(
      this.supplierId,
      this.subject,
      this.description,
      this.deliveryDate,
      newItems,
      this.createdBy,
      {
        id: this.id,
        purchaseOrderNumber: this.purchaseOrderNumber,
        contactPerson: this.contactPerson,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        shippingAddress: this.shippingAddress,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        approvedAt: this.approvedAt,
        approvedBy: this.approvedBy,
        orderedAt: this.orderedAt,
        orderedBy: this.orderedBy,
        createdAt: this.createdAt,
        updatedAt: new Date(),
        orderDate: this.orderDate
      }
    );
  }

  public updateItem(updatedItem: PurchaseOrderItem): PurchaseOrder {
    const newItems = this.items.map(item =>
      item.id === updatedItem.id ? updatedItem : item
    );

    return new PurchaseOrder(
      this.supplierId,
      this.subject,
      this.description,
      this.deliveryDate,
      newItems,
      this.createdBy,
      {
        id: this.id,
        purchaseOrderNumber: this.purchaseOrderNumber,
        contactPerson: this.contactPerson,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        shippingAddress: this.shippingAddress,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        approvedAt: this.approvedAt,
        approvedBy: this.approvedBy,
        orderedAt: this.orderedAt,
        orderedBy: this.orderedBy,
        createdAt: this.createdAt,
        updatedAt: new Date(),
        orderDate: this.orderDate
      }
    );
  }

  public approve(approvedBy: string): PurchaseOrder {
    if (this.status !== PurchaseOrderStatus.ENTWURF) {
      throw new Error('Only draft purchase orders can be approved');
    }

    return new PurchaseOrder(
      this.supplierId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.items,
      this.createdBy,
      {
        id: this.id,
        purchaseOrderNumber: this.purchaseOrderNumber,
        contactPerson: this.contactPerson,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        shippingAddress: this.shippingAddress,
        notes: this.notes,
        status: PurchaseOrderStatus.FREIGEGEBEN,
        version: this.version + 1,
        approvedAt: new Date(),
        approvedBy: approvedBy,
        orderedAt: this.orderedAt,
        orderedBy: this.orderedBy,
        createdAt: this.createdAt,
        updatedAt: new Date(),
        orderDate: this.orderDate
      }
    );
  }

  public order(orderedBy: string): PurchaseOrder {
    if (this.status !== PurchaseOrderStatus.FREIGEGEBEN) {
      throw new Error('Only approved purchase orders can be ordered');
    }

    return new PurchaseOrder(
      this.supplierId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.items,
      this.createdBy,
      {
        id: this.id,
        purchaseOrderNumber: this.purchaseOrderNumber,
        contactPerson: this.contactPerson,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        shippingAddress: this.shippingAddress,
        notes: this.notes,
        status: PurchaseOrderStatus.BESTELLT,
        version: this.version + 1,
        approvedAt: this.approvedAt,
        approvedBy: this.approvedBy,
        orderedAt: new Date(),
        orderedBy: orderedBy,
        createdAt: this.createdAt,
        updatedAt: new Date(),
        orderDate: this.orderDate
      }
    );
  }

  public markPartiallyDelivered(): PurchaseOrder {
    if (this.status !== PurchaseOrderStatus.BESTELLT && this.status !== PurchaseOrderStatus.TEILGELIEFERT) {
      throw new Error('Only ordered purchase orders can be marked as delivered');
    }

    return new PurchaseOrder(
      this.supplierId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.items,
      this.createdBy,
      {
        id: this.id,
        purchaseOrderNumber: this.purchaseOrderNumber,
        contactPerson: this.contactPerson,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        shippingAddress: this.shippingAddress,
        notes: this.notes,
        status: PurchaseOrderStatus.TEILGELIEFERT,
        version: this.version + 1,
        approvedAt: this.approvedAt,
        approvedBy: this.approvedBy,
        orderedAt: this.orderedAt,
        orderedBy: this.orderedBy,
        createdAt: this.createdAt,
        updatedAt: new Date(),
        orderDate: this.orderDate
      }
    );
  }

  public markDelivered(): PurchaseOrder {
    if (this.status !== PurchaseOrderStatus.BESTELLT && this.status !== PurchaseOrderStatus.TEILGELIEFERT) {
      throw new Error('Only ordered purchase orders can be marked as delivered');
    }

    return new PurchaseOrder(
      this.supplierId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.items,
      this.createdBy,
      {
        id: this.id,
        purchaseOrderNumber: this.purchaseOrderNumber,
        contactPerson: this.contactPerson,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        shippingAddress: this.shippingAddress,
        notes: this.notes,
        status: PurchaseOrderStatus.GELIEFERT,
        version: this.version + 1,
        approvedAt: this.approvedAt,
        approvedBy: this.approvedBy,
        orderedAt: this.orderedAt,
        orderedBy: this.orderedBy,
        createdAt: this.createdAt,
        updatedAt: new Date(),
        orderDate: this.orderDate
      }
    );
  }

  public cancel(): PurchaseOrder {
    if (this.status === PurchaseOrderStatus.GELIEFERT) {
      throw new Error('Delivered purchase orders cannot be cancelled');
    }

    return new PurchaseOrder(
      this.supplierId,
      this.subject,
      this.description,
      this.deliveryDate,
      this.items,
      this.createdBy,
      {
        id: this.id,
        purchaseOrderNumber: this.purchaseOrderNumber,
        contactPerson: this.contactPerson,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        shippingAddress: this.shippingAddress,
        notes: this.notes,
        status: PurchaseOrderStatus.STORNIERT,
        version: this.version + 1,
        approvedAt: this.approvedAt,
        approvedBy: this.approvedBy,
        orderedAt: this.orderedAt,
        orderedBy: this.orderedBy,
        createdAt: this.createdAt,
        updatedAt: new Date(),
        orderDate: this.orderDate
      }
    );
  }

  public canBeModified(): boolean {
    return this.status === PurchaseOrderStatus.ENTWURF;
  }

  public canBeApproved(): boolean {
    return this.status === PurchaseOrderStatus.ENTWURF;
  }

  public canBeOrdered(): boolean {
    return this.status === PurchaseOrderStatus.FREIGEGEBEN;
  }

  public isOverdue(): boolean {
    return new Date() > this.deliveryDate && this.status !== PurchaseOrderStatus.GELIEFERT;
  }

  public toJSON() {
    return {
      id: this.id,
      purchaseOrderNumber: this.purchaseOrderNumber,
      supplierId: this.supplierId,
      subject: this.subject,
      description: this.description,
      status: this.status,
      orderDate: this.orderDate.toISOString(),
      deliveryDate: this.deliveryDate.toISOString(),
      contactPerson: this.contactPerson,
      paymentTerms: this.paymentTerms,
      currency: this.currency,
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
        deliveryDate: item.deliveryDate?.toISOString(),
        notes: item.notes
      })),
      subtotal: this.subtotal,
      taxRate: this.taxRate,
      taxAmount: this.taxAmount,
      totalAmount: this.totalAmount,
      shippingAddress: this.shippingAddress,
      notes: this.notes,
      createdBy: this.createdBy,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      version: this.version,
      approvedAt: this.approvedAt?.toISOString(),
      approvedBy: this.approvedBy,
      orderedAt: this.orderedAt?.toISOString(),
      orderedBy: this.orderedBy
    };
  }
}