"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Receipt = exports.QualityIssueType = exports.InspectionStatus = exports.ReceiptStatus = void 0;
const crypto_1 = require("crypto");
var ReceiptStatus;
(function (ReceiptStatus) {
    ReceiptStatus["DRAFT"] = "draft";
    ReceiptStatus["RECEIVED"] = "received";
    ReceiptStatus["INSPECTED"] = "inspected";
    ReceiptStatus["ACCEPTED"] = "accepted";
    ReceiptStatus["REJECTED"] = "rejected";
    ReceiptStatus["PARTIALLY_ACCEPTED"] = "partially_accepted";
    ReceiptStatus["RETURNED"] = "returned";
    ReceiptStatus["CANCELLED"] = "cancelled";
})(ReceiptStatus || (exports.ReceiptStatus = ReceiptStatus = {}));
var InspectionStatus;
(function (InspectionStatus) {
    InspectionStatus["PENDING"] = "pending";
    InspectionStatus["PASSED"] = "passed";
    InspectionStatus["FAILED"] = "failed";
    InspectionStatus["CONDITIONAL"] = "conditional";
})(InspectionStatus || (exports.InspectionStatus = InspectionStatus = {}));
var QualityIssueType;
(function (QualityIssueType) {
    QualityIssueType["DAMAGED"] = "damaged";
    QualityIssueType["WRONG_ITEM"] = "wrong_item";
    QualityIssueType["SHORT_QUANTITY"] = "short_quantity";
    QualityIssueType["POOR_QUALITY"] = "poor_quality";
    QualityIssueType["MISSING_DOCUMENTATION"] = "missing_documentation";
    QualityIssueType["EXPIRED"] = "expired";
    QualityIssueType["CONTAMINATED"] = "contaminated";
    QualityIssueType["OTHER"] = "other";
})(QualityIssueType || (exports.QualityIssueType = QualityIssueType = {}));
class Receipt {
    constructor(props) {
        this.id = props.id || (0, crypto_1.randomUUID)();
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
    markAsReceived() {
        if (this.status !== ReceiptStatus.DRAFT) {
            throw new Error('Only draft receipts can be marked as received');
        }
        this.status = ReceiptStatus.RECEIVED;
        this.header.receiptDate = new Date();
        this.updatedAt = new Date();
    }
    startInspection(inspectionMethod = 'visual') {
        if (this.status !== ReceiptStatus.RECEIVED) {
            throw new Error('Receipt must be received before inspection');
        }
        this.status = ReceiptStatus.INSPECTED;
        this.header.inspectionMethod = inspectionMethod;
        this.updatedAt = new Date();
    }
    completeInspection(inspection) {
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
            }
            else if (inspection.overallResult === InspectionStatus.CONDITIONAL) {
                // Partial acceptance - would need more complex logic
                item.quantityAccepted = Math.floor(item.quantityReceived * inspection.passRate / 100);
                item.quantityRejected = item.quantityReceived - item.quantityAccepted;
            }
            else {
                item.quantityAccepted = item.quantityReceived;
                item.quantityRejected = 0;
            }
        }
        this.calculateSummary();
        this.updateStatus();
        this.updatedAt = new Date();
    }
    acceptReceipt(notes) {
        if (this.status !== ReceiptStatus.INSPECTED) {
            throw new Error('Receipt must be inspected before acceptance');
        }
        this.status = ReceiptStatus.ACCEPTED;
        this.processingNotes = notes;
        this.updatedAt = new Date();
    }
    rejectReceipt(reason, returnItems) {
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
    partiallyAccept(acceptances) {
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
    returnItems(returnItems) {
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
    cancel(reason) {
        if (this.status === ReceiptStatus.CANCELLED) {
            return;
        }
        this.status = ReceiptStatus.CANCELLED;
        this.processingNotes = reason;
        this.updatedAt = new Date();
    }
    // Analysis and Reporting Methods
    getQualityMetrics() {
        const itemsInspected = this.items.filter(item => item.inspectionStatus !== InspectionStatus.PENDING).length;
        const itemsPassed = this.items.filter(item => item.inspectionStatus === InspectionStatus.PASSED ||
            item.inspectionStatus === InspectionStatus.CONDITIONAL).length;
        const itemsFailed = this.items.filter(item => item.inspectionStatus === InspectionStatus.FAILED).length;
        let criticalIssues = 0;
        let majorIssues = 0;
        let minorIssues = 0;
        for (const item of this.items) {
            for (const issue of item.qualityIssues) {
                switch (issue.severity) {
                    case 'critical':
                        criticalIssues++;
                        break;
                    case 'major':
                        majorIssues++;
                        break;
                    case 'minor':
                        minorIssues++;
                        break;
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
    getReceiptSummary() {
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
    getProcessingTime() {
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
    validateForCompletion() {
        const errors = [];
        const warnings = [];
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
    generateReceiptNumber() {
        const timestamp = Date.now().toString().slice(-6);
        const random = Math.random().toString(36).substring(2, 5).toUpperCase();
        return `REC-${timestamp}-${random}`;
    }
    calculateSummary() {
        this.totalItems = this.items.length;
        this.totalQuantityReceived = this.items.reduce((sum, item) => sum + item.quantityReceived, 0);
        this.totalQuantityAccepted = this.items.reduce((sum, item) => sum + item.quantityAccepted, 0);
        this.totalQuantityRejected = this.items.reduce((sum, item) => sum + item.quantityRejected, 0);
        this.totalQuantityReturned = this.items.reduce((sum, item) => sum + item.quantityReturned, 0);
        this.totalValue = this.items.reduce((sum, item) => sum + item.lineTotal, 0);
        this.currency = this.items[0]?.currency || 'EUR';
    }
    updateStatus() {
        const hasAccepted = this.totalQuantityAccepted > 0;
        const hasRejected = this.totalQuantityRejected > 0;
        const allAccepted = this.totalQuantityAccepted === this.totalQuantityReceived;
        const allRejected = this.totalQuantityRejected === this.totalQuantityReceived;
        if (allAccepted && !hasRejected) {
            this.status = ReceiptStatus.ACCEPTED;
        }
        else if (allRejected && !hasAccepted) {
            this.status = ReceiptStatus.REJECTED;
        }
        else if (hasAccepted && hasRejected) {
            this.status = ReceiptStatus.PARTIALLY_ACCEPTED;
        }
        else if (hasRejected) {
            this.status = ReceiptStatus.REJECTED;
        }
        // Otherwise keep current status
    }
    updateTimestamp() {
        this.updatedAt = new Date();
    }
}
exports.Receipt = Receipt;
