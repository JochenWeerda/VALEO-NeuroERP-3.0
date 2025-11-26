/**
 * Sales Invoice Entity
 * Complete Invoice Management with delivery-to-invoice conversion
 */

import { randomUUID } from 'crypto';

export type SalesInvoiceStatus = 
  | 'DRAFT'           // Entwurf
  | 'ISSUED'          // Erstellt
  | 'SENT'            // Versendet
  | 'PAID'            // Bezahlt
  | 'PARTIAL_PAID'    // Teilbezahlt
  | 'OVERDUE'         // Überfällig
  | 'CANCELLED';      // Storniert

export type SalesInvoiceItemType = 'PRODUCT' | 'SERVICE';

export interface SalesInvoiceItem {
  id: string;
  sourceOrderItemId?: string;      // Verknüpfung zum Original-Auftragsposten
  sourceDeliveryItemId?: string;   // Verknüpfung zum Lieferscheinposten
  itemType: SalesInvoiceItemType;
  articleId?: string;
  description: string;
  deliveredQuantity: number;       // Gelieferte Menge
  invoicedQuantity: number;        // Berechnete Menge
  unitPrice: number;
  discountPercent: number;
  netAmount: number;
  taxRate: number;
  taxAmount: number;
  totalAmount: number;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateSalesInvoiceInput {
  customerId: string;
  sourceOrderId?: string;
  sourceDeliveryNoteId?: string;
  subject: string;
  description: string;
  invoiceDate: Date;
  dueDate: Date;
  paymentTerms: string;
  currency: string;
  taxRate: number;
  billingAddress: {
    name: string;
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  notes?: string;
  items: Omit<SalesInvoiceItem, 'id' | 'createdAt' | 'updatedAt'>[];
}

export interface UpdateSalesInvoiceInput {
  subject?: string;
  description?: string;
  invoiceDate?: Date;
  dueDate?: Date;
  paymentTerms?: string;
  currency?: string;
  taxRate?: number;
  billingAddress?: {
    name: string;
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  notes?: string;
}

export class SalesInvoice {
  public readonly id: string;
  public readonly invoiceNumber: string;
  public readonly customerId: string;
  public readonly sourceOrderId?: string;
  public readonly sourceDeliveryNoteId?: string;
  public subject: string;
  public description: string;
  public status: SalesInvoiceStatus;
  public invoiceDate: Date;
  public dueDate: Date;
  public paymentTerms: string;
  public currency: string;
  public taxRate: number;
  public billingAddress: {
    name: string;
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  public notes?: string;
  public items: SalesInvoiceItem[];
  public subtotalAmount: number;
  public taxAmount: number;
  public totalAmount: number;
  public paidAmount: number;
  public remainingAmount: number;
  public version: number;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public readonly createdBy: string;
  public updatedBy?: string;
  public issuedAt?: Date;
  public issuedBy?: string;
  public sentAt?: Date;
  public sentBy?: string;
  public paidAt?: Date;
  public cancelledAt?: Date;
  public cancelledBy?: string;
  public cancellationReason?: string;

  constructor(
    customerId: string,
    subject: string,
    description: string,
    invoiceDate: Date,
    dueDate: Date,
    billingAddress: {
      name: string;
      street: string;
      postalCode: string;
      city: string;
      country: string;
      state?: string;
    },
    items: SalesInvoiceItem[],
    createdBy: string,
    options: {
      id?: string;
      invoiceNumber?: string;
      sourceOrderId?: string;
      sourceDeliveryNoteId?: string;
      paymentTerms?: string;
      currency?: string;
      taxRate?: number;
      notes?: string;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.invoiceNumber = options.invoiceNumber || this.generateInvoiceNumber();
    this.customerId = customerId;
    this.sourceOrderId = options.sourceOrderId;
    this.sourceDeliveryNoteId = options.sourceDeliveryNoteId;
    this.subject = subject;
    this.description = description;
    this.status = 'DRAFT';
    this.invoiceDate = invoiceDate;
    this.dueDate = dueDate;
    this.paymentTerms = options.paymentTerms || '30 days net';
    this.currency = options.currency || 'EUR';
    this.taxRate = options.taxRate || 19.0;
    this.billingAddress = billingAddress;
    this.notes = options.notes;
    this.items = items;
    this.paidAmount = 0;
    this.version = 1;
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.createdBy = createdBy;

    // Calculate totals
    this.calculateTotals();
  }

  private generateInvoiceNumber(): string {
    const now = new Date();
    const year = now.getFullYear().toString().slice(-2);
    const month = (now.getMonth() + 1).toString().padStart(2, '0');
    const day = now.getDate().toString().padStart(2, '0');
    const time = now.getTime().toString().slice(-6);
    return `INV-${year}${month}${day}-${time}`;
  }

  private calculateTotals(): void {
    this.subtotalAmount = this.items.reduce((sum, item) => sum + item.netAmount, 0);
    this.taxAmount = this.items.reduce((sum, item) => sum + item.taxAmount, 0);
    this.totalAmount = this.subtotalAmount + this.taxAmount;
    this.remainingAmount = this.totalAmount - this.paidAmount;
  }

  public updateBasicInfo(updates: UpdateSalesInvoiceInput, updatedBy: string): void {
    if (!['DRAFT'].includes(this.status)) {
      throw new Error('Can only update draft invoices');
    }

    if (updates.subject !== undefined) this.subject = updates.subject;
    if (updates.description !== undefined) this.description = updates.description;
    if (updates.invoiceDate !== undefined) this.invoiceDate = updates.invoiceDate;
    if (updates.dueDate !== undefined) this.dueDate = updates.dueDate;
    if (updates.paymentTerms !== undefined) this.paymentTerms = updates.paymentTerms;
    if (updates.currency !== undefined) this.currency = updates.currency;
    if (updates.taxRate !== undefined) this.taxRate = updates.taxRate;
    if (updates.billingAddress !== undefined) this.billingAddress = updates.billingAddress;
    if (updates.notes !== undefined) this.notes = updates.notes;

    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public addItem(item: Omit<SalesInvoiceItem, 'id' | 'createdAt' | 'updatedAt'>): SalesInvoiceItem {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only add items to draft invoices');
    }

    const newItem: SalesInvoiceItem = {
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

  public updateItem(itemId: string, updates: Partial<Omit<SalesInvoiceItem, 'id' | 'createdAt' | 'updatedAt'>>): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only update items in draft invoices');
    }

    const itemIndex = this.items.findIndex(item => item.id === itemId);
    if (itemIndex === -1) {
      throw new Error('Item not found');
    }

    const item = this.items[itemIndex];
    Object.assign(item, updates, { updatedAt: new Date() });

    // Recalculate item totals if quantities or pricing changed
    if (updates.invoicedQuantity !== undefined || updates.unitPrice !== undefined || 
        updates.discountPercent !== undefined || updates.taxRate !== undefined) {
      
      const invoicedQuantity = updates.invoicedQuantity ?? item.invoicedQuantity;
      const unitPrice = updates.unitPrice ?? item.unitPrice;
      const discountPercent = updates.discountPercent ?? item.discountPercent;
      const taxRate = updates.taxRate ?? item.taxRate;

      item.netAmount = invoicedQuantity * unitPrice * (1 - discountPercent / 100);
      item.taxAmount = item.netAmount * (taxRate / 100);
      item.totalAmount = item.netAmount + item.taxAmount;
    }

    this.calculateTotals();
    this.updatedAt = new Date();
    this.version++;
  }

  public removeItem(itemId: string): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only remove items from draft invoices');
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

  public issue(issuedBy: string): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only issue draft invoices');
    }

    if (this.items.length === 0) {
      throw new Error('Cannot issue invoice without items');
    }

    this.status = 'ISSUED';
    this.issuedAt = new Date();
    this.issuedBy = issuedBy;
    this.updatedBy = issuedBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public send(sentBy: string): void {
    if (this.status !== 'ISSUED') {
      throw new Error('Can only send issued invoices');
    }

    this.status = 'SENT';
    this.sentAt = new Date();
    this.sentBy = sentBy;
    this.updatedBy = sentBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public recordPayment(amount: number, paidBy: string): void {
    if (!['ISSUED', 'SENT', 'PARTIAL_PAID', 'OVERDUE'].includes(this.status)) {
      throw new Error('Invalid status for payment recording');
    }

    if (amount <= 0) {
      throw new Error('Payment amount must be positive');
    }

    if (this.paidAmount + amount > this.totalAmount) {
      throw new Error('Payment amount exceeds remaining balance');
    }

    this.paidAmount += amount;
    this.remainingAmount = this.totalAmount - this.paidAmount;

    if (this.remainingAmount === 0) {
      this.status = 'PAID';
      this.paidAt = new Date();
    } else {
      this.status = 'PARTIAL_PAID';
    }

    this.updatedBy = paidBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public markOverdue(): void {
    if (['SENT', 'PARTIAL_PAID'].includes(this.status) && new Date() > this.dueDate) {
      this.status = 'OVERDUE';
      this.updatedAt = new Date();
      this.version++;
    }
  }

  public cancel(cancelledBy: string, reason: string): void {
    if (['PAID', 'CANCELLED'].includes(this.status)) {
      throw new Error('Cannot cancel paid or already cancelled invoices');
    }

    this.status = 'CANCELLED';
    this.cancelledAt = new Date();
    this.cancelledBy = cancelledBy;
    this.cancellationReason = reason;
    this.updatedBy = cancelledBy;
    this.updatedAt = new Date();
    this.version++;
  }

  public canBeSent(): boolean {
    return this.status === 'ISSUED';
  }

  public canReceivePayment(): boolean {
    return ['ISSUED', 'SENT', 'PARTIAL_PAID', 'OVERDUE'].includes(this.status);
  }

  public canBeCancelled(): boolean {
    return !['PAID', 'CANCELLED'].includes(this.status);
  }

  public isOverdue(): boolean {
    return ['SENT', 'PARTIAL_PAID'].includes(this.status) && new Date() > this.dueDate;
  }

  public getDaysOverdue(): number {
    if (!this.isOverdue()) return 0;
    const now = new Date();
    return Math.ceil((now.getTime() - this.dueDate.getTime()) / (1000 * 60 * 60 * 24));
  }

  public getPaymentProgress(): number {
    if (this.totalAmount === 0) return 0;
    return (this.paidAmount / this.totalAmount) * 100;
  }

  public toJSON(): any {
    return {
      id: this.id,
      invoiceNumber: this.invoiceNumber,
      customerId: this.customerId,
      sourceOrderId: this.sourceOrderId,
      sourceDeliveryNoteId: this.sourceDeliveryNoteId,
      subject: this.subject,
      description: this.description,
      status: this.status,
      invoiceDate: this.invoiceDate.toISOString(),
      dueDate: this.dueDate.toISOString(),
      paymentTerms: this.paymentTerms,
      currency: this.currency,
      taxRate: this.taxRate,
      billingAddress: this.billingAddress,
      notes: this.notes,
      items: this.items.map(item => ({
        ...item,
        createdAt: item.createdAt.toISOString(),
        updatedAt: item.updatedAt.toISOString()
      })),
      subtotalAmount: this.subtotalAmount,
      taxAmount: this.taxAmount,
      totalAmount: this.totalAmount,
      paidAmount: this.paidAmount,
      remainingAmount: this.remainingAmount,
      paymentProgress: this.getPaymentProgress(),
      daysOverdue: this.getDaysOverdue(),
      version: this.version,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      createdBy: this.createdBy,
      updatedBy: this.updatedBy,
      issuedAt: this.issuedAt?.toISOString(),
      issuedBy: this.issuedBy,
      sentAt: this.sentAt?.toISOString(),
      sentBy: this.sentBy,
      paidAt: this.paidAt?.toISOString(),
      cancelledAt: this.cancelledAt?.toISOString(),
      cancelledBy: this.cancelledBy,
      cancellationReason: this.cancellationReason
    };
  }
}
