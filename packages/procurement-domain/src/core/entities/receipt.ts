import { randomUUID } from 'crypto';

export type ReceiptId = string & { readonly __brand: 'ReceiptId' };
export type ReceiptItemId = string & { readonly __brand: 'ReceiptItemId' };

export enum ReceiptStatus {
  DRAFT = 'draft',
  RECEIVED = 'received',
  INSPECTED = 'inspected',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  PARTIALLY_ACCEPTED = 'partially_accepted',
  RETURNED = 'returned',
  CANCELLED = 'cancelled'
}

export enum InspectionStatus {
  PENDING = 'pending',
  PASSED = 'passed',
  FAILED = 'failed',
  CONDITIONAL = 'conditional'
}

export enum QualityIssueType {
  DAMAGED = 'damaged',
  WRONG_ITEM = 'wrong_item',
  SHORT_QUANTITY = 'short_quantity',
  POOR_QUALITY = 'poor_quality',
  MISSING_DOCUMENTATION = 'missing_documentation',
  EXPIRED = 'expired',
  CONTAMINATED = 'contaminated',
  OTHER = 'other'
}

export interface ReceiptItem {
  id: ReceiptItemId;
  purchaseOrderItemId: string;
  sku: string;
  name: string;
  description: string;

  // Quantities
  quantityOrdered: number;
  quantityReceived: number;
  quantityAccepted: number;
  quantityRejected: number;
  quantityReturned: number;

  // Quality Inspection
  inspectionStatus: InspectionStatus;
  qualityIssues: Array<{
    type: QualityIssueType;
    severity: 'minor' | 'major' | 'critical';
    description: string;
    quantityAffected: number;
  }>;

  // Packaging and Documentation
  packagingIntact: boolean;
  documentationComplete: boolean;
  serialNumbers?: string[];
  batchNumbers?: string[];
  expiryDates?: Date[];

  // Location and Storage
  receivedLocation: string;
  storageLocation?: string;
  handlingInstructions?: string;

  // Financial Impact
  unitPrice: number;
  lineTotal: number;
  currency: string;

  // Notes and Comments
  receiverNotes?: string;
  inspectorNotes?: string;
  supplierNotes?: string;
}

export interface ReceiptHeader {
  receiptNumber: string;
  receiptDate: Date;
  receivedBy: string;
  receiverName: string;

  // Supplier Information
  supplierId: string;
  supplierName: string;
  supplierDeliveryNote?: string;
  carrierName?: string;
  carrierTrackingNumber?: string;

  // References
  purchaseOrderId: string;
  purchaseOrderNumber: string;

  // Location Information
  receivingLocation: string;
  locationName: string;

  // Inspection Information
  inspectedBy?: string;
  inspectedAt?: Date;
  inspectionMethod: 'visual' | 'detailed' | 'sampled' | 'automated';
}

export interface QualityInspection {
  inspectionId: string;
  itemId: ReceiptItemId;
  inspectorId: string;
  inspectorName: string;
  inspectionDate: Date;
  inspectionMethod: 'aql' | 'full' | 'automated' | 'supplier_certified';

  // AQL Sampling (if applicable)
  sampleSize?: number;
  acceptanceLevel?: number;
  rejectionLevel?: number;

  // Results
  overallResult: InspectionStatus;
  passRate: number; // 0-100

  // Detailed Findings
  findings: Array<{
    criterion: string;
    result: 'pass' | 'fail';
    severity: 'minor' | 'major' | 'critical';
    notes?: string;
  }>;

  // Actions Required
  actions: Array<{
    action: string;
    responsible: string;
    dueDate: Date;
    priority: 'low' | 'medium' | 'high';
  }>;

  // Documentation
  photos?: string[];
  certificates?: string[];
  testResults?: Record<string, any>;
}

export class Receipt {
  public readonly id: ReceiptId;
  public receiptNumber: string;
  public status: ReceiptStatus;

  // Header Information
  public header: ReceiptHeader;

  // Items
  public items: ReceiptItem[];

  // Quality Inspections
  public inspections: QualityInspection[];

