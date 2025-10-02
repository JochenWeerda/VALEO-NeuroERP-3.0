"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Requisition = exports.ApprovalStatus = exports.RequisitionStatus = void 0;
const crypto_1 = require("crypto");
var RequisitionStatus;
(function (RequisitionStatus) {
    RequisitionStatus["DRAFT"] = "draft";
    RequisitionStatus["SUBMITTED"] = "submitted";
    RequisitionStatus["APPROVAL_PENDING"] = "approval_pending";
    RequisitionStatus["APPROVED"] = "approved";
    RequisitionStatus["REJECTED"] = "rejected";
    RequisitionStatus["ORDERED"] = "ordered";
    RequisitionStatus["PARTIALLY_ORDERED"] = "partially_ordered";
    RequisitionStatus["COMPLETED"] = "completed";
    RequisitionStatus["CANCELLED"] = "cancelled";
})(RequisitionStatus || (exports.RequisitionStatus = RequisitionStatus = {}));
var ApprovalStatus;
(function (ApprovalStatus) {
    ApprovalStatus["PENDING"] = "pending";
    ApprovalStatus["APPROVED"] = "approved";
    ApprovalStatus["REJECTED"] = "rejected";
    ApprovalStatus["ESCALATED"] = "escalated";
    ApprovalStatus["AUTO_APPROVED"] = "auto_approved";
})(ApprovalStatus || (exports.ApprovalStatus = ApprovalStatus = {}));
class Requisition {
    id;
    title;
    description;
    status;
    // Requester Information
    requesterId;
    requesterName;
    department;
    costCenter;
    project;
    // Business Context
    businessJustification;
    urgency;
    expectedDeliveryDate;
    // Financial Information
    currency;
    estimatedTotal;
    budgetCode;
    accountCode;
    // Items
    items;
    // Approval
    approval;
    // Purchase Orders (when converted)
    purchaseOrders; // PO IDs
    // Metadata
    tenantId;
    attachments;
    tags;
    createdAt;
    submittedAt;
    approvedAt;
    rejectedAt;
    completedAt;
    updatedAt;
    constructor(props) {
        this.id = props.id || (0, crypto_1.randomUUID)();
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
    submit() {
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
    startApproval(approvalWorkflow) {
        if (this.status !== RequisitionStatus.SUBMITTED) {
            throw new Error('Requisition must be submitted before approval');
        }
        this.approval = approvalWorkflow;
        this.status = RequisitionStatus.APPROVAL_PENDING;
        this.updatedAt = new Date();
    }
    approve(approverId, comments) {
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
        }
        else if (allStepsApproved) {
            this.status = RequisitionStatus.APPROVED;
            this.approvedAt = new Date();
            this.approval.overallStatus = ApprovalStatus.APPROVED;
            this.approval.completedAt = new Date();
        }
        else {
            // Move to next step
            this.approval.currentStep++;
        }
        this.updatedAt = new Date();
    }
    reject(reason, rejectedBy) {
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
    convertToPurchaseOrder(poId) {
        if (this.status !== RequisitionStatus.APPROVED) {
            throw new Error('Only approved requisitions can be converted to purchase orders');
        }
        this.purchaseOrders.push(poId);
        this.status = this.purchaseOrders.length === 1 ? RequisitionStatus.ORDERED : RequisitionStatus.PARTIALLY_ORDERED;
        this.updatedAt = new Date();
    }
    complete() {
        if (this.status !== RequisitionStatus.ORDERED && this.status !== RequisitionStatus.PARTIALLY_ORDERED) {
            throw new Error('Requisition must be ordered before completion');
        }
        this.status = RequisitionStatus.COMPLETED;
        this.completedAt = new Date();
        this.updatedAt = new Date();
    }
    cancel(reason) {
        if (this.status === RequisitionStatus.COMPLETED || this.status === RequisitionStatus.CANCELLED) {
            throw new Error('Cannot cancel completed or already cancelled requisition');
        }
        this.status = RequisitionStatus.CANCELLED;
        this.updatedAt = new Date();
    }
    addItem(item) {
        if (this.status !== RequisitionStatus.DRAFT) {
            throw new Error('Can only add items to draft requisitions');
        }
        this.items.push(item);
        this.calculateEstimatedTotal();
        this.updatedAt = new Date();
    }
    updateItem(itemId, updates) {
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
    removeItem(itemId) {
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
    getApprovalProgress() {
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
    getItemSummary() {
        const totalItems = this.items.length;
        const totalQuantity = this.items.reduce((sum, item) => sum + item.quantity, 0);
        const categories = {};
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
    isOverdue() {
        if (!this.approval)
            return false;
        const currentStep = this.approval.steps[this.approval.currentStep - 1];
        if (!currentStep || !currentStep.dueDate)
            return false;
        return new Date() > currentStep.dueDate;
    }
    getDaysSinceSubmission() {
        if (!this.submittedAt)
            return 0;
        return Math.floor((Date.now() - this.submittedAt.getTime()) / (24 * 60 * 60 * 1000));
    }
    // Validation Methods
    validateForSubmission() {
        const errors = [];
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
    calculateEstimatedTotal() {
        this.estimatedTotal = this.items.reduce((total, item) => {
            const itemTotal = item.totalPrice || (item.unitPrice || 0) * item.quantity;
            return total + itemTotal;
        }, 0);
    }
    updateTimestamp() {
        this.updatedAt = new Date();
    }
}
exports.Requisition = Requisition;
