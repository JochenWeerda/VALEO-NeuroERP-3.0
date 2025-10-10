import { randomUUID } from 'crypto';

export type RequisitionId = string & { readonly __brand: 'RequisitionId' };
export type RequisitionItemId = string & { readonly __brand: 'RequisitionItemId' };

export enum RequisitionStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVAL_PENDING = 'approval_pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ORDERED = 'ordered',
  PARTIALLY_ORDERED = 'partially_ordered',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum ApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ESCALATED = 'escalated',
  AUTO_APPROVED = 'auto_approved'
}

export interface RequisitionItem {
  id: RequisitionItemId;
  catalogItemId?: string; // From catalog
  customItem?: {
    name: string;
    description: string;
    category: string;
    specifications: Record<string, any>;
  };
  quantity: number;
  unitPrice?: number; // Estimated or from catalog
  totalPrice?: number;
  currency: string;
  requiredByDate: Date;
  justification: string;
  attachments: string[]; // File references
  alternatives?: string[]; // Alternative item IDs
  supplierSuggestions?: string[]; // Suggested supplier IDs
}

export interface ApprovalStep {
  id: string;
  stepOrder: number;
  approverRole: string;
  approverUserId?: string;
  approvalType: 'serial' | 'parallel' | 'any';
  approvalCriteria: {
    amountThreshold?: number;
    categoryCheck?: string[];
    departmentCheck?: string[];
  };
  status: ApprovalStatus;
  approvedAt?: Date;
  approvedBy?: string;
  comments?: string;
  escalationReason?: string;
  dueDate?: Date;
}

export interface RequisitionApproval {
  workflowId: string;
  steps: ApprovalStep[];
  currentStep: number;
  overallStatus: ApprovalStatus;
  startedAt: Date;
  completedAt?: Date;
  autoApproved: boolean;
  escalationLevel: number;
}

export class Requisition {
  public readonly id: RequisitionId;
  public title: string;
  public description: string;
  public status: RequisitionStatus;

  // Requester Information
  public requesterId: string;
  public requesterName: string;
  public department: string;
  public costCenter: string;
  public project?: string;

  // Business Context
  public businessJustification: string;
  public urgency: 'low' | 'medium' | 'high' | 'critical';
  public expectedDeliveryDate: Date;

  // Financial Information
  public currency: string;
  public estimatedTotal!: number;
  public budgetCode: string | undefined;
  public accountCode: string | undefined;

  // Items
  public items: RequisitionItem[];

  // Approval
  public approval?: RequisitionApproval;

  // Purchase Orders (when converted)
  public purchaseOrders: string[]; // PO IDs

  // Metadata
  public tenantId: string;
  public attachments: string[];
  public tags: string[];
  public readonly createdAt: Date;
  public submittedAt?: Date;
  public approvedAt?: Date;
  public rejectedAt?: Date;
  public completedAt?: Date;
  public updatedAt: Date;

  constructor(props: {
    id?: RequisitionId;
    title: string;
    description: string;
    requesterId: string;
    requesterName: string;
    department: string;
    costCenter: string;
    businessJustification: string;
    urgency?: 'low' | 'medium' | 'high' | 'critical';
    expectedDeliveryDate: Date;
    currency: string;
    items: RequisitionItem[];
    tenantId: string;
    project?: string;
    budgetCode?: string;
    accountCode?: string;
    attachments?: string[];
    tags?: string[];
  }) {
    this.id = props.id || (randomUUID() as RequisitionId);
    this.title = props.title;
    this.description = props.description;
    this.status = RequisitionStatus.DRAFT;
    this.requesterId = props.requesterId;
    this.requesterName = props.requesterName;
    this.department = props.department;
    this.costCenter = props.costCenter;
    this.businessJustification = props.businessJustification;
    this.urgency = props.urgency || 'medium';
    this.expectedDeliveryDate = props.expectedDeliveryDate;
    this.currency = props.currency;
    this.items = props.items;
    this.tenantId = props.tenantId;
    this.project = props.project || undefined;
    this.budgetCode = props.budgetCode || undefined;
    this.accountCode = props.accountCode || undefined;
    this.attachments = props.attachments || [];
    this.tags = props.tags || [];
    this.purchaseOrders = [];
    this.createdAt = new Date();
    this.updatedAt = new Date();

    this.calculateEstimatedTotal();
  }