  // Summary Information
  public totalItems!: number;
  public totalQuantityReceived!: number;
  public totalQuantityAccepted!: number;
  public totalQuantityRejected!: number;
  public totalQuantityReturned!: number;

  // Financial Summary
  public totalValue!: number;
  public currency!: string;

  // Processing Information
  public processingNotes?: string;
  public urgent: boolean;
  public requiresFollowUp: boolean;

  // References and Links
  public relatedDocuments: string[]; // Invoice IDs, return IDs, etc.

  // Audit and System Fields
  public readonly tenantId: string;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public createdBy: string;
  public lastModifiedBy: string;

  constructor(props: {
    id?: ReceiptId;
    receiptNumber?: string;
    header: ReceiptHeader;
    items: ReceiptItem[];
    tenantId: string;
    createdBy: string;
    urgent?: boolean;
  }) {
    this.id = props.id || (randomUUID() as ReceiptId);
    this.receiptNumber = props.receiptNumber || this.generateReceiptNumber();
    this.status = ReceiptStatus.DRAFT;
    this.header = props.header;
    this.items = props.items;
    this.inspections = [];
    this.relatedDocuments = [];
    this.tenantId = props.tenantId;
    this.createdBy = props.createdBy;
    this.lastModifiedBy = props.createdBy;
    this.urgent = props.urgent || false;
    this.requiresFollowUp = false;

    this.createdAt = new Date();
    this.updatedAt = new Date();

    this.calculateSummary();
  }

  // Business Logic Methods
  public markAsReceived(): void {
    if (this.status !== ReceiptStatus.DRAFT) {
      throw new Error('Only draft receipts can be marked as received');
    }

    this.status = ReceiptStatus.RECEIVED;
    this.header.receiptDate = new Date();
    this.updatedAt = new Date();
  }

  public startInspection(inspectionMethod: 'visual' | 'detailed' | 'sampled' | 'automated' = 'visual'): void {
    if (this.status !== ReceiptStatus.RECEIVED) {
      throw new Error('Receipt must be received before inspection');
    }

    this.status = ReceiptStatus.INSPECTED;
    this.header.inspectionMethod = inspectionMethod;
    this.updatedAt = new Date();
  }

  public completeInspection(inspection: QualityInspection): void {
    if (this.status !== ReceiptStatus.INSPECTED) {
      throw new Error('Receipt must be in inspection status');
    }

    // Add inspection
    this.inspections.push(inspection);

    // Update item inspection results
    const item = this.items.find(i => i.id === inspection.itemId);
    if (item) {
      item.inspectionStatus = inspection.overallResult;

      // Update quantities based on inspection
      if (inspection.overallResult === InspectionStatus.FAILED) {
        item.quantityRejected = item.quantityReceived;
        item.quantityAccepted = 0;
      } else if (inspection.overallResult === InspectionStatus.CONDITIONAL) {
        // Partial acceptance - would need more complex logic
        item.quantityAccepted = Math.floor(item.quantityReceived * inspection.passRate / 100);
        item.quantityRejected = item.quantityReceived - item.quantityAccepted;
      } else {
        item.quantityAccepted = item.quantityReceived;
        item.quantityRejected = 0;
      }
    }

    this.calculateSummary();
    this.updateStatus();
    this.updatedAt = new Date();
  }

  public acceptReceipt(notes?: string): void {
    if (this.status !== ReceiptStatus.INSPECTED) {
      throw new Error('Receipt must be inspected before acceptance');
    }

    this.status = ReceiptStatus.ACCEPTED;
    this.processingNotes = notes;
    this.updatedAt = new Date();
  }

  public rejectReceipt(reason: string, returnItems?: Array<{ itemId: ReceiptItemId; quantity: number }>): void {
    if (this.status === ReceiptStatus.REJECTED || this.status === ReceiptStatus.CANCELLED) {
      return;
    }

    // Handle returns if specified
    if (returnItems) {
      for (const returnItem of returnItems) {
        const item = this.items.find(i => i.id === returnItem.itemId);
        if (item) {
          item.quantityReturned = Math.min(returnItem.quantity, item.quantityReceived);
        }
      }
    }

    this.status = ReceiptStatus.REJECTED;
    this.processingNotes = reason;
    this.requiresFollowUp = true;
    this.calculateSummary();
    this.updatedAt = new Date();
  }

