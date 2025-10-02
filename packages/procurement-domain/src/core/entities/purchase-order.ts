import { randomUUID } from 'crypto';

export type PurchaseOrderId = string & { readonly __brand: 'PurchaseOrderId' };
export type PurchaseOrderItemId = string & { readonly __brand: 'PurchaseOrderItemId' };

export enum PurchaseOrderStatus {
  DRAFT = 'draft',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  SENT_TO_SUPPLIER = 'sent_to_supplier',
  CONFIRMED = 'confirmed',
  PARTIALLY_RECEIVED = 'partially_received',
  RECEIVED = 'received',
  INVOICED = 'invoiced',
  PAID = 'paid',
  CANCELLED = 'cancelled',
  CLOSED = 'closed'
}

export enum PurchaseOrderType {
  STANDARD = 'standard',
  BLANKET = 'blanket',
  CONTRACT = 'contract',
  RELEASE = 'release'
}

export interface PurchaseOrderItem {
  id: PurchaseOrderItemId;
  requisitionItemId?: string; // Link to original requisition
  catalogItemId?: string; // Link to catalog item
  lineNumber: number;

  // Item Details
  sku: string;
  name: string;
  description: string;
  category: string;

  // Quantity and Pricing
  quantity: number;
  unitOfMeasure: string;
  unitPrice: number;
  lineTotal: number;
  currency: string;

  // Delivery
  deliveryDate: Date;
  shipToLocation: string;

  // Tax and Accounting
  taxCode?: string;
  taxRate?: number;
  taxAmount?: number;
  accountCode?: string;
  costCenter?: string;
  project?: string;

  // Status Tracking
  quantityOrdered: number;
  quantityReceived: number;
  quantityInvoiced: number;
  quantityCancelled: number;

  // Custom Fields
  specifications: Record<string, any>;
  notes?: string;
}

export interface PurchaseOrderTerms {
  paymentTerms: string;
  paymentMethod: string;
  shippingTerms: string;
  deliveryTerms: string;
  warrantyTerms?: string;
  returnPolicy?: string;
  insurance?: string;
  packaging?: string;

  // Commercial Terms
  discountTerms?: string;
  penaltyTerms?: string;
  bonusTerms?: string;

  // Legal Terms
  governingLaw?: string;
  disputeResolution?: string;
}

export interface PurchaseOrderHeader {
  purchaseOrderNumber: string;
  revision: number;
  orderDate: Date;
  requiredDeliveryDate: Date;

  // Parties
  buyer: {
    companyId: string;
    companyName: string;
    contactName: string;
    contactEmail: string;
    contactPhone?: string;
    address: {
      street: string;
      city: string;
      state: string;
      postalCode: string;
      country: string;
    };
  };

  supplier: {
    supplierId: string;
    supplierName: string;
    contactName: string;
    contactEmail: string;
    contactPhone?: string;
    address: {
      street: string;
      city: string;
      state: string;
      postalCode: string;
      country: string;
    };
  };

  // References
  requisitionId?: string;
  contractId?: string;
  projectId?: string;
  costCenter?: string;

  // Shipping and Billing
  shipTo: {
    locationId: string;
    locationName: string;
    address: {
      street: string;
      city: string;
      state: string;
      postalCode: string;
      country: string;
    };
    contactName?: string;
    contactPhone?: string;
  };

  billTo: {
    locationId: string;
    locationName: string;
    address: {
      street: string;
      city: string;
      state: string;
      postalCode: string;
      country: string;
    };
  };
}

export class PurchaseOrder {
  public readonly id: PurchaseOrderId;
  public purchaseOrderNumber: string;
  public revision: number;
  public status: PurchaseOrderStatus;
  public type: PurchaseOrderType;

  // Header Information
  public header: PurchaseOrderHeader;

  // Items
  public items: PurchaseOrderItem[];

  // Terms and Conditions
  public terms: PurchaseOrderTerms;

  // Financial Summary
  public subtotal!: number;
  public taxTotal!: number;
  public discountTotal!: number;
  public shippingTotal!: number;
  public totalAmount!: number;
  public currency!: string;

  // Status Tracking
  public approvalStatus: 'pending' | 'approved' | 'rejected';
  public approvalDate?: Date;
  public approvedBy?: string;

  public sentToSupplierDate?: Date;
  public supplierConfirmationDate?: Date;
  public supplierNotes?: string;

  // Fulfillment Tracking
  public totalOrdered!: number;
  public totalReceived!: number;
  public totalInvoiced!: number;
  public totalCancelled!: number;