  // Business Logic Methods
  public submit(): void {
    if (this.status !== RequisitionStatus.DRAFT) {
      throw new Error('Only draft requisitions can be submitted');
    }
    if (this.items.length === 0) {
      throw new Error('Requisition must have at least one item');
    }
    if (!this.businessJustification.trim()) {
      throw new Error('Business justification is required');
    }

    this.status = RequisitionStatus.SUBMITTED;
    this.submittedAt = new Date();
    this.updatedAt = new Date();
  }

  public startApproval(approvalWorkflow: RequisitionApproval): void {
    if (this.status !== RequisitionStatus.SUBMITTED) {
      throw new Error('Requisition must be submitted before approval');
    }

    this.approval = approvalWorkflow;
    this.status = RequisitionStatus.APPROVAL_PENDING;
    this.updatedAt = new Date();
  }

  public approve(approverId: string, comments?: string): void {
    if (this.status !== RequisitionStatus.APPROVAL_PENDING) {
      throw new Error('Requisition must be in approval pending status');
    }
    if (!this.approval) {
      throw new Error('No approval workflow configured');
    }

    // Update current approval step
    const currentStep = this.approval.steps[this.approval.currentStep - 1];
    if (currentStep) {
      currentStep.status = ApprovalStatus.APPROVED;
      currentStep.approvedAt = new Date();
      currentStep.approvedBy = approverId;
      currentStep.comments = comments || undefined;
    }

    // Check if approval is complete
    const allStepsApproved = this.approval.steps.every(step => step.status === ApprovalStatus.APPROVED);
    const anyStepRejected = this.approval.steps.some(step => step.status === ApprovalStatus.REJECTED);

    if (anyStepRejected) {
      this.reject('Approval rejected by one or more approvers');
    } else if (allStepsApproved) {
      this.status = RequisitionStatus.APPROVED;
      this.approvedAt = new Date();
      this.approval.overallStatus = ApprovalStatus.APPROVED;
      this.approval.completedAt = new Date();
    } else {
      // Move to next step
      this.approval.currentStep++;
    }

    this.updatedAt = new Date();
  }

  public reject(reason: string, rejectedBy?: string): void {
    if (this.status === RequisitionStatus.REJECTED || this.status === RequisitionStatus.CANCELLED) {
      return;
    }

    this.status = RequisitionStatus.REJECTED;
    this.rejectedAt = new Date();

    if (this.approval) {
      this.approval.overallStatus = ApprovalStatus.REJECTED;
      this.approval.completedAt = new Date();

      // Mark current step as rejected
      const currentStep = this.approval.steps[this.approval.currentStep - 1];
      if (currentStep) {
        currentStep.status = ApprovalStatus.REJECTED;
        currentStep.comments = reason || undefined;
        currentStep.approvedBy = rejectedBy;
        currentStep.approvedAt = new Date();
      }
    }

    this.updatedAt = new Date();
  }

  public convertToPurchaseOrder(poId: string): void {
    if (this.status !== RequisitionStatus.APPROVED) {
      throw new Error('Only approved requisitions can be converted to purchase orders');
    }

    this.purchaseOrders.push(poId);
    this.status = this.purchaseOrders.length === 1 ? RequisitionStatus.ORDERED : RequisitionStatus.PARTIALLY_ORDERED;
    this.updatedAt = new Date();
  }

  public complete(): void {
    if (this.status !== RequisitionStatus.ORDERED && this.status !== RequisitionStatus.PARTIALLY_ORDERED) {
      throw new Error('Requisition must be ordered before completion');
    }

    this.status = RequisitionStatus.COMPLETED;
    this.completedAt = new Date();
    this.updatedAt = new Date();
  }

  public cancel(reason?: string): void {
    if (this.status === RequisitionStatus.COMPLETED || this.status === RequisitionStatus.CANCELLED) {
      throw new Error('Cannot cancel completed or already cancelled requisition');
    }

    this.status = RequisitionStatus.CANCELLED;
    this.updatedAt = new Date();
  }

  public addItem(item: RequisitionItem): void {
    if (this.status !== RequisitionStatus.DRAFT) {
      throw new Error('Can only add items to draft requisitions');
    }

    this.items.push(item);
    this.calculateEstimatedTotal();
    this.updatedAt = new Date();
  }