  public partiallyAccept(acceptances: Array<{ itemId: ReceiptItemId; quantityAccepted: number; notes?: string }>): void {
    for (const acceptance of acceptances) {
      const item = this.items.find(i => i.id === acceptance.itemId);
      if (item) {
        item.quantityAccepted = Math.min(acceptance.quantityAccepted, item.quantityReceived);
        item.quantityRejected = item.quantityReceived - item.quantityAccepted;
        if (acceptance.notes) {
          item.receiverNotes = acceptance.notes;
        }
      }
    }

    this.status = ReceiptStatus.PARTIALLY_ACCEPTED;
    this.calculateSummary();
    this.updatedAt = new Date();
  }

  public returnItems(returnItems: Array<{ itemId: ReceiptItemId; quantity: number; reason: string }>): void {
    for (const returnItem of returnItems) {
      const item = this.items.find(i => i.id === returnItem.itemId);
      if (item) {
        item.quantityReturned = Math.min(returnItem.quantity, item.quantityReceived);
        item.receiverNotes = returnItem.reason;
      }
    }

    this.status = ReceiptStatus.RETURNED;
    this.requiresFollowUp = true;
    this.calculateSummary();
    this.updatedAt = new Date();
  }

  public cancel(reason?: string): void {
    if (this.status === ReceiptStatus.CANCELLED) {
      return;
    }

    this.status = ReceiptStatus.CANCELLED;
    this.processingNotes = reason;
    this.updatedAt = new Date();
  }

  // Analysis and Reporting Methods
  public getQualityMetrics(): {
    overallPassRate: number;
    criticalIssues: number;
    majorIssues: number;
    minorIssues: number;
    itemsInspected: number;
    itemsPassed: number;
    itemsFailed: number;
  } {
    const itemsInspected = this.items.filter(item => item.inspectionStatus !== InspectionStatus.PENDING).length;
    const itemsPassed = this.items.filter(item =>
      item.inspectionStatus === InspectionStatus.PASSED ||
      item.inspectionStatus === InspectionStatus.CONDITIONAL
    ).length;
    const itemsFailed = this.items.filter(item => item.inspectionStatus === InspectionStatus.FAILED).length;

    let criticalIssues = 0;
    let majorIssues = 0;
    let minorIssues = 0;

    for (const item of this.items) {
      for (const issue of item.qualityIssues) {
        switch (issue.severity) {
          case 'critical': criticalIssues++; break;
          case 'major': majorIssues++; break;
          case 'minor': minorIssues++; break;
        }
      }
    }

    return {
      overallPassRate: itemsInspected > 0 ? (itemsPassed / itemsInspected) * 100 : 0,
      criticalIssues,
      majorIssues,
      minorIssues,
      itemsInspected,
      itemsPassed,
      itemsFailed
    };
  }

  public getReceiptSummary(): {
    totalItems: number;
    totalQuantityReceived: number;
    totalQuantityAccepted: number;
    totalQuantityRejected: number;
    totalValue: number;
    currency: string;
    hasQualityIssues: boolean;
    requiresAction: boolean;
  } {
    return {
      totalItems: this.totalItems,
      totalQuantityReceived: this.totalQuantityReceived,
      totalQuantityAccepted: this.totalQuantityAccepted,
      totalQuantityRejected: this.totalQuantityRejected,
      totalValue: this.totalValue,
      currency: this.currency,
      hasQualityIssues: this.items.some(item => item.qualityIssues.length > 0),
      requiresAction: this.requiresFollowUp || this.status === ReceiptStatus.REJECTED
    };
  }