  // References and Links
  public requisitionId?: string;
  public contractId?: string;
  public relatedDocuments: string[]; // Invoice IDs, receipt IDs, etc.

  // Audit and Compliance
  public createdBy: string;
  public lastModifiedBy: string;
  public readonly tenantId: string;

  // System Fields
  public readonly createdAt: Date;
  public updatedAt: Date;
  public version: number;

  constructor(props: {
    id?: PurchaseOrderId;
    purchaseOrderNumber?: string;
    type?: PurchaseOrderType;
    header: PurchaseOrderHeader;
    items: PurchaseOrderItem[];
    terms: PurchaseOrderTerms;
    requisitionId?: string;
    contractId?: string;
    createdBy: string;
    tenantId: string;
  }) {
    this.id = props.id || (randomUUID() as PurchaseOrderId);
    this.purchaseOrderNumber = props.purchaseOrderNumber || this.generatePurchaseOrderNumber();
    this.revision = 1;
    this.status = PurchaseOrderStatus.DRAFT;
    this.type = props.type || PurchaseOrderType.STANDARD;

    this.header = props.header;
    this.items = props.items;
    this.terms = props.terms;

    this.requisitionId = props.requisitionId || undefined;
    this.contractId = props.contractId || undefined;
    this.relatedDocuments = [];

    this.createdBy = props.createdBy;
    this.lastModifiedBy = props.createdBy;
    this.tenantId = props.tenantId;

    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.version = 1;

    this.approvalStatus = 'pending';

    // Initialize financial summary
    this.calculateFinancialSummary();

    // Initialize fulfillment tracking
    this.initializeFulfillmentTracking();
  }

  // Business Logic Methods
  public submitForApproval(): void {
    if (this.status !== PurchaseOrderStatus.DRAFT) {
      throw new Error('Only draft purchase orders can be submitted for approval');
    }
    if (this.items.length === 0) {
      throw new Error('Purchase order must have at least one item');
    }

    this.status = PurchaseOrderStatus.PENDING_APPROVAL;
    this.updatedAt = new Date();
    this.version++;
  }

  public approve(approvedBy: string): void {
    if (this.status !== PurchaseOrderStatus.PENDING_APPROVAL) {
      throw new Error('Purchase order must be pending approval');
    }

    this.approvalStatus = 'approved';
    this.approvalDate = new Date();
    this.approvedBy = approvedBy;
    this.status = PurchaseOrderStatus.APPROVED;
    this.updatedAt = new Date();
    this.version++;
  }

  public reject(rejectionReason?: string): void {
    if (this.status !== PurchaseOrderStatus.PENDING_APPROVAL) {
      throw new Error('Purchase order must be pending approval');
    }

    this.approvalStatus = 'rejected';
    this.status = PurchaseOrderStatus.CANCELLED;
    this.updatedAt = new Date();
    this.version++;
  }

  public sendToSupplier(): void {
    if (this.status !== PurchaseOrderStatus.APPROVED) {
      throw new Error('Purchase order must be approved before sending to supplier');
    }

    this.status = PurchaseOrderStatus.SENT_TO_SUPPLIER;
    this.sentToSupplierDate = new Date();
    this.updatedAt = new Date();
    this.version++;
  }

  public confirmBySupplier(confirmationNotes?: string): void {
    if (this.status !== PurchaseOrderStatus.SENT_TO_SUPPLIER) {
      throw new Error('Purchase order must be sent to supplier before confirmation');
    }

    this.status = PurchaseOrderStatus.CONFIRMED;
    this.supplierConfirmationDate = new Date();
    this.supplierNotes = confirmationNotes || undefined;
    this.updatedAt = new Date();
    this.version++;
  }

  public recordReceipt(receipts: Array<{
    itemId: PurchaseOrderItemId;
    quantityReceived: number;
    receiptDate: Date;
    receiptId: string;
  }>): void {
    if (![PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.PARTIALLY_RECEIVED].includes(this.status)) {
      throw new Error('Purchase order must be confirmed or partially received');
    }

    for (const receipt of receipts) {
      const item = this.items.find(i => i.id === receipt.itemId);
      if (!item) {
        throw new Error(`Item ${receipt.itemId} not found in purchase order`);
      }

      if (item.quantityReceived + receipt.quantityReceived > item.quantityOrdered) {
        throw new Error(`Cannot receive more than ordered quantity for item ${receipt.itemId}`);
      }

      item.quantityReceived += receipt.quantityReceived;
    }

    // Update related documents
    this.relatedDocuments.push(...receipts.map(r => r.receiptId));

    // Update status
    this.updateFulfillmentStatus();
    this.updatedAt = new Date();
    this.version++;
  }

