export type RequisitionId = string & {
    readonly __brand: 'RequisitionId';
};
export type RequisitionItemId = string & {
    readonly __brand: 'RequisitionItemId';
};
export declare enum RequisitionStatus {
    DRAFT = "draft",
    SUBMITTED = "submitted",
    APPROVAL_PENDING = "approval_pending",
    APPROVED = "approved",
    REJECTED = "rejected",
    ORDERED = "ordered",
    PARTIALLY_ORDERED = "partially_ordered",
    COMPLETED = "completed",
    CANCELLED = "cancelled"
}
export declare enum ApprovalStatus {
    PENDING = "pending",
    APPROVED = "approved",
    REJECTED = "rejected",
    ESCALATED = "escalated",
    AUTO_APPROVED = "auto_approved"
}
export interface RequisitionItem {
    id: RequisitionItemId;
    catalogItemId?: string;
    customItem?: {
        name: string;
        description: string;
        category: string;
        specifications: Record<string, any>;
    };
    quantity: number;
    unitPrice?: number;
    totalPrice?: number;
    currency: string;
    requiredByDate: Date;
    justification: string;
    attachments: string[];
    alternatives?: string[];
    supplierSuggestions?: string[];
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
export declare class Requisition {
    readonly id: RequisitionId;
    title: string;
    description: string;
    status: RequisitionStatus;
    requesterId: string;
    requesterName: string;
    department: string;
    costCenter: string;
    project?: string;
    businessJustification: string;
    urgency: 'low' | 'medium' | 'high' | 'critical';
    expectedDeliveryDate: Date;
    currency: string;
    estimatedTotal: number;
    budgetCode: string | undefined;
    accountCode: string | undefined;
    items: RequisitionItem[];
    approval?: RequisitionApproval;
    purchaseOrders: string[];
    tenantId: string;
    attachments: string[];
    tags: string[];
    readonly createdAt: Date;
    submittedAt?: Date;
    approvedAt?: Date;
    rejectedAt?: Date;
    completedAt?: Date;
    updatedAt: Date;
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
    });
    submit(): void;
    startApproval(approvalWorkflow: RequisitionApproval): void;
    approve(approverId: string, comments?: string): void;
    reject(reason: string, rejectedBy?: string): void;
    convertToPurchaseOrder(poId: string): void;
    complete(): void;
    cancel(reason?: string): void;
    addItem(item: RequisitionItem): void;
    updateItem(itemId: RequisitionItemId, updates: Partial<RequisitionItem>): void;
    removeItem(itemId: RequisitionItemId): void;
    getApprovalProgress(): {
        totalSteps: number;
        completedSteps: number;
        pendingSteps: number;
        rejectedSteps: number;
        currentStepDueDate?: Date;
    };
    getItemSummary(): {
        totalItems: number;
        totalQuantity: number;
        categories: Record<string, number>;
        estimatedValue: number;
    };
    isOverdue(): boolean;
    getDaysSinceSubmission(): number;
    validateForSubmission(): {
        isValid: boolean;
        errors: string[];
    };
    private calculateEstimatedTotal;
    updateTimestamp(): void;
}
//# sourceMappingURL=requisition.d.ts.map