  public getProcessingTime(): {
    timeToReceive: number; // hours from PO to receipt
    timeToInspect: number; // hours from receipt to inspection
    timeToComplete: number; // hours from receipt to completion
    isDelayed: boolean;
  } {
    const now = new Date();
    const receivedAt = this.header.receiptDate;
    const inspectedAt = this.header.inspectedAt;

    const timeToReceive = receivedAt ? (now.getTime() - receivedAt.getTime()) / (1000 * 60 * 60) : 0;
    const timeToInspect = inspectedAt ? (inspectedAt.getTime() - receivedAt.getTime()) / (1000 * 60 * 60) : 0;
    const timeToComplete = receivedAt ? (now.getTime() - receivedAt.getTime()) / (1000 * 60 * 60) : 0;

    // Consider delayed if not completed within 24 hours for standard items
    const isDelayed = !this.urgent && timeToComplete > 24 &&
      [ReceiptStatus.DRAFT, ReceiptStatus.RECEIVED, ReceiptStatus.INSPECTED].includes(this.status);

    return {
      timeToReceive,
      timeToInspect,
      timeToComplete,
      isDelayed
    };
  }

  // Validation Methods
  public validateForCompletion(): { isValid: boolean; errors: string[]; warnings: string[] } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Basic validations
    if (!this.header.receiptDate) {
      errors.push('Receipt date is required');
    }

    if (this.items.length === 0) {
      errors.push('Receipt must have at least one item');
    }

    // Item validations
    for (let i = 0; i < this.items.length; i++) {
      const item = this.items[i];

      if (item && item.quantityReceived <= 0) {
        errors.push(`Item ${i + 1}: Received quantity must be greater than 0`);
      }

      if (item && item.quantityReceived > item.quantityOrdered) {
        warnings.push(`Item ${i + 1}: Received quantity exceeds ordered quantity`);
      }

      if (item && item.inspectionStatus === InspectionStatus.PENDING && this.status === ReceiptStatus.INSPECTED) {
        errors.push(`Item ${i + 1}: Inspection is required before completion`);
      }

      if (item && item.quantityAccepted + item.quantityRejected !== item.quantityReceived) {
        errors.push(`Item ${i + 1}: Accepted + rejected quantities must equal received quantity`);
      }
    }

    // Status validations
    if (this.status === ReceiptStatus.ACCEPTED && this.totalQuantityAccepted === 0) {
      errors.push('Cannot accept receipt with no accepted items');
    }

    if (this.status === ReceiptStatus.REJECTED && this.totalQuantityRejected === 0) {
      errors.push('Cannot reject receipt with no rejected items');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  // Private helper methods
  private generateReceiptNumber(): string {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.random().toString(36).substring(2, 5).toUpperCase();
    return `REC-${timestamp}-${random}`;
  }

  private calculateSummary(): void {
    this.totalItems = this.items.length;
    this.totalQuantityReceived = this.items.reduce((sum, item) => sum + item.quantityReceived, 0);
    this.totalQuantityAccepted = this.items.reduce((sum, item) => sum + item.quantityAccepted, 0);
    this.totalQuantityRejected = this.items.reduce((sum, item) => sum + item.quantityRejected, 0);
    this.totalQuantityReturned = this.items.reduce((sum, item) => sum + item.quantityReturned, 0);
    this.totalValue = this.items.reduce((sum, item) => sum + item.lineTotal, 0);
    this.currency = this.items[0]?.currency || 'EUR';
  }

  private updateStatus(): void {
    const hasAccepted = this.totalQuantityAccepted > 0;
    const hasRejected = this.totalQuantityRejected > 0;
    const allAccepted = this.totalQuantityAccepted === this.totalQuantityReceived;
    const allRejected = this.totalQuantityRejected === this.totalQuantityReceived;

    if (allAccepted && !hasRejected) {
      this.status = ReceiptStatus.ACCEPTED;
    } else if (allRejected && !hasAccepted) {
      this.status = ReceiptStatus.REJECTED;
    } else if (hasAccepted && hasRejected) {
      this.status = ReceiptStatus.PARTIALLY_ACCEPTED;
    } else if (hasRejected) {
      this.status = ReceiptStatus.REJECTED;
    }
    // Otherwise keep current status
  }

  public updateTimestamp(): void {
    this.updatedAt = new Date();
  }
}