  public recordInvoice(invoiceId: string, invoicedItems: Array<{
    itemId: PurchaseOrderItemId;
    quantityInvoiced: number;
  }>): void {
    for (const invoiceItem of invoicedItems) {
      const item = this.items.find(i => i.id === invoiceItem.itemId);
      if (!item) {
        throw new Error(`Item ${invoiceItem.itemId} not found in purchase order`);
      }

      if (item.quantityInvoiced + invoiceItem.quantityInvoiced > item.quantityOrdered) {
        throw new Error(`Cannot invoice more than ordered quantity for item ${invoiceItem.itemId}`);
      }

      item.quantityInvoiced += invoiceItem.quantityInvoiced;
    }

    // Update related documents
    this.relatedDocuments.push(invoiceId);

    // Update status
    if (this.totalInvoiced === this.totalOrdered) {
      this.status = PurchaseOrderStatus.INVOICED;
    }

    this.updatedAt = new Date();
    this.version++;
  }

  public recordPayment(paymentId: string): void {
    if (this.status !== PurchaseOrderStatus.INVOICED) {
      throw new Error('Purchase order must be invoiced before payment');
    }

    this.status = PurchaseOrderStatus.PAID;
    this.relatedDocuments.push(paymentId);
    this.updatedAt = new Date();
    this.version++;
  }

  public close(): void {
    if (![PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.PAID].includes(this.status)) {
      throw new Error('Purchase order must be received or paid before closing');
    }

    this.status = PurchaseOrderStatus.CLOSED;
    this.updatedAt = new Date();
    this.version++;
  }

  public cancel(reason?: string): void {
    if ([PurchaseOrderStatus.CLOSED, PurchaseOrderStatus.CANCELLED].includes(this.status)) {
      throw new Error('Cannot cancel closed or already cancelled purchase order');
    }

    // Cancel remaining quantities
    for (const item of this.items) {
      item.quantityCancelled = item.quantityOrdered - item.quantityReceived - item.quantityInvoiced;
    }

    this.status = PurchaseOrderStatus.CANCELLED;
    this.updateFulfillmentTracking();
    this.updatedAt = new Date();
    this.version++;
  }

  public revise(revisionReason: string, revisedBy: string): PurchaseOrder {
    const revisedPO = new PurchaseOrder({
      purchaseOrderNumber: this.purchaseOrderNumber,
      header: { ...this.header },
      items: this.items.map(item => ({ ...item })),
      terms: { ...this.terms },
      ...(this.requisitionId && { requisitionId: this.requisitionId }),
      ...(this.contractId && { contractId: this.contractId }),
      createdBy: this.createdBy,
      tenantId: this.tenantId
    });

    revisedPO.revision = this.revision + 1;
    revisedPO.status = PurchaseOrderStatus.DRAFT;
    revisedPO.lastModifiedBy = revisedBy;

    return revisedPO;
  }

  // Analysis and Reporting Methods
  public getFulfillmentStatus(): {
    totalOrdered: number;
    totalReceived: number;
    totalInvoiced: number;
    totalCancelled: number;
    fulfillmentRate: number;
    onTimeDelivery: boolean;
    qualityIssues: boolean;
  } {
    const fulfillmentRate = this.totalOrdered > 0 ? this.totalReceived / this.totalOrdered : 0;

    // Check if delivery is on time (simplified)
    const onTimeDelivery = this.items.every(item =>
      item.quantityReceived >= item.quantityOrdered ||
      new Date() <= item.deliveryDate
    );

    return {
      totalOrdered: this.totalOrdered,
      totalReceived: this.totalReceived,
      totalInvoiced: this.totalInvoiced,
      totalCancelled: this.totalCancelled,
      fulfillmentRate,
      onTimeDelivery,
      qualityIssues: false // Would be determined by quality inspections
    };
  }

  public getFinancialSummary(): {
    subtotal: number;
    taxTotal: number;
    discountTotal: number;
    shippingTotal: number;
    totalAmount: number;
    currency: string;
    outstandingAmount: number;
  } {
    const outstandingAmount = this.totalAmount - (this.totalInvoiced * (this.totalAmount / this.totalOrdered));

    return {
      subtotal: this.subtotal,
      taxTotal: this.taxTotal,
      discountTotal: this.discountTotal,
      shippingTotal: this.shippingTotal,
      totalAmount: this.totalAmount,
      currency: this.currency,
      outstandingAmount
    };
  }