  public updateItem(itemId: RequisitionItemId, updates: Partial<RequisitionItem>): void {
    if (this.status !== RequisitionStatus.DRAFT) {
      throw new Error('Can only update items in draft requisitions');
    }

    const item = this.items.find(i => i.id === itemId);
    if (!item) {
      throw new Error('Item not found');
    }

    Object.assign(item, updates);
    this.calculateEstimatedTotal();
    this.updatedAt = new Date();
  }

  public removeItem(itemId: RequisitionItemId): void {
    if (this.status !== RequisitionStatus.DRAFT) {
      throw new Error('Can only remove items from draft requisitions');
    }

    const index = this.items.findIndex(i => i.id === itemId);
    if (index === -1) {
      throw new Error('Item not found');
    }

    this.items.splice(index, 1);
    this.calculateEstimatedTotal();
    this.updatedAt = new Date();
  }

  // Analysis Methods
  public getApprovalProgress(): {
    totalSteps: number;
    completedSteps: number;
    pendingSteps: number;
    rejectedSteps: number;
    currentStepDueDate?: Date;
  } {
    if (!this.approval) {
      return { totalSteps: 0, completedSteps: 0, pendingSteps: 0, rejectedSteps: 0 };
    }

    const totalSteps = this.approval.steps.length;
    const completedSteps = this.approval.steps.filter(s => s.status === ApprovalStatus.APPROVED).length;
    const rejectedSteps = this.approval.steps.filter(s => s.status === ApprovalStatus.REJECTED).length;
    const pendingSteps = totalSteps - completedSteps - rejectedSteps;

    const currentStep = this.approval.steps[this.approval.currentStep - 1];
    const currentStepDueDate = currentStep?.dueDate;

    return {
      totalSteps,
      completedSteps,
      pendingSteps,
      rejectedSteps,
      ...(currentStepDueDate && { currentStepDueDate })
    };
  }

  public getItemSummary(): {
    totalItems: number;
    totalQuantity: number;
    categories: Record<string, number>;
    estimatedValue: number;
  } {
    const totalItems = this.items.length;
    const totalQuantity = this.items.reduce((sum, item) => sum + item.quantity, 0);

    const categories: Record<string, number> = {};
    for (const item of this.items) {
      const category = item.catalogItemId ? 'catalog' : item.customItem?.category || 'other';
      categories[category] = (categories[category] || 0) + 1;
    }

    return {
      totalItems,
      totalQuantity,
      categories,
      estimatedValue: this.estimatedTotal
    };
  }

  public isOverdue(): boolean {
    if (!this.approval) return false;

    const currentStep = this.approval.steps[this.approval.currentStep - 1];
    if (!currentStep?.dueDate) return false;

    return new Date() > currentStep.dueDate;
  }

  public getDaysSinceSubmission(): number {
    if (!this.submittedAt) return 0;
    return Math.floor((Date.now() - this.submittedAt.getTime()) / (24 * 60 * 60 * 1000));
  }

  // Validation Methods
  public validateForSubmission(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.title.trim()) {
      errors.push('Title is required');
    }

    if (!this.businessJustification.trim()) {
      errors.push('Business justification is required');
    }

    if (this.items.length === 0) {
      errors.push('At least one item is required');
    }

    if (this.expectedDeliveryDate < new Date()) {
      errors.push('Expected delivery date cannot be in the past');
    }

    // Validate items
    for (let i = 0; i < this.items.length; i++) {
      const item = this.items[i];
      if (item && item.quantity <= 0) {
        errors.push(`Item ${i + 1}: Quantity must be greater than 0`);
      }
      if (item && !item.catalogItemId && !item.customItem) {
        errors.push(`Item ${i + 1}: Must specify either catalog item or custom item details`);
      }
      if (item && item.requiredByDate < new Date()) {
        errors.push(`Item ${i + 1}: Required by date cannot be in the past`);
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  private calculateEstimatedTotal(): void {
    this.estimatedTotal = this.items.reduce((total, item) => {
      const itemTotal = item.totalPrice || (item.unitPrice || 0) * item.quantity;
      return total + itemTotal;
    }, 0);
  }

  public updateTimestamp(): void {
    this.updatedAt = new Date();
  }
}