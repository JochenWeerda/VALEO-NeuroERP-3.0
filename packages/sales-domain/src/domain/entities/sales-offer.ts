/**
 * Sales Offer Domain Entity
 * ISO 27001 Communications Security Compliant
 */

import { randomUUID } from 'crypto';

export enum SalesOfferStatus {
  ENTWURF = 'ENTWURF',
  VERSENDET = 'VERSENDET',
  ANGEnommen = 'ANGENOMMEN',
  ABGELEHNT = 'ABGELEHNT',
  ABGELAUFEN = 'ABGELAUFEN'
}

export enum SalesOfferItemType {
  PRODUCT = 'PRODUCT',
  SERVICE = 'SERVICE',
  DISCOUNT = 'DISCOUNT',
  SHIPPING = 'SHIPPING'
}

export class SalesOfferItem {
  public readonly id: string;
  public readonly offerId: string;
  public readonly itemType: SalesOfferItemType;
  public readonly articleId: string | undefined;
  public readonly description: string;
  public readonly quantity: number;
  public readonly unitPrice: number;
  public readonly discountPercent: number;
  public readonly discountAmount: number;
  public readonly totalAmount: number;
  public readonly notes: string | undefined;

  constructor(
    offerId: string,
    itemType: SalesOfferItemType,
    description: string,
    quantity: number,
    unitPrice: number,
    discountPercent: number = 0,
    articleId?: string,
    notes?: string,
    id?: string
  ) {
    this.id = id || randomUUID();
    this.offerId = offerId;
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

  public updateQuantity(quantity: number): SalesOfferItem {
    return new SalesOfferItem(
      this.offerId,
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

  public updateDiscount(discountPercent: number): SalesOfferItem {
    return new SalesOfferItem(
      this.offerId,
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

export interface CreateSalesOfferInput {
  customerId: string;
  subject: string;
  description: string;
  validUntil: Date;
  items: Array<{
    itemType: SalesOfferItemType;
    articleId?: string;
    description: string;
    quantity: number;
    unitPrice: number;
    discountPercent?: number;
    notes?: string;
  }>;
  customerInquiryId?: string;
  contactPerson?: string;
  deliveryDate?: Date;
  paymentTerms?: string;
  currency?: string;
  taxRate?: number;
  notes?: string;
}

export interface UpdateSalesOfferInput {
  subject?: string;
  description?: string;
  validUntil?: Date;
  contactPerson?: string;
  deliveryDate?: Date;
  paymentTerms?: string;
  currency?: string;
  taxRate?: number;
  notes?: string;
}

export type SalesOfferStatusType = SalesOfferStatus;

export class SalesOffer {
  public readonly id: string;
  public readonly offerNumber: string;
  public readonly customerId: string;
  public readonly customerInquiryId: string | undefined;
  public readonly subject: string;
  public readonly description: string;
  public readonly status: SalesOfferStatus;
  public readonly validUntil: Date;
  public readonly contactPerson: string | undefined;
  public readonly deliveryDate: Date | undefined;
  public readonly paymentTerms: string | undefined;
  public readonly currency: string;
  public readonly items: SalesOfferItem[];
  public readonly subtotal: number;
  public readonly taxRate: number;
  public readonly taxAmount: number;
  public readonly totalAmount: number;
  public readonly notes: string | undefined;
  public readonly createdBy: string;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;
  public readonly version: number;

  // Status tracking
  public readonly sentAt: Date | undefined;
  public readonly sentBy: string | undefined;
  public readonly acceptedAt: Date | undefined;
  public readonly acceptedBy: string | undefined;
  public readonly rejectedAt: Date | undefined;
  public readonly rejectedBy: string | undefined;
  public readonly rejectionReason: string | undefined;

  constructor(
    customerId: string,
    subject: string,
    description: string,
    validUntil: Date,
    items: SalesOfferItem[],
    createdBy: string,
    options: {
      id?: string;
      offerNumber?: string;
      customerInquiryId?: string;
      contactPerson?: string;
      deliveryDate?: Date;
      paymentTerms?: string;
      currency?: string;
      taxRate?: number;
      notes?: string;
      status?: SalesOfferStatus;
      version?: number;
      sentAt?: Date;
      sentBy?: string;
      acceptedAt?: Date;
      acceptedBy?: string;
      rejectedAt?: Date;
      rejectedBy?: string;
      rejectionReason?: string;
      createdAt?: Date;
      updatedAt?: Date;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.offerNumber = options.offerNumber || this.generateOfferNumber();
    this.customerId = customerId;
    this.customerInquiryId = options.customerInquiryId;
    this.subject = subject;
    this.description = description;
    this.status = options.status || SalesOfferStatus.ENTWURF;
    this.validUntil = validUntil;
    this.contactPerson = options.contactPerson;
    this.deliveryDate = options.deliveryDate;
    this.paymentTerms = options.paymentTerms;
    this.currency = options.currency || 'EUR';
    this.items = items;
    this.taxRate = options.taxRate || 19.0; // Default German VAT
    this.createdBy = createdBy;
    this.createdAt = options.createdAt || new Date();
    this.updatedAt = options.updatedAt || new Date();
    this.version = options.version || 1;

    // Status tracking
    this.sentAt = options.sentAt;
    this.sentBy = options.sentBy;
    this.acceptedAt = options.acceptedAt;
    this.acceptedBy = options.acceptedBy;
    this.rejectedAt = options.rejectedAt;
    this.rejectedBy = options.rejectedBy;
    this.rejectionReason = options.rejectionReason;

    // Calculate totals
    this.subtotal = this.calculateSubtotal();
    this.taxAmount = (this.subtotal * this.taxRate) / 100;
    this.totalAmount = this.subtotal + this.taxAmount;
    this.notes = options.notes;
  }

  private generateOfferNumber(): string {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const timestamp = now.getTime().toString().slice(-4);
    return `OFF-${year}${month}${day}-${timestamp}`;
  }

  private calculateSubtotal(): number {
    return this.items.reduce((sum, item) => sum + item.totalAmount, 0);
  }

  public addItem(item: SalesOfferItem): SalesOffer {
    if (item.offerId !== this.id) {
      throw new Error('Item does not belong to this offer');
    }

    const newItems = [...this.items, item];
    return new SalesOffer(
      this.customerId,
      this.subject,
      this.description,
      this.validUntil,
      newItems,
      this.createdBy,
      {
        id: this.id,
        offerNumber: this.offerNumber,
        customerInquiryId: this.customerInquiryId,
        contactPerson: this.contactPerson,
        deliveryDate: this.deliveryDate,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        sentAt: this.sentAt,
        sentBy: this.sentBy,
        acceptedAt: this.acceptedAt,
        acceptedBy: this.acceptedBy,
        rejectedAt: this.rejectedAt,
        rejectedBy: this.rejectedBy,
        rejectionReason: this.rejectionReason,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public removeItem(itemId: string): SalesOffer {
    const newItems = this.items.filter(item => item.id !== itemId);
    if (newItems.length === this.items.length) {
      throw new Error('Item not found in offer');
    }

    return new SalesOffer(
      this.customerId,
      this.subject,
      this.description,
      this.validUntil,
      newItems,
      this.createdBy,
      {
        id: this.id,
        offerNumber: this.offerNumber,
        customerInquiryId: this.customerInquiryId,
        contactPerson: this.contactPerson,
        deliveryDate: this.deliveryDate,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        sentAt: this.sentAt,
        sentBy: this.sentBy,
        acceptedAt: this.acceptedAt,
        acceptedBy: this.acceptedBy,
        rejectedAt: this.rejectedAt,
        rejectedBy: this.rejectedBy,
        rejectionReason: this.rejectionReason,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public updateItem(updatedItem: SalesOfferItem): SalesOffer {
    const newItems = this.items.map(item =>
      item.id === updatedItem.id ? updatedItem : item
    );

    return new SalesOffer(
      this.customerId,
      this.subject,
      this.description,
      this.validUntil,
      newItems,
      this.createdBy,
      {
        id: this.id,
        offerNumber: this.offerNumber,
        customerInquiryId: this.customerInquiryId,
        contactPerson: this.contactPerson,
        deliveryDate: this.deliveryDate,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        notes: this.notes,
        status: this.status,
        version: this.version + 1,
        sentAt: this.sentAt,
        sentBy: this.sentBy,
        acceptedAt: this.acceptedAt,
        acceptedBy: this.acceptedBy,
        rejectedAt: this.rejectedAt,
        rejectedBy: this.rejectedBy,
        rejectionReason: this.rejectionReason,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public send(sentBy: string): SalesOffer {
    if (this.status !== SalesOfferStatus.ENTWURF) {
      throw new Error('Only draft offers can be sent');
    }

    return new SalesOffer(
      this.customerId,
      this.subject,
      this.description,
      this.validUntil,
      this.items,
      this.createdBy,
      {
        id: this.id,
        offerNumber: this.offerNumber,
        customerInquiryId: this.customerInquiryId,
        contactPerson: this.contactPerson,
        deliveryDate: this.deliveryDate,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        notes: this.notes,
        status: SalesOfferStatus.VERSENDET,
        version: this.version + 1,
        sentAt: new Date(),
        sentBy: sentBy,
        acceptedAt: this.acceptedAt,
        acceptedBy: this.acceptedBy,
        rejectedAt: this.rejectedAt,
        rejectedBy: this.rejectedBy,
        rejectionReason: this.rejectionReason,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public accept(acceptedBy: string): SalesOffer {
    if (this.status !== SalesOfferStatus.VERSENDET) {
      throw new Error('Only sent offers can be accepted');
    }

    if (new Date() > this.validUntil) {
      throw new Error('Offer has expired');
    }

    return new SalesOffer(
      this.customerId,
      this.subject,
      this.description,
      this.validUntil,
      this.items,
      this.createdBy,
      {
        id: this.id,
        offerNumber: this.offerNumber,
        customerInquiryId: this.customerInquiryId,
        contactPerson: this.contactPerson,
        deliveryDate: this.deliveryDate,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        notes: this.notes,
        status: SalesOfferStatus.ANGEnommen,
        version: this.version + 1,
        sentAt: this.sentAt,
        sentBy: this.sentBy,
        acceptedAt: new Date(),
        acceptedBy: acceptedBy,
        rejectedAt: this.rejectedAt,
        rejectedBy: this.rejectedBy,
        rejectionReason: this.rejectionReason,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public reject(rejectedBy: string, reason: string): SalesOffer {
    if (this.status !== SalesOfferStatus.VERSENDET) {
      throw new Error('Only sent offers can be rejected');
    }

    return new SalesOffer(
      this.customerId,
      this.subject,
      this.description,
      this.validUntil,
      this.items,
      this.createdBy,
      {
        id: this.id,
        offerNumber: this.offerNumber,
        customerInquiryId: this.customerInquiryId,
        contactPerson: this.contactPerson,
        deliveryDate: this.deliveryDate,
        paymentTerms: this.paymentTerms,
        currency: this.currency,
        taxRate: this.taxRate,
        notes: this.notes,
        status: SalesOfferStatus.ABGELEHNT,
        version: this.version + 1,
        sentAt: this.sentAt,
        sentBy: this.sentBy,
        acceptedAt: this.acceptedAt,
        acceptedBy: this.acceptedBy,
        rejectedAt: new Date(),
        rejectedBy: rejectedBy,
        rejectionReason: reason,
        createdAt: this.createdAt,
        updatedAt: new Date()
      }
    );
  }

  public isExpired(): boolean {
    return new Date() > this.validUntil;
  }

  public canBeModified(): boolean {
    return this.status === SalesOfferStatus.ENTWURF;
  }

  public toJSON() {
    return {
      id: this.id,
      offerNumber: this.offerNumber,
      customerId: this.customerId,
      customerInquiryId: this.customerInquiryId,
      subject: this.subject,
      description: this.description,
      status: this.status,
      validUntil: this.validUntil.toISOString(),
      contactPerson: this.contactPerson,
      deliveryDate: this.deliveryDate?.toISOString(),
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
        notes: item.notes
      })),
      subtotal: this.subtotal,
      taxRate: this.taxRate,
      taxAmount: this.taxAmount,
      totalAmount: this.totalAmount,
      notes: this.notes,
      createdBy: this.createdBy,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      version: this.version,
      sentAt: this.sentAt?.toISOString(),
      sentBy: this.sentBy,
      acceptedAt: this.acceptedAt?.toISOString(),
      acceptedBy: this.acceptedBy,
      rejectedAt: this.rejectedAt?.toISOString(),
      rejectedBy: this.rejectedBy,
      rejectionReason: this.rejectionReason
    };
  }
}