  public getDeliverySchedule(): Array<{
    itemId: string;
    itemName: string;
    deliveryDate: Date;
    quantityOrdered: number;
    quantityReceived: number;
    status: 'pending' | 'partial' | 'complete' | 'overdue';
  }> {
    return this.items.map(item => {
      let status: 'pending' | 'partial' | 'complete' | 'overdue' = 'pending';

      if (item.quantityReceived === 0) {
        status = new Date() > item.deliveryDate ? 'overdue' : 'pending';
      } else if (item.quantityReceived < item.quantityOrdered) {
        status = 'partial';
      } else {
        status = 'complete';
      }

      return {
        itemId: item.id,
        itemName: item.name,
        deliveryDate: item.deliveryDate,
        quantityOrdered: item.quantityOrdered,
        quantityReceived: item.quantityReceived,
        status
      };
    });
  }

  public isOverdue(): boolean {
    return this.items.some(item =>
      item.quantityReceived < item.quantityOrdered &&
      new Date() > item.deliveryDate
    );
  }

  public getDaysToDelivery(): number {
    if (this.items.length === 0) return 0;

    const earliestDelivery = this.items.reduce((earliest, item) =>
      item.deliveryDate < earliest ? item.deliveryDate : earliest,
      this.items[0]?.deliveryDate || new Date()
    );

    return Math.ceil((earliestDelivery.getTime() - Date.now()) / (24 * 60 * 60 * 1000));
  }

  // Validation Methods
  public validateForApproval(): { isValid: boolean; errors: string[]; warnings: string[] } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Basic validations
    if (!this.purchaseOrderNumber) {
      errors.push('Purchase order number is required');
    }

    if (this.items.length === 0) {
      errors.push('Purchase order must have at least one item');
    }

    // Header validations
    if (!this.header.buyer.contactEmail) {
      errors.push('Buyer contact email is required');
    }

    if (!this.header.supplier.contactEmail) {
      errors.push('Supplier contact email is required');
    }

    // Item validations
    for (let i = 0; i < this.items.length; i++) {
      const item = this.items[i];

      if (item && item.quantity <= 0) {
        errors.push(`Item ${i + 1}: Quantity must be greater than 0`);
      }

      if (item && item.unitPrice < 0) {
        errors.push(`Item ${i + 1}: Unit price cannot be negative`);
      }

      if (item && item.deliveryDate < new Date()) {
        warnings.push(`Item ${i + 1}: Delivery date is in the past`);
      }

      if (item && !item.accountCode) {
        warnings.push(`Item ${i + 1}: Account code not specified`);
      }
    }

    // Financial validations
    if (this.totalAmount <= 0) {
      errors.push('Total amount must be greater than 0');
    }

    // Contract validations
    if (this.contractId) {
      // Would validate against contract terms
      warnings.push('Contract terms validation not implemented');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  // Private helper methods
  private generatePurchaseOrderNumber(): string {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.random().toString(36).substring(2, 5).toUpperCase();
    return `PO-${timestamp}-${random}`;
  }

  private calculateFinancialSummary(): void {
    this.subtotal = this.items.reduce((sum, item) => sum + item.lineTotal, 0);
    this.taxTotal = this.items.reduce((sum, item) => sum + (item.taxAmount || 0), 0);
    this.discountTotal = 0; // Would be calculated based on terms
    this.shippingTotal = 0; // Would be calculated based on shipping terms
    this.totalAmount = this.subtotal + this.taxTotal - this.discountTotal + this.shippingTotal;
    this.currency = this.items[0]?.currency || 'EUR';
  }

  private initializeFulfillmentTracking(): void {
    this.totalOrdered = this.items.reduce((sum, item) => sum + item.quantityOrdered, 0);
    this.totalReceived = 0;
    this.totalInvoiced = 0;
    this.totalCancelled = 0;
  }

  private updateFulfillmentStatus(): void {
    this.updateFulfillmentTracking();

    if (this.totalReceived === 0) {
      // Status unchanged
    } else if (this.totalReceived < this.totalOrdered) {
      this.status = PurchaseOrderStatus.PARTIALLY_RECEIVED;
    } else if (this.totalReceived === this.totalOrdered) {
      this.status = PurchaseOrderStatus.RECEIVED;
    }
  }

  private updateFulfillmentTracking(): void {
    this.totalOrdered = this.items.reduce((sum, item) => sum + item.quantityOrdered, 0);
    this.totalReceived = this.items.reduce((sum, item) => sum + item.quantityReceived, 0);
    this.totalInvoiced = this.items.reduce((sum, item) => sum + item.quantityInvoiced, 0);
    this.totalCancelled = this.items.reduce((sum, item) => sum + item.quantityCancelled, 0);
  }

  public updateTimestamp(): void {
    this.updatedAt = new Date();
    this.version++;
  